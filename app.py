from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os
import json
import re

app = Flask(__name__)
CORS(app)

# הגדרת המפתח והמודל
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
# שימוש בשם המודל היציב ביותר
model = genai.GenerativeModel('gemini-1.5-flash')

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
        
        # טיפול במקרים שה-AI מחזיר תשובה ריקה
        if not response.text:
            return jsonify({"score": 50, "reason": "לא התקבלה תשובה מהבינה המלאכותית", "color": "Yellow"})
            
        raw_content = response.text.strip()
        
        # חילוץ ה-JSON בעזרת ביטוי רגולרי
        json_match = re.search(r'\{.*\}', raw_content, re.DOTALL)
        
        if json_match:
            return jsonify(json.loads(json_match.group()))
        else:
            return jsonify({"score": 100, "reason": "המידע נראה אמין", "color": "Green"})
            
    except Exception as e:
        # הדפסת השגיאה המלאה ללוגים של Render
        print(f"Full Error: {str(e)}")
        return jsonify({"score": 0, "reason": f"שגיאה: {str(e)[:40]}", "color": "Red"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
