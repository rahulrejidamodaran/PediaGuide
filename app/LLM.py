# ============================================================
# PediaGuide AI
# LLM, Age Detection, Question Understanding
# and Conversation Logic
# ============================================================

from pathlib import Path
from getpass import getpass
from datetime import datetime
import json
import re
import uuid

from openai import OpenAI

from app.retrieve import retrieve_evidence, close_retriever


# ============================================================
# 1. SETTINGS
# ============================================================

MODEL_NAME = "openai/gpt-oss-20b"

API_KEY_FILE = Path(".venv/groq_api_key.txt")

CONVERSATIONS_FOLDER = Path("data/conversations")
CURRENT_SESSION_FILE = Path("data/current_session.txt")

MAX_HISTORY = 10
NUMBER_OF_SOURCES = 5


# ============================================================
# 2. CONNECT TO GROQ
# ============================================================

def get_groq_api_key():
    """
    Read the Groq API key from the local file.

    If the file does not exist, ask for the key once
    and save it.
    """

    if API_KEY_FILE.exists():

        key = API_KEY_FILE.read_text(
            encoding="utf-8"
        ).strip()

        if key:
            return key

    print("Groq API key not found.Please paste your Groq API key.It will be saved locally for future runs.")

    key = getpass(
        "Paste your Groq API key: "
    ).strip()

    if not key:
        raise RuntimeError(
            "Groq API key cannot be empty."
        )

    API_KEY_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    API_KEY_FILE.write_text(
        key,
        encoding="utf-8"
    )

    return key


# Groq provides an OpenAI-compatible API.
groq = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=get_groq_api_key()
)


# ============================================================
# 3. PEDIA GUIDE SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are PediaGuide AI, an evidence-grounded pediatric
information assistant for newborns through 15 years.

Your purpose is to help parents and caregivers understand
pediatric health information using the medical evidence
retrieved from the PediaGuide knowledge base.

IMPORTANT RULES:

- Use the retrieved medical evidence as the primary source.
- Do not invent medical facts.
- Do not invent sources.
- Do not give a definite diagnosis.
- Do not prescribe medicines.
- Do not calculate medicine doses.
- Always consider the child's age.
- If evidence is insufficient, clearly say so.
- If the evidence describes warning signs or urgent care,
  clearly tell the user that professional medical care may
  be needed.
- Do not replace a pediatrician, doctor, or emergency service.
- Explain medical terms in simple language when useful.
- Use previous conversation messages for follow-up questions.
- Do not ask the user to repeat information already present
  in the conversation.
- Keep the answer clear and reasonably concise.
-Format responses using clean Markdown.
-Do not use raw HTML tags such as <br>, <div>, <span>, or <table>.
-Use Markdown tables, bullet lists, numbered lists, headings, and bold text when appropriate.

The retrieved evidence will be provided as [Source 1],
[Source 2], etc.

