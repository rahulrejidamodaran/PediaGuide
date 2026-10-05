# ============================================================
# PediaGuide AI - FastAPI Backend
# ============================================================

from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from app.LLM import (
    ask_pediaguide,
    create_conversation_from_question,
    list_conversations,
    load_conversation,
    delete_conversation,
    analyze_first_question,
    first_question_response
)

# ============================================================
# 1. CREATE FASTAPI APP
# ============================================================

app = FastAPI(
    title="PediaGuide AI",
    version="0.1.0"
)


# ============================================================
# 2. CONNECT FRONTEND FILES
# ============================================================

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


templates = Jinja2Templates(
    directory="templates"
)


# ============================================================
# 3. HOME PAGE
# ============================================================

@app.get(
    "/",
    response_class=HTMLResponse
)
def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )


# ============================================================
# 4. CHAT REQUEST
# ============================================================

class ChatRequest(BaseModel):

    conversation_id: Optional[str] = None
    message: str


# ============================================================
# 5. GET SAVED CONVERSATIONS
# ============================================================

@app.get("/conversations")
def get_conversations():

    return {
        "conversations":
            list_conversations()
    }


# ============================================================
# 6. OPEN ONE CONVERSATION
# ============================================================

@app.get(
    "/conversations/{conversation_id}"
)
def get_conversation(
    conversation_id: str
):

    conversation = load_conversation(
        conversation_id
    )

    if conversation is None:

        raise HTTPException(
            status_code=404,
            detail="Conversation not found"
        )

    return conversation


# ============================================================
# 7. CHAT
# ============================================================

@app.post("/chat")
def chat(request: ChatRequest):

    question = request.message.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty."
        )

    # ========================================================
    # NEW CHAT
    # ========================================================

    if not request.conversation_id:

        decision = analyze_first_question(
            question
        )

        # ----------------------------------------------------
        # Greeting or unrelated question
        # ----------------------------------------------------

        if decision in {
            "greeting",
            "outside_context"
        }:

            return {
                "answer":
                    first_question_response(
                        question
                    ),

                "sources": [],

                "conversation_id":
                    None,

                "needs_age":
                    False
            }

        # ----------------------------------------------------
        # Pediatric question but no age
        # ----------------------------------------------------

        if decision == "pediatric_without_age":

            return {
                "answer":
                    first_question_response(
                        question
                    ),

                "sources": [],

                "conversation_id":
                    None,

                "needs_age":
                    True
            }

        # ----------------------------------------------------
        # Pediatric question with age
        # ----------------------------------------------------

        conversation = (
            create_conversation_from_question(
                question
            )
        )

        if conversation is None:

            return {
                "answer":
                    "Please provide your child's age "
                    "so I can retrieve age-appropriate "
                    "medical evidence.",

                "sources": [],

                "conversation_id":
                    None,

                "needs_age":
                    True
            }

    # ========================================================
    # EXISTING CONVERSATION
    # ========================================================

    else:

        conversation = load_conversation(
            request.conversation_id
        )

        if conversation is None:

            raise HTTPException(
                status_code=404,
                detail="Conversation not found."
            )

    # ========================================================
    # MEDICAL QUESTION
    # ========================================================

    answer, sources = ask_pediaguide(
        conversation,
        question
    )

    return {

        "answer":
            answer,

        "sources":
            sources,

        "conversation_id":
            conversation[
                "conversation_id"
            ],

        "needs_age":
            False
    }


# ============================================================
# DELETE CONVERSATION
# ============================================================

@app.delete("/conversations/{conversation_id}")
def delete_chat(conversation_id: str):

    deleted = delete_conversation(conversation_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Conversation not found."
        )

    return {
        "message": "Conversation deleted successfully."
    }