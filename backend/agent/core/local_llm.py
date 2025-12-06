# from llama_cpp import Llama
# import os
# import json


# class LocalLLM:
#     def __init__(
#         self,
#         model_path="models/llm/Phi-3.5-mini-instruct-Q6_K.gguf",
#         instructions_file=None,
#     ):
#         self.model = Llama(
#             model_path=model_path,
#             n_gpu_layers=40, 
#             n_ctx=4096,
#             n_threads=8,
#         )

#         self.system_prompt = ""
#         if instructions_file and os.path.exists(instructions_file):
#             with open(instructions_file, "r", encoding="utf-8") as f:
#                 self.system_prompt = f.read()

#     def ask(self, state: dict):
#       missing = [k for k, v in state.items() if v is None]
    
#       if not missing:
#           return ""
    
#       field = missing[0]
    
#       field_questions = {
#           "crop": "Sir, what crop are you cultivating on this land?",
#           "area": "Sir, kindly mention the cultivation area (in acres or hectares).",
#           "fertilizer_type": "Sir, do you prefer organic or chemical fertilizer?",
#           "deficiency": "Please upload a clear leaf image for deficiency detection."
#       }
    
#       if field == "deficiency":
#           return "Sir, please upload a clear image of the plant leaf to detect deficiency."
    
#       return field_questions[field]

