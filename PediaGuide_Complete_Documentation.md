# PediaGuide AI --- Complete Project Documentation

## 1. Project Overview

**PediaGuide AI** is an evidence-grounded pediatric information
assistant designed to help users understand a child's health situation
using retrieved medical evidence.

The system is intended to:

-   explain relevant medical terms in understandable language
-   identify information that may matter in a child's situation
-   explain what information a user may need to monitor
-   help users prepare questions for a healthcare professional
-   provide source-backed information
-   use the child's age when retrieving age-appropriate evidence
-   preserve conversation context for follow-up questions

PediaGuide AI is an **information and evidence-support system**, not an
autonomous pediatrician.

It should not be treated as a replacement for a qualified healthcare
professional or emergency medical service.

------------------------------------------------------------------------

# 2. Main Goals

The main goals of the project are:

1.  Build a practical Retrieval-Augmented Generation (RAG) application.
2.  Use a curated pediatric medical knowledge base rather than relying
    only on the LLM's internal knowledge.
3.  Retrieve evidence relevant to the child's age and question.
4.  Provide source information with generated answers.
5.  Maintain conversation context for follow-up questions.
6.  Provide a simple web interface.
7.  Demonstrate a complete AI application using FastAPI, embeddings,
    Qdrant, and an LLM API.

------------------------------------------------------------------------

# 3. Important Safety Boundaries

PediaGuide AI is designed as an educational and information-support
application.

The system should:

-   use retrieved medical evidence as the primary information source
-   consider the child's age
-   communicate uncertainty when evidence is insufficient
-   avoid inventing sources or medical facts
-   avoid presenting a definite diagnosis
-   avoid prescribing medication
-   avoid calculating medication doses
-   encourage professional medical evaluation when appropriate
-   clearly communicate that emergency situations require appropriate
    emergency care

The project is a portfolio/learning implementation and is **not
clinically validated or approved for real-world clinical
decision-making**.

A real clinical deployment would require appropriate clinical
validation, privacy/security controls, governance, regulatory review,
and professional oversight.

------------------------------------------------------------------------

# 4. High-Level Features

## 4.1 Pediatric Question Handling

The system accepts pediatric health questions and uses the child's age
as part of the retrieval process.

Example:

> My 3-year-old has fever and cough. What should I know?

The system extracts the age and uses it to retrieve more appropriate
evidence.

------------------------------------------------------------------------

## 4.2 Age-Aware Retrieval

Age is important because pediatric guidance can differ between:

-   newborns
-   young infants
-   children
-   older children
-   adolescents

The current retrieval system maps the child's age in months to an age
group and applies that group during vector retrieval.

------------------------------------------------------------------------

## 4.3 Evidence-Grounded Answers

The system retrieves relevant chunks from the medical knowledge base
before asking the LLM to generate an answer.

Conceptually:

``` text
User Question
      ↓
Age-aware retrieval
      ↓
Relevant medical chunks
      ↓
LLM context
      ↓
Generated answer
```

------------------------------------------------------------------------

## 4.4 Conversation Memory

Each conversation has a conversation ID.

The system stores:

-   conversation ID
-   child age
-   messages
-   assistant responses
-   retrieved sources
-   timestamps

This allows follow-up questions to use the previous conversation
context.

------------------------------------------------------------------------

## 4.5 Source Display

Assistant responses can include the retrieved medical sources and page
numbers used by the system.

This helps users understand where the information came from.

------------------------------------------------------------------------

# 5. System Architecture

The overall architecture is:

``` text
                         USER
                           │
                           ▼
                    Browser / UI
                           │
                           ▼
                     FastAPI API
                           │
                           ▼
                    main.py
                           │
                 ┌─────────┴─────────┐
                 │                   │
                 ▼                   ▼
          Conversation          LLM.py
             Logic                 │
                                   ▼
                              retrieve.py
                                   │
                                   ▼
                                Qdrant
                                   │
                                   ▼
                           Retrieved Evidence
                                   │
                                   ▼
                              GPT-OSS-20B
                                   │
                                   ▼
                              LLM Response
                                   │
                                   ▼
                              FastAPI
                                   │
                                   ▼
                              Browser
```

The browser communicates with FastAPI through HTTP requests.

The frontend JavaScript sends requests such as:

