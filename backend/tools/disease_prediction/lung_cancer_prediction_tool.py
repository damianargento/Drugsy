"""
Lung cancer prediction tool using a machine learning model.
"""

import os
import pickle
import numpy as np
import json
from pathlib import Path
from langchain_core.tools import BaseTool
from typing import Dict, Any, Optional
import warnings

# Suppress scikit-learn version warnings
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

from .model_cache import model_cache

def lung_cancer_prediction_tool(patient_data: Dict[str, Any]) -> Dict[str, Any]:
    # Inicializar el modelo como None
    lung_cancer_prediction_tool.model = getattr(lung_cancer_prediction_tool, 'model', None)
    
    # Add prominent debug message
    print("\n==== LUNG CANCER PREDICTION TOOL CALLED ====\n")
    print(f"PATIENT DATA: {json.dumps(patient_data, indent=2)}")
    """
    Predicts lung cancer risk based on patient data.
    
    Args:
        patient_data: Dictionary containing patient information with the following keys:
            - Smoking: Smoking status (1=Yes, 0=No)
            - YellowFingers: Yellow fingers (1=Yes, 0=No)
            - Anxiety: Anxiety (1=Yes, 0=No)
            - PeerPressure: Peer pressure (1=Yes, 0=No)
            - ChronicDisease: Chronic disease (1=Yes, 0=No)
            - Fatigue: Fatigue (1=Yes, 0=No)
            - Allergy: Allergy (1=Yes, 0=No)
            - Wheezing: Wheezing (1=Yes, 0=No)
            - AlcoholConsuming: Alcohol consuming (1=Yes, 0=No)
            - Coughing: Coughing (1=Yes, 0=No)
            - SwallowingDifficulty: Swallowing difficulty (1=Yes, 0=No)
            - ChestPain: Chest pain (1=Yes, 0=No)
            
    Returns:
        dict: Prediction results with risk assessment and confidence score
    """
    # Log tool call with parameters
    print(f"Lung cancer prediction tool called with parameters: {json.dumps(patient_data)}")
    try:
        # Check if all required fields are present
        required_fields = [
            'Smoking', 'YellowFingers', 'Anxiety', 
            'PeerPressure', 'ChronicDisease', 'Fatigue', 'Allergy', 
            'Wheezing', 'AlcoholConsuming', 'Coughing',
            'SwallowingDifficulty', 'ChestPain'
        ]
        
        missing_fields = [field for field in required_fields if field not in patient_data]
        if missing_fields:
            return {
                "status": "error",
                "error": f"Missing required fields: {', '.join(missing_fields)}",
                "missing_fields": missing_fields
            }
        
        # Load the local lung cancer model instead of using the cached model
        local_model_path = Path('/Users/damianargento/Desktop/Drugsy/backend/models/lung_cancer_symptom_model.pkl')
        if not local_model_path.exists():
            print(f"Local lung cancer model not found at: {local_model_path}")
            return {
                "status": "error",
                "error": f"Local lung cancer model not found at: {local_model_path}"
            }
        
        try:
            print(f"Loading local lung cancer model from: {local_model_path}")
            # Configurar XGBoost para ignorar errores de compatibilidad
            import xgboost as xgb
            # Configurar el entorno para XGBoost
            os.environ['PYTHONPATH'] = os.environ.get('PYTHONPATH', '') + ':' + os.path.dirname(xgb.__file__)
            
            # Cargar el modelo con pickle pero con manejo especial para XGBoost
            with open(local_model_path, 'rb') as f:
                model = pickle.load(f)
            print("Local lung cancer model loaded successfully")
            print(f"Model type: {type(model).__name__}")
            
            # Inspeccionar el modelo en detalle
            if hasattr(model, 'estimators_'):
                print(f"Model has estimators_ attribute with {len(model.estimators_)} items")
                print(f"Type of estimators_: {type(model.estimators_)}")
                
                # Inspeccionar cada estimador
                for i, estimator_item in enumerate(model.estimators_):
                    print(f"Estimator item {i} type: {type(estimator_item)}")
                    
                    # Si es una tupla, extraer nombre y estimador
                    if isinstance(estimator_item, tuple) and len(estimator_item) == 2:
                        name, est = estimator_item
                        print(f"  Estimator {i}: {name} - {type(est).__name__}")
                    else:
                        print(f"  Estimator {i}: {type(estimator_item).__name__}")
                        
            # Verificar otros atributos importantes
            for attr in ['classes_', 'estimator', 'estimators', 'named_estimators']:
                if hasattr(model, attr):
                    attr_value = getattr(model, attr)
                    print(f"Model has {attr}: {type(attr_value)}")
                    
            # Guardar el modelo para uso posterior
            lung_cancer_prediction_tool.model = model
        except Exception as e:
            print(f"Error loading local lung cancer model: {str(e)}")
            return {
                "status": "error",
                "error": f"Failed to load local lung cancer model: {str(e)}"
            }
        
        # Prepare input features in the correct order for the new model
        # El nuevo modelo espera exactamente estas 12 características en este orden
        print("Preparing features for the model - using the 12 features expected by the new model")
        features = np.array([
            [
                float(patient_data['Smoking']),
                float(patient_data['YellowFingers']),
                float(patient_data['Anxiety']),
                float(patient_data['PeerPressure']),
                float(patient_data['ChronicDisease']),
                float(patient_data['Fatigue']),
                float(patient_data['Allergy']),
                float(patient_data['Wheezing']),
                float(patient_data['AlcoholConsuming']),
                float(patient_data['Coughing']),
                float(patient_data['SwallowingDifficulty']),
                float(patient_data['ChestPain'])
            ]
        ])
        print(f"Feature shape: {features.shape}")
        
        # Make prediction
        try:
            # Usar el modelo guardado en la función
            model = lung_cancer_prediction_tool.model
            
            # Si es un VotingClassifier con problemas, intentamos usar directamente los estimadores
            if hasattr(model, 'estimators_'):
                print("Using direct estimator access for prediction")
                
                # Intentar usar el primer estimador que funcione
                prediction = None
                confidence = 0.0
                
                for estimator_item in model.estimators_:
                    try:
                        # Manejar diferentes estructuras de estimadores
                        if isinstance(estimator_item, tuple) and len(estimator_item) == 2:
                            name, estimator = estimator_item
                        else:
                            name = f"estimator_{id(estimator_item)}"
                            estimator = estimator_item
                            
                        print(f"Trying estimator: {name}")
                        
                        # Intentar predicción
                        if hasattr(estimator, 'predict'):
                            est_prediction = estimator.predict(features)
                            print(f"Prediction successful with {name}: {est_prediction}")
                            prediction = est_prediction
                            
                            # Intentar obtener probabilidades
                            try:
                                if hasattr(estimator, 'predict_proba'):
                                    proba = estimator.predict_proba(features)
                                    print(f"Got probabilities from {name}: shape {proba.shape}")
                                    if proba.shape[1] > 1:  # Binary classification
                                        confidence = float(proba[0][1])
                                    else:  # Solo una clase en la salida
                                        confidence = float(proba[0][0])
                                else:
                                    confidence = float(est_prediction[0])
                            except Exception as prob_err:
                                print(f"Error getting probability with {name}: {str(prob_err)}")
                                confidence = float(est_prediction[0])
                                
                            # Si llegamos aquí, tenemos una predicción exitosa
                            break
                        else:
                            print(f"Estimator {name} doesn't have predict method")
                            
                    except Exception as est_err:
                        print(f"Error with estimator {name}: {str(est_err)}")
                        continue
                        
                # Verificar si obtuvimos una predicción
                if prediction is None:
                    # Intentar usar el método predict del VotingClassifier directamente
                    try:
                        print("Trying VotingClassifier's predict method directly")
                        prediction = model.predict(features)
                        print(f"VotingClassifier prediction successful: {prediction}")
                        
                        # Intentar obtener probabilidades
                        try:
                            if hasattr(model, 'predict_proba'):
                                proba = model.predict_proba(features)
                                if proba.shape[1] > 1:  # Binary classification
                                    confidence = float(proba[0][1])
                                else:  # Solo una clase en la salida
                                    confidence = float(proba[0][0])
                            else:
                                confidence = float(prediction[0])
                        except Exception as prob_err:
                            print(f"Error getting VotingClassifier probability: {str(prob_err)}")
                            confidence = float(prediction[0])
                    except Exception as vc_err:
                        print(f"Error using VotingClassifier predict: {str(vc_err)}")
                        raise Exception("All prediction methods failed")
            else:
                # Modelo normal, intentar predicción directa
                print("Using standard prediction")
                prediction = model.predict(features)
                print(f"Raw prediction result: {prediction}")
                
                # Obtener probabilidad si está disponible
                confidence = 0.0
                try:
                    if hasattr(model, 'predict_proba'):
                        proba = model.predict_proba(features)
                        print(f"Probability shape: {proba.shape}")
                        if proba.shape[1] > 1:  # Binary classification
                            confidence = float(proba[0][1])
                        else:  # Solo una clase en la salida
                            confidence = float(proba[0][0])
                    else:
                        # Algunos modelos no soportan predict_proba
                        confidence = float(prediction[0])
                except Exception as prob_error:
                    print(f"Error getting prediction probability: {str(prob_error)}")
                    # Fallback al valor de predicción
                    confidence = float(prediction[0])
                    
        except Exception as pred_error:
            print(f"Error during prediction: {str(pred_error)}")
            return {
                "status": "error",
                "error": f"Error during prediction: {str(pred_error)}"
            }
        
        # Interpret results
        is_at_risk = bool(prediction[0] == 1)
        
        result = {
            "is_at_risk": is_at_risk,
            "confidence": confidence,
            "status": "success",
            "risk_assessment": "High risk of lung cancer" if is_at_risk else "Low risk of lung cancer"
        }
        print(f"Model type: {type(model)}")
        print(f"Classes: {model.classes_ if hasattr(model, 'classes_') else 'N/A'}")
        # Log prediction result
        print(f"Lung cancer prediction result: {json.dumps(result)}")
        
        return result
        
    except Exception as e:
        error_result = {
            "status": "error",
            "error": f"Error during prediction: {str(e)}"
        }
        print(f"Lung cancer prediction error: {str(e)}")
        return error_result

# Export the function directly instead of creating a LangChain Tool class
# This avoids Pydantic compatibility issues with the current version
