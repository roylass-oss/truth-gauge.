
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import os

app = Flask(name)
CORS(app)

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-pro')

@app.route('/analyze', methods=['POST'])
def analyze():
data = request.json
text = data.get("text", "")
prompt = f"נתח את הטקסט הבא לאמינות. החזר JSON עם: score (מספר בין 0 ל-100), reason (הסבר קצר של שורה אחת), color (Red/Yellow/Green). טקסט: {text}"
try:
response = model.generate_content(prompt)
return response.text
except:
return jsonify({"score": 50, "reason": "שגיאה בחיבור ל-AI", "color": "Yellow"})

if name == 'main':
app.run()