``` text
POST /chat
GET /conversations
GET /conversations/{conversation_id}
DELETE /conversations/{conversation_id}
```

------------------------------------------------------------------------

# 6. Two Major Parts of the System

The project can be understood as two major worlds.

## World 1 --- Build the Knowledge Base

This happens during knowledge-base preparation.

``` text
PDF documents
     ↓
ingestion.py
     ↓
Text extraction
     ↓
cleaning.py
     ↓
Clean text
     ↓
chunking.py
     ↓
Semantic chunks
     ↓
embedding.py
     ↓
Embeddings
     ↓
qdrant_store.py
     ↓
Qdrant
```

This work does not need to happen for every user question.

------------------------------------------------------------------------

## World 2 --- Serve the Knowledge

This happens when a user asks a question.

``` text
User
  ↓
Frontend
  ↓
FastAPI
  ↓
LLM.py
  ↓
retrieve.py
  ↓
Qdrant
  ↓
Relevant evidence
  ↓
LLM
  ↓
Answer
  ↓
FastAPI
  ↓
Frontend
```

------------------------------------------------------------------------

# 7. Technology Stack

## Backend

-   Python
-   FastAPI
-   Pydantic
-   Uvicorn

## Frontend

-   HTML
-   CSS
-   JavaScript
-   Jinja2 template rendering for the initial HTML page

## Retrieval / RAG

-   Hugging Face embedding model
-   BAAI/bge-small-en-v1.5
-   Qdrant
-   LangChain Hugging Face integration

## LLM

-   GPT-OSS-20B
-   Hosted through Groq's OpenAI-compatible API
-   Python `openai` client

## Project / Environment Management

-   `uv`
-   `pyproject.toml`
-   `uv.lock`

------------------------------------------------------------------------

# 8. Project Structure

``` text
PediaGuide AI/
│
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── LLM.py
│   ├── retrieve.py
│   ├── ingestion.py
│   ├── cleaning.py
│   ├── chunking.py
│   ├── embedding.py
│   └── qdrant_store.py
│
├── data/
│   ├── raw/
│   ├── processed/
│   ├── cleaned/
│   ├── chunks/
│   ├── embeddings/
│   ├── qdrant/
│   └── conversations/
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
│
├── templates/
│   └── index.html
│
├── pyproject.toml
├── uv.lock
├── .gitignore
└── README.md
```

------------------------------------------------------------------------

# 9. Purpose of Each Python File

## `main.py`

FastAPI application and web/API layer.

Responsibilities:

-   create FastAPI application
-   serve the frontend
-   define API endpoints
-   validate incoming chat data
-   decide whether a request is a new or existing conversation
-   call the PediaGuide logic
-   return JSON responses
-   handle HTTP errors

It does not perform the actual RAG retrieval or LLM generation.

------------------------------------------------------------------------

## `LLM.py`

Main application/LLM orchestration layer.

Responsibilities include:

-   API key handling
-   Groq/OpenAI-compatible client setup
-   model selection
-   system prompt
-   pediatric question classification
-   age extraction
-   conversation creation/loading/saving
-   medical evidence formatting
-   LLM call
-   conversation memory

The main RAG orchestration function is:

``` text
ask_pediaguide()
```

------------------------------------------------------------------------

## `retrieve.py`

Retrieval layer.

Responsibilities:

-   load the embedding model
-   convert the user question into an embedding
-   determine the child's age group
-   apply the age-related Qdrant filter
-   perform vector similarity search
-   return relevant evidence

------------------------------------------------------------------------

## `ingestion.py`

Knowledge-base ingestion.

Responsibilities:

-   find source PDFs
-   extract text and page information
-   preserve document/page metadata
-   create processed JSON files

------------------------------------------------------------------------

## `cleaning.py`

Text cleaning.

Responsibilities:

-   remove extraction noise
-   normalize Unicode
-   clean unnecessary spacing
-   remove meaningless pages
-   preserve useful medical text
-   preserve page metadata

------------------------------------------------------------------------

## `chunking.py`

Document chunking.

Responsibilities:

-   divide documents into smaller meaningful pieces
-   keep headings associated with content
-   preserve page numbers
-   attach metadata
-   identify age-related information where possible
-   create stable chunk IDs

------------------------------------------------------------------------

## `embedding.py`

Embedding generation.

Responsibilities:

-   load the embedding model
-   convert chunks into vectors
-   preserve the original text and metadata
-   save embedded chunks

------------------------------------------------------------------------

## `qdrant_store.py`

Vector database preparation.

Responsibilities:

-   create the local Qdrant collection
-   load embeddings
-   create stable vector point IDs
-   store vectors
-   store text and metadata as payload

------------------------------------------------------------------------

# 10. Medical Knowledge Strategy

The project uses a curated medical knowledge approach rather than
collecting a large number of random documents.

The intended source hierarchy is:

``` text
Tier 1
Government / WHO / official health guidance
        ↓
Tier 2
Recognized pediatric organizations
        ↓
Tier 3
Approved educational references
        ↓
Tier 4
Supplementary material such as lectures/videos
```

Higher-priority official clinical guidance should be preferred when
sources overlap.

Supplementary videos should not automatically outrank official clinical
guidelines.

------------------------------------------------------------------------

# 11. Knowledge Base Documents

The current knowledge preparation work has used pediatric/newborn
medical documents including:

-   Essential Newborn Care Course, 2nd Edition
-   Facility Based Newborn Care Operational Guidelines
-   IMNCI Chart Booklet for Medical Officers
-   Management of Pneumonia and Diarrhoea in Children up to 10 Years
-   Routine Immunization Manual for Health Workers

The knowledge base is intended to focus on reliable pediatric and
newborn guidance.

------------------------------------------------------------------------

# 12. Knowledge Preparation Pipeline

The complete offline pipeline is:

``` text
Raw PDF
   ↓
ingestion.py
   ↓
Processed JSON
   ↓
cleaning.py
   ↓
Cleaned JSON
   ↓
chunking.py
   ↓
Chunk JSON
   ↓
embedding.py
   ↓
Embedded JSON
   ↓
qdrant_store.py
   ↓
Qdrant collection
```

------------------------------------------------------------------------

# 13. Document Ingestion

`ingestion.py` uses PDF extraction to convert source documents into
structured page-level data.

The important idea is:

``` text
PDF
 ↓
Extract text
 ↓
Keep page information
 ↓
Save structured JSON
```

Page numbers are retained because they are important for source
attribution.

------------------------------------------------------------------------

# 14. Cleaning

Extracted PDF text can contain:

-   unnecessary whitespace
-   formatting artifacts
-   empty pages
-   page-number-only pages
-   Unicode inconsistencies
-   extraction noise

The cleaning stage removes unnecessary noise while attempting to
preserve meaningful medical content.

The cleaned data remains structured by page.

------------------------------------------------------------------------

# 15. Chunking

Large documents are not sent directly to the embedding model as complete
documents.

Instead, they are divided into smaller chunks.

Example:

``` text
Large PDF
   ↓
Section
   ↓
Paragraphs
   ↓
Small semantic chunks
```

A chunk contains:

``` json
{
  "chunk_id": "fbnc_2025_p25_c01",
  "text": "Admission criteria at different levels of care...",
  "metadata": {
    "document_id": "fbnc_2025",
    "document_title": "Facility Based Newborn Care Operational Guidelines",
    "year": 2025,
    "page_number": 25,
    "source_type": "india_government_guideline"
  }
}
```

The current chunking implementation uses a custom Python chunking
process rather than a LangChain text splitter.

------------------------------------------------------------------------

# 16. Why Chunk Documents?

The retrieval system needs to find the **specific part of a document**
that is relevant to the question.

If an entire 200-page document were represented by one vector, retrieval
would be too broad.

Instead:

``` text
200-page document
      ↓
hundreds of chunks
      ↓
one vector per chunk
      ↓
retrieve the most relevant chunks
```

This makes evidence retrieval more precise.

------------------------------------------------------------------------

# 17. Embeddings

An embedding converts text into a numerical vector.

The project uses:

``` text
BAAI/bge-small-en-v1.5
```

The model produces:

``` text
384-dimensional vectors
```

Conceptually:

``` text
Medical text
     ↓
Embedding model
     ↓
[0.01, 0.04, -0.07, ...]
```

The vector represents the semantic position of the text.

------------------------------------------------------------------------

# 18. Why BGE-small?

The selected embedding model was chosen as a practical local model
because the project requirements included:

