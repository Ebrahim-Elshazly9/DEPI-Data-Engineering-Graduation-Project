import re
from textblob import TextBlob
from typing import Optional


EMOTION_KEYWORDS = {
    "happy": ["happy", "joy", "excited", "wonderful", "great", "amazing", "grateful", "blessed", "delighted", "cheerful"],
    "sad": ["sad", "unhappy", "down", "depressed", "gloomy", "miserable", "heartbroken", "crying", "tears", "lonely"],
    "anxious": ["anxious", "nervous", "worried", "panic", "fear", "scared", "terrified", "dread", "uneasy", "restless"],
    "angry": ["angry", "frustrated", "irritated", "annoyed", "furious", "rage", "hostile", "resentful", "bitter"],
    "stressed": ["stressed", "overwhelmed", "burned out", "exhausted", "pressure", "overworked", "drained", "tension"],
    "calm": ["calm", "peaceful", "relaxed", "serene", "tranquil", "content", "balanced", "centered", "mindful"],
    "hopeful": ["hopeful", "optimistic", "positive", "encouraged", "motivated", "inspired", "determined", "confident"],
}

STRESS_INDICATORS = [
    "stress", "overwhelmed", "pressure", "burnout", "exhausted",
    "tired", "overwork", "deadline", "struggling", "can't cope",
]

ANXIETY_INDICATORS = [
    "worry", "panic", "fear", "nervous", "dread",
    "restless", "racing", "heart", "sweat", "tremble",
]

DEPRESSION_INDICATORS = [
    "hopeless", "worthless", "empty", "numb", "tired",
    "sleep", "appetite", "concentrate", "interest", "pleasure",
]

BURNOUT_INDICATORS = [
    "exhausted", "drained", "cynical", "detached", "ineffective",
    "overwhelmed", "burnout", "depleted", "frustrated", "tired",
]

SLEEP_KEYWORDS = [
    "sleep", "insomnia", "nightmare", "restless", "tired",
    "exhausted", "fatigue", "bed", "awake", "night",
]

ISOLATION_KEYWORDS = [
    "alone", "lonely", "isolated", "no friends", "nobody",
    "abandoned", "left out", "ignored", "solitary", "withdrawn",
]

URGENCY_KEYWORDS = [
    "help", "emergency", "crisis", "urgent", "suicide",
    "kill myself", "end my life", "want to die", "can't go on",
    "self-harm", "hurt myself", "988", "crisis line",
]


def analyze_sentiment(text: str) -> dict:
    blob = TextBlob(text)
    polarity = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity

    if polarity > 0.3:
        label = "positive"
    elif polarity < -0.3:
        label = "negative"
    else:
        label = "neutral"

    return {"score": round(polarity, 3), "label": label, "subjectivity": round(subjectivity, 3)}


def detect_emotions(text: str) -> dict:
    text_lower = text.lower()
    scores = {}
    for emotion, keywords in EMOTION_KEYWORDS.items():
        count = sum(1 for kw in keywords if kw in text_lower)
        scores[emotion] = count

    sorted_emotions = sorted(scores.items(), key=lambda x: -x[1])
    primary = sorted_emotions[0][0] if sorted_emotions[0][1] > 0 else "neutral"
    secondary = [e for e, s in sorted_emotions[1:4] if s > 0]

    return {"primary": primary, "secondary": secondary, "scores": scores}


def calculate_stress_level(text: str) -> float:
    text_lower = text.lower()
    words = text_lower.split()
    indicator_count = sum(1 for ind in STRESS_INDICATORS if ind in text_lower)
    if len(words) == 0:
        return 0.0
    raw_score = indicator_count / max(len(words) * 0.1, 1)
    return min(round(raw_score * 2, 2), 10.0)


def calculate_indicator_score(text: str, indicators: list[str]) -> float:
    text_lower = text.lower()
    words = text_lower.split()
    count = sum(1 for ind in indicators if ind in text_lower)
    if len(words) == 0:
        return 0.0
    raw = count / max(len(words) * 0.1, 1)
    return min(round(raw * 2, 2), 10.0)


def extract_keywords(text: str) -> list[str]:
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())
    stop_words = {
        "the", "and", "for", "are", "but", "not", "you", "all", "can", "had",
        "her", "was", "one", "our", "out", "has", "have", "been", "some", "them",
        "than", "its", "over", "very", "just", "also", "about", "into", "only",
        "other", "more", "these", "that", "this", "with", "from", "what", "which",
        "when", "where", "will", "would", "could", "should", "their", "there",
    }
    return list(dict.fromkeys([w for w in words if w not in stop_words])[:15])


def extract_topics(text: str) -> list[str]:
    text_lower = text.lower()
    topic_map = {
        "work": ["work", "job", "career", "office", "boss", "colleague", "professional"],
        "relationships": ["relationship", "partner", "friend", "family", "love", "marriage"],
        "health": ["health", "exercise", "diet", "sleep", "doctor", "therapy", "medication"],
        "finance": ["money", "finance", "debt", "bill", "expense", "salary", "budget"],
        "education": ["study", "school", "college", "university", "exam", "course", "class"],
        "self-care": ["meditation", "mindfulness", "yoga", "self-care", "relax", "breathing"],
        "anxiety": ["anxiety", "panic", "worry", "nervous", "fear", "dread"],
        "depression": ["depression", "sad", "hopeless", "empty", "worthless", "numb"],
        "trauma": ["trauma", "abuse", "hurt", "painful", "memory", "flashback"],
        "goals": ["goal", "aspire", "dream", "future", "plan", "ambition", "purpose"],
    }
    found = []
    for topic, keywords in topic_map.items():
        if any(kw in text_lower for kw in keywords):
            found.append(topic)
    return found


def check_crisis(text: str) -> bool:
    text_lower = text.lower()
    crisis_phrases = [
        "suicide", "kill myself", "want to die", "end my life",
        "self-harm", "hurt myself", "better off dead",
        "can't go on", "no reason to live", "end it all",
    ]
    return any(phrase in text_lower for phrase in crisis_phrases)


async def run_nlp_pipeline(text: str) -> dict:
    sentiment = analyze_sentiment(text)
    emotions = detect_emotions(text)
    stress_level = calculate_stress_level(text)
    anxiety = calculate_indicator_score(text, ANXIETY_INDICATORS)
    depression = calculate_indicator_score(text, DEPRESSION_INDICATORS)
    burnout = calculate_indicator_score(text, BURNOUT_INDICATORS)
    sleep_issues = any(kw in text.lower() for kw in SLEEP_KEYWORDS)
    isolation = any(kw in text.lower() for kw in ISOLATION_KEYWORDS)
    urgency = calculate_indicator_score(text, URGENCY_KEYWORDS)
    crisis = check_crisis(text)

    return {
        "sentiment": sentiment,
        "emotions": emotions,
        "stress_level": stress_level,
        "anxiety_indicators": anxiety,
        "depression_indicators": depression,
        "burnout_indicators": burnout,
        "sleep_issues": sleep_issues,
        "social_isolation": isolation,
        "confidence_level": round(max(0, min(10, 10 - stress_level * 0.5)), 2),
        "urgency_score": urgency,
        "crisis_detected": crisis,
        "keywords": extract_keywords(text),
        "topics": extract_topics(text),
        "entities": [],
        "user_goals": [],
        "behavioral_patterns": [],
    }
