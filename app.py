from flask import Flask, render_template, request, jsonify, send_from_directory

app = Flask(__name__)


# ==========================================================
# Flask
# ==========================================================

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/student")
def student_view():
    return render_template("student.html")


@app.route("/teacher")
def teacher_view():
    return render_template("teacher.html")


# ==========================================================
# (기존 AI 필터 API - 현재는 항상 통과)
# ==========================================================

@app.route("/api/predict", methods=["POST"])
def predict():
    data = request.get_json()
    text = data.get("text", "")

    if not text.strip():
        return jsonify({
            "status": "empty",
            "result": 1
        })

    # AI 모델 제거 → 항상 정상 메시지로 처리
    return jsonify({
        "status": "success",
        "result": 1
    })


@app.route("/firebase-messaging-sw.js")
def serve_service_worker():
    return send_from_directory(
        ".",
        "firebase-messaging-sw.js",
        mimetype="application/javascript"
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)
