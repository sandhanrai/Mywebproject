import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.model_selection import train_test_split, StratifiedKFold
import joblib
import os

def load_and_preprocess_data(file_path='data/synthetic_symptoms_dataset.csv', test_size=0.2, random_state=42):
    """
    Load and preprocess the symptom dataset with proper train-test split
    
    Args:
        file_path: Path to the dataset CSV file
        test_size: Proportion of data to use for testing
        random_state: Random seed for reproducibility
    
    Returns:
        X_train, X_test, y_train, y_test, label_encoder, df, feature_names
    """
    # Load the dataset
    df = pd.read_csv(file_path)

    # Drop columns with all NaN values (like 'Unnamed: 133')
    df = df.dropna(axis=1, how='all')

    # Separate features and target
    # Keep demographic features for analysis but exclude from ML training initially
    demographic_features = ['age', 'gender', 'symptom_duration']
    symptom_features = [col for col in df.columns if col not in ['prognosis'] + demographic_features]

    X = df[symptom_features]
    y = df['prognosis']
    
    # Encode the target variable
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    
    # Save the label encoder for later use
    models_dir = os.path.join(os.path.dirname(__file__), '../models')
    os.makedirs(models_dir, exist_ok=True)
    encoder_path = os.path.join(models_dir, 'label_encoder.joblib')
    joblib.dump(label_encoder, encoder_path)
    
    # Perform proper stratified train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=test_size, random_state=random_state, 
        stratify=y_encoded
    )
    
    # For algorithms that require non-negative values (like MultinomialNB), we'll use MinMax scaling
    # For others, we'll use Standard scaling
    from sklearn.preprocessing import MinMaxScaler
    
    # Create both scalers
    standard_scaler = StandardScaler()
    minmax_scaler = MinMaxScaler()
    
    X_train_standard = standard_scaler.fit_transform(X_train)
    X_test_standard = standard_scaler.transform(X_test)
    
    X_train_minmax = minmax_scaler.fit_transform(X_train)
    X_test_minmax = minmax_scaler.transform(X_test)
    
    # Save the scalers
    scaler_path = os.path.join(models_dir, 'feature_scaler_standard.joblib')
    joblib.dump(standard_scaler, scaler_path)
    
    scaler_path = os.path.join(models_dir, 'feature_scaler_minmax.joblib')
    joblib.dump(minmax_scaler, scaler_path)
    
    return (X_train_standard, X_test_standard, X_train_minmax, X_test_minmax, 
            y_train, y_test, label_encoder, df, symptom_features, demographic_features)

def get_symptom_list(df, include_demographics=False):
    """
    Get the list of symptoms from the dataset

    Args:
        df: The dataframe containing the dataset
        include_demographics: Whether to include demographic features

    Returns:
        List of symptom feature names
    """
    if include_demographics:
        return [col for col in df.columns if col != 'prognosis']
    else:
        return [col for col in df.columns if col not in ['prognosis', 'age', 'gender', 'symptom_duration']]

def get_disease_mapping(label_encoder):
    """
    Get the mapping of encoded labels to disease names
    """
    return {i: disease for i, disease in enumerate(label_encoder.classes_)}

def get_cross_validator(n_splits=5, random_state=42):
    """
    Get a stratified k-fold cross-validator for proper model evaluation
    """
    return StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=random_state)

def prepare_data_for_prediction(symptoms_dict, df, include_demographics=False):
    """
    Prepare input data for prediction from symptom dictionary
    
    Args:
        symptoms_dict: Dictionary with symptom names as keys and values
        df: Original dataframe to get feature order
        include_demographics: Whether to include demographic features
    
    Returns:
        Numpy array ready for prediction
    """
    feature_names = get_symptom_list(df, include_demographics)
    input_data = []
    
    for feature in feature_names:
        input_data.append(symptoms_dict.get(feature, 0))
    
    return np.array(input_data).reshape(1, -1)

if __name__ == "__main__":
    # Test the enhanced preprocessing
    X_train, X_test, y_train, y_test, label_encoder, df, symptoms, demographics = load_and_preprocess_data()
    
    print("Enhanced dataset preprocessing completed!")
    print(f"Training set shape: {X_train.shape}")
    print(f"Test set shape: {X_test.shape}")
    print(f"Number of diseases: {len(label_encoder.classes_)}")
    print(f"Symptom features: {len(symptoms)}")
    print(f"Demographic features: {len(demographics)}")
    print(f"Class distribution in training: {np.bincount(y_train)}")
    print(f"Class distribution in test: {np.bincount(y_test)}")
