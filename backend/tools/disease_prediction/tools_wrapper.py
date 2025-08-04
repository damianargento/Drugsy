"""
Wrapper for disease prediction tools to make them compatible with LangChain and Pydantic.
"""

from typing import Dict, Any, Type, Annotated
from langchain_core.tools import BaseTool, tool
from pydantic import BaseModel, Field

from .diabetes_prediction_tool import diabetes_prediction_tool
from .heart_disease_prediction_tool import heart_disease_prediction_tool
from .lung_cancer_prediction_tool import lung_cancer_prediction_tool
from .thyroid_prediction_tool import thyroid_prediction_tool

# Diabetes prediction tool wrapper
@tool("diabetes_prediction", return_direct=False)
def diabetes_prediction_wrapper(
    pregnancies: int = Field(..., description="Number of pregnancies"),
    glucose: float = Field(..., description="Plasma glucose concentration (mg/dL)"),
    blood_pressure: float = Field(..., description="Diastolic blood pressure (mm Hg)"),
    skin_thickness: float = Field(..., description="Triceps skin fold thickness (mm)"),
    insulin: float = Field(..., description="2-Hour serum insulin (mu U/ml)"),
    bmi: float = Field(..., description="Body mass index (weight in kg/(height in m)^2)"),
    age: int = Field(..., description="Age in years"),
    mother_has_diabetes: int = Field(..., description="Whether the mother has diabetes (1=Yes, 0=No)"),
    father_has_diabetes: int = Field(..., description="Whether the father has diabetes (1=Yes, 0=No)"),
    diabetic_siblings: int = Field(..., description="Number of siblings with diabetes"),
    diabetic_children: int = Field(..., description="Number of children with diabetes"),
    second_degree_relatives: int = Field(..., description="Whether any second-degree relatives have diabetes (1=Yes, 0=No)")
) -> Dict[str, Any]:
    """Predicts the risk of diabetes based on patient data."""
    patient_data = {
        "Pregnancies": pregnancies,
        "Glucose": glucose,
        "BloodPressure": blood_pressure,
        "SkinThickness": skin_thickness,
        "Insulin": insulin,
        "BMI": bmi,
        "Age": age,
        "MotherHasDiabetes": mother_has_diabetes,
        "FatherHasDiabetes": father_has_diabetes,
        "DiabeticSiblings": diabetic_siblings,
        "DiabeticChildren": diabetic_children,
        "SecondDegreeRelatives": second_degree_relatives
    }
    return diabetes_prediction_tool(patient_data)

# Heart disease prediction tool wrapper
@tool("heart_disease_prediction", return_direct=False)
def heart_disease_prediction_wrapper(
    age: int = Field(..., description="Age in years"),
    sex: int = Field(..., description="Sex (1=Male, 0=Female)"),
    chest_pain_type: int = Field(..., description="Type of chest pain (0-3)"),
    resting_bp: int = Field(..., description="Resting blood pressure (mm Hg)"),
    cholesterol: int = Field(..., description="Serum cholesterol (mg/dl)"),
    fasting_bs: int = Field(..., description="Fasting blood sugar > 120 mg/dl (1=True, 0=False)"),
    resting_ecg: int = Field(..., description="Resting electrocardiographic results (0-2)"),
    max_hr: int = Field(..., description="Maximum heart rate achieved"),
    exercise_angina: int = Field(..., description="Exercise-induced angina (1=Yes, 0=No)"),
    oldpeak: float = Field(..., description="ST depression induced by exercise relative to rest"),
    st_slope: int = Field(..., description="Slope of the peak exercise ST segment (0-2)")
) -> Dict[str, Any]:
    """Predicts the risk of heart disease based on patient data."""
    patient_data = {
        "Age": age,
        "Sex": sex,
        "ChestPainType": chest_pain_type,
        "RestingBP": resting_bp,
        "Cholesterol": cholesterol,
        "FastingBS": fasting_bs,
        "RestingECG": resting_ecg,
        "MaxHR": max_hr,
        "ExerciseAngina": exercise_angina,
        "Oldpeak": oldpeak,
        "ST_Slope": st_slope
    }
    return heart_disease_prediction_tool(patient_data)

