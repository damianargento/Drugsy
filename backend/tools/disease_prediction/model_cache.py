"""
Model cache manager for disease prediction tools.
Handles downloading and caching of models to avoid redundant downloads.
"""

import os
import pickle
import kagglehub
from pathlib import Path
import json
import warnings

# Suppress scikit-learn version warnings
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")

class ModelCache:
    """Singleton class to manage model caching for disease prediction tools."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModelCache, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize the cache manager."""
        self.model_name = "sanjaykumar567/mediai-smart-disease-predictor/scikitLearn/healthpredict-ai-powered-disease-detection"
        self.model_dir = None
        self.models = {}
        self.cache_file = Path(__file__).parent / 'model_cache.json'
        self.loaded = False
    
    def _load_cache_info(self):
        """Load cached model path from file if it exists."""
        try:
            if self.cache_file.exists():
                with open(self.cache_file, 'r') as f:
                    cache_data = json.load(f)
                    self.model_dir = cache_data.get('model_dir')
                    
                    if self.model_dir and Path(self.model_dir).exists():
                        print(f"Found cached model directory at: {self.model_dir}")
                        return True
        except Exception as e:
            print(f"Error loading cache info: {str(e)}")
        
        return False
    
    def _save_cache_info(self):
        """Save model directory path to cache file."""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump({
                    'model_dir': self.model_dir,
                    'timestamp': str(Path(self.model_dir).stat().st_mtime)
                }, f)
            print(f"Saved model directory to cache: {self.model_dir}")
        except Exception as e:
            print(f"Error saving cache info: {str(e)}")
    
    def ensure_models_loaded(self):
        """Ensure models are downloaded and cached."""
        if self.loaded:
            return True
            
        # First check if we have cached model directory
        if self._load_cache_info():
            self.loaded = True
            return True
            
        # No cache or invalid cache, download the model
        try:
            print(f"Downloading model from Kaggle: {self.model_name}")
            self.model_dir = kagglehub.model_download(self.model_name)
            print(f"Model downloaded to: {self.model_dir}")
            
            # Save cache info
            self._save_cache_info()
            self.loaded = True
            return True
        except Exception as e:
            print(f"Error downloading model: {str(e)}")
            return False
    
    def get_model(self, model_type):
        """
        Get a specific model by type.
        
        Args:
            model_type (str): Type of model to load ('diabetes', 'heart', 'lung', 'thyroid')
            
        Returns:
            object: Loaded model or None if not found
        """
        # Check if model is already loaded
        if model_type in self.models:
            return self.models[model_type]
        
        # Ensure models are downloaded
        if not self.ensure_models_loaded() or not self.model_dir:
            return None
        
        # Find the specific model file - check both .pkl and .sav extensions
        model_path = None
        
        if model_type == 'diabetes':
            model_files = list(Path(self.model_dir).glob('diabetes*.[ps][ka][lv]')) + list(Path(self.model_dir).glob('*diabetes*.[ps][ka][lv]'))
        elif model_type == 'heart':
            model_files = list(Path(self.model_dir).glob('heart*.[ps][ka][lv]')) + list(Path(self.model_dir).glob('*heart*.[ps][ka][lv]'))
        elif model_type == 'lung':
            model_files = list(Path(self.model_dir).glob('lung*.[ps][ka][lv]')) + list(Path(self.model_dir).glob('*lung*.[ps][ka][lv]'))
            # Also check for 'lungs' plural form
            if not model_files:
                model_files = list(Path(self.model_dir).glob('lungs*.[ps][ka][lv]')) + list(Path(self.model_dir).glob('*lungs*.[ps][ka][lv]'))
        elif model_type == 'thyroid':
            model_files = list(Path(self.model_dir).glob('thyroid*.[ps][ka][lv]')) + list(Path(self.model_dir).glob('*thyroid*.[ps][ka][lv]')) + list(Path(self.model_dir).glob('*Thyroid*.[ps][ka][lv]'))
        else:
            model_files = []
        
        # If specific model not found, try to use any model file
        if not model_files:
            model_files = list(Path(self.model_dir).glob('*.[ps][ka][lv]'))
            print(f"No specific {model_type} model found, using any available model file")
        
        if not model_files:
            print(f"No model files found for {model_type} in {self.model_dir}")
            return None
        
        # Load the model
        try:
            model_path = model_files[0]
            print(f"Loading {model_type} model from: {model_path}")
            
            with open(model_path, 'rb') as f:
                model = pickle.load(f)
            
            # Cache the loaded model
            self.models[model_type] = model
            return model
        except Exception as e:
            print(f"Error loading {model_type} model: {str(e)}")
            return None

# Create singleton instance
model_cache = ModelCache()
