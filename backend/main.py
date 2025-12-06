# from fastapi import FastAPI, UploadFile, Form, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from agent.core.agent_orchestrator import AgentOrchestrator
# import tempfile
# import shutil
#
# # FastAPI app
# app = FastAPI()
#
# # CORS for frontend
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_methods=["*"],
#     allow_headers=["*"]
# )
#
# # Load your trained CV model
# model_path = "models/banana_deficiency_model.pth"
# class_names = ["Boron", "Calcium", "Healthy", "Iron", "Magnesium", "Manganese", "Potassium","Sulphur","Zinc"]
# agent = AgentOrchestrator(cv_model_path=model_path, class_names=class_names)
#
# # API endpoint
# @app.post("/chat")
# async def chat(file: UploadFile = None, user_answer: str = Form(None)):
#     image_path = None
#     if file:
#         with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
#             shutil.copyfileobj(file.file, tmp)
#             image_path = tmp.name
#
#     response = agent.run(image_path=image_path, user_answer=user_answer)
#     return response
#
# @app.post("/reset")
# async def reset_conversation():
#     """
#     Reset the global agent so it forgets previous conversation.
#     """
#     global agent
#     try:
#         # Recreate a fresh AgentOrchestrator with same model + classes
#         agent = AgentOrchestrator(cv_model_path=model_path, class_names=class_names)
#         return {"status": "ok", "message": "Conversation reset"}
#     except Exception as e:
#         print("Error resetting agent:", e)
#         raise HTTPException(status_code=500, detail="Failed to reset agent")
#


