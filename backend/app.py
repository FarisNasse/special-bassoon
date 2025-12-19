from flask import Flask, request, jsonify
from flask_cors import CORS
from processor import DataProcessor
import pandas as pd
import os

app = Flask(__name__)
CORS(app) # Allow React to talk to Flask

processor = DataProcessor()
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/analyze', methods=['POST'])
def analyze_finances():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)

    try:
        # 1. Process Data
        df = processor.process(filepath)
        
        # 2. Generate Summary for Graphs
        # Group by Category
        category_summary = df.groupby('category')['amount'].sum().reset_index().to_dict(orient='records')
        
        # Group by Month (for trend lines)
        monthly_trend = df.groupby('month')['amount'].sum().reset_index().to_dict(orient='records')

        # 3. Detect Anomalies
        anomalies = processor.detect_anomalies(df)

        return jsonify({
            "summary": category_summary,
            "trend": monthly_trend,
            "anomalies": anomalies,
            "raw_data": df.head(50).to_dict(orient='records') # Send first 50 rows for preview
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)