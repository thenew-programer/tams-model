import pandas as pd
import numpy as np
import joblib
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import CountVectorizer
from typing import List, Dict, Any, Union
import os

class TAMSPredictor:
    def __init__(self, model_path: str = None):
        if model_path is None:
            model_path = os.path.join(os.path.dirname(__file__), "ml_models", "tams-prediction-model.pkl")
        
        self.model = None
        self.model_loaded = False
        
        try:
            # Load the trained model
            if os.path.exists(model_path):
                self.model = joblib.load(model_path)
                self.model_loaded = True
                print(f"Model loaded successfully from {model_path}")
            else:
                print(f"Warning: Model file not found at {model_path}")
                print("Using fallback prediction logic")
                
        except Exception as e:
            print(f"Warning: Error loading model: {str(e)}")
            print("Using fallback prediction logic")
    
    def _prepare_features(self, data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> np.ndarray:
        """Prepare features for prediction"""
        if isinstance(data, dict):
            data = [data]
        
        df = pd.DataFrame(data)
        
        # Fill missing values
        df = df.fillna("unknown")
        
        # For new data, we need to handle encoding differently
        # In a production system, you'd save the encoders during training
        required_cols = ["systeme", "description"]
        
        # Simple encoding for demo - in production, use saved encoders
        numeric_features = []
        for col in ["systeme"]:
            if col in df.columns:
                # Simple hash-based encoding for unseen categories
                encoded = df[col].apply(lambda x: hash(str(x)) % 1000)
                numeric_features.append(encoded.values.reshape(-1, 1))
        
        # Text vectorization for description
        if "description" in df.columns:
            # For demo, use simple bag of words
            descriptions = df["description"].fillna("").astype(str)
            
            # Create a simple vectorization
            vocab_size = 100
            text_features = np.zeros((len(descriptions), vocab_size))
            
            for i, desc in enumerate(descriptions):
                words = desc.lower().split()[:vocab_size]
                for j, word in enumerate(words):
                    if j < vocab_size:
                        text_features[i, j] = hash(word) % 100
        else:
            text_features = np.zeros((len(df), 100))
        
        # Combine features
        if numeric_features:
            X = np.concatenate([np.hstack(numeric_features), text_features], axis=1)
        else:
            X = text_features
        
        return X
    
    def _fallback_prediction(self, anomaly_data: Dict[str, Any]) -> Dict[str, int]:
        """Fallback prediction when model is not available"""
        # Simple rule-based prediction based on keywords in description
        description = str(anomaly_data.get('description', '')).lower()
        
        # Initialize with medium scores
        fiabilite_score = 3
        disponibilite_score = 3
        process_safety_score = 3
        
        # Adjust scores based on keywords
        critical_keywords = ['failure', 'broken', 'leak', 'fire', 'explosion', 'pressure', 'overheat']
        medium_keywords = ['wear', 'drift', 'irregularities', 'drop', 'issue']
        low_keywords = ['calibration', 'maintenance', 'check']
        
        if any(keyword in description for keyword in critical_keywords):
            fiabilite_score = 4
            disponibilite_score = 4
            process_safety_score = 5
        elif any(keyword in description for keyword in medium_keywords):
            fiabilite_score = 3
            disponibilite_score = 3
            process_safety_score = 3
        elif any(keyword in description for keyword in low_keywords):
            fiabilite_score = 2
            disponibilite_score = 2
            process_safety_score = 2
        
        # Adjust based on system type
        system = str(anomaly_data.get('systeme', '')).lower()
        if 'electrical' in system:
            process_safety_score = min(5, process_safety_score + 1)
        elif 'hydraulic' in system or 'pneumatic' in system:
            disponibilite_score = min(5, disponibilite_score + 1)
        
        criticality_level = fiabilite_score + disponibilite_score + process_safety_score
        
        return {
            "ai_fiabilite_integrite_score": fiabilite_score,
            "ai_disponibilite_score": disponibilite_score,
            "ai_process_safety_score": process_safety_score,
            "ai_criticality_level": criticality_level
        }
    
    def predict_single(self, anomaly_data: Dict[str, Any]) -> Dict[str, int]:
        """Predict scores for a single anomaly"""
        try:
            if self.model_loaded and self.model is not None:
                X = self._prepare_features(anomaly_data)
                
                # Make prediction
                prediction = self.model.predict(X)
                
                # Extract predictions (assuming model predicts 3 values: fiabilite, disponibilite, process_safety)
                fiabilite_score = max(1, min(5, int(round(prediction[0][0]))))
                disponibilite_score = max(1, min(5, int(round(prediction[0][1]))))
                process_safety_score = max(1, min(5, int(round(prediction[0][2]))))
                
                # Calculate criticality as sum of the three scores
                criticality_level = fiabilite_score + disponibilite_score + process_safety_score
                
                return {
                    "ai_fiabilite_integrite_score": fiabilite_score,
                    "ai_disponibilite_score": disponibilite_score,
                    "ai_process_safety_score": process_safety_score,
                    "ai_criticality_level": criticality_level
                }
            else:
                # Use fallback prediction
                return self._fallback_prediction(anomaly_data)
        except Exception as e:
            print(f"Prediction error: {e}")
            # Return fallback prediction on error
            return self._fallback_prediction(anomaly_data)
    
    def predict_batch(self, anomalies_data: List[Dict[str, Any]]) -> List[Dict[str, int]]:
        """Predict scores for multiple anomalies"""
        try:
            if self.model_loaded and self.model is not None:
                X = self._prepare_features(anomalies_data)
                
                # Make predictions
                predictions = self.model.predict(X)
                
                results = []
                for i, prediction in enumerate(predictions):
                    fiabilite_score = max(1, min(5, int(round(prediction[0]))))
                    disponibilite_score = max(1, min(5, int(round(prediction[1]))))
                    process_safety_score = max(1, min(5, int(round(prediction[2]))))
                    
                    criticality_level = fiabilite_score + disponibilite_score + process_safety_score
                    
                    results.append({
                        "ai_fiabilite_integrite_score": fiabilite_score,
                        "ai_disponibilite_score": disponibilite_score,
                        "ai_process_safety_score": process_safety_score,
                        "ai_criticality_level": criticality_level
                    })
                
                return results
            else:
                # Use fallback predictions
                return [self._fallback_prediction(anomaly) for anomaly in anomalies_data]
        except Exception as e:
            print(f"Batch prediction error: {e}")
            # Return fallback predictions for all items if prediction fails
            return [self._fallback_prediction(anomaly) for anomaly in anomalies_data]

# Global predictor instance
predictor = TAMSPredictor()
