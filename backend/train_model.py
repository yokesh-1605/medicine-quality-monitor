"""
AI Model Training Script for Medicine Quality Monitor
Creates and trains an Isolation Forest model for anomaly detection
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
from datetime import datetime, timedelta
import random
import os

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

def generate_synthetic_data(n_samples=200):
    """Generate synthetic medicine data for training"""
    data = []
    
    # Generate legitimate medicines (80% of data)
    for i in range(int(n_samples * 0.8)):
        manufacturer_score = np.random.normal(8.5, 1.2)  # Good manufacturers
        manufacturer_score = max(5, min(10, manufacturer_score))  # Clamp between 5-10
        
        days_to_expiry = np.random.exponential(180) + 30  # Exponential distribution, min 30 days
        days_to_expiry = min(days_to_expiry, 1095)  # Max 3 years
        
        scan_count = np.random.poisson(3) + 1  # Normal scan frequency
        distinct_locations = min(scan_count, np.random.poisson(2) + 1)
        
        # Additional features for legitimate medicines
        batch_age_days = np.random.uniform(30, 365)  # Time since manufacturing
        verification_ratio = np.random.uniform(0.7, 1.0)  # High verification success rate
        
        data.append({
            'manufacturer_score': manufacturer_score,
            'days_to_expiry': days_to_expiry,
            'scan_count': scan_count,
            'distinct_locations': distinct_locations,
            'batch_age_days': batch_age_days,
            'verification_ratio': verification_ratio,
            'label': 0  # Normal
        })
    
    # Generate suspicious/counterfeit medicines (20% of data)
    for i in range(int(n_samples * 0.2)):
        # Suspicious patterns
        if random.random() < 0.3:  # Low manufacturer score
            manufacturer_score = np.random.uniform(2, 5)
        elif random.random() < 0.5:  # Expired or near-expired
            days_to_expiry = np.random.uniform(-30, 15)
        else:  # Other anomalies
            manufacturer_score = np.random.normal(8, 1)
            days_to_expiry = np.random.uniform(30, 200)
        
        # Suspicious scanning patterns
        scan_count = np.random.poisson(8) + 5  # High scan frequency (suspicious)
        distinct_locations = min(scan_count, np.random.poisson(4) + 2)
        
        batch_age_days = np.random.uniform(1, 730)  # Wider range
        verification_ratio = np.random.uniform(0.2, 0.8)  # Lower verification success
        
        data.append({
            'manufacturer_score': manufacturer_score,
            'days_to_expiry': days_to_expiry,
            'scan_count': scan_count,
            'distinct_locations': distinct_locations,
            'batch_age_days': batch_age_days,
            'verification_ratio': verification_ratio,
            'label': 1  # Anomaly
        })
    
    return pd.DataFrame(data)

def train_isolation_forest():
    """Train and save the Isolation Forest model"""
    print("Generating synthetic training data...")
    df = generate_synthetic_data(200)
    
    # Prepare features (exclude label for unsupervised training)
    features = ['manufacturer_score', 'days_to_expiry', 'scan_count', 
                'distinct_locations', 'batch_age_days', 'verification_ratio']
    X = df[features]
    
    print("Training Isolation Forest model...")
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Train Isolation Forest
    # contamination=0.2 means we expect 20% of data to be anomalies
    model = IsolationForest(
        contamination=0.2,
        random_state=42,
        n_estimators=100
    )
    
    model.fit(X_scaled)
    
    # Test the model
    predictions = model.predict(X_scaled)
    anomaly_scores = model.decision_function(X_scaled)
    
    # Convert predictions: -1 (anomaly) to 1, 1 (normal) to 0
    predictions_binary = [1 if pred == -1 else 0 for pred in predictions]
    
    # Calculate accuracy against our synthetic labels
    actual_labels = df['label'].tolist()
    correct = sum(1 for a, p in zip(actual_labels, predictions_binary) if a == p)
    accuracy = correct / len(actual_labels)
    
    print(f"Model training completed!")
    print(f"Training accuracy: {accuracy:.2%}")
    print(f"Detected {sum(predictions_binary)} anomalies out of {len(predictions_binary)} samples")
    
    # Save model and scaler
    os.makedirs('/app/backend/models', exist_ok=True)
    joblib.dump(model, '/app/backend/models/anomaly_model.joblib')
    joblib.dump(scaler, '/app/backend/models/scaler.joblib')
    
    print("Model and scaler saved successfully!")
    
    return model, scaler, accuracy

if __name__ == "__main__":
    model, scaler, accuracy = train_isolation_forest()