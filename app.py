from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from akinator_python import Akinator
import os

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

akinator_sessions = {}

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start_game():
    data = request.json
    theme = data.get('theme', 'characters')
    session_id = data.get('session_id')

    if not session_id:
        return jsonify({"error": "Session ID is required"}), 400

    try:
        akinator = Akinator(theme=theme, lang="en")
        akinator_sessions[session_id] = akinator
        question = akinator.start_game()
        return jsonify({"question": question, "progression": akinator.progression})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/answer', methods=['POST'])
def post_answer():
    data = request.json
    session_id = data.get('session_id')
    answer = data.get('answer')

    if session_id not in akinator_sessions:
        return jsonify({"error": "Session not found"}), 404
        
    akinator = akinator_sessions[session_id]
    try:
        result = akinator.post_answer(answer)
        if akinator.answer_id:
            return jsonify({
                "name": akinator.name,
                "description": akinator.description,
                "photo": akinator.photo,
                "progression": akinator.progression
            })
        return jsonify({"question": akinator.question, "progression": akinator.progression})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/go_back', methods=['POST'])
def go_back():
    data = request.json
    session_id = data.get('session_id')

    if session_id not in akinator_sessions:
        return jsonify({"error": "Session not found"}), 404

    akinator = akinator_sessions[session_id]
    try:
        akinator.go_back()
        return jsonify({"question": akinator.question, "progression": akinator.progression})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
