 from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os
import json
import re

app = Flask(__name__)
CORS(app)

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash')
@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        text = data.get("text", "")
        prompt = f"Analyze this text and return ONLY a JSON object with: 'score' (0-100), 'reason' (Hebrew), 'color' (Red/Yellow/Green). Text: {text}"
        
        response = model.generate_content(prompt)
        raw_text = response.text.strip()
        
        # חילוץ ה-JSON בעזרת ביטוי רגולרי (למקרה שה-AI הוסיף טקסט מיותר)
        match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        if match:
            clean_json = json.loads(match.group())
            return jsonify(clean_json)
        else:
            raise ValueError("No JSON found")
            
    except Exception as e:
        return jsonify({"score": 50, "reason": "ניתוח הטקסט נכשל, נסה שוב", "color": "Yellow"})

if __name__ == '__main__':
    app.run()
