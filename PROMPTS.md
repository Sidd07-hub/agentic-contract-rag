# My RAG Pipeline Refinement Diary & Prompts Log

Here is the actual documentation of how I started this contract extraction project, the prompts I used, the walls I hit with the AI, and how I ended up fixing the code to make it work correctly.

---

## How I Started This Project (My Day 1 Prompt)

When I first sat down after reading the assignment brief, I wanted to map out a quick prototype using local embeddings and a vector store. This is the exact prompt I shot over to get a basic structure going:

```text
I need to build a prototype RAG (Retrieval-Augmented Generation) pipeline for a coding challenge. The goal is to take a messy legal contract PDF, extract specific fields from it, and return a clean JSON object that matches a strict JSON Schema. 

The contract PDF contains some tricky elements: multi-page clauses, nested bullet points, and tables (like milestone payment tables and fee schedules). The schema requires details like party names, addresses, signatory titles, dates, fees, and a milestones array. 

One of the biggest constraints is that the system needs to be extremely critical. It shouldn't just extract data; it needs to validate it. If a field isn't in the document, it needs to return null instead of hallucinating, and it needs to actively catch contradictions or errors in the text (like if someone is called a CFO on page 2 but signed as COO on page 8). All of these discrepancies must be logged in a "validation_notes" array in the output JSON.

Can you help me design the architecture for this pipeline in Python? Recommend a solid tech stack (preferably using libraries like PyMuPDF or pdfplumber, FAISS or similar vector DB, and Sentence Transformers for local embeddings) and outline a folder structure. Let's keep it clean, modular, and explain how the extraction and validator agents would work together.
```

---

## Technical Refinements & Debugging the AI

During development, the AI wrote several pieces of code that looked correct on the surface but failed completely under real-world contract constraints. Here are the four biggest issues I had to catch and rewrite myself.

### 1. Naive Text Splitting Breaking Tables
The AI initially tried to split the contract using a standard character-based recursive splitter. The code it gave me looked like this:

```python
# What the AI generated for chunking
from langchain.text_splitter import RecursiveCharacterTextSplitter

def naive_chunk_document(text: str) -> list[str]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", " ", ""]
    )
    return splitter.split_text(text)
```

**Why it failed:** 
This splitter is completely blind to document layout. When it hit the milestone payments table in our sample PDF, it split it right in the middle of a row. This separated the milestone ID (like "M1") and the deliverable text from the actual target date and fee percentage. When this chunk was embedded, it lost its association, causing the LLM to return `null` or wrong values for the milestones. It also split important legal clauses in half, removing their heading context.

**The Fix:**
I threw out the recursive character splitter and wrote a custom layout-aware chunker in `app/chunking/semantic_chunker.py`. My chunker parses page-by-page, extracts tables as unified objects using `pdfplumber`, and splits text blocks based on major numbered section headings (like `1.`, `2.`, `3.`) and schedule prefixes (`SCHEDULE A`). This keeps tables and legal clauses fully intact.

```python
# The custom logic I wrote to detect section boundaries
@staticmethod
def _is_major_heading(line: str) -> bool:
    line = line.strip()
    if re.match(r"^\d+\.\s+", line):
        if re.match(r"^\d+\.\d+", line):  # Skip subsections (e.g. 4.1, 4.2)
            return False
        return True
    if re.match(r"^SCHEDULE\s+[A-Z]\s+[—\-:]\s+.+", line, re.IGNORECASE):
        return True
    return False
```

---

### 2. The Vague Retrieval/Extraction Trap
The AI tried to query the vector store using a broad "parent-level" approach. It mapped all sub-fields under `parties` and `fees` to the same query:

```python
# The generic queries the AI wrote
FIELD_QUERIES = {
    "parties": "provider client legal name registered office address signatory",
    "fees": "headline fee total payable currency reimbursement cap"
}
```

**Why it failed:**
In the extraction agent, when the retriever asked for `parties.provider.legal_name` or `parties.client.signatory_title`, the pipeline resolved to the generic parent query `"parties"`. 

Because of this, the vector store returned a mix of chunks containing both client and provider signature blocks. The LLM ended up extracting the provider's title (`"Designated Partner"`) and assigning it to the client signatory (Siddhartha Patil), who was actually the `Chief Operating Officer (COO)` according to the document text.

**The Fix:**
I refactored `app/retrieval/field_queries.py` to specify targeted, leaf-level natural language queries for every single field in the JSON Schema. This ensures that the vector store returns the precise page context for each party and fee detail:

```python
# Specific queries I wrote to resolve mapping errors
FIELD_QUERIES = {
    "parties.provider.legal_name": "provider company name service provider entity legal name party hereinafter referred to as provider",
    "parties.provider.signatory_title": "provider signatory title designation chief officer director on behalf of provider title role",
    "parties.client.legal_name": "client company name customer entity legal name party hereinafter referred to as client",
    "parties.client.signatory_title": "client signatory title designation chief officer director on behalf of client title role"
}
```

