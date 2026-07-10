from typing import Optional


def calculate_wellness_score(nlp_result: dict) -> float:
    stress = nlp_result.get("stress_level", 0)
    anxiety = nlp_result.get("anxiety_indicators", 0)
    depression = nlp_result.get("depression_indicators", 0)
    burnout = nlp_result.get("burnout_indicators", 0)
    sentiment_score = nlp_result.get("sentiment", {}).get("score", 0)

    negative_factors = (stress + anxiety + depression + burnout) / 4
    sentiment_factor = (1 - sentiment_score) * 5

    raw_score = 10 - (negative_factors * 0.6 + sentiment_factor * 0.4)
    return round(max(0, min(10, raw_score)), 2)


def get_risk_category(score: float) -> str:
    if score >= 8:
        return "Low"
    elif score >= 5:
        return "Medium"
    elif score >= 3:
        return "High"
    return "Critical"


def get_risk_reasoning(nlp_result: dict) -> str:
    parts = []
    if nlp_result.get("stress_level", 0) > 7:
        parts.append("high stress levels detected")
    if nlp_result.get("anxiety_indicators", 0) > 7:
        parts.append("elevated anxiety indicators")
    if nlp_result.get("depression_indicators", 0) > 7:
        parts.append("depression indicators present")
    if nlp_result.get("burnout_indicators", 0) > 7:
        parts.append("burnout risk detected")
    if nlp_result.get("sleep_issues"):
        parts.append("sleep-related concerns")
    if nlp_result.get("social_isolation"):
        parts.append("social isolation indicators")
    if nlp_result.get("crisis_detected"):
        parts.append("CRISIS INDICATORS - immediate attention required")

    if not parts:
        return "No significant risk factors detected. Maintaining healthy patterns."
    return "Risk factors: " + "; ".join(parts) + "."


