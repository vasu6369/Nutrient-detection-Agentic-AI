from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, List


@dataclass
class ConversationState:
    deficiency: str | None = None
    cv_confidence: float | None = None

    crop: str | None = None
    area: str | float | int | None = None
    fertilizer_type: str | None = None 

    irrigation_type: str | None = None    
    growth_stage: str | None = None     
    symptom_duration: str | None = None   
    leaf_age: str | None = None 

    done: bool = False

    def to_dict(self) -> dict:
        return asdict(self)

    def update(self, field: str, value: Any) -> None:
        if hasattr(self, field):
            setattr(self, field, value)

    def extra_questions_for(self, deficiency: str | None) -> List[str]:
        """
        Decide which extra fields to ask based on deficiency.
        This is where you can customize per nutrient.
        """
        if not deficiency:
            return []

        d = deficiency.lower()

        if d == "iron":
            return ["leaf_age", "irrigation_type", "symptom_duration"]

        if d == "potassium":
            return ["leaf_age", "growth_stage", "symptom_duration"]

        if d == "magnesium":
            return ["leaf_age", "growth_stage", "symptom_duration"]

        return ["growth_stage", "symptom_duration"]

    def missing_fields(self) -> list[str]:
        """
        Return ordered list of fields we still need to ask the user.
        """
        if self.done:
            return []

        base_fields: list[str] = ["crop", "area", "fertilizer_type"]

        base_fields += self.extra_questions_for(self.deficiency)

        missing: list[str] = []
        for f in base_fields:
            value = getattr(self, f, None)
            if value in (None, "", 0, False):
                missing.append(f)

        return missing
