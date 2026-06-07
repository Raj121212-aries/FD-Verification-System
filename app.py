from flask import Flask, request, jsonify, render_template
import pandas as pd
import os
import json
from scraper import get_product_data, get_amazon_alternatives
from ml_model import predict_decision, append_to_dataset

app = Flask(__name__)

DATA_FILE = "data/dataset.csv"
HISTORY_FILE = "data/history.json"
PRODUCT_CACHE = {} # Cache for same-URL stability and speed

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.json
        url = data.get("url")
        
        if not url:
            return jsonify({"error": "No URL provided"}), 400
            
        # Check cache first for absolute stability
        if url in PRODUCT_CACHE:
            return jsonify(PRODUCT_CACHE[url])
            
        # 1. Scrape data
        product_data = get_product_data(url)
        
        if product_data["title"] == "Error" or product_data["title"] == "Blocked by Amazon":
            return jsonify({
                "error": "Failed to extract product data",
                "details": product_data
            }), 400
            
        # 2. Predict using ML model (Deterministic now)
        prediction_result = predict_decision(product_data)
        
        # 3. Store data in CSV for analytics
        features = prediction_result["features"]
        append_to_dataset(
            rating=features["rating"],
            discount=features["discount"],
            reviews=features["reviews"],
            decision=prediction_result["decision"]
        )
        
        # 4. Fetch Alternatives
        alternatives = get_amazon_alternatives(product_data["title"])
        
        # 5. Save to History
        history_entry = {
            "url": url,
            "title": product_data["title"],
            "price": product_data["price"],
            "rating": product_data["rating"],
            "decision": prediction_result["decision"]
        }
        
        try:
            history_list = []
            if os.path.exists(HISTORY_FILE):
                with open(HISTORY_FILE, "r") as f:
                    history_list = json.load(f)
            history_list.insert(0, history_entry)
            history_list = history_list[:50] # Keep last 50 items
            with open(HISTORY_FILE, "w") as f:
                json.dump(history_list, f)
        except Exception as e:
            print("Error saving history:", e)
        
        response_data = {
            "product": product_data,
            "prediction": prediction_result["decision"],
            "confidence": prediction_result["confidence"],
            "features": features,
            "safety_evaluation": prediction_result.get("safety_evaluation", {}),
            "alternatives": alternatives
        }
        
        # Save to cache
        PRODUCT_CACHE[url] = response_data
        
        return jsonify(response_data)
    except Exception as e:
        print("Prediction Error:", e)
        return jsonify({"error": "An internal server error occurred."}), 500

@app.route("/analytics", methods=["GET"])
def analytics():
    try:
        if not os.path.exists(DATA_FILE):
            return jsonify({"error": "Dataset not found"}), 404
            
        df = pd.read_csv(DATA_FILE)
        df.fillna(0, inplace=True)
        
        # 1. Pie Chart
        decision_counts = df["decision"].value_counts().to_dict()
        
        # 2. Line Chart: Trend over time
        df["date"] = pd.to_datetime(df["timestamp"]).dt.date
        trend = df.groupby("date").size().to_dict()
        trend_labels = [str(k) for k in trend.keys()]
        trend_values = list(trend.values())
        
        # 3. Histogram: Rating distribution
        bins = [0, 1, 2, 3, 4, 5]
        labels = ["0-1", "1-2", "2-3", "3-4", "4-5"]
        df['rating_bin'] = pd.cut(df['rating'], bins=bins, labels=labels, include_lowest=True)
        rating_counts = df["rating_bin"].value_counts().reindex(labels, fill_value=0).to_dict()
        
        # 4. Scatter Plot: Discount vs Decision
        safe_discounts = df[df["decision"] == "Safe"]["discount"].tolist()
        moderate_discounts = df[df["decision"] == "Moderate"]["discount"].tolist()
        risky_discounts = df[df["decision"] == "Risky"]["discount"].tolist()
        
        # Handle backward compatibility with old 'Buy'/'Not Buy' data
        buy_discounts = df[df["decision"] == "Buy"]["discount"].tolist()
        not_buy_discounts = df[df["decision"] == "Not Buy"]["discount"].tolist()
        
        return jsonify({
            "pie_chart": decision_counts,
            "line_chart": {
                "labels": trend_labels,
                "values": trend_values
            },
            "histogram": rating_counts,
            "scatter": {
                "safe": safe_discounts + buy_discounts,
                "moderate": moderate_discounts,
                "risky": risky_discounts + not_buy_discounts
            },
            "total_items": len(df)
        })
    except Exception as e:
        print("Analytics Error:", e)
        return jsonify({"error": "Failed to load analytics"}), 500

@app.route("/api/history", methods=["GET"])
def get_history():
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r") as f:
                history_list = json.load(f)
            return jsonify(history_list[:5])
        return jsonify([])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Ensure data dir exists
    if not os.path.exists("data"):
        os.makedirs("data")
    app.run(debug=True, port=5000)