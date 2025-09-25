import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
from sklearn.model_selection import cross_val_score, GridSearchCV
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
from src.data_preprocessing import load_and_preprocess_data

import os

def train_models():
    """Train multiple machine learning models and evaluate their performance"""
    # Create models directory if it doesn't exist
    models_dir = os.path.join(os.path.dirname(__file__), '../models')
    os.makedirs(models_dir, exist_ok=True)
    # Load and preprocess data
    X_train_standard, X_test_standard, X_train_minmax, X_test_minmax, y_train, y_test, label_encoder, df, _, _ = load_and_preprocess_data('data/disease.csv')
    
    # Initialize models
    models = {
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
        'Decision Tree': DecisionTreeClassifier(random_state=42),
        'Multinomial NB': MultinomialNB(),
        'SVM': SVC(probability=True, random_state=42)
    }
    
    results = {}
    
    # Hyperparameter tuning for Random Forest
    rf_param_grid = {
        'n_estimators': [50, 100, 200],
        'max_depth': [None, 10, 20, 30],
        'min_samples_split': [2, 5, 10]
    }
    
    # Train and evaluate each model
    for name, model in models.items():
        print(f"\nTraining {name}...")
        
        # Use appropriate scaled data for each algorithm
        if name == 'Multinomial NB':
            # Use MinMax scaled data for algorithms that require non-negative values
            X_train_current = X_train_minmax
            X_test_current = X_test_minmax
        else:
            # Use Standard scaled data for other algorithms
            X_train_current = X_train_standard
            X_test_current = X_test_standard
        
        # Hyperparameter tuning for Random Forest
        if name == 'Random Forest':
            grid_search = GridSearchCV(model, rf_param_grid, cv=5, scoring='accuracy', n_jobs=-1)
            grid_search.fit(X_train_current, y_train)
            model = grid_search.best_estimator_
            print(f"Best parameters for {name}: {grid_search.best_params_}")
        
        # Train the model
        model.fit(X_train_current, y_train)
        
        # Make predictions
        y_pred = model.predict(X_test_current)
        
        # Calculate metrics
        accuracy = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, average='weighted')
        recall = recall_score(y_test, y_pred, average='weighted')
        f1 = f1_score(y_test, y_pred, average='weighted')
        
        results[name] = {
            'model': model,
            'accuracy': accuracy,
            'precision': precision,
            'recall': recall,
            'f1': f1
        }
        
        print(f"{name} Results:")
        print(f"  Accuracy: {accuracy:.4f}")
        print(f"  Precision: {precision:.4f}")
        print(f"  Recall: {recall:.4f}")
        print(f"  F1 Score: {f1:.4f}")
        
        # Save classification report
        test_classes = np.unique(y_test)
        target_names = [label_encoder.classes_[i] for i in test_classes]
        
        report = classification_report(y_test, y_pred, target_names=target_names)
        report_path = os.path.join(models_dir, f'{name.lower().replace(" ", "_")}_report.txt')
        with open(report_path, 'w') as f:
            f.write(report)
    
    # Select the best model based on accuracy
    best_model_name = max(results.items(), key=lambda x: x[1]['accuracy'])[0]
    best_model = results[best_model_name]['model']
    
    print(f"\nBest model: {best_model_name} with accuracy: {results[best_model_name]['accuracy']:.4f}")
    
    # Save the best model
    best_model_path = os.path.join(models_dir, 'best_model.joblib')
    joblib.dump(best_model, best_model_path)
    print(f"Best model saved to '{best_model_path}'")
    
    # Save all results for comparison
    results_path = os.path.join(models_dir, 'model_results.joblib')
    joblib.dump(results, results_path)
    
    return results, best_model_name

def plot_model_comparison(results, models_dir):
    """
    Create visualization comparing model performance
    """
    metrics = ['accuracy', 'precision', 'recall', 'f1']
    model_names = list(results.keys())
    
    fig, axes = plt.subplots(2, 2, figsize=(15, 10))
    axes = axes.flatten()
    
    for i, metric in enumerate(metrics):
        values = [results[name][metric] for name in model_names]
        axes[i].bar(model_names, values, color=['skyblue', 'lightgreen', 'lightcoral'])
        axes[i].set_title(f'{metric.capitalize()} Comparison')
        axes[i].set_ylabel(metric.capitalize())
        axes[i].tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for j, v in enumerate(values):
            axes[i].text(j, v + 0.01, f'{v:.3f}', ha='center', va='bottom')
    
    plt.tight_layout()
    plot_path = os.path.join(models_dir, 'model_comparison.png')
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"Model comparison plot saved to '{plot_path}'")

if __name__ == "__main__":
    # Train models and evaluate
    results, best_model_name = train_models()
    
    # Create visualizations
    models_dir = os.path.join(os.path.dirname(__file__), '../models')
    plot_model_comparison(results, models_dir)
    
    print("\nModel training completed successfully!")
