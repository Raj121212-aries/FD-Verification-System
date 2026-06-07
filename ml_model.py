import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import os
import random
from datetime import datetime
import pickle
import re

DATA_FILE = "data/dataset.csv"
MODEL_FILE = "data/model.pkl"
SCALER_FILE = "data/scaler.pkl"

def init_dataset():
    if not os.path.exists("data"):
        os.makedirs("data")
    
    if not os.path.exists(DATA_FILE):
        # Generate dummy data deterministically
        random.seed(42)
        np.random.seed(42)
        
        data = []
        for _ in range(200):
            rating = round(random.uniform(1.0, 5.0), 1)
            discount = round(random.uniform(0, 90), 2)
            reviews = random.randint(0, 10000)
            
            # Deterministic label logic for training
            score = 0
            if rating >= 4.0: score += 40
            elif rating <= 2.5: score -= 40
            
            if 5 <= discount <= 50: score += 30
            elif discount > 60: score -= 50
            
            if reviews > 500: score += 30
            elif reviews < 50: score -= 20
            
            # Map score to category
            if score >= 50: decision = "Safe"
            elif score >= 10: decision = "Moderate"
            else: decision = "Risky"
            
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data.append([timestamp, rating, discount, reviews, decision])
            
        df = pd.DataFrame(data, columns=["timestamp", "rating", "discount", "reviews", "decision"])
        df.to_csv(DATA_FILE, index=False)

def train_model():
    if not os.path.exists(DATA_FILE):
        init_dataset()
        
    df = pd.read_csv(DATA_FILE)
    
    # Feature Engineering
    X = df[["rating", "discount", "reviews"]].fillna(0)
    y = df["decision"]
    
    # Scale features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Train deterministic model
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_scaled, y)
    
    with open(MODEL_FILE, "wb") as f:
        pickle.dump(model, f)
        
    with open(SCALER_FILE, "wb") as f:
        pickle.dump(scaler, f)
        
    return model, scaler

def extract_features(data_dict):
    # 1. Rating
    rating_val = 0.0
    try:
        if data_dict["rating"] and data_dict["rating"] != "Not Found":
            rating_val = float(data_dict["rating"].split()[0])
    except:
        rating_val = 0.0
        
    # 2. Discount
    discount_val = 0.0
    try:
        if data_dict["price"] != "Not Found" and data_dict["mrp"] != "Not Found":
            price_str = str(data_dict["price"]).replace(",", "")
            mrp_str = str(data_dict["mrp"]).replace(",", "")
            
            p_match = re.search(r'(\d+(?:\.\d+)?)', price_str)
            m_match = re.search(r'(\d+(?:\.\d+)?)', mrp_str)
            
            if p_match and m_match:
                p = float(p_match.group(1))
                m = float(m_match.group(1))
                if m > 0 and m > p:
                    discount_val = round(((m - p) / m) * 100, 2)
                else:
                    discount_val = 0.0
            else:
                discount_val = 0.0
    except Exception as e:
        print("Discount Extraction Error:", e)
        discount_val = 0.0
        
    # 3. Reviews
    reviews_val = 0
    try:
        if "reviews" in data_dict and data_dict["reviews"] and data_dict["reviews"] != "Not Found":
            rev_str = str(data_dict["reviews"]).split()[0]
            rev_str = rev_str.replace(",", "").strip()
            if rev_str.isdigit():
                reviews_val = int(rev_str)
    except:
        reviews_val = 0
            
    return rating_val, discount_val, reviews_val

def predict_decision(data_dict):
    if not os.path.exists(MODEL_FILE) or not os.path.exists(SCALER_FILE):
        model, scaler = train_model()
    else:
        with open(MODEL_FILE, "rb") as f:
            model = pickle.load(f)
        with open(SCALER_FILE, "rb") as f:
            scaler = pickle.load(f)
            
    rating, discount, reviews = extract_features(data_dict)
    
    features = np.array([[rating, discount, reviews]])
    scaled_features = scaler.transform(features)
    
    prediction = model.predict(scaled_features)[0]
    
    # Calculate deterministic Safe Score
    probabilities = model.predict_proba(scaled_features)[0]
    safe_index = list(model.classes_).index("Safe") if "Safe" in model.classes_ else -1
    
    # Base formula score (deterministic based on values)
    base_score = 50
    if rating >= 4.0: base_score += 20
    elif rating <= 2.5: base_score -= 30
    
    if 5 <= discount <= 50: base_score += 10
    elif discount > 60: base_score -= 30
    
    if reviews > 500: base_score += 20
    elif reviews < 50: base_score -= 10
    
    # Incorporate sentiment proxy
    sentiment_score = rating * 4
    base_score += sentiment_score - 10
    
    # Incorporate ML prediction probability if available
    if safe_index != -1:
        ml_safe_prob = probabilities[safe_index] * 100
        final_score = (base_score * 0.5) + (ml_safe_prob * 0.5)
    else:
        final_score = base_score
        
    final_score = max(0, min(100, round(final_score)))
    
    # Re-evaluate decision strictly based on final score
    if final_score >= 70:
        prediction = "Safe"
    elif final_score >= 40:
        prediction = "Moderate"
    else:
        prediction = "Risky"
        
    pros = []
    cons = []
    if reviews > 500: pros.append(f"High number of ratings ({reviews}) indicates reliability.")
    elif reviews < 50: cons.append("Low review count - unproven product.")
        
    if rating >= 4.0: pros.append(f"Highly rated product ({rating} stars).")
    elif rating <= 3.0 and rating > 0: cons.append(f"Low rating ({rating} stars) - check reviews carefully.")
    elif rating == 0: cons.append("No ratings found.")
        
    if discount > 60: cons.append(f"Suspiciously high discount ({discount}%) - might be fake MRP.")
    elif 10 <= discount <= 50: pros.append(f"Reasonable discount offered ({discount}%).")

    return {
        "decision": prediction,
        "confidence": final_score,
        "features": {
            "rating": rating,
            "discount": discount,
            "reviews": reviews
        },
        "safety_evaluation": {
            "pros": pros,
            "cons": cons
        }
    }

def append_to_dataset(rating, discount, reviews, decision):
    if not os.path.exists(DATA_FILE):
        init_dataset()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    df = pd.DataFrame([[timestamp, rating, discount, reviews, decision]], 
                      columns=["timestamp", "rating", "discount", "reviews", "decision"])
    df.to_csv(DATA_FILE, mode='a', header=False, index=False)
    # Model retrain removed for stability