# from fastapi import FastAPI, UploadFile, Form, HTTPException, BackgroundTasks
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import FileResponse
# from agent.core.agent_orchestrator import AgentOrchestrator
# import tempfile
# import shutil
# import uuid
# import os
#
# import edge_tts  # 👈 Edge TTS
#
#
# # FastAPI app
# app = FastAPI()
#
# app.add_middleware(
#         CORSMiddleware,
#         allow_origins=["*"],
#         allow_methods=["*"],
#         allow_headers=["*"]
#     )
#
#
# model_path = "models/banana_deficiency_model.pth"
# class_names = ["Boron", "Calcium", "Healthy", "Iron", "Magnesium", "Manganese", "Potassium","Sulphur","Zinc"]
# agent = AgentOrchestrator(cv_model_path=model_path, class_names=class_names)
#
#
# import os
# import uuid
# import tempfile
# import edge_tts
# import re  # add this
#
# def clean_text_for_tts(text: str) -> str:
#     """
#     Remove emojis, markdown symbols (*, _, ~, etc.) so TTS doesn't read them aloud.
#     """
#     if not text:
#         return ""
#
#     # remove markdown symbols
#     text = re.sub(r'[*_~`>|#]', ' ', text)
#
#     # remove emojis (big unicode ranges)
#     emoji_pattern = re.compile(
#         "["
#         "\U0001F300-\U0001F5FF"
#         "\U0001F600-\U0001F64F"
#         "\U0001F680-\U0001F6FF"
#         "\U0001F700-\U0001F77F"
#         "\U0001F780-\U0001F7FF"
#         "\U0001F800-\U0001F8FF"
#         "\U0001F900-\U0001F9FF"
#         "\U0001FA00-\U0001FAFF"
#         "\U00002700-\U000027BF"
#         "\U00002600-\U000026FF"
#         "]+",
#         flags=re.UNICODE,
#     )
#     text = emoji_pattern.sub(" ", text)
#
#     # collapse spaces
#     text = re.sub(r"\s+", " ", text).strip()
#
#     return text
#
#
#
#
# async def synthesize_speech(text: str, voice: str = "en-IN-NeerjaNeural") -> str:
#         """
#         Generate speech using Edge TTS and save to a temp mp3 file.
#         Returns the file path.
#         """
#         if not text.strip():
#             raise ValueError("Empty text for TTS")
#
#     # unique temp file
#         out_path = os.path.join(
#             tempfile.gettempdir(),
#             f"tts_{uuid.uuid4().hex}.mp3"
#         )
#
#         communicate = edge_tts.Communicate(text, voice)
#         await communicate.save(out_path)
#         return out_path
#
#
#
# from typing import Optional
#
# @app.post("/chat")
# async def chat(file: Optional[UploadFile] = None, user_answer: str = Form(None)):
#         image_path = None
#         if file:
#             with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
#                 shutil.copyfileobj(file.file, tmp)
#                 image_path = tmp.name
#
#         # Normalize text
#         text = (user_answer or "").strip()
#         lower = text.lower()
#
#         # --- 1) If NO image and user just greets / random talk, DON'T call the agent ---
#         if not image_path:
#             # simple greeting detection
#             greetings = ["hi", "hello", "hey", "yo", "good morning", "good evening"]
#             if any(lower == g for g in greetings) or any(lower.startswith(g + " ") for g in greetings):
#                 return {
#                     "ask_user": (
#                         "Hi! 👋 I’m your plant nutrient assistant.\n\n"
#                         "Please upload a clear photo of your plant so I can start the diagnosis."
#                     )
#                 }
#
#             # thanks / okay / bye
#             if lower in ["thanks", "thank you", "ok", "okay", "bye", "good night"]:
#                 return {
#                     "ask_user": (
#                         "You’re welcome! 🌱\n"
#                         "If you want a diagnosis, just upload a plant photo anytime."
#                     )
#                 }
#
#             # If user types something that clearly has nothing to do with plants
#             # If user types something clearly unrelated to plants, show a gentle message.
#             # But allow:
#             #   - numbers like "25"
#             #   - short answers like "organic", "chemical fertilizer", "urea", etc.
#             plant_keywords = [
#                 "leaf", "leaves", "plant", "banana", "spot", "yellow", "disease", "deficiency",
#                 "soil", "water", "fertilizer", "organic", "chemical", "compost",
#                 "manure", "urea", "npk", "spray", "irrigation", "pest", "farm", "hectare", "acre"
#             ]
#
#             tokens = lower.split()
#             is_number = lower.replace(".", "", 1).isdigit()
#
#             # Only block if:
#             #  - user typed more than 2 words (a full sentence)
#             #  - NO plant keywords
#             #  - NOT just a number (like "25")
#             if text and len(tokens) > 2 and not any(k in lower for k in plant_keywords) and not is_number:
#                 return {
#                     "ask_user": (
#                         "I’m designed specifically to help with plant nutrient and disease issues. 🌿\n\n"
#                         "Please upload a photo of your plant or describe what’s happening to the leaves "
#                         "(spots, yellowing, drying, etc.), and I’ll guide you."
#                     )
#                 }
#
#         # --- 2) Normal path: call your agent ---
#         response = agent.run(image_path=image_path, user_answer=user_answer)
#         return response
#
#
# @app.post("/tts")
# async def tts(
#     background_tasks: BackgroundTasks,
#     text: str = Form(...)
# ):
#     """
#     Convert text to speech using Edge TTS and return an MP3 file.
#     """
#     try:
#         clean = clean_text_for_tts(text)
#
#         if not clean:
#             raise HTTPException(status_code=400, detail="Nothing to read after cleaning.")
#
#         audio_path = await synthesize_speech(clean)
#
#     except ValueError as e:
#         raise HTTPException(status_code=400, detail=str(e))
#     except Exception as e:
#         print("TTS error:", e)
#         raise HTTPException(status_code=500, detail="TTS generation failed")
#
#     # Delete the temp file after response is sent
#     background_tasks.add_task(os.remove, audio_path)
#
#     return FileResponse(
#         audio_path,
#         media_type="audio/mpeg",
#         filename="speech.mp3"
#     )
#
#
#
# @app.post("/reset")
# async def reset_conversation():
#         """
#         Reset the global agent so it forgets previous conversation.
#         """
#         global agent
#         try:
#             # Recreate a fresh AgentOrchestrator with same model + classes
#             agent = AgentOrchestrator(cv_model_path=model_path, class_names=class_names)
#             return {"status": "ok", "message": "Conversation reset"}
#         except Exception as e:
#             print("Error resetting agent:", e)
#             raise HTTPException(status_code=500, detail="Failed to reset agent")





from fastapi import FastAPI, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from agent.core.agent_orchestrator import AgentOrchestrator

from typing import Optional
import tempfile
import shutil
import uuid
import os
import re

import edge_tts  # Edge TTS


# -----------------------------
# FastAPI app setup
# -----------------------------
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------
# Model / Agent setup
# -----------------------------
model_path = "models/banana_deficiency_model.pth"
class_names = [
    "Boron", "Calcium", "Healthy", "Iron", "Magnesium",
    "Manganese", "Potassium", "Sulphur", "Zinc"
]
agent = AgentOrchestrator(cv_model_path=model_path, class_names=class_names)


# -----------------------------
# TTS text cleaning
# -----------------------------
def clean_text_for_tts(text: str) -> str:
    """
    Remove emojis, markdown symbols (*, _, ~, etc.) so TTS doesn't read them aloud.
    """
    if not text:
        return ""

    # Remove markdown / formatting symbols
    text = re.sub(r'[*_~`>|#]', ' ', text)

    # Remove emojis (unicode ranges)
    emoji_pattern = re.compile(
        "["
        "\U0001F300-\U0001F5FF"  # symbols & pictographs
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F680-\U0001F6FF"  # transport & map
        "\U0001F700-\U0001F77F"
        "\U0001F780-\U0001F7FF"
        "\U0001F800-\U0001F8FF"
        "\U0001F900-\U0001F9FF"
        "\U0001FA00-\U0001FAFF"
        "\U00002700-\U000027BF"  # dingbats
        "\U00002600-\U000026FF"  # misc symbols
        "]+",
        flags=re.UNICODE,
    )
    text = emoji_pattern.sub(" ", text)

    # Collapse multiple spaces
    text = re.sub(r"\s+", " ", text).strip()

    return text


