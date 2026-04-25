from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os
import json

app = Flask(__name__)
CORS(app)

# הגדרת המודל
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

# הגדרות בטיחות - מאפשר ל-AI לנתח גם תוכן רגיש בלי לחסום
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

model = genai.GenerativeModel('gemini-pro', safety_settings=safety_settings)

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    text = data.get("text", "")
    
    prompt = f"""
    Analyze this text for news reliability. 
    Return ONLY a raw JSON object with these keys:
    "score": (0-100),
    "reason": (short Hebrew explanation),
    "color": ("Red", "Yellow", or "Green")
    
    Text to analyze: {text}
    """
    
    try:
        response = model.generate_content(prompt)
        
        # חילוץ הטקסט מהתשובה
        content = response.text.strip()
        
        # ניקוי שאריות Markdown אם קיימות
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].strip()

        # בדיקה שהתוכן נראה כמו JSON (מתחיל ב-{)
        start_idx = content.find('{')
        end_idx = content.rfind('}')
        if start_idx != -1 and end_idx != -1:
            content = content[start_idx:end_idx+1]

        result = json.loads(content)
        return jsonify(result)
        
    except Exception as e:
        print(f"Detailed Error: {e}")
        return jsonify({
            "score": 0, 
            "reason": "ה-AI התקשה לעבד את הטקסט. נסה לקצר את הידיעה או להזין טקסט אחר.", 
            "color": "Red"
        })

if __name__ == '__main__':
    app.run()
