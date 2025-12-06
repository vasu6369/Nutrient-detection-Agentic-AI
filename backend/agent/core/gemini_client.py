from __future__ import annotations

import os
import json
from dotenv import load_dotenv
from google import genai

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise RuntimeError("GEMINI_API_KEY not set in .env")

client = genai.Client(api_key=GEMINI_API_KEY)

DEFAULT_INSTRUCTIONS = """
You are an Agricultural Expert Assistant from Tamil Nadu.
Speak mostly in English, but with a friendly Tamil tone.
Use simple words that farmers can understand.
Ask EXACTLY ONE question at a time.
Do NOT answer your own questions.
Do NOT suggest remedies or fertilizer advice until all required data is collected.
Be short, polite and farmer-friendly.
Your questions should sound natural and conversational (like talking to a farmer),
around 5–12 words, not too formal.
"""


def ask_for_field(state: dict, field: str, instructions: str | None = None) -> str:
    """
    Use Gemini to generate ONE short question for the specific field:
      - "crop"
      - "area"
      - "fertilizer_type"
      - "irrigation_type"
      - "growth_stage"
      - "symptom_duration"
      - "leaf_age"
    """

    sys = instructions or DEFAULT_INSTRUCTIONS

    filled = {
        k: v for k, v in state.items()
        if v not in (None, "", 0, False)
    }

    if field == "crop":
        field_desc = "the crop name (for example: banana, rice, maize, etc.)"
    elif field == "area":
        field_desc = "the cultivation area size in hectares (numeric like 1, 5, 10, 20)"
    elif field == "fertilizer_type":
        field_desc = "whether they prefer organic or chemical fertilizer"
    elif field == "irrigation_type":
        field_desc = "whether the field is irrigated (borewell/canal) or rainfed"
    elif field == "growth_stage":
        field_desc = (
            "the current crop growth stage such as seedling, vegetative, "
            "flowering or fruiting"
        )
    elif field == "symptom_duration":
        field_desc = (
            "how long the nutrient deficiency symptoms have been visible, "
            "in days or weeks"
        )
    elif field == "leaf_age":
        field_desc = (
            "whether symptoms appear more on younger leaves or on older leaves"
        )
    else:
        field_desc = field

    prompt = f"""
{sys}

You are inside a nutrient deficiency assistant that already detected leaf issues using a CV model.

Current known information (JSON):
{json.dumps(filled, ensure_ascii=False, indent=2)}

Your task now:
- Ask EXACTLY ONE short and casual question.
- The question MUST collect the specific field: "{field}" which means: {field_desc}.
- Do NOT ask about any fields that are already known in the JSON above.
- Do NOT ask multiple questions in one message.
- Do NOT explain anything or give suggestions.
- Just return the question sentence only, nothing else.
"""

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
    )
    text = response.text.strip()
    return text.splitlines()[0]

def generate_remedy(
    deficiency: str,
    crop: str | None,
    state: dict,
    rag_chunks: list[dict],
    fertilizer_plan: dict,
    instructions: str | None = None,
) -> str:
    """
    Use Gemini to combine RAG chunks + fertilizer plan + conversation state
    into one clear, farmer-friendly remedy message.
    """

    sys = (instructions or DEFAULT_INSTRUCTIONS) + """
Now your task is to give nutrient management advice.
Very important rules:
- Base your answer ONLY on the given RAG notes and fertilizer plan.
- Do NOT invent new chemical names or doses.
- Use simple language, friendly tone, like talking to a farmer from Tamil Nadu.
- Mix a little Tamil flavour with simple English, but keep it understandable.
- Keep the answer in 2–4 short paragraphs plus bullet points if needed.
"""

    rag_texts = "\n\n---\n\n".join(rag_chunks)


    prompt = f"""
System context:
{sys}

Detected deficiency: {deficiency}
Crop: {crop}

Conversation state (JSON):
{json.dumps(state, ensure_ascii=False, indent=2)}

Fertilizer plan (kg or g based on your tool output):
{json.dumps(fertilizer_plan, ensure_ascii=False, indent=2)}

Relevant RAG notes (do not ignore these):

{rag_texts}

Your task:
- Summarise the key remedy steps for this farmer.
- Include:
  - What the problem is (few lines).
  - Exact fertilizer / spray recommendation (from fertilizer_plan + RAG notes).
  - Any timing, mixing, or safety precautions (from RAG text).
- Answer as ONE helpful message.
"""

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
    )
    return response.text.strip()