# -----------------------------
# Edge TTS synthesis
# -----------------------------
async def synthesize_speech(text: str, voice: str = "en-IN-NeerjaNeural") -> str:
    """
    Generate speech using Edge TTS and save to a temp mp3 file.
    Returns the file path.
    """
    if not text.strip():
        raise ValueError("Empty text for TTS")

    # unique temp file
    out_path = os.path.join(
        tempfile.gettempdir(),
        f"tts_{uuid.uuid4().hex}.mp3"
    )

    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(out_path)
    return out_path


# -----------------------------
# Chat endpoint
# -----------------------------
@app.post("/chat")
async def chat(
    file: Optional[UploadFile] = None,
    user_answer: str = Form(None),
):
    image_path = None

    # If image uploaded, save to temp file
    if file:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            shutil.copyfileobj(file.file, tmp)
            image_path = tmp.name

    # Normalize text
    text = (user_answer or "").strip()
    lower = text.lower()

    # --- 1) If NO image and user just greets / random talk, DON'T call the agent ---
    if not image_path:
        # Simple greeting detection
        greetings = ["hi", "hello", "hey", "yo", "good morning", "good evening"]
        if any(lower == g for g in greetings) or any(lower.startswith(g + " ") for g in greetings):
            return {
                "ask_user": (
                    "Hi! 👋 I’m your plant nutrient assistant.\n\n"
                    "Please upload a clear photo of your plant so I can start the diagnosis."
                )
            }

        # Thanks / okay / bye
        if lower in ["thanks", "thank you", "ok", "okay", "bye", "good night"]:
            return {
                "ask_user": (
                    "You’re welcome! 🌱\n"
                    "If you want a diagnosis, just upload a plant photo anytime."
                )
            }

        # If user types something clearly unrelated to plants, show a gentle message.
        # But allow:
        #   - numbers like "25"
        #   - short answers like "organic", "chemical fertilizer", "urea", etc.
        plant_keywords = [
            "leaf", "leaves", "plant", "banana", "spot", "yellow", "disease", "deficiency",
            "soil", "water", "fertilizer", "organic", "chemical", "compost",
            "manure", "urea", "npk", "spray", "irrigation", "pest",
            "farm", "hectare", "acre"
        ]

        tokens = lower.split()
        is_number = lower.replace(".", "", 1).isdigit()

        # Only block if:
        #  - user typed more than 2 words (a full sentence)
        #  - NO plant keywords
        #  - NOT just a number (like "25")
        if text and len(tokens) > 2 and not any(k in lower for k in plant_keywords) and not is_number:
            return {
                "ask_user": (
                    "I’m designed specifically to help with plant nutrient and disease issues. 🌿\n\n"
                    "Please upload a photo of your plant or describe what’s happening to the leaves "
                    "(spots, yellowing, drying, etc.), and I’ll guide you."
                )
            }

    # --- 2) Normal path: call your agent (image or valid text) ---
    response = agent.run(image_path=image_path, user_answer=user_answer)
    return response


# -----------------------------
# TTS endpoint
# -----------------------------
@app.post("/tts")
async def tts(
    background_tasks: BackgroundTasks,
    text: str = Form(...),
):
    """
    Convert text to speech using Edge TTS and return an MP3 file.
    """
    # Clean text so TTS doesn't read emojis/symbols
    clean = clean_text_for_tts(text)

    if not clean:
        raise HTTPException(status_code=400, detail="Nothing to read after cleaning.")

    try:
        audio_path = await synthesize_speech(clean)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print("TTS error:", e)
        raise HTTPException(status_code=500, detail="TTS generation failed")

    # Delete the temp file after response is sent
    background_tasks.add_task(os.remove, audio_path)

    return FileResponse(
        audio_path,
        media_type="audio/mpeg",
        filename="speech.mp3",
    )


# -----------------------------
# Reset conversation endpoint
# -----------------------------
@app.post("/reset")
async def reset_conversation():
    """
    Reset the global agent so it forgets previous conversation.
    """
    global agent
    try:
        agent = AgentOrchestrator(cv_model_path=model_path, class_names=class_names)
        return {"status": "ok", "message": "Conversation reset"}
    except Exception as e:
        print("Error resetting agent:", e)
        raise HTTPException(status_code=500, detail="Failed to reset agent")
    


    