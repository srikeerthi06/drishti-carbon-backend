
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from .agent import root_agent

from .tools.summary import (
    get_summary,
    get_monthly_trend,
    get_weekly_trend,
    get_dashboard_data
)

from .tools.reduction_tips import suggest_reductions


# ==========================================
# FASTAPI APPLICATION
# ==========================================

app = FastAPI(
    title="Drishti Carbon Coach API",
    description="API for carbon footprint tracking, AI chat and carbon reduction insights",
    version="1.1.0"
)


# ==========================================
# CORS CONFIGURATION
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"]
)


# ==========================================
# GOOGLE ADK RUNNER AND SESSION SERVICE
# ==========================================

APP_NAME = "drishti_carbon_coach"

session_service = InMemorySessionService()

runner = Runner(
    agent=root_agent,
    app_name=APP_NAME,
    session_service=session_service
)


# ==========================================
# CHAT REQUEST MODEL
# ==========================================

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    user_id: str = "web_user"


# ==========================================
# HOME ENDPOINT
# ==========================================

@app.get("/")
def home():
    return {
        "message": "Welcome to Drishti Carbon Coach API",
        "status": "running"
    }


# ==========================================
# CHATBOT ENDPOINT
# ==========================================

@app.post("/api/chat")
async def chat(request: ChatRequest):

    if not request.message.strip():
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty."
        )

    try:
        if request.session_id:

            session = await session_service.get_session(
                app_name=APP_NAME,
                user_id=request.user_id,
                session_id=request.session_id
            )

            if session is None:
                raise HTTPException(
                    status_code=404,
                    detail="Chat session not found."
                )

        else:

            session = await session_service.create_session(
                app_name=APP_NAME,
                user_id=request.user_id
            )

        new_message = types.Content(
            role="user",
            parts=[
                types.Part(text=request.message)
            ]
        )

        response_text = ""

        async for event in runner.run_async(
            user_id=request.user_id,
            session_id=session.id,
            new_message=new_message
        ):

            if event.is_final_response() and event.content:
                if event.content.parts:
                    response_text = "\n".join(
                        part.text
                        for part in event.content.parts
                        if part.text
                    )

        if not response_text:
            response_text = (
                "I couldn't generate a response. Please try again."
            )

        return {
            "response": response_text,
            "session_id": session.id,
            "user_id": request.user_id
        }

    except HTTPException:
        raise

    except Exception as error:
        print("Chat API error:", str(error))

        raise HTTPException(
            status_code=500,
            detail="Unable to process your message. Please try again."
        )


# ==========================================
# SUMMARY ENDPOINT
# ==========================================

@app.get("/api/summary")
def summary(period: str = "week"):

    if period not in ["day", "week", "month"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid period. Use day, week or month."
        )

    return get_summary(period)


# ==========================================
# DASHBOARD ENDPOINT
# ==========================================

@app.get("/api/dashboard")
def dashboard():
    return get_dashboard_data()


# ==========================================
# MONTHLY TREND ENDPOINT
# ==========================================

@app.get("/api/monthly-trend")
def monthly_trend(months: int = 6):

    if months < 1 or months > 24:
        raise HTTPException(
            status_code=400,
            detail="Months must be between 1 and 24."
        )

    return {
        "monthly_trend": get_monthly_trend(months)
    }


# ==========================================
# WEEKLY TREND ENDPOINT
# ==========================================

@app.get("/api/weekly-trend")
def weekly_trend():
    return {
        "weekly_trend": get_weekly_trend()
    }


# ==========================================
# CATEGORY BREAKDOWN ENDPOINT
# ==========================================

@app.get("/api/category-breakdown")
def category_breakdown():

    summary_data = get_summary("month")

    return {
        "category_totals": summary_data["category_totals"],
        "total_emissions_kg_co2e": (
            summary_data["total_emissions_kg_co2e"]
        ),
        "highest_emission_category": (
            summary_data["highest_emission_category"]
        )
    }


# ==========================================
# CARBON REDUCTION SUGGESTIONS ENDPOINT
# ==========================================

@app.get("/api/reductions")
def carbon_reductions(period: str = "week"):

    if period not in ["day", "week", "month"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid period. Use day, week or month."
        )

    result = suggest_reductions(period)

    if "error" in result:
        raise HTTPException(
            status_code=500,
            detail=result["error"]
        )

    return result