def generate_recommendations(nlp_result: dict, wellness_score: float) -> list[dict]:
    recs = []

    if wellness_score < 4:
        recs.append({
            "category": "Crisis",
            "title": "Contact Crisis Support",
            "description": "Please reach out to a mental health professional or crisis hotline. In the US, call or text 988.",
            "priority": 1,
            "reason": "Critical wellness indicators detected",
        })

    if nlp_result.get("stress_level", 0) > 6:
        recs.append({
            "category": "Breathing Exercises",
            "title": "Deep Breathing Exercise",
            "description": "Try the 4-7-8 breathing technique: inhale for 4 seconds, hold for 7, exhale for 8. Repeat 4 times.",
            "priority": 2,
            "estimated_time": "5 minutes",
            "difficulty": "Easy",
            "reason": "High stress levels detected",
            "expected_benefit": "Immediate stress reduction and calmness",
        })
        recs.append({
            "category": "Mindfulness",
            "title": "5-Minute Body Scan",
            "description": "Close your eyes and slowly scan attention from your toes to the top of your head. Notice sensations without judgment.",
            "priority": 3,
            "estimated_time": "5 minutes",
            "difficulty": "Easy",
            "reason": "Stress management support",
            "expected_benefit": "Reduced muscle tension and mental clarity",
        })

    if nlp_result.get("anxiety_indicators", 0) > 6:
        recs.append({
            "category": "Meditation",
            "title": "Guided Anxiety Relief Meditation",
            "description": "Find a quiet space and listen to a guided meditation focused on releasing anxiety and finding inner peace.",
            "priority": 2,
            "estimated_time": "10 minutes",
            "difficulty": "Medium",
            "reason": "Elevated anxiety indicators",
            "expected_benefit": "Reduced anxiety and improved emotional regulation",
        })

    if nlp_result.get("depression_indicators", 0) > 6:
        recs.append({
            "category": "Exercise",
            "title": "Gentle Walk in Nature",
            "description": "Take a 15-20 minute walk outside in a park or green space. Focus on your surroundings and breathing.",
            "priority": 3,
            "estimated_time": "20 minutes",
            "difficulty": "Easy",
            "reason": "Depression indicators detected",
            "expected_benefit": "Improved mood through physical activity and nature exposure",
        })
        recs.append({
            "category": "Gratitude",
            "title": "Three Good Things Journal",
            "description": "Write down three positive things that happened today, no matter how small. Reflect on why they happened.",
            "priority": 4,
            "estimated_time": "5 minutes",
            "difficulty": "Easy",
            "reason": "Support positive thinking patterns",
            "expected_benefit": "Shifted focus toward positive experiences",
        })

    if nlp_result.get("sleep_issues"):
        recs.append({
            "category": "Sleep",
            "title": "Sleep Hygiene Routine",
            "description": "Establish a consistent bedtime routine: dim lights 1 hour before bed, avoid screens, read a book, or practice gentle stretches.",
            "priority": 3,
            "estimated_time": "30 minutes",
            "difficulty": "Medium",
            "reason": "Sleep-related concerns identified",
            "expected_benefit": "Improved sleep quality and duration",
        })

    if nlp_result.get("social_isolation"):
        recs.append({
            "category": "Social Activities",
            "title": "Reach Out to a Friend",
            "description": "Send a message to a trusted friend or family member today. Even a brief conversation can help you feel connected.",
            "priority": 3,
            "estimated_time": "10 minutes",
            "difficulty": "Medium",
            "reason": "Social isolation indicators detected",
            "expected_benefit": "Reduced loneliness and improved social connection",
        })

    if nlp_result.get("burnout_indicators", 0) > 5:
        recs.append({
            "category": "Productivity",
            "title": "Take a Strategic Break",
            "description": "Step away from work for 15 minutes. Use the Pomodoro technique: 25 minutes work, 5 minutes break.",
            "priority": 2,
            "estimated_time": "15 minutes",
            "difficulty": "Easy",
            "reason": "Burnout indicators detected",
            "expected_benefit": "Prevented burnout and improved productivity",
        })
        recs.append({
            "category": "Nutrition",
            "title": "Hydrate and Nourish",
            "description": "Drink a glass of water and eat a balanced snack with protein and complex carbohydrates to stabilize your energy.",
            "priority": 4,
            "estimated_time": "5 minutes",
            "difficulty": "Easy",
            "reason": "Support physical well-being during stress",
            "expected_benefit": "Stabilized energy levels and improved focus",
        })

    if wellness_score >= 7:
        recs.append({
            "category": "Reading",
            "title": "Explore Personal Growth Reading",
            "description": "Read a chapter from a book on personal development, positive psychology, or a topic that interests you.",
            "priority": 5,
            "estimated_time": "15 minutes",
            "difficulty": "Easy",
            "reason": "Maintain positive mental health trajectory",
            "expected_benefit": "Continued personal growth and insight",
        })

    return sorted(recs, key=lambda r: r["priority"])


async def generate_predictions(nlp_result: dict, user_id: str) -> dict:
    wellness = calculate_wellness_score(nlp_result)
    risk_cat = get_risk_category(wellness)
    reasoning = get_risk_reasoning(nlp_result)

    predictions = {
        "wellness_score": wellness,
        "stress_level": nlp_result.get("stress_level", 0),
        "burnout_risk": "High" if nlp_result.get("burnout_indicators", 0) > 7 else "Moderate" if nlp_result.get("burnout_indicators", 0) > 4 else "Low",
        "depression_risk": "High" if nlp_result.get("depression_indicators", 0) > 7 else "Moderate" if nlp_result.get("depression_indicators", 0) > 4 else "Low",
        "anxiety_risk": "High" if nlp_result.get("anxiety_indicators", 0) > 7 else "Moderate" if nlp_result.get("anxiety_indicators", 0) > 4 else "Low",
        "sleep_quality": "Poor" if nlp_result.get("sleep_issues") else "Good",
        "mood_trend": nlp_result.get("sentiment", {}).get("label", "neutral"),
        "emotional_stability": round(max(0, min(10, 10 - (nlp_result.get("stress_level", 0) + nlp_result.get("anxiety_indicators", 0)) * 0.3)), 2),
        "confidence_score": nlp_result.get("confidence_level", 5),
    }

    recommendations = generate_recommendations(nlp_result, wellness)

    return {
        "predictions": predictions,
        "risk_category": risk_cat,
        "reasoning": reasoning,
        "recommendations": recommendations,
    }