# Lung cancer prediction tool wrapper
@tool("lung_cancer_prediction", return_direct=False)
def lung_cancer_prediction_wrapper(
    smoking: int = Field(..., description="Smoking status (1=Yes, 0=No)"),
    yellow_fingers: int = Field(..., description="Yellow fingers (1=Yes, 0=No)"),
    anxiety: int = Field(..., description="Anxiety (1=Yes, 0=No)"),
    peer_pressure: int = Field(..., description="Peer pressure (1=Yes, 0=No)"),
    chronic_disease: int = Field(..., description="Chronic disease (1=Yes, 0=No)"),
    fatigue: int = Field(..., description="Fatigue (1=Yes, 0=No)"),
    allergy: int = Field(..., description="Allergy (1=Yes, 0=No)"),
    wheezing: int = Field(..., description="Wheezing (1=Yes, 0=No)"),
    alcohol_consuming: int = Field(..., description="Alcohol consuming (1=Yes, 0=No)"),
    coughing: int = Field(..., description="Coughing (1=Yes, 0=No)"),
    swallowing_difficulty: int = Field(..., description="Swallowing difficulty (1=Yes, 0=No)"),
    chest_pain: int = Field(..., description="Chest pain (1=Yes, 0=No)")
) -> Dict[str, Any]:
    """Predicts the risk of lung cancer based on patient data."""
    patient_data = {
        "Smoking": smoking,
        "YellowFingers": yellow_fingers,
        "Anxiety": anxiety,
        "PeerPressure": peer_pressure,
        "ChronicDisease": chronic_disease,
        "Fatigue": fatigue,
        "Allergy": allergy,
        "Wheezing": wheezing,
        "AlcoholConsuming": alcohol_consuming,
        "Coughing": coughing,
        "SwallowingDifficulty": swallowing_difficulty,
        "ChestPain": chest_pain
    }
    return lung_cancer_prediction_tool(patient_data)

# Thyroid prediction tool wrapper
@tool("thyroid_prediction", return_direct=False)
def thyroid_prediction_wrapper(
    age: int = Field(..., description="Age in years"),
    sex: int = Field(..., description="Sex (1=Male, 0=Female)"),
    tsh: float = Field(..., description="Thyroid Stimulating Hormone level"),
    t3: float = Field(..., description="Triiodothyronine level"),
    tt4: float = Field(..., description="Total Thyroxine level"),
    t4u: float = Field(..., description="Thyroxine Uptake"),
    fti: float = Field(..., description="Free Thyroxine Index"),
    on_thyroxine: int = Field(..., description="On thyroxine medication (1=Yes, 0=No)"),
    query_on_thyroxine: int = Field(..., description="Query on thyroxine (1=Yes, 0=No)"),
    on_antithyroid_medication: int = Field(..., description="On antithyroid medication (1=Yes, 0=No)"),
    sick: int = Field(..., description="Sick (1=Yes, 0=No)"),
    pregnant: int = Field(..., description="Pregnant (1=Yes, 0=No)"),
    thyroid_surgery: int = Field(..., description="Thyroid surgery (1=Yes, 0=No)"),
    i131_treatment: int = Field(..., description="I131 treatment (1=Yes, 0=No)"),
    query_hypothyroid: int = Field(..., description="Query hypothyroid (1=Yes, 0=No)"),
    query_hyperthyroid: int = Field(..., description="Query hyperthyroid (1=Yes, 0=No)"),
    lithium: int = Field(..., description="Lithium (1=Yes, 0=No)"),
    goitre: int = Field(..., description="Goitre (1=Yes, 0=No)"),
    tumor: int = Field(..., description="Tumor (1=Yes, 0=No)"),
    hypopituitary: int = Field(..., description="Hypopituitary (1=Yes, 0=No)"),
    psych: int = Field(..., description="Psychological symptoms (1=Yes, 0=No)"),
    tsh_measured: int = Field(..., description="TSH measured (1=Yes, 0=No)"),
    t3_measured: int = Field(..., description="T3 measured (1=Yes, 0=No)"),
    tt4_measured: int = Field(..., description="TT4 measured (1=Yes, 0=No)"),
    t4u_measured: int = Field(..., description="T4U measured (1=Yes, 0=No)"),
    fti_measured: int = Field(..., description="FTI measured (1=Yes, 0=No)"),
    tbg_measured: int = Field(..., description="TBG measured (1=Yes, 0=No)"),
    tbg: float = Field(..., description="Thyroxine Binding Globulin level"),
    referral: str = Field(..., description="Referral source")
) -> Dict[str, Any]:
    """Predicts the risk of hypothyroidism based on patient data."""
    patient_data = {
        "Age": age,
        "Sex": sex,
        "TSH": tsh,
        "T3": t3,
        "TT4": tt4,
        "T4U": t4u,
        "FTI": fti,
        "OnThyroxine": on_thyroxine,
        "QueryOnThyroxine": query_on_thyroxine,
        "OnAntithyroidMedication": on_antithyroid_medication,
        "Sick": sick,
        "Pregnant": pregnant,
        "ThyroidSurgery": thyroid_surgery,
        "I131Treatment": i131_treatment,
        "QueryHypothyroid": query_hypothyroid,
        "QueryHyperthyroid": query_hyperthyroid,
        "Lithium": lithium,
        "Goitre": goitre,
        "Tumor": tumor,
        "Hypopituitary": hypopituitary,
        "Psych": psych,
        "TSHMeasured": tsh_measured,
        "T3Measured": t3_measured,
        "TT4Measured": tt4_measured,
        "T4UMeasured": t4u_measured,
        "FTIMeasured": fti_measured,
        "TBGMeasured": tbg_measured,
        "TBG": tbg,
        "Referral": referral
    }
    return thyroid_prediction_tool(patient_data)

# Export the tools
__all__ = [
    'diabetes_prediction_wrapper',
    'heart_disease_prediction_wrapper',
    'lung_cancer_prediction_wrapper',
    'thyroid_prediction_wrapper'
]
