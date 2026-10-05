PediaGuide AI - Setup Instructions
===================================

Follow these steps after cloning the PediaGuide AI repository.


1. CLONE THE PROJECT
--------------------

Open a terminal and run:

git clone YOUR_GITHUB_REPOSITORY_URL

Then enter the project folder:

cd "PediaGuide AI"


2. INSTALL THE PROJECT
----------------------

Make sure Python 3.12.14 and uv are installed.

Then run:

uv sync

This creates the virtual environment and installs all required
dependencies from pyproject.toml and uv.lock.

Then Activate the Venv : venv\Scripts\activate


3. GET THE GROQ API KEY
-----------------------

PediaGuide AI uses the following model:

openai/gpt-oss-20b

The model is accessed through Groq's OpenAI-compatible API.

Get your Groq API key here:

https://console.groq.com/keys

Create an account if you do not already have one.

Create a new API key and copy it.


4. RUN THE APPLICATION
----------------------

Start the FastAPI server:

uv run uvicorn app.main:app --reload

On the first run, the application will ask:

Paste your Groq API key:

Paste the API key you obtained from:

https://console.groq.com/keys

The application stores the key locally inside:

.venv/groq_api_key.txt

The .venv folder is ignored by Git, so your API key will NOT be
uploaded to GitHub.


5. OPEN THE APPLICATION
-----------------------

After the server starts, open:

http://127.0.0.1:8000


6. FASTAPI API DOCUMENTATION
----------------------------

You can view the API documentation at:

http://127.0.0.1:8000/docs


7. THAT'S IT
------------

The basic setup is:

Clone repository
       ↓
uv sync
       ↓
Get Groq API key
       ↓
Run FastAPI
       ↓
Open http://127.0.0.1:8000


IMPORTANT
---------

Do not share your Groq API key with anyone.

Do not add the API key to source code or README files.

The project stores the local key inside .venv/, which is ignored
by Git.
