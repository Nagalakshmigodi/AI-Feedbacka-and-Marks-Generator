from flask import Flask, render_template, request, jsonify
import json
import re
import google.generativeai as genai

app = Flask(__name__) 

# Load questions from JSON file
with open("questions.json", "r") as f:
    questions = json.load(f)

# Configure Gemini API (Replace with your API Key)
genai.configure(api_key="AIzaSyAuz5GJSHFpNm7-QG9CKEl6PxNITpIQvLg")
model = genai.GenerativeModel("gemini-pro")

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/get_question/<int:qid>")
def get_question(qid):
    for q in questions:
        if q["id"] == qid:
            return jsonify(q)
    return jsonify({"error": "Question not found"}), 404

@app.route("/evaluate", methods=["POST"])
def evaluate():
    data = request.json
    question = data.get("question")
    user_answer = data.get("answer")

    # Gemini prompt to evaluate the answer
    prompt = f"""
    Evaluate the user's answer based on the given question.

    **Question:** {question}

    **User Answer:** {user_answer}

    Provide a detailed evaluation of the user's answer in a single paragraph, considering:
    - **Accuracy:** How well the answer matches the correct response.
    - **Clarity:** Whether the explanation is well-structured and easy to understand.
    - **Completeness:** Does the answer cover all key points?
    
    response format: the response from the llm should be in plain text only not in markdown format.

    After the evaluation, provide the **correct answer** to the question.

    Do not include any score in the feedback.

    Now, separately assign a **final correctness score (out of 10)** considering:
    - If the answer is completely wrong or too vague, give **a score below 3**.
    - If the answer is partially correct but lacks key details, give **a score between 4-6**.
    - If the answer is well-explained but could be improved, give **a score between 7-8**.
    - If the answer is fully correct and clear, give **a score between 9-10**.

    **Correctness Score: X/10**
    IMPORTANT: Format your response in plain text only. Do not use markdown.
    
    
"""

    response = model.generate_content(prompt)
    response_text = response.text

# Extract Score using Regular Expression
    score_match = re.search(r"\*\*Correctness Score:\s*(\d+)/10\*\*", response_text)
    score = score_match.group(1) if score_match else "N/A"

# Extract Feedback and clean it into a single paragraph (removes score from feedback)
    feedback = re.sub(r"\*\*Correctness Score:.*?\*\*", "", response_text).strip()
    feedback = " ".join(feedback.splitlines())  # Remove newlines and join into a paragraph

    return jsonify({"score": score, "feedback": feedback})


if __name__ == "__main__":
    app.run(debug=True)
