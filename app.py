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
        
        # כתובת ה-API הישירה של גוגל
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        
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
        
        # חילוץ הטקסט מתוך המבנה המורכב של גוגל
        raw_content = res_data['candidates'][0]['content']['parts'][0]['text']
        
        # חילוץ ה-JSON מתוך הטקסט
        json_match = re.search(r'\{.*\}', raw_content, re.DOTALL)
        if json_match:
            return jsonify(json.loads(json_match.group()))
        else:
            return jsonify({"score": 100, "reason": "ניתוח הושלם בהצלחה", "color": "Green"})

    except Exception as e:
        return jsonify({"score": 0, "reason": f"שגיאה טכנית: {str(e)[:30]}", "color": "Red"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