Never invent a source that was not retrieved.
"""


# ============================================================
# 4. GENERAL QUESTION UNDERSTANDING
# ============================================================

# Words that strongly indicate that the user is talking
# about a child or pediatric health.
CHILD_WORDS = {
    "child",
    "children",
    "kid",
    "kids",
    "baby",
    "babies",
    "infant",
    "infants",
    "newborn",
    "newborns",
    "toddler",
    "toddlers",
    "boy",
    "girl",
    "son",
    "daughter",
    "pediatric",
    "paediatric",
    "childhood"
}


# Common pediatric health terms.
PEDIATRIC_HEALTH_WORDS = {
    "fever",
    "cough",
    "cold",
    "breathing",
    "breath",
    "breathing difficulty",
    "difficulty breathing",
    "shortness of breath",
    "wheezing",
    "wheeze",
    "pneumonia",
    "bronchiolitis",
    "asthma",
    "diarrhea",
    "diarrhoea",
    "vomiting",
    "vomit",
    "dehydration",
    "rash",
    "pain",
    "headache",
    "stomach ache",
    "abdominal pain",
    "feeding",
    "breastfeeding",
    "feeding problem",
    "poor feeding",
    "vaccination",
    "vaccine",
    "immunization",
    "immunisation",
    "growth",
    "development",
    "weight",
    "height",
    "nutrition",
    "malnutrition",
    "constipation",
    "seizure",
    "seizures",
    "convulsion",
    "convulsions",
    "diarrhoea",
    "stool",
    "urine",
    "urination",
    "ear pain",
    "ear infection",
    "sore throat",
    "throat",
    "jaundice",
    "yellow skin",
    "yellow eyes",
    "newborn care",
    "baby care",
    "child health",
    "pediatric health",
    "paediatric health"
}


# Topics that are clearly outside this application's purpose.
NON_PEDIATRIC_TOPICS = {
    "global warming",
    "climate change",
    "politics",
    "election",
    "president",
    "prime minister",
    "stock market",
    "stocks",
    "cryptocurrency",
    "bitcoin",
    "programming",
    "python",
    "javascript",
    "html",
    "css",
    "coding",
    "software",
    "computer",
    "movie",
    "movies",
    "song",
    "songs",
    "cricket",
    "football",
    "weather",
    "recipe",
    "recipes",
    "travel",
    "tourism",
    "history",
    "geography",
    "mathematics",
    "math"
}


# Simple greetings should not require an age.
GREETING_WORDS = {
    "hi",
    "hello",
    "hey",
    "hai",
    "good morning",
    "good afternoon",
    "good evening"
}


def normalize_question(question):
    """
    Make the question easier to analyze.
    """

    question = question.lower().strip()

    # Convert different hyphens to a normal hyphen.
    question = (
        question
        .replace("–", "-")
        .replace("—", "-")
        .replace("-", "-")
    )

    # Remove repeated spaces.
    question = re.sub(
        r"\s+",
        " ",
        question
    )

    return question


def is_greeting(question):
    """
    # Check whether the user only sent a greeting.
    """

    text = normalize_question(question)

    text = re.sub(
        r"[!?.,]+",
        "",
        text
    ).strip()

    return text in GREETING_WORDS


def is_pediatric_question(question):
    """
    Decide whether the question is related to
    pediatric health.

    This is intentionally simple and transparent.
    """

    text = normalize_question(question)

    # Clearly unrelated topics.
    for topic in NON_PEDIATRIC_TOPICS:

        if topic in text:
            return False

    # Child-related words.
    for word in CHILD_WORDS:

        if re.search(
            rf"\b{re.escape(word)}\b",
            text
        ):
            return True

    # Pediatric health terms.
    for word in PEDIATRIC_HEALTH_WORDS:

        if word in text:
            return True

    return False


# ============================================================
# 5. AGE DETECTION
# ============================================================

def extract_age_months(question):
    """
    Extract the child's age and convert it into months.

    Supports natural variations such as:

        3-year-old
        3 year old
        3 years old
        3 yr old
        3yo
        3 y/o

        18-month-old
        18 months old
        18 months

        age 2
        age: 2
        age is 2
        aged 2

        child is 2
        kid is 2
        child aged 2

        1 year 3 months
        1 year and 3 months

    If a number follows "age" without a unit,
    it is treated as years.
    """

    text = normalize_question(question)

    # --------------------------------------------------------
    # 1. "age 2", "age: 2", "age is 2"
    # --------------------------------------------------------

    age_pattern = (
        r"\bage\s*"
        r"(?:is|=|:)?\s*"
        r"(\d+(?:\.\d+)?)"
        r"\s*"
        r"(year|years|yr|yrs|y|"
        r"month|months|mo|mos|m)?\b"
    )

    age_match = re.search(
        age_pattern,
        text
    )

    if age_match:

        number = float(
            age_match.group(1)
        )

        unit = age_match.group(2)

        if unit in {
            "month",
            "months",
            "mo",
            "mos",
            "m"
        }:

            total_months = round(
                number
            )

        else:
            # "age 2" means 2 years.
            total_months = round(
                number * 12
            )

        if 0 <= total_months <= 180:
            return total_months

        return None

    # --------------------------------------------------------
    # 2. "child is 2", "kid is 2", "baby is 6 months"
    # --------------------------------------------------------

    child_age_pattern = (
        r"\b(?:child|kid|baby|infant|"
        r"son|daughter|boy|girl)\b"
        r".{0,25}?"
        r"\b(?:is|aged|age(?:d)?)\b"
        r"\s*"
        r"(\d+(?:\.\d+)?)"
        r"\s*"
        r"(year|years|yr|yrs|y|"
        r"month|months|mo|mos|m)?\b"
    )

    child_age_match = re.search(
        child_age_pattern,
        text
    )

    if child_age_match:

        number = float(
            child_age_match.group(1)
        )

        unit = child_age_match.group(2)

        if unit in {
            "month",
            "months",
            "mo",
            "mos",
            "m"
        }:

            total_months = round(
                number
            )

        else:
            total_months = round(
                number * 12
            )

        if 0 <= total_months <= 180:
            return total_months

        return None

    # --------------------------------------------------------
    # 3. Standard "3-year-old" / "18-month-old"
    # --------------------------------------------------------

    year_old_pattern = (
        r"\b(\d+(?:\.\d+)?)"
        r"\s*-?\s*"
        r"(?:year|years|yr|yrs)"
        r"\s*-?\s*"
        r"old\b"
    )

    year_old_match = re.search(
        year_old_pattern,
        text
    )

    month_old_pattern = (
        r"\b(\d+(?:\.\d+)?)"
        r"\s*-?\s*"
        r"(?:month|months|mo|mos)"
        r"\s*-?\s*"
        r"old\b"
    )

    month_old_match = re.search(
        month_old_pattern,
        text
    )

    if year_old_match:

        years = float(
            year_old_match.group(1)
        )

        # Look for an additional month value nearby.
        month_match = re.search(
            r"(\d+(?:\.\d+)?)\s*"
            r"(?:month|months|mo|mos)",
            text
        )

        months = (
            float(month_match.group(1))
            if month_match
            else 0
        )

        total_months = round(
            (years * 12) + months
        )

        if 0 <= total_months <= 180:
            return total_months

        return None

    if month_old_match:

        months = float(
            month_old_match.group(1)
        )

        if 0 <= months <= 180:
            return round(months)

        return None

    # --------------------------------------------------------
    # 4. "3 years old" / "18 months"
    # --------------------------------------------------------

    year_pattern = (
        r"\b(\d+(?:\.\d+)?)"
        r"\s*(?:year|years|yr|yrs)\b"
    )

    month_pattern = (
        r"\b(\d+(?:\.\d+)?)"
        r"\s*(?:month|months|mo|mos)\b"
    )

    year_match = re.search(
        year_pattern,
        text
    )

    month_match = re.search(
        month_pattern,
        text
    )

    if year_match:

        years = float(
            year_match.group(1)
        )

        months = (
            float(month_match.group(1))
            if month_match
            else 0
        )

        total_months = round(
            (years * 12) + months
        )

        if 0 <= total_months <= 180:
            return total_months

    elif month_match:

        months = float(
            month_match.group(1)
        )

        if 0 <= months <= 180:
            return round(months)

    # --------------------------------------------------------
    # 5. "3yo", "3 y/o", "18mo"
    # --------------------------------------------------------

    compact_pattern = (
        r"\b(\d+(?:\.\d+)?)\s*"
        r"(y/o|yo|yrs?|y|mos?|mo|m)"
        r"\b"
    )

    compact_match = re.search(
        compact_pattern,
        text
    )

    if compact_match:

        number = float(
            compact_match.group(1)
        )

        unit = compact_match.group(2)

        if unit in {
            "mo",
            "mos",
            "m"
        }:

            total_months = round(
                number
            )

        else:

            total_months = round(
                number * 12
            )

        if 0 <= total_months <= 180:
            return total_months

    return None


def is_valid_age(age_months):
    """
    PediaGuide supports newborn to 15 years.
    """

    if age_months is None:
        return False

    return 0 <= age_months <= 180


def age_text(age_months):
    """
    Convert months into a simple readable age.
    """

    if age_months is None:
        return "Age not provided"

    if age_months < 12:

        return (
            f"{age_months} "
            f"month"
            f"{'s' if age_months != 1 else ''} old"
        )

    years = age_months // 12
    months = age_months % 12

    if months == 0:

        return (
            f"{years} "
            f"year"
            f"{'s' if years != 1 else ''} old"
        )

    return (
        f"{years} year"
        f"{'s' if years != 1 else ''} "
        f"{months} month"
        f"{'s' if months != 1 else ''} old"
    )


# ============================================================
# 6. FIRST QUESTION DECISION
# ============================================================

def analyze_first_question(question):
    """
    Decide what to do with the first user question.

    Returns:

        greeting
        pediatric_with_age
        pediatric_without_age
        outside_context
    """

    if is_greeting(question):
        return "greeting"

    if not is_pediatric_question(question):
        return "outside_context"

    age_months = extract_age_months(
        question
    )

    if is_valid_age(age_months):
        return "pediatric_with_age"

    return "pediatric_without_age"


def first_question_response(question):
    """
    Return a response when a new conversation does not
    need to enter the medical retrieval pipeline.
    """

    decision = analyze_first_question(
        question
    )

    if decision == "greeting":

        return (
            "Hello! I'm PediaGuide AI. "
            "I can help with pediatric health questions "
            "for newborns, children, and adolescents up to "
            "15 years. Tell me what is happening and "
            "mention your child's age when it is relevant."
        )

    if decision == "outside_context":

        return (
            "That question is outside PediaGuide AI's "
            "pediatric health context. I can help with "
            "health questions about newborns, children, "
            "and adolescents up to 15 years."
        )

    if decision == "pediatric_without_age":

        return (
            "I can help with that. I just need your "
            "child's age so I can use the appropriate "
            "age-specific medical evidence.\n\n"
            "For example:\n"
            "\"My kid is 2 years old and has a breathing "
            "problem.\""
        )

    return None


# ============================================================
# 7. CONVERSATION STORAGE
# ============================================================

def get_conversation_file(conversation_id):
    """
    Return the JSON file for a conversation.
    """

    return (
        CONVERSATIONS_FOLDER
        / f"{conversation_id}.json"
    )


def save_conversation(conversation):
    """
    Save a conversation.
    """

    CONVERSATIONS_FOLDER.mkdir(
        parents=True,
        exist_ok=True
    )

    file_path = get_conversation_file(
        conversation["conversation_id"]
    )

    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            conversation,
            file,
            indent=4,
            ensure_ascii=False
        )


def load_conversation(conversation_id):
    """
    Load one conversation.
    """

    file_path = get_conversation_file(
        conversation_id
    )

    if not file_path.exists():
        return None

    with open(
        file_path,
        "r",
        encoding="utf-8"
    ) as file:

        return json.load(file)


# ============================================================
# 8. CURRENT SESSION
# ============================================================

def save_current_session(conversation_id):
    """
    Remember the currently active conversation.
    """

    CURRENT_SESSION_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    CURRENT_SESSION_FILE.write_text(
        conversation_id,
        encoding="utf-8"
    )


def load_current_session():
    """
    Load the currently active conversation.
    """

    if not CURRENT_SESSION_FILE.exists():
        return None

    conversation_id = (
        CURRENT_SESSION_FILE
        .read_text(
            encoding="utf-8"
        )
        .strip()
    )

    if not conversation_id:
        return None

    return load_conversation(
        conversation_id
    )


# ============================================================
# 9. CREATE CONVERSATION
# ============================================================

def create_conversation(age_months):
    """
    Create and save a new conversation.
    """

    conversation_id = (
        f"conv_{uuid.uuid4().hex[:8]}"
    )

    now = datetime.now().isoformat()

    conversation = {

        "conversation_id":
            conversation_id,

        "title":
            "New conversation",

        "age_months":
            age_months,

        "created_at":
            now,

        "updated_at":
            now,

        "messages":
            []
    }

    save_conversation(
        conversation
    )

    save_current_session(
        conversation_id
    )

    return conversation


def create_conversation_from_question(question):
    """
    Create a conversation if the first question
    is a pediatric question and contains a valid age.

    Returns None when the question needs an age or
    is outside PediaGuide's context.
    """

    age_months = extract_age_months(
        question
    )

    if not is_valid_age(age_months):
        return None

    return create_conversation(
        age_months
    )


# ============================================================
# 10. LIST CONVERSATIONS
# ============================================================

def list_conversations():
    """
    Return conversations for the sidebar.
    """

    CONVERSATIONS_FOLDER.mkdir(
        parents=True,
        exist_ok=True
    )

    conversations = []

    for file_path in CONVERSATIONS_FOLDER.glob(
        "conv_*.json"
    ):

        try:

            with open(
                file_path,
                "r",
                encoding="utf-8"
            ) as file:

                conversation = json.load(
                    file
                )

            messages = conversation.get(
                "messages",
                []
            )

            title = conversation.get(
                "title",
                "New conversation"
            )

            if (
                title == "New conversation"
                and messages
            ):

                title = messages[0].get(
                    "content",
                    "New conversation"
                )[:60]

            conversations.append({

                "conversation_id":
                    conversation.get(
                        "conversation_id"
                    ),

                "title":
                    title,

                "age_months":
                    conversation.get(
                        "age_months"
                    ),

                "updated_at":
                    conversation.get(
                        "updated_at"
                    )
            })

        except (
            OSError,
            json.JSONDecodeError
        ):

            continue

    conversations.sort(
        key=lambda conversation:
            conversation.get(
                "updated_at",
                ""
            ),
        reverse=True
    )

    return conversations


# ============================================================
# 11. CLEAN SOURCE NAME
# ============================================================

def clean_source_name(document_name):
    """
    Make the document name nicer for the UI.

    Example:

    IMNCI_Chart_Booklet_MO_2023_RAG_Normalized
    becomes:

    IMNCI_Chart_Booklet_MO_2023
    """

    if not document_name:
        return "Unknown source"

    name = Path(
        str(document_name)
    ).name

    # Remove PDF extension.
    name = re.sub(
        r"\.pdf$",
        "",
        name,
        flags=re.IGNORECASE
    )

    # Remove our internal normalization label.
    name = re.sub(
        r"_RAG_Normalized$",
        "",
        name,
        flags=re.IGNORECASE
    )

    return name


# ============================================================
# 12. RETRIEVE MEDICAL EVIDENCE
# ============================================================

def get_medical_evidence(
    question,
    age_months
):
    """
    Retrieve age-appropriate medical evidence.
    """

    results = retrieve_evidence(
        question,
        age_months,
        limit=NUMBER_OF_SOURCES
    )

    evidence_parts = []
    sources = []

    for number, result in enumerate(
        results,
        start=1
    ):

        data = result.payload or {}

        document = data.get(
            "document_id",
            "Unknown"
        )

        page = data.get(
            "page_number",
            "Unknown"
        )

        chunk_id = data.get(
            "chunk_id",
            "Unknown"
        )

        text = data.get(
            "text",
            ""
        )

        display_name = clean_source_name(
            document
        )

        evidence_parts.append(
            f"""
