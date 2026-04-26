from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os
import json
import re

app = Flask(__name__)
CORS(app)

# הגדרת המפתח והמודל החדש
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash-latest')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        text = data.get("text", "")
        
        prompt = f"""
        Analyze this Hebrew text for reliability. 
        Return ONLY a JSON object with: 
        "score": (0-100), 
        "reason": (short Hebrew explanation), 
        "color": ("Red", "Yellow", or "Green")
        
        Text: {text}
        """
        
        response = model.generate_content(prompt)
        raw_text = response.text.strip()
        
        # חילוץ ה-JSON
        match = re.search(r'\{.*\}', raw_text, re.DOTALL)
        if match:
            return jsonify(json.loads(match.group()))
        else:
            return jsonify({"score": 50, "reason": "לא התקבל מבנה נתונים תקין", "color": "Yellow"})
            
    except Exception as e:
        print(f"Detailed Error: {e}")
        return jsonify({"score": 0, "reason": f"שגיאה פנימית: {str(e)[:30]}", "color": "Red"})

if __name__ == '__main__':
    # התאמה לפורט של Render
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
