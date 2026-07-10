from app.config import settings
from typing import Optional
import httpx


def get_llm_client() -> tuple[str, dict[str, str]]:
    if settings.ai_provider == "groq" and settings.groq_api_key:
        return settings.groq_base_url, {
            "Authorization": f"Bearer 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",
            "Content-Type": "application/json",
        }
    if settings.ai_provider == "openai" and settings.openai_api_key:
        return "https://api.openai.com/v1", {
            "Authorization": f"Bearer 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",
            "Content-Type": "application/json",
        }
    return "", {}


def get_model() -> str:
    return settings.ai_model


async def generate_chat_response(
    system_prompt: str,
    user_message: str,
    context: Optional[str] = None,
    max_tokens: int = 500,
) -> str:
    base_url, headers = get_llm_client()
    if not base_url:
        return ""

    model = get_model()
    messages = [{"role": "system", "content": system_prompt}]

    if context:
        messages.append({"role": "system", "content": f"Relevant context:\n{context[:2000]}"})

    messages.append({"role": "user", "content": user_message})

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{base_url}/chat/completions",
                headers=headers,
                json={
                    "model": model,
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": 0.7,
                },
            )
            data = resp.json()
            return data["choices"][0]["message"]["content"].strip()
    except Exception:
        return ""


async def generate_assessment_analysis(
    assessment_type: str,
    score: int,
    max_score: int,
    severity: str,
    answers: dict,
) -> dict:
    system_prompt = (
        "You are a clinical AI wellness analyst. Analyze the assessment results "
        "and provide: 1) A brief AI summary (2-3 sentences), 2) Risk category (Low/Medium/High/Critical), "
        "3) Personalized recommendations (list of 3-5 actionable items). "
        "Respond in JSON format with keys: summary, risk_category, recommendations (list)."
    )
    user_prompt = (
        f"Assessment: {assessment_type}\n"
        f"Score: {score}/{max_score}\n"
        f"Severity: {severity}\n"
        f"Answers: {answers}\n\n"
        "Provide the analysis in JSON format."
    )

    base_url, headers = get_llm_client()
    if not base_url:
        return {}

    model = get_model()
    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{base_url}/chat/completions",
                headers=headers,
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "max_tokens": 800,
                    "temperature": 0.3,
                    "response_format": {"type": "json_object"},
                },
            )
            data = resp.json()
            import json
            return json.loads(data["choices"][0]["message"]["content"])
    except Exception:
        return {}
