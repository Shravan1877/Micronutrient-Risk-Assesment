"""
Academic Metabolic Diagnostic API (Backend)
-------------------------------------------
A decoupled FastAPI REST service for evaluating micronutrient deficiencies.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import uvicorn

# --- 1. THE KNOWLEDGE BASE ---
TARGET_NUTRIENTS = [
    "Vitamin D", "Vitamin B12", "Folic Acid (B9)", "Vitamin A", 
    "Riboflavin (B2)", "Vitamin C", "Thiamine (B1)", "Vitamin B6", 
    "Niacin (B3)", "Vitamin E", "Iron", "Zinc", "Calcium", "Iodine"
]

SCORING_RULES = {
    "diet_strict_vegan": {"Vitamin B12": 2, "Iron": 2, "Zinc": 2, "Calcium": 1},
    "diet_vegetarian": {"Vitamin B12": 1, "Iron": 1, "Zinc": 1},
    "carbs_polished": {"Thiamine (B1)": 2, "Niacin (B3)": 2},
    "veg_heavily_cooked": {"Vitamin C": 2, "Folic Acid (B9)": 2},
    "dals_never_soaked": {"Iron": 2, "Zinc": 2},
    "dals_sometimes_soaked": {"Iron": 1, "Zinc": 1},
    "dairy_rare": {"Calcium": 2, "Riboflavin (B2)": 2},
    "dairy_infrequent": {"Calcium": 1, "Riboflavin (B2)": 1},
    "greens_rare": {"Vitamin A": 2, "Folic Acid (B9)": 1},
    "greens_infrequent": {"Vitamin A": 1},
    "sun_none": {"Vitamin D": 2, "Calcium": 1},
    "sun_minimal": {"Vitamin D": 1},
    "oil_refined": {"Vitamin E": 2},
    "oil_mixed": {"Vitamin E": 1},
    "salt_unfortified": {"Iodine": 3},
    "sym_fatigue": {"Folic Acid (B9)": 1, "Thiamine (B1)": 1, "Niacin (B3)": 1, "Iron": 1},
    "sym_brain_fog": {"Vitamin B12": 1, "Niacin (B3)": 1},
    "sym_tingling": {"Vitamin B12": 1, "Thiamine (B1)": 1},
    "sym_weight_loss": {"Zinc": 1},
    "sym_weight_gain": {"Iodine": 1},
    "sym_mood": {"Vitamin B6": 1},
    "sym_muscle_weakness": {"Vitamin D": 1, "Thiamine (B1)": 1, "Vitamin E": 1, "Calcium": 1},
    "sym_bone_ache": {"Vitamin D": 1, "Calcium": 1},
    "sym_frequent_sickness": {"Vitamin D": 1, "Vitamin A": 1, "Zinc": 1},
    "sym_slow_healing": {"Vitamin C": 1, "Zinc": 1},
    "sym_dry_skin": {"Vitamin A": 1, "Vitamin C": 1, "Vitamin E": 1, "Iodine": 1},
    "sym_hair_fall": {"Vitamin D": 1, "Iron": 1},
    "sym_early_graying": {"Folic Acid (B9)": 1},
    "sym_poor_vision": {"Vitamin A": 1, "Vitamin E": 1},
    "sym_pale_skin": {"Vitamin B12": 1, "Iron": 1},
    "clin_bleeding_gums": {"Vitamin C": 3},
    "clin_mouth_cracks": {"Riboflavin (B2)": 3, "Vitamin B6": 2},
    "clin_smooth_tongue": {"Folic Acid (B9)": 3, "Riboflavin (B2)": 3},
    "clin_mouth_ulcers": {"Vitamin B12": 3, "Folic Acid (B9)": 3},
    "clin_tooth_decay": {"Calcium": 3},
    "clin_brittle_nails": {"Calcium": 2, "Iron": 2},
    "clin_spoon_nails": {"Iron": 3},
    "clin_bruise_easily": {"Vitamin C": 3},
    "clin_sun_rash": {"Niacin (B3)": 3},
    "clin_goiter": {"Iodine": 3},
    "clin_loss_taste_smell": {"Zinc": 3},
    "clin_severe_dry_eyes": {"Vitamin A": 3}
}

ADVICE_DB = {
    "Vitamin D": { "Moderate": "Increase early morning sun exposure (15-30 mins).", "High": "Clinical deficiency highly likely. Seek a 25-OH Vitamin D blood test for D3 supplementation." },
    "Vitamin B12": { "Moderate": "Include more fortified plant milks or nutritional yeast.", "High": "Critical risk of megaloblastic anemia. Immediate B12 supplementation strongly recommended." },
    "Folic Acid (B9)": { "Moderate": "Increase intake of lightly cooked dark leafy greens.", "High": "Critical for DNA synthesis. Consider L-methylfolate supplementation." },
    "Vitamin A": { "Moderate": "Consume more beta-carotene rich foods paired with healthy fats.", "High": "High risk of immune suppression and ocular damage. Dietary overhaul required." },
    "Riboflavin (B2)": { "Moderate": "Increase intake of dairy products or fortified cereals.", "High": "Mouth sores indicate severe tissue depletion. Broad-spectrum B-complex advised." },
    "Vitamin C": { "Moderate": "Include raw sources of Vitamin C daily (citrus, amla).", "High": "Scurvy-like symptoms present. Immediate high-dose ascorbic acid intervention required." },
    "Thiamine (B1)": { "Moderate": "Switch to unpolished whole grains.", "High": "Neurological symptoms suggest high risk. Consider benfotiamine supplement." },
    "Vitamin B6": { "Moderate": "Increase consumption of chickpeas or poultry.", "High": "High risk of neurotransmitter disruption. P-5-P supplementation may be required." },
    "Niacin (B3)": { "Moderate": "Incorporate peanuts and mushrooms into your diet.", "High": "Pellagra-like dermatological symptoms present. Requires therapeutic Niacin intervention." },
    "Vitamin E": { "Moderate": "Use unrefined cold-pressed oils or eat whole nuts/seeds.", "High": "Significant oxidative stress risk. Urgently incorporate sunflower seeds or almonds." },
    "Iron": { "Moderate": "Combine iron-rich foods with Vitamin C. Always soak grains.", "High": "Clinical anemia risk detected. Consult a doctor for a full ferritin panel." },
    "Zinc": { "Moderate": "Include pumpkin seeds in your diet. Ensure legumes are soaked.", "High": "Immune/sensory dysfunction present. Consider bioavailable zinc picolinate." },
    "Calcium": { "Moderate": "Increase dairy intake or sesame seeds. Ensure adequate Vitamin D.", "High": "Severe risk to bone density. Consider calcium citrate paired with K2 and D3." },
    "Iodine": { "Moderate": "Ensure the salt used is explicitly fortified with iodine.", "High": "High risk of severe thyroid dysfunction (goiter). Endocrine evaluation required." }
}

# --- 2. CORE ENGINE ---
class MetabolicDiagnosticEngine:
    def __init__(self):
        self.nutrient_scores = {nutrient: 0 for nutrient in TARGET_NUTRIENTS}
        self.processed_inputs = set()

    def process_intake(self, user_inputs: List[str]) -> None:
        for input_key in user_inputs:
            if input_key in self.processed_inputs:
                continue
            self.processed_inputs.add(input_key)
            if input_key in SCORING_RULES:
                for nutrient, points in SCORING_RULES[input_key].items():
                    if nutrient in self.nutrient_scores:
                        self.nutrient_scores[nutrient] += points

    def calculate_risk_profile(self) -> Dict[str, Any]:
        deficiencies = []
        is_optimal_health = True

        for nutrient, score in self.nutrient_scores.items():
            if score <= 2:
                continue  # Sub-clinical / Optimal
            
            is_optimal_health = False
            severity_label = "High Clinical Risk" if score >= 6 else "Moderate / Developing Risk"
            severity_key = "High" if score >= 6 else "Moderate"
            
            deficiencies.append({
                "nutrient": nutrient,
                "score": score,
                "severity": severity_label,
                "advice": ADVICE_DB.get(nutrient, {}).get(severity_key, "Consult a professional.")
            })

        deficiencies.sort(key=lambda x: x["score"], reverse=True)
        return {
            "is_optimal_health": is_optimal_health,
            "total_risks_identified": len(deficiencies),
            "deficiencies": deficiencies
        }

# --- 3. FAST API SETUP ---
app = FastAPI(title="Diagnostic Engine API")

# Allow requests from the frontend (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Data Model
class IntakePayload(BaseModel):
    answers: List[str]

@app.get("/")
def health_check():
    return {"status": "Engine Online", "version": "1.0"}

@app.post("/api/analyze")
def analyze_patient(payload: IntakePayload):
    try:
        engine = MetabolicDiagnosticEngine()
        engine.process_intake(payload.answers)
        report = engine.calculate_risk_profile()
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    # Run the server on port 3000
    uvicorn.run(app, host="127.0.0.1", port=3000)