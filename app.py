from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os
import json

app = Flask(__name__)
CORS(app)

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.json
    text = data.get("text", "")
    
    # הנחיה קשיחה יותר ל-AI להחזיר רק JSON
    prompt = f"Analyze the following Hebrew text for reliability. You MUST return ONLY a valid JSON object (no markdown, no extra text) with these keys: 'score' (number 0-100), 'reason' (short string in Hebrew), 'color' ('Red', 'Yellow', or 'Green'). Text: {text}"
    
    try:
        response = model.generate_content(prompt)
        content = response.text.strip()
        
        # ניקוי סימני Markdown אם ה-AI הוסיף אותם בטעות
        if content.startswith("```json"):
            content = content.replace("```json", "").replace("```", "").strip()
        
        # המרה לאובייקט JSON כדי לוודא תקינות
        result = json.loads(content)
        return jsonify(result)
        
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"score": 50, "reason": f"ה-AI התבלבל, נסה שוב. שגיאה: {str(e)[:20]}", "color": "Yellow"})

if __name__ == '__main__':
    app.run()