-   semantic retrieval
-   English text
-   local execution
-   relatively small model size
-   CPU usability
-   manageable vector size
-   simple integration

The model produces 384-dimensional vectors.

------------------------------------------------------------------------

# 19. Why Store the Original Text With the Vector?

The vector itself is not readable medical evidence.

For example:

``` text
[0.01, 0.04, -0.07, ...]
```

does not help the LLM.

Therefore, the system stores:

``` json
{
  "chunk_id": "encc_p10_c03",
  "text": "The newborn should...",
  "vector": [0.01, 0.04, -0.07],
  "metadata": {
    "document_id": "encc",
    "page_number": 10
  }
}
```

The vector is used to **find** relevant information.

The original text is used to **provide** that information to the LLM.

``` text
Vector
  ↓
Find relevant chunk
  ↓
Retrieve original text
  ↓
Send text to LLM
```

------------------------------------------------------------------------

# 20. Qdrant

Qdrant is the vector database used by PediaGuide.

A traditional database may store:

``` text
id | name | age | city
```

Qdrant stores vector points containing:

``` text
ID
VECTOR
PAYLOAD
```

For PediaGuide:

``` text
Qdrant
│
├── vector
│     └── 384 numbers
│
└── payload
      ├── chunk_id
      ├── text
      ├── document_id
      ├── page_number
      └── other metadata
```

------------------------------------------------------------------------

# 21. Qdrant Retrieval Concept

The retrieval process is conceptually:

``` text
User question
      ↓
Question embedding
      ↓
Qdrant similarity search
      ↓
Relevant vector points
      ↓
Payload
      ↓
Original medical text
```

The Qdrant collection uses cosine similarity for vector comparison.

The vector size must match the embedding model output:

``` text
BGE-small
   ↓
384 dimensions

Qdrant
   ↓
384-dimensional vectors
```

------------------------------------------------------------------------

# 22. Age-Aware Retrieval

The current retrieval system converts age in months into an age group.

Conceptually:

``` text
0–1 month
   → young infant

2–59 months
   → child_2_59_months

60–119 months
   → child_5_9_years

120–179 months
   → child_10_14_years

180+ months
   → adolescent_15_years
```

The exact age-group mapping is implemented in `retrieve.py`.

The system uses the age group as a retrieval filter and also allows
chunks whose age metadata is not specified.

------------------------------------------------------------------------

# 23. Retrieval and Relevance

Age filtering and semantic similarity have different jobs.

``` text
Age filter
    ↓
Which chunks are eligible?

Vector similarity
    ↓
Which eligible chunks are most relevant?
```

The current system retrieves up to five relevant results.

The five results are not divided into a fixed number of age-specific and
generic results. They are the highest-ranked results among the chunks
that satisfy the filter.

------------------------------------------------------------------------

# 24. LLM Layer

`LLM.py` connects the application to the language model.

It handles:

``` text
API key
   ↓
Groq client
   ↓
Model selection
   ↓
System prompt
   ↓
Retrieved evidence
   ↓
Conversation history
   ↓
LLM call
   ↓
Answer
```

The current model configuration uses:

``` text
openai/gpt-oss-20b
```

through Groq's OpenAI-compatible API.

------------------------------------------------------------------------

# 25. RAG Generation

The current RAG flow is:

``` text
User Question
      ↓
Retrieve evidence
      ↓
Qdrant results
      ↓
Format evidence
      ↓
Add age
      ↓
Add previous conversation
      ↓
Add safety instructions
      ↓
Send prompt to LLM
      ↓
Generate answer
```

The LLM receives both the question and the retrieved medical evidence.

------------------------------------------------------------------------

# 26. Main LLM Orchestration

The central application flow is handled by:

``` text
ask_pediaguide()
```

Conceptually it does:

``` text
1. Get child's age
2. Retrieve evidence
3. Get previous messages
4. Build system + conversation messages
5. Add retrieved evidence
6. Add current question
7. Call GPT-OSS
8. Get answer
9. Save conversation
10. Return answer + sources
```

------------------------------------------------------------------------

# 27. Conversation Memory

Conversations are stored locally as JSON files.

A conversation contains information such as:

``` json
{
  "conversation_id": "conv_example",
  "age_months": 36,
  "title": "My 3-year-old has fever",
  "messages": [],
  "updated_at": "..."
}
```

Messages contain user/assistant content and assistant source
information.

