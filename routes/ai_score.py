"""
ai_score.py — OpenRouter AI scoring endpoint for StayMatch room listings.

POST /api/rooms/ai-score
  Body (JSON):
    {
      "title": "Sunny 1BHK near Metro",
      "location": "Koramangala, Bangalore",
      "price": "18000",
      "description": "...",
      "room_type": "Single",
      "furnishing": "Furnished",
      "amenities": ["WiFi", "Gym"],
      "hygiene_score": 85,       // 0-100 from Hygiene step
      "safety_score": 75,        // 0-100 from Safety step
      "lifestyle_choices": ["No smoking", "Vegetarian preferred"],
      "photo_count": 4           // how many photos were uploaded
    }

  Returns:
    {
      "success": true,
      "ai_score": 8.7,           // 0-10 scale (for room card display)
      "hygiene": 88,
      "safety": 76,
      "lifestyle": 82,
      "feedback": "Great listing! ...",
      "tips": ["Add CCTV for +15 safety score", "..."]
    }
"""

import os
import json
import requests
from flask import Blueprint, request, jsonify
from routes.matches import token_required

ai_score_bp = Blueprint('ai_score', __name__)

OPENROUTER_API_KEY = "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"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "openai/gpt-4o-mini"   # cheap + fast, great for structured JSON


def call_openrouter(prompt: str) -> dict:
    """Call OpenRouter and return parsed JSON from the model."""
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://staymatch.app",
        "X-Title": "StayMatch Room AI Scorer"
    }
    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a real estate and roommate matching expert AI for an Indian housing app called StayMatch. "
                    "Analyze room listings and provide REAL, accurate scores based on the data given. "
                    "Respond ONLY with valid JSON as specified. No markdown, no explanation, only raw JSON."
                )
            },
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3,
        "max_tokens": 600
    }
    resp = requests.post(OPENROUTER_URL, headers=headers, json=payload, timeout=20)
    resp.raise_for_status()
    raw = resp.json()["choices"][0]["message"]["content"].strip()
    # Strip any accidental markdown fences
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


@ai_score_bp.route('/ai-score', methods=['POST'])
@token_required
def analyze_room(user_id):
    data = request.json or {}

    title = data.get('title', 'Unknown Room')
    location = data.get('location', 'Unknown')
    price = data.get('price', '0')
    description = data.get('description', '')
    room_type = data.get('room_type', 'Single')
    furnishing = data.get('furnishing', 'Unfurnished')
    amenities = data.get('amenities', [])
    hygiene_score = int(data.get('hygiene_score', 50))
    safety_score = int(data.get('safety_score', 50))
    lifestyle_choices = data.get('lifestyle_choices', [])
    photo_count = int(data.get('photo_count', 0))
    description_length = len(description)

    # Build a detailed prompt
    prompt = f"""
Analyze this Indian room listing for StayMatch and give realistic scores.

ROOM DETAILS:
- Title: {title}
- Location: {location}
- Monthly Rent: ₹{price}
- Room Type: {room_type}
- Furnishing: {furnishing}
- Amenities: {', '.join(amenities) if amenities else 'None mentioned'}
- Description length: {description_length} characters
- Description: {description[:300] if description else 'Not provided'}
- Photos uploaded: {photo_count}
- Lifestyle preferences: {', '.join(lifestyle_choices) if lifestyle_choices else 'None'}
- User-rated Hygiene: {hygiene_score}/100
- User-rated Safety: {safety_score}/100

Scoring rules:
- hygiene: Use the user-provided hygiene_score as a BASE but adjust ±15 based on description keywords (clean, neat, maintained = +, dirty, old, cramped = -)
- safety: Use user-provided safety_score as BASE, adjust based on amenities (CCTV, guard, gated = +15 each) and location reputation
- lifestyle: Score 0-100 based on lifestyle_choices and amenities (WiFi, gym, AC, parking = higher score)
- overall: Weighted average: hygiene*0.35 + safety*0.30 + lifestyle*0.25 + (photo_count >= 3 ? 10 : 0)
- Convert overall to 0-10 scale for "ai_score"
- feedback: 2-3 sentence honest assessment mentioning strong points and weak points
- tips: List of 2-4 specific actionable tips to improve the score

Respond with ONLY this JSON (no markdown):
{{
  "hygiene": <integer 0-100>,
  "safety": <integer 0-100>,
  "lifestyle": <integer 0-100>,
  "overall": <integer 0-100>,
  "ai_score": <float 0.0-10.0, one decimal>,
  "feedback": "<2-3 sentence assessment>",
  "tips": ["<tip1>", "<tip2>", "<tip3>"]
}}
"""

    try:
        result = call_openrouter(prompt)

        # Validate and clamp all scores
        hygiene = max(0, min(100, int(result.get('hygiene', hygiene_score))))
        safety = max(0, min(100, int(result.get('safety', safety_score))))
        lifestyle = max(0, min(100, int(result.get('lifestyle', 60))))
        overall = max(0, min(100, int(result.get('overall', 70))))
        ai_score = max(0.0, min(10.0, float(result.get('ai_score', overall / 10))))
        feedback = str(result.get('feedback', 'Good listing.'))
        tips = result.get('tips', [])

        return jsonify({
            "success": True,
            "ai_score": ai_score,
            "hygiene": hygiene,
            "safety": safety,
            "lifestyle": lifestyle,
            "overall": overall,
            "feedback": feedback,
            "tips": tips
        })

    except requests.Timeout:
        return jsonify({"success": False, "message": "AI service timed out. Please try again."}), 504
    except Exception as e:
        print(f"OpenRouter error: {e}")
        # Fallback: rule-based scoring if AI fails
        lifestyle = min(100, len(amenities) * 12 + len(lifestyle_choices) * 8)
        overall = int(hygiene_score * 0.35 + safety_score * 0.30 + lifestyle * 0.25 + (10 if photo_count >= 3 else 0))
        ai_score = round(overall / 10, 1)
        return jsonify({
            "success": True,
            "ai_score": ai_score,
            "hygiene": hygiene_score,
            "safety": safety_score,
            "lifestyle": lifestyle,
            "overall": overall,
            "feedback": "Your listing looks good! Add more details and photos to improve your AI score.",
            "tips": [
                "Add at least 3 clear photos to boost your score by 10 points.",
                "Include a detailed description with keywords like 'clean', 'maintained', 'secure'.",
                "List all available amenities to improve your Lifestyle score."
            ]
        })