[Source {number}]
Document: {display_name}
Page: {page}

{text}
"""
        )

        sources.append({

            "source_number":
                number,

            "document":
                display_name,

            "page":
                page,

            "chunk_id":
                chunk_id,

            "score":
                round(
                    result.score,
                    4
                )
        })

    if evidence_parts:

        evidence = "\n".join(
            evidence_parts
        )

    else:

        evidence = (
            "No relevant medical evidence "
            "was retrieved."
        )

    return evidence, sources


# ============================================================
# 13. ASK PEDIA GUIDE
# ============================================================

def ask_pediaguide(
    conversation,
    question
):
    """
    Main medical question function.

    The child's age comes from the conversation,
    so follow-up questions do not need to repeat it.
    """

    age_months = conversation[
        "age_months"
    ]

    # --------------------------------------------------------
    # Retrieve evidence
    # --------------------------------------------------------

    evidence, sources = (
        get_medical_evidence(
            question,
            age_months
        )
    )

    # --------------------------------------------------------
    # Previous conversation
    # --------------------------------------------------------

    previous_messages = (
        conversation.get(
            "messages",
            []
        )[-MAX_HISTORY:]
    )

    messages = [

        {
            "role":
                "system",

            "content":
                SYSTEM_PROMPT
        }
    ]

    # Add previous messages.
    for message in previous_messages:

        role = message.get(
            "role"
        )

        content = message.get(
            "content"
        )

        if (
            role in
            {"user", "assistant"}
            and content
        ):

            messages.append({

                "role":
                    role,

                "content":
                    content
            })

    # --------------------------------------------------------
    # Current question + evidence
    # --------------------------------------------------------

    current_prompt = f"""