The conversation ID allows the frontend and backend to identify the
correct conversation.

------------------------------------------------------------------------

# 28. FastAPI Backend

FastAPI is the web/API framework used by the project.

The application is created using:

``` python
app = FastAPI(
    title="PediaGuide AI",
    version="0.1.0"
)
```

FastAPI acts as the communication layer between the browser and the
Python backend.

It is not the LLM and does not perform the vector search itself.

------------------------------------------------------------------------

# 29. Main FastAPI Endpoints

## Home

``` text
GET /
```

Returns the main `index.html` page.

------------------------------------------------------------------------

## Conversation List

``` text
GET /conversations
```

Returns saved conversations.

------------------------------------------------------------------------

## Open Conversation

``` text
GET /conversations/{conversation_id}
```

Returns one saved conversation.

------------------------------------------------------------------------

## Chat

``` text
POST /chat
```

Receives a user question and returns the generated answer and sources.

------------------------------------------------------------------------

## Delete Conversation

``` text
DELETE /conversations/{conversation_id}
```

Deletes a saved conversation.

------------------------------------------------------------------------

# 30. Chat Request Structure

The `/chat` endpoint expects:

``` python
class ChatRequest(BaseModel):
    conversation_id: Optional[str] = None
    message: str
```

This is a Pydantic data model.

It defines the expected incoming JSON structure.

Example:

``` json
{
  "conversation_id": "conv_123",
  "message": "What should I monitor?"
}
```

`conversation_id` is optional because the first message may create a new
conversation.

------------------------------------------------------------------------

# 31. New Conversation Flow

When no conversation ID is provided:

``` text
POST /chat
      ↓
No conversation_id
      ↓
Analyze first question
      ↓
┌──────────────┬──────────────────┐
│              │                  │
Greeting   Outside context   Pediatric question
                                  │
                           ┌──────┴──────┐
                           │             │
                        No age          Has age
                           │             │
                       Ask age      Create conversation
                                         │
                                         ▼
                                  ask_pediaguide()
```

------------------------------------------------------------------------

# 32. Existing Conversation Flow

When a conversation ID exists:

``` text
POST /chat
      ↓
conversation_id exists
      ↓
load conversation
      ↓
Check conversation exists
      ↓
ask_pediaguide()
      ↓
retrieve evidence
      ↓
LLM
      ↓
save updated conversation
      ↓
return answer
```

------------------------------------------------------------------------

# 33. Frontend

The frontend consists of:

``` text
templates/index.html
static/css/style.css
static/js/app.js
```

### HTML

Provides the page structure:

-   sidebar
-   new chat button
-   conversation list
-   welcome screen
-   chat area
-   input box
-   send button

### CSS

Controls the appearance and layout.

### JavaScript

Provides the dynamic interaction with FastAPI.

------------------------------------------------------------------------

# 34. Frontend ↔ FastAPI Communication

The HTML does not directly call FastAPI.

JavaScript performs the communication.

For example:

``` javascript
fetch("/chat", {
    method: "POST",
    headers: {
        "Content-Type": "application/json"
    },
    body: JSON.stringify({
        conversation_id: conversationId,
        message: message
    })
});
```

The connection exists because both sides use the same HTTP endpoint:

``` text
JavaScript
    ↓
POST /chat
    ↓
FastAPI
    ↓
@app.post("/chat")
```

FastAPI does not import JavaScript.

The browser communicates with FastAPI through HTTP.

------------------------------------------------------------------------

# 35. Complete Chat Request Flow

Suppose the user enters:

> My 3-year-old has fever and cough.

The complete flow is:

``` text
1. User enters question
        ↓
2. HTML contains the input field
        ↓
3. JavaScript reads the input
        ↓
4. JavaScript sends POST /chat
        ↓
5. FastAPI receives JSON
        ↓
6. Pydantic validates ChatRequest
        ↓
7. main.py checks conversation state
        ↓
8. Age is extracted
        ↓
9. Conversation is created/loaded
        ↓
10. ask_pediaguide()
        ↓
11. retrieve.py creates query embedding
        ↓
12. Qdrant searches medical evidence
        ↓
13. Relevant chunks are returned
        ↓
14. LLM.py builds the RAG prompt
        ↓
15. GPT-OSS generates the answer
        ↓
16. Conversation and sources are saved
        ↓
17. FastAPI returns JSON
        ↓
18. JavaScript reads response.json()
        ↓
19. JavaScript adds the answer to the chat
        ↓
20. User sees the response
```

