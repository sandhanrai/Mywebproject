import numpy as np
import pandas as pd
import joblib
from src.data_preprocessing import get_symptom_list, get_disease_mapping
from src.logger import setup_logger

class SymptomPredictor:
    def __init__(self, model_path='models/best_model.joblib', encoder_path='models/label_encoder.joblib'):
        """
        Initialize the symptom predictor with trained model and label encoder
        """
        self.model = joblib.load(model_path)
        self.label_encoder = joblib.load(encoder_path)
        self.disease_mapping = get_disease_mapping(self.label_encoder)
        self.logger = setup_logger()
        
    def predict_disease(self, symptoms_dict, df):
        """
        Predict disease based on symptoms input
        
        Args:
            symptoms_dict: Dictionary with symptom names as keys and values (0 or 1)
            df: Original dataframe to get symptom order
            
        Returns:
            Dictionary with predictions and probabilities
        """
        # Get the complete list of symptoms in correct order
        all_symptoms = get_symptom_list(df)
        
        # Create input array with correct order
        input_data = []
        for symptom in all_symptoms:
            input_data.append(symptoms_dict.get(symptom, 0))
        
        # Convert to numpy array and reshape for prediction
        input_array = np.array(input_data).reshape(1, -1)
        
        # Make prediction
        prediction = self.model.predict(input_array)[0]
        probabilities = self.model.predict_proba(input_array)[0]
        
        # Get top 4 predictions with highest probabilities
        top_indices = probabilities.argsort()[-4:][::-1]  # Get top 4, highest first
        top_predictions = []

        for idx in top_indices:
            top_predictions.append({
                'disease': self.disease_mapping[idx],
                'probability': float(probabilities[idx])
            })
        
        # Log the prediction
        selected_symptoms = [symptom for symptom, value in symptoms_dict.items() if value == 1]
        self.logger.info(f"Prediction made - Symptoms: {selected_symptoms}, Primary Prediction: {self.disease_mapping[prediction]}, Confidence: {probabilities[prediction]:.2%}")
        
        return {
            'primary_prediction': self.disease_mapping[prediction],
            'primary_probability': float(probabilities[prediction]),
            'all_predictions': top_predictions
        }
    
    def get_symptom_descriptions(self):
        """
        Return descriptions for common symptoms
        """
        symptom_descriptions = {
            'fever': 'Elevated body temperature (above 37°C/98.6°F)',
            'cough': 'Sudden expulsion of air from the lungs',
            'headache': 'Pain or discomfort in the head or neck area',
            'fatigue': 'Extreme tiredness or lack of energy',
            'chest_pain': 'Pain or discomfort in the chest area',
            'shortness_of_breath': 'Difficulty breathing or feeling breathless',
            'nausea': 'Feeling of sickness with an inclination to vomit',
            'vomiting': 'Forceful expulsion of stomach contents',
            'diarrhea': 'Loose, watery bowel movements',
            'abdominal_pain': 'Pain or discomfort in the stomach area',
            'rash': 'Change in skin color or texture',
            'muscle_pain': 'Pain or soreness in muscles',
            'sore_throat': 'Pain, scratchiness or irritation of the throat',
            'runny_nose': 'Excess nasal drainage',
            'sneezing': 'Sudden, forceful expulsion of air through the nose'
        }
        return symptom_descriptions

def create_symptom_input_template(df):
    """
    Create a template dictionary for symptom input
    """
    symptoms = get_symptom_list(df)
    return {symptom: 0 for symptom in symptoms}

if __name__ == "__main__":
    # Test the prediction system
    from src.data_preprocessing import load_and_preprocess_data

    # Load data to get symptom list
    _, _, _, _, _, _, _, df, _, _ = load_and_preprocess_data('data/disease.csv')
    
    # Initialize predictor
    predictor = SymptomPredictor()
    
    # Test prediction
    test_symptoms = create_symptom_input_template(df)
    test_symptoms['fever'] = 1
    test_symptoms['cough'] = 1
    test_symptoms['headache'] = 1
    
    result = predictor.predict_disease(test_symptoms, df)
    
    print("Test Prediction Results:")
    print(f"Primary Prediction: {result['primary_prediction']}")
    print(f"Probability: {result['primary_probability']:.2%}")
    print("\nTop Predictions:")
    for pred in result['all_predictions']:
        print(f"  {pred['disease']}: {pred['probability']:.2%}")