Child age:
{age_text(age_months)}
({age_months} months)

Retrieved medical evidence from the PediaGuide
knowledge base:

{evidence}

Current user question:

{question}

Answer the current question using the retrieved
medical evidence and the previous conversation.

Important:

- Use the evidence as the primary source.
- Do not invent information.
- Do not make a definite diagnosis.
- Do not prescribe medicine or calculate doses.
- If the evidence is insufficient, say so clearly.
- Consider the child's age when explaining the evidence.
"""

    messages.append({

        "role":
            "user",

        "content":
            current_prompt
    })

    # --------------------------------------------------------
    # Call GPT-OSS
    # --------------------------------------------------------

    response = groq.chat.completions.create(

        model=MODEL_NAME,

        messages=messages
    )

    answer = (
        response
        .choices[0]
        .message
        .content
        .strip()
    )

    # --------------------------------------------------------
    # Save the conversation
    # --------------------------------------------------------

    if not conversation.get(
        "messages"
    ):

        conversation["title"] = (
            question[:60]
        )

    conversation["messages"].append({

        "role":
            "user",

        "content":
            question
    })

    conversation["messages"].append({

        "role":
            "assistant",

        "content":
            answer,

        "sources":
            sources
    })

    conversation["updated_at"] = (
        datetime.now().isoformat()
    )

    save_conversation(
        conversation
    )

    save_current_session(
        conversation[
            "conversation_id"
        ]
    )

    return answer, sources


# ============================================================
# 14. DELETE CONVERSATION
# ============================================================

def delete_conversation(conversation_id):
    """
    Delete a saved conversation.
    """

    conversation_file = (
        get_conversation_file(
            conversation_id
        )
    )

    if not conversation_file.exists():
        return False

    conversation_file.unlink()

    # Check the actual current conversation ID.
    current_conversation = (
        load_current_session()
    )

    if (
        current_conversation
        and
        current_conversation.get(
            "conversation_id"
        ) == conversation_id
    ):

        if CURRENT_SESSION_FILE.exists():
            CURRENT_SESSION_FILE.unlink()

    return True


# ============================================================
# 15. COMMAND-LINE VERSION
# ============================================================

def main():

    print("\nPediaGuide AI")
    print("=" * 60)

    print(
        "PediaGuide supports pediatric health "
        "questions from newborn to 15 years."
    )

    print(
        "Type /exit to close.\n"
    )

    conversation = (
        load_current_session()
    )

    try:

        while True:

            question = input(
                "You: "
            ).strip()

            if not question:
                continue

            if question.lower() == "/exit":
                break

            # ------------------------------------------------
            # New conversation
            # ------------------------------------------------

            if conversation is None:

                decision = (
                    analyze_first_question(
                        question
                    )
                )

                # Greeting
                if decision == "greeting":

                    print(
                        "\nPediaGuide:"
                    )

                    print(
                        first_question_response(
                            question
                        )
                    )

                    print()
                    continue

                # Outside context
                if decision == "outside_context":

                    print(
                        "\nPediaGuide:"
                    )

                    print(
                        first_question_response(
                            question
                        )
                    )

                    print()
                    continue

                # Pediatric question but no age
                if decision == "pediatric_without_age":

                    print(
                        "\nPediaGuide:"
                    )

                    print(
                        first_question_response(
                            question
                        )
                    )

                    print()
                    continue

                # Pediatric question with age
                conversation = (
                    create_conversation_from_question(
                        question
                    )
                )

            # ------------------------------------------------
            # Ask PediaGuide
            # ------------------------------------------------

            answer, _ = ask_pediaguide(
                conversation,
                question
            )

            print("\nPediaGuide:")
            print(answer)
            print()

    finally:

        close_retriever()


# ============================================================
# START
# ============================================================

if __name__ == "__main__":
    main()