---

### 3. The "Stupid" Schema Validator
The AI originally implemented a validator that simply ran the extracted JSON through a basic JSON Schema validation library:

```python
# Simple validator generated by the AI
from jsonschema import validate

class ValidatorAgent:
    def __init__(self, schema):
        self.schema = schema
        
    def validate(self, data):
        validate(instance=data, schema=self.schema)
        return data
```

**Why it failed:**
Standard schema checks only verify syntactic formats (like checking if a date is a string). It cannot check for semantic problems. 

For instance, the sample contract had duplicate milestone dates (M1 and M2 both set to June 5, 2026) and a title mismatch (Siddhartha Patil signed as "Designated Partner" but was introduced as "Chief Operating Officer"). The AI's validator passed the JSON structure because it was technically valid, completely failing to log these critical issues in `validation_notes`.

**The Fix:**
I completely rewrote `app/agents/validator_agent.py` to use a dual-pass approach. The first pass handles the structural schema checks, while the second pass extracts the full raw text of the contract and feeds it alongside the extracted JSON to the LLM via a custom auditing prompt (`app/prompts/validation_prompt.py`). This allows the LLM to critically inspect the document for logical clashes.

```python
# Dual-pass LLM validation logic I implemented
def _validate_with_llm(self, extracted: dict[str, Any], notes: list[dict[str, str]]) -> None:
    prompt = build_validation_prompt(
        extracted_json=extracted,
        full_document_text=self.full_document_text,
    )
    response = self.llm.generate_with_system(
        prompt=prompt,
        system_prompt=VALIDATION_SYSTEM_PROMPT,
        temperature=0.0
    )
    parsed = json.loads(response)
    notes.extend(parsed.get("issues", []))
```

---

### 4. Paid Fallback & Free-Tier Rate Limits
When implementing the OpenAI client, the AI wrote a generic client class that checked both `GITHUB_TOKEN` and `OPENAI_API_KEY`, default-routing requests blindly with no error handling:

```python
# Original client configuration from the AI
class OpenAIProvider(BaseLLM):
    def __init__(self) -> None:
        self.api_key = GITHUB_TOKEN or OPENAI_API_KEY
        self.client = OpenAI(api_key=self.api_key, base_url=OPENAI_API_BASE)
```

**Why it failed:**
1. **Financial Risk**: If the free `GITHUB_TOKEN` was missing, it fell back to `OPENAI_API_KEY` and silently routed requests to my paid OpenAI account.
2. **Rate Limit Crash**: The GitHub Models free tier has a strict limit of 10 requests per minute. Sequentially running 21 extraction fields triggered a `RateLimitError` (HTTP 429) at field 11, crashing the pipeline.
3. **Wait Time Parser Bug**: When I tried to implement backoff, the parser got stuck because the GitHub API returned wait times in milliseconds (e.g. `Please wait 84995 milliseconds before retrying`), causing my simple regex search to wait for 23 hours instead of 85 seconds.

**The Fix:**
I rewrote `app/llm/openai_provider.py` to only accept keys starting with `github_pat_`, ensuring we stay strictly on the free tier. I also switched the default model to `gpt-4o-mini` (faster, lower rate limit window) and wrote a robust rate-limit handler that catches 429 errors, parses both second and millisecond values, and automatically pauses the runner before retrying:

```python
# Robust backoff parsing I wrote
@staticmethod
def _parse_wait_time(error_message: str) -> int:
    match_ms = re.search(r"wait (\d+)\s*(ms|millisecond)", error_message, re.IGNORECASE)
    if match_ms:
        return max(1, int(match_ms.group(1)) // 1000) + 2

    match_sec = re.search(r"wait (\d+)\s*(s|second)", error_message, re.IGNORECASE)
    if match_sec:
        sec = int(match_sec.group(1))
        if sec > 3600:  # Caught a millisecond value labeled as seconds
            return max(1, sec // 1000) + 2
        return sec + 2

    return 62  # Safe fallback
```

---

## Reflections on AI Blindspots in RAG Pipelines

Working with the LLM on this project showed me that AI models are heavily biased toward the "first-seen" information and struggle with logical synthesis. For example, during fee extraction, the LLM consistently extracted the $75,000 professional fee in Section 4.1 and wrote it down as both the `headline_fee` and the `total_payable`. It completely ignored the surcharge and onboarding clauses in Section 4.3 that modified that amount, because it didn't think to do the arithmetic across sections. 

The AI also struggled to understand the structural layout of data. It treated tables as raw sentences rather than atomic data grids, necessitating the custom layout parser to prevent milestones from losing their target dates. It also repeatedly assumed that `validation_notes` was just a debugging list for schema warnings, rather than a place to report legal contradictions. Ultimately, while the AI is incredibly fast at generating base structures, it takes a human developer to introduce critical routing checks, enforce strict local data boundaries, and audit the output for semantic accuracy.
