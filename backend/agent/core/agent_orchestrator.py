from __future__ import annotations

import os
import re

from agent.state.conversation_state import ConversationState
from agent.tools.cv_tool import CVTool
from agent.tools.rag_tool import RAGTool
from agent.tools.fertilizer_tool import FertilizerTool
from agent.core.gemini_client import ask_for_field, generate_remedy


class AgentOrchestrator:
    def __init__(self, cv_model_path, class_names, instruction_file: str | None = None):
        """
        cv_model_path: path to your trained PyTorch model (.pth)
        class_names: list of labels your CV model predicts
        """
        self.cv_tool = CVTool(model_path=cv_model_path, class_names=class_names)
        self.rag_tool = RAGTool()
        self.fert_tool = FertilizerTool()
        self.state = ConversationState()

        self.instructions = ""
        if instruction_file is None:
            instruction_file = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "agent_instructions.txt")
            )
        if os.path.exists(instruction_file):
            with open(instruction_file, "r", encoding="utf-8") as f:
                self.instructions = f.read()

    def run(self, image_path: str | None = None, user_answer: str | None = None):
        """
        Main agent logic.
        - image_path: new leaf image from frontend (optional)
        - user_answer: user's reply to last question (optional)

        Returns a dict with one of:
          - {"ask_user": "...", "conversation_state": {...}}
          - {"diagnosis": "...", "remedy_text": "...", "fertilizer_plan": {...}, "conversation_state": {...}}
        """

        if image_path is not None and user_answer is None:
            self.state = ConversationState()

        missing_before = self.state.missing_fields()
        if user_answer and missing_before:
            next_field = missing_before[0]
            self._fill_field(next_field, user_answer)

        if image_path is not None:
            cv_result = self.cv_tool.run(image_path)
            self.state.update("deficiency", cv_result["deficiency"])
            self.state.update("cv_confidence", cv_result["confidence"])

        if (
            self.state.deficiency is None
            and self.state.crop is None
            and self.state.area is None
            and self.state.fertilizer_type is None
        ):
            if image_path is None:
                return {
                    "ask_user": (
                        "Sir, please upload a clear image of the affected plant leaf "
                        "so I can analyse the deficiency."
                    ),
                    "conversation_state": self.state.to_dict(),
                }

        missing = self.state.missing_fields()
        if missing:
            field = missing[0]
            question = ask_for_field(
                state=self.state.to_dict(),
                field=field,
                instructions=self.instructions or None,
            )
            return {
                "ask_user": question,
                "conversation_state": self.state.to_dict(),
            }

        if not self.state.deficiency:
            return {
                "ask_user": (
                    "Sir, please upload a clear close-up image of the leaf "
                    "so I can detect the nutrient deficiency."
                ),
                "conversation_state": self.state.to_dict(),
            }

        deficiency = self.state.deficiency
        crop = self.state.crop
        area_val = self._parse_area(self.state.area)

        rag_query_parts = [
            f"{deficiency} deficiency remedy",
        ]
        if crop:
            rag_query_parts.append(f"for {crop}")
        if self.state.growth_stage:
            rag_query_parts.append(f"at {self.state.growth_stage} stage")
        if self.state.irrigation_type:
            rag_query_parts.append(f"in {self.state.irrigation_type} fields")

        rag_query = " ".join(rag_query_parts)

        rag_result = self.rag_tool.search(rag_query, top_k=4)
        rag_chunks = rag_result["results"]

        fert_result = self.fert_tool.calculate(
            deficiency=deficiency,
            crop=crop,
            area_hectares=area_val,
            irrigation_type=self.state.irrigation_type,
            growth_stage=self.state.growth_stage,
        )
        fertilizer_plan = fert_result.get("fertilizer_recommendation", {})

        diagnosis = f"The plant shows {deficiency} deficiency."

        remedy_text = generate_remedy(
            deficiency=deficiency,
            crop=crop,
            state=self.state.to_dict(),
            rag_chunks=rag_chunks,
            fertilizer_plan=fertilizer_plan,
            instructions=self.instructions or None,
        )

        self.state.done = True

        return {
            "diagnosis": diagnosis,
            "remedy_text": remedy_text,
            "fertilizer_plan": fertilizer_plan,
            "conversation_state": self.state.to_dict(),
        }

    def _fill_field(self, field: str, answer: str):
        """Fill crop / area / fertilizer_type / extra fields deterministically (no LLM guessing)."""
        answer_clean = answer.strip()

        if field == "crop":
            self.state.update("crop", answer_clean)

        elif field == "area":
            num = self._extract_number(answer_clean)
            self.state.update("area", str(num) if num is not None else answer_clean)

        elif field == "fertilizer_type":
            lower = answer_clean.lower()
            if "organic" in lower:
                self.state.update("fertilizer_type", "organic")
            elif "chemical" in lower or "ure" in lower:
                self.state.update("fertilizer_type", "chemical")
            else:
                self.state.update("fertilizer_type", answer_clean)

        elif field == "irrigation_type":
            lower = answer_clean.lower()
            if "rain" in lower:
                self.state.update("irrigation_type", "rainfed")
            elif any(x in lower for x in ["bore", "canal", "drip"]):
                self.state.update("irrigation_type", "irrigated")
            else:
                self.state.update("irrigation_type", answer_clean)

        elif field == "growth_stage":
            self.state.update("growth_stage", answer_clean)

        elif field == "symptom_duration":
            self.state.update("symptom_duration", answer_clean)

        elif field == "leaf_age":
            lower = answer_clean.lower()
            if "young" in lower or "new" in lower:
                self.state.update("leaf_age", "young leaves")
            elif any(x in lower for x in ["old", "lower"]):
                self.state.update("leaf_age", "older leaves")
            else:
                self.state.update("leaf_age", answer_clean)

    def _extract_number(self, text: str):
        match = re.search(r"(\d+(\.\d+)?)", text)
        if match:
            return float(match.group(1))
        return None

    def _parse_area(self, area_raw):
        """Convert stored area to float safely."""
        if area_raw is None:
            return 1.0 
        if isinstance(area_raw, (int, float)):
            return float(area_raw)
        num = self._extract_number(str(area_raw))
        return num if num is not None else 1.0
    