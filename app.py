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
        
        # כתובת ישירה ומפורשת - הגרסה היציבה ביותר
        url = f"https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key={api_key}"
        
        # שלח פקודה באנגלית כדי למנוע בעיות קידוד
        prompt = f"Analyze this text for reliability. Return ONLY JSON with: 'score' (0-100), 'reason' (short explanation in HEBREW), 'color' (Red/Yellow/Green). Text: {text}"
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}]
        }
        
        headers = {'Content-Type': 'application/json'}
        response = requests.post(url, headers=headers, json=payload)
        res_data = response.json()
        
        if 'error' in res_data:
            # אם יש שגיאה, נחזיר אותה באנגלית כדי לראות מה קרה
            return jsonify({"score": 0, "reason": res_data['error']['message'], "color": "Red"})

        if 'candidates' in res_data:
            raw_content = res_data['candidates'][0]['content']['parts'][0]['text']
            # חילוץ ה-JSON
            match = re.search(r'\{.*\}', raw_content, re.DOTALL)
            if match:
                # מבטיח שהעברית תעבור נכון חזרה ללפטופ
                return jsonify(json.loads(match.group()))
        
        return jsonify({"score": 50, "reason": "AI Error - No Content", "color": "Yellow"})

    except Exception as e:
        return jsonify({"score": 0, "reason": str(e), "color": "Red"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
