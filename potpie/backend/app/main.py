import os
from typing import Dict, List, Optional

import httpx
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from pydantic import BaseModel, Field, ValidationError
from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers.openrouter import OpenRouterProvider


class FailureRequest(BaseModel):
    description: str = Field(..., min_length=20, description="Detailed failure description")
    effort_level: Optional[int] = Field(None, ge=0, le=10, description="Self-reported effort level")
    preparation_hours: Optional[int] = Field(None, ge=0, description="Hours of preparation")
    confidence_before: Optional[int] = Field(None, ge=0, le=10, description="Confidence before the attempt")


class FailureAnalysis(BaseModel):
    primary_root_cause: str
    secondary_causes: List[str]
    repeated_behavior_pattern: str
    false_beliefs_or_assumptions: List[str]
    harsh_truth: str
    corrective_actions: List[str]
    seven_day_recovery_plan: Dict[str, str]
    long_term_warning: str


import pathlib

backend_dir = pathlib.Path(__file__).parent.parent
env_path = backend_dir / ".env"
load_dotenv(dotenv_path=env_path)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
MODEL_NAME = os.getenv("OPENROUTER_MODEL", "mistralai/mixtral-8x7b-instruct")

def build_agent() -> Agent[FailureAnalysis]:
    api_key = OPENROUTER_API_KEY if OPENROUTER_API_KEY and OPENROUTER_API_KEY != "your_key_here" else None
    provider = OpenRouterProvider(api_key=api_key)
    model = OpenAIChatModel(model_name=MODEL_NAME, provider=provider)
    system_prompt = (
        "You are 'Explain My Failure' — a brutally honest analyst. "
        "Return concise, specific critiques. Avoid generic coaching. "
        "Use the user's context to surface patterns and actionable fixes."
    )
    return Agent(model=model, output_type=FailureAnalysis, system_prompt=system_prompt, retries=2)


agent = build_agent()
app = FastAPI(title="Explain My Failure API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health") 
async def health():
    return {"status": "ok"}


def generate_demo_response(description: str, effort: int, prep_hours: int, confidence: int) -> FailureAnalysis:
    desc_lower = description.lower()
    is_exam = any(word in desc_lower for word in ["exam", "test", "quiz", "exam"])
    is_interview = any(word in desc_lower for word in ["interview", "interviewed", "interviewing"])
    is_project = any(word in desc_lower for word in ["project", "assignment", "deadline"])
    
    if is_exam:
        root_cause = "Passive learning without active recall. You consumed content but didn't test your understanding under pressure."
        pattern = "Cramming → False confidence → Performance anxiety → Failure"
        truth = "Watching videos isn't studying. You need to solve problems yourself, time yourself, and fail in practice before the real test."
    elif is_interview:
        root_cause = "Insufficient mock practice and overconfidence from solving problems in isolation."
        pattern = "LeetCode in comfort → Avoiding system design → No mock interviews → Freezing under pressure"
        truth = "You prepared for the wrong thing. Interviews test communication and problem-solving under pressure, not just coding ability."
    elif is_project:
        root_cause = "Poor planning and underestimating complexity. Started coding before understanding requirements."
        pattern = "Jumping to code → Scope creep → Deadline pressure → Rushed work → Failure"
        truth = "You confused activity with progress. Planning and breaking down problems saves more time than it costs."
    else:
        root_cause = "Gap between perceived effort and actual effective work. You did things that felt productive but didn't address core weaknesses."
        pattern = "Surface-level preparation → Avoiding difficult practice → Overconfidence → Reality check → Failure"
        truth = "Effort without direction is just busywork. You need to identify your weakest points and attack them directly."
    
    return FailureAnalysis(
        primary_root_cause=root_cause,
        secondary_causes=[
            "Insufficient practice under realistic conditions",
            "Avoiding difficult or uncomfortable practice scenarios",
            "Overestimating readiness based on passive learning"
        ],
        repeated_behavior_pattern=pattern,
        false_beliefs_or_assumptions=[
            f"Effort level {effort}/10 was sufficient",
            f"{prep_hours} hours of preparation was enough",
            f"Confidence level {confidence}/10 reflected actual ability"
        ],
        harsh_truth=truth,
        corrective_actions=[
            "Identify the 3 weakest areas and practice them daily",
            "Create realistic practice scenarios that mirror the actual challenge",
            "Track metrics: time spent, accuracy, consistency",
            "Get external feedback before the next attempt",
            "Build a recovery timeline with specific milestones"
        ],
        seven_day_recovery_plan={
            "Day 1": "Honest self-assessment: List exactly what went wrong and why",
            "Day 2": "Identify 3 core weaknesses and find resources to address them",
            "Day 3": "Create a structured practice schedule with daily goals",
            "Day 4": "Start practicing the hardest problems/scenarios first",
            "Day 5": "Get feedback from someone who succeeded in this area",
            "Day 6": "Simulate the actual conditions and test yourself",
            "Day 7": "Review progress, adjust plan, commit to long-term improvement"
        },
        long_term_warning="If you don't change your approach fundamentally, you'll repeat this cycle. Stop doing what feels comfortable and start doing what's actually effective."
    )


@app.post("/analyze", response_model=FailureAnalysis)
async def analyze_failure(payload: FailureRequest):
    # Demo mode if API key is missing
    use_demo = not OPENROUTER_API_KEY or OPENROUTER_API_KEY == "your_key_here"
    
    if use_demo:
        logger.info("Using demo mode - API key not set")
        return generate_demo_response(
            payload.description,
            payload.effort_level or 5,
            payload.preparation_hours or 0,
            payload.confidence_before or 5
        )

    prompt = f"""
Failure description:
{payload.description}

Effort level: {payload.effort_level}
Preparation hours: {payload.preparation_hours}
Confidence before: {payload.confidence_before}

Provide a concise, structured diagnosis.
"""

    try:
        # pydantic-ai v1.x returns an AgentRunResult with validated `.data`
        result = await agent.run(prompt)
        logger.info("Analysis completed")
        return result.data
    except ValidationError as ve:
        logger.error(f"Validation error: {ve}")
        raise HTTPException(status_code=500, detail=f"Agent validation failed: {str(ve)}")
    except httpx.HTTPError as he:
        logger.error(f"HTTP error calling model: {he}")
        raise HTTPException(status_code=502, detail=f"Model provider unavailable: {str(he)}")
    except Exception as exc:  # pragma: no cover
        logger.exception(f"Unexpected error: {exc}")
        error_msg = str(exc)
        # Fallback to demo mode on API errors
        if "api_key" in error_msg.lower() or "authentication" in error_msg.lower() or "401" in error_msg:
            logger.warning("API error detected, falling back to demo mode")
            return generate_demo_response(
                payload.description,
                payload.effort_level or 5,
                payload.preparation_hours or 0,
                payload.confidence_before or 5
            )
        raise HTTPException(status_code=500, detail=f"Server error: {error_msg}")

