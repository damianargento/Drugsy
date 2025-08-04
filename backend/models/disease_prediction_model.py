import pickle
import numpy as np
from sklearn.preprocessing import StandardScaler
import os
import json
from pathlib import Path
import kagglehub
import warnings

# Suppress scikit-learn version warnings
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

class DiseasePredictionModel:
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.model_name = "sanjaykumar567/mediai-smart-disease-predictor/scikitLearn/healthpredict-ai-powered-disease-detection"
        self.model_path = None
        self.is_model_loaded = False
        self.cache_file = Path(__file__).parent / 'model_cache.json'
        
        # Try to load the model immediately at initialization
        try:
            print("Initializing disease prediction model...")
            self.load_model()
        except Exception as e:
            print(f"Failed to initialize model at startup: {str(e)}")
            print("Model will be loaded on first prediction request")
        
    def _load_cache(self):
        """Load cached model path from file if it exists"""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r') as f:
                    cache_data = json.load(f)
                    self.model_path = cache_data.get('model_path')
                    model_file_path = cache_data.get('model_file_path')
                    
                    if self.model_path and model_file_path and Path(model_file_path).exists():
                        print(f"Found cached model at: {model_file_path}")
                        return model_file_path
        except Exception as e:
            print(f"Error loading cache: {str(e)}")
        
        return None
    
    def _save_cache(self, model_path, model_file_path):
        """Save model path to cache file"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump({
                    'model_path': model_path,
                    'model_file_path': str(model_file_path),
                    'timestamp': str(Path(model_file_path).stat().st_mtime)
                }, f)
            print(f"Saved model path to cache: {model_file_path}")
        except Exception as e:
            print(f"Error saving cache: {str(e)}")
    
    def load_model(self):
        """Load the disease prediction model, downloading only if necessary"""
        try:
            # First check if we have a cached model file path
            cached_model_path = self._load_cache()
            
            if cached_model_path:
                model_file_path = Path(cached_model_path)
                print(f"Using cached model from: {model_file_path}")
            else:
                # No cache or invalid cache, download the model
                print(f"Downloading model from Kaggle: {self.model_name}")
                self.model_path = kagglehub.model_download(self.model_name)
                print(f"Model downloaded to: {self.model_path}")
                
                # Find the model file in the downloaded directory
                model_files = list(Path(self.model_path).glob('*.pkl')) + list(Path(self.model_path).glob('*.sav'))
                if not model_files:
                    print("No pickle model files found in the downloaded directory")
                    print("Model is not available")
                    self.is_model_loaded = False
                    return False
                    
                # Load the first pickle file found
                model_file_path = model_files[0]
                print(f"Found model file: {model_file_path}")
                
                # Save to cache for future use
                self._save_cache(self.model_path, model_file_path)
            
            # Load the model from file
            print(f"Loading model from: {model_file_path}")
            with open(model_file_path, 'rb') as model_file:
                model_data = pickle.load(model_file)
                
                # Check if the loaded data is a dictionary containing both model and scaler
                if isinstance(model_data, dict) and 'model' in model_data and 'scaler' in model_data:
                    self.model = model_data['model']
                    self.scaler = model_data['scaler']
                    print("Loaded model and scaler from pickle file")
                else:
                    # If it's just the model, use it directly
                    self.model = model_data
                    # Initialize a new scaler with default parameters
                    self.scaler = StandardScaler()
                    # Fit the scaler with some reasonable default values for medical data
                    # This is a fallback and might need adjustment based on actual data ranges
                    default_data = np.array([
                        [50, 0, 120, 200, 100, 25, 0],  # Average values
                        [20, 0, 90, 150, 70, 18, 0],   # Low values
                        [80, 1, 160, 300, 140, 35, 1]  # High values
                    ])
                    self.scaler.fit(default_data)
                    print("Initialized scaler with default values")
                
            self.is_model_loaded = True
            print("Model loaded successfully")
            return True
            
        except Exception as e:
            print(f"Error loading model: {str(e)}")
            return False
    
    def predict_disease_risk(self, patient_data):
        """
        Predict disease risk based on patient data
        
        Args:
            patient_data (dict): Dictionary containing patient information with the following keys:
                - age: int
                - sex: int (0=Female, 1=Male)
                - blood_pressure: int
                - cholesterol: int
                - glucose_level: int
                - bmi: float
                - family_history: int (0=No, 1=Yes)
                
        Returns:
            dict: Prediction results with risk assessment and confidence score
        """
        # Check if model is loaded
        if not self.is_model_loaded:
            success = self.load_model()
            if not success:
                return {
                    "error": "Model is not available. No valid model file could be found or downloaded.",
                    "status": "error"
                }
        
        # Validate input data
        required_fields = ['age', 'sex', 'blood_pressure', 'cholesterol', 
                          'glucose_level', 'bmi', 'family_history']
        
        missing_fields = [field for field in required_fields if field not in patient_data]
        if missing_fields:
            return {
                "error": f"Missing required fields: {', '.join(missing_fields)}",
                "missing_fields": missing_fields,
                "status": "incomplete_data"
            }
        
        # Convert patient data to numpy array
        try:
            print(f"Processing prediction with input data: {patient_data}")
            
            input_data = np.array([[
                patient_data["age"], 
                patient_data["sex"], 
                patient_data["blood_pressure"],
                patient_data["cholesterol"], 
                patient_data["glucose_level"],
                patient_data["bmi"], 
                patient_data["family_history"]
            ]])
            
            print(f"Input data array shape: {input_data.shape}")
            
            try:
                # Standardize the input features - only transform, don't fit on each prediction
                input_data_scaled = self.scaler.transform(input_data)
                print("Data standardization successful")
            except Exception as scale_error:
                print(f"Error during data standardization: {str(scale_error)}")
                # If transform fails, try with fit_transform as a fallback
                print("Attempting fallback with fit_transform")
                input_data_scaled = self.scaler.fit_transform(input_data)
            
            # Make prediction
            print("Making prediction with model")
            prediction = self.model.predict(input_data_scaled)
            print(f"Raw prediction result: {prediction}")
            
            # Get prediction probability if available
            confidence = 0.0
            try:
                confidence = float(self.model.predict_proba(input_data_scaled)[0][1])
                print(f"Prediction confidence: {confidence}")
            except Exception as prob_error:
                print(f"Could not get prediction probability: {str(prob_error)}")
                # Some models don't support predict_proba
                confidence = float(prediction[0])
                print(f"Using prediction value as confidence: {confidence}")
            
            # Interpret results
            is_at_risk = bool(prediction[0] == 1)
            print(f"Final prediction - is_at_risk: {is_at_risk}, confidence: {confidence}")
            
            return {
                "is_at_risk": is_at_risk,
                "confidence": confidence,
                "status": "success",
                "message": "Disease risk prediction successful"
            }
            
        except Exception as e:
            return {
                "error": f"Error during prediction: {str(e)}",
                "status": "error"
            }

    def get_required_fields(self):
        """
        Get the required fields for disease prediction with their descriptions
        
        Returns:
            list: List of dictionaries with field information
        """
        return [
            {
                "name": "age",
                "type": "integer",
                "description": "Patient age in years",
                "min": 0,
                "max": 120
            },
            {
                "name": "sex",
                "type": "integer",
                "description": "Patient sex (0=Female, 1=Male)",
                "options": [
                    {"value": 0, "label": "Female"},
                    {"value": 1, "label": "Male"}
                ]
            },
            {
                "name": "blood_pressure",
                "type": "integer",
                "description": "Systolic blood pressure in mmHg",
                "min": 70,
                "max": 220
            },
            {
                "name": "cholesterol",
                "type": "integer",
                "description": "Total cholesterol level in mg/dL",
                "min": 100,
                "max": 400
            },
            {
                "name": "glucose_level",
                "type": "integer",
                "description": "Fasting blood glucose level in mg/dL",
                "min": 50,
                "max": 300
            },
            {
                "name": "bmi",
                "type": "float",
                "description": "Body Mass Index",
                "min": 10.0,
                "max": 50.0
            },
            {
                "name": "family_history",
                "type": "integer",
                "description": "Family history of cardiovascular disease (0=No, 1=Yes)",
                "options": [
                    {"value": 0, "label": "No"},
                    {"value": 1, "label": "Yes"}
                ]
            }
        ]

# Singleton instance
disease_model = DiseasePredictionModel()
