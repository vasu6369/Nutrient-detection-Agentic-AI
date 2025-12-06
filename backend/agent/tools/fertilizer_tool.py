from __future__ import annotations

from typing import Dict, Any


class FertilizerTool:
    """
    This tool calculates recommended fertilizer dosage based on:
    - deficiency (Boron, Calcium, Iron, Magnesium, Manganese, Potassium, Sulphur, Zinc)
    - crop type
    - area in hectares
    - optional context: irrigation_type, growth_stage
    """

    BASE_DOSAGE: Dict[str, Dict[str, float]] = {
        "Boron": {
            "Borax (10% B)": 2.0,     
        },
        "Calcium": {
            "Calcium Nitrate": 40.0,
        },
        "Iron": {
            "Ferrous Sulphate (FeSO4)": 25.0,
        },
        "Magnesium": {
            "Magnesium Sulphate (MgSO4)": 25.0,
        },
        "Manganese": {
            "Manganese Sulphate (MnSO4)": 10.0,
        },
        "Potassium": {
            "MOP (Muriate of Potash)": 60.0,
        },
        "Sulphur": {
            "Gypsum": 30.0,
        },
        "Zinc": {
            "Zinc Sulphate (ZnSO4)": 20.0,
        },
    }

    def calculate(
        self,
        deficiency: str,
        crop: str | None,
        area_hectares: float,
        irrigation_type: str | None = None,
        growth_stage: str | None = None,
    ) -> Dict[str, Any]:
        """
        Returns fertilizer recommendation with simple contextual adjustment.
        """

        if deficiency not in self.BASE_DOSAGE:
            return {"error": f"Unknown deficiency type: {deficiency}"}

        fert_info = self.BASE_DOSAGE[deficiency]

        recommendation = {
            fert: round(qty * area_hectares, 2)
            for fert, qty in fert_info.items()
        }

        recommendation = self._apply_context_adjustment(
            recommendation,
            irrigation_type=irrigation_type,
            growth_stage=growth_stage,
        )

        return {
            "deficiency": deficiency,
            "crop": crop,
            "area_hectares": area_hectares,
            "irrigation_type": irrigation_type,
            "growth_stage": growth_stage,
            "fertilizer_recommendation": recommendation,
        }

    def _apply_context_adjustment(
        self,
        recommendation: Dict[str, float],
        irrigation_type: str | None,
        growth_stage: str | None,
    ) -> Dict[str, float]:
        """
        Adjust the dosage roughly based on irrigation and crop stage.
        You can tune this logic later.
        """
        irrig = (irrigation_type or "").lower()
        stage = (growth_stage or "").lower()

        adjusted = dict(recommendation)

        if "rain" in irrig:
            for k in adjusted:
                adjusted[k] = round(adjusted[k] * 0.85, 2)

        if "seedling" in stage:
            for k in adjusted:
                adjusted[k] = round(adjusted[k] * 0.5, 2)

        return adjusted
1