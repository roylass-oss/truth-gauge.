from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
import json
import re

app = Flask(__name__)
CORS(app)

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        text = data.get("text", "")
        api_key = os.environ.get("GEMINI_API_KEY")
        
        # שימוש במודל gemini-pro - הוא הכי יציב בשיטה הזו
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": f"Analyze this Hebrew text for reliability. Return ONLY a JSON object with: 'score' (0-100), 'reason' (short Hebrew explanation), 'color' (Red/Yellow/Green). Text: {text}"
                }]
            }]
        }
        
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, headers=headers, json=payload)
        res_data = response.json()
        
        # אם יש שגיאה מהשרת של גוגל
        if 'error' in res_data:
            return jsonify({"score": 0, "reason": f"גוגל אומר: {res_data['error']['message']}", "color": "Red"})

        # שליפת הטקסט
        try:
            raw_content = res_data['candidates'][0]['content']['parts'][0]['text']
            
            # חילוץ ה-JSON
            json_match = re.search(r'\{.*\}', raw_content, re.DOTALL)
            if json_match:
                return jsonify(json.loads(json_match.group()))
            else:
                return jsonify({"score": 100, "reason": "ניתוח הושלם", "color": "Green"})
        except:
            return jsonify({"score": 50, "reason": "תשובה לא צפויה מה-AI", "color": "Yellow"})

    except Exception as e:
        return jsonify({"score": 0, "reason": f"שגיאה: {str(e)[:30]}", "color": "Red"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