------------------------------------------------------------------------

# 36. Why JavaScript Is Used Instead of Jinja2 for Chat Messages

Jinja2 is used to render the initial HTML page.

The ongoing chat is handled by JavaScript.

``` text
Initial page
    ↓
Jinja2
    ↓
index.html
```

After the page loads:

``` text
User interaction
    ↓
JavaScript
    ↓
FastAPI
    ↓
JSON
    ↓
JavaScript
    ↓
Update page
```

This avoids reloading the entire page after every chat message.

------------------------------------------------------------------------

# 37. Error Handling

FastAPI uses HTTP status codes for errors.

Examples:

``` text
400
Bad request

404
Resource not found

200
Successful request
```

For example, if a conversation does not exist:

``` python
raise HTTPException(
    status_code=404,
    detail="Conversation not found."
)
```

The frontend can then display an appropriate message.

------------------------------------------------------------------------

# 38. Environment and API Key

The LLM requires an API key.

The API key should **never be committed to GitHub**.

For local development, use an environment variable or another local
secret mechanism.

For deployment, configure the API key as a secret/environment variable
provided by the hosting platform.

Do not place the real key directly inside source code.

------------------------------------------------------------------------

# 39. Running the Project Locally

The project uses `uv` for Python environment and dependency management.

The intended Python version for the current development environment is:

``` text
Python 3.12.14
```

Create/install the environment according to the project's
`pyproject.toml` and `uv.lock`.

Then start the development server with:

``` bash
uv run uvicorn app.main:app --reload
```

The application is then available locally at:

``` text
http://127.0.0.1:8000
```

FastAPI documentation is available at:

``` text
http://127.0.0.1:8000/docs
```

------------------------------------------------------------------------

# 40. Knowledge Base Rebuilding

The knowledge base is built in stages.

A typical preparation sequence is:

``` text
1. Add source PDFs
       ↓
2. Run ingestion.py
       ↓
3. Run cleaning.py
       ↓
4. Run chunking.py
       ↓
5. Run embedding.py
       ↓
6. Run qdrant_store.py
```

After changing:

-   source documents
-   cleaning logic
-   chunking logic
-   embedding model

the relevant downstream stages should be rebuilt.

For example, changing the embedding model requires new embeddings and a
compatible Qdrant collection.

------------------------------------------------------------------------

# 41. Important Deployment Considerations

The current local-development architecture uses local files and local
Qdrant storage.

Before public hosting, the following areas must be reviewed:

## API key

Use hosting secrets/environment variables.

## Qdrant persistence

Ensure the deployment environment provides persistent vector storage or
use an appropriate hosted/persistent Qdrant setup.

## Conversation storage

The current JSON conversation storage is local.

A production deployment with multiple users would require a proper
persistent database and user/session strategy.

## File storage

Do not assume that local filesystem changes survive every deployment
platform restart or redeployment.

## Security

A public deployment needs:

-   secret management
-   input validation
-   appropriate logging
-   access controls where required
-   privacy/security review
-   protection against abuse

## Medical use

The current project should remain clearly identified as an
educational/evidence-support system unless it undergoes appropriate
clinical validation and governance.

------------------------------------------------------------------------

# 42. GitHub Preparation

Before publishing the repository, make sure secrets and
generated/private data are excluded.

A `.gitignore` should normally include items such as:

``` gitignore
.venv/
__pycache__/
*.pyc

.env
*.env

data/conversations/
data/qdrant/

.venv/groq_api_key.txt

.vscode/
.ipynb_checkpoints/
```

Do not commit API keys.

Do not commit private conversation data.

Large generated datasets and vector stores should be evaluated before
committing because they can make the repository unnecessarily large.

------------------------------------------------------------------------

# 43. Limitations of the Current System

The current implementation has several limitations.

### Medical limitations

The system is not clinically validated and should not be treated as a
diagnostic or treatment system.

### Retrieval limitations

Vector retrieval can return content that is semantically similar but not
perfectly relevant.

Age metadata is also dependent on what age information was identified
during chunk preparation.

### Source limitations

The system is only as reliable as the curated documents available in the
knowledge base.

### LLM limitations

The LLM can still produce incorrect or incomplete responses.

Retrieved evidence reduces this risk but does not eliminate it.

### Conversation storage

The current local JSON approach is suitable for a learning/portfolio
project but is not a complete multi-user production database
architecture.

### Deployment limitations

Local Qdrant and local file storage require additional work for reliable
public hosting.

------------------------------------------------------------------------

# 44. Future Improvements

Possible future improvements include:

1.  Add more curated pediatric guidelines.
2.  Improve age metadata coverage.
3.  Add stronger retrieval evaluation.
4.  Add retrieval relevance thresholds.
5.  Add reranking.
6.  Add structured safety routing.
7.  Improve insufficient-evidence detection.
8.  Add better conversation/database persistence.
9.  Add authentication if required.
10. Add separate parent and clinician presentation modes.
11. Add automated evaluation cases.
12. Add monitoring and logging.
13. Add deployment-ready persistent vector storage.
14. Improve source/date presentation.
15. Add tests for age extraction, retrieval, API routes, and response
    structure.

------------------------------------------------------------------------

# 45. Suggested Evaluation

A useful evaluation framework can test:

## Retrieval

-   Was the correct document retrieved?
-   Was the correct page/chunk retrieved?
-   Was the evidence age-appropriate?

## Answer quality

-   Does the answer address the question?
-   Is it grounded in retrieved evidence?
-   Are sources correctly displayed?

## Safety

-   Does the system avoid definite diagnosis?
-   Does it avoid unsupported medication instructions?
-   Does it communicate insufficient evidence?
-   Does it recognize situations requiring professional/emergency
    attention?

## Conversation

-   Is the child age retained?
-   Does the system maintain previous context?
-   Does the correct conversation load?

------------------------------------------------------------------------

# 46. Simple Mental Model of the Whole Project

The easiest way to remember PediaGuide AI is:

``` text
                 PediaGuide AI

        ┌──────────────────────────┐
        │        FRONTEND          │
        │ HTML + CSS + JavaScript  │
        └────────────┬─────────────┘
                     │
                     │ HTTP
                     ▼
        ┌──────────────────────────┐
        │         FASTAPI          │
        │        main.py           │
        └────────────┬─────────────┘
                     │
                     ▼
        ┌──────────────────────────┐
        │          LLM.py          │
        │ Application orchestration│
        └────────────┬─────────────┘
                     │
                     ▼
        ┌──────────────────────────┐
        │       retrieve.py        │
        └────────────┬─────────────┘
                     │
                     ▼
        ┌──────────────────────────┐
        │          QDRANT          │
        │      Vector database     │
        └────────────┬─────────────┘
                     │
                     ▼
              Medical Evidence
                     │
                     ▼
        ┌──────────────────────────┐
        │       GPT-OSS-20B        │
        └────────────┬─────────────┘
                     │
                     ▼
                  Answer
```

------------------------------------------------------------------------

# 47. Knowledge Base Mental Model

``` text
PDF
 ↓
Extract
 ↓
Clean
 ↓
Chunk
 ↓
Embed
 ↓
Store in Qdrant
```

Then during a question:

``` text
Question
 ↓
Embed question
 ↓
Search Qdrant
 ↓
Get relevant chunks
 ↓
Give chunks to LLM
 ↓
Generate grounded answer
```

This is the core RAG concept used by PediaGuide AI.

------------------------------------------------------------------------

# 48. Final Project Summary

PediaGuide AI combines:

``` text
FastAPI
    +
HTML/CSS/JavaScript
    +
Pydantic
    +
Local embeddings
    +
Qdrant
    +
RAG
    +
GPT-OSS-20B
    +
Medical knowledge documents
    +
Conversation memory
```

The system separates the responsibilities clearly:

``` text
Frontend
→ User interaction

FastAPI
→ HTTP/API communication

LLM.py
→ Application and LLM orchestration

retrieve.py
→ Evidence retrieval

Qdrant
→ Vector storage/search

Embedding model
→ Text → vector representation

GPT-OSS-20B
→ Evidence-grounded response generation

Knowledge pipeline
→ Medical documents → searchable knowledge base
```

The overall objective is to demonstrate a complete, understandable RAG
application while keeping the medical scope evidence-grounded and
clearly bounded.
