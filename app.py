import os
import zipfile
import traceback
import gdown
import torch
from flask import Flask, render_template, request, jsonify, send_from_directory
from transformers import ElectraForSequenceClassification, ElectraTokenizer

# ==========================================================
# 📥 구글 드라이브에서 KoElectra 모델 자동 다운로드 및 압축 해제
# ==========================================================

MODEL_PATH = os.path.abspath("koelectra_model")

if not os.path.exists(MODEL_PATH):
    print("📢 [모델 감지] 로컬 모델 폴더가 존재하지 않아 구글 드라이브에서 다운로드를 시작합니다...")

    file_id = "1M4rnWBmhZwSTCN7rZP5-4k2TU1TZnoOm"
    url = f"https://drive.google.com/uc?id={file_id}"
    output = "koelectra_model.zip"

    try:
        gdown.download(url, output, quiet=False)

        print("📦 다운로드 완료. 압축을 해제합니다...")

        with zipfile.ZipFile(output, "r") as zip_ref:
            zip_ref.extractall(".")

        os.remove(output)

        print("✅ 모델 다운로드 및 압축 해제가 완료되었습니다!")

    except Exception as e:
        print("❌ 모델 다운로드 실패")
        traceback.print_exc()

app = Flask(__name__)

# ==========================================================
# 🔍 Render 디버깅 정보
# ==========================================================

print("=" * 60)
print("현재 작업 폴더 :", os.getcwd())
print("MODEL_PATH :", MODEL_PATH)
print("현재 폴더 목록 :", os.listdir("."))

print("MODEL_PATH 존재 :", os.path.exists(MODEL_PATH))
print("MODEL_PATH 폴더 :", os.path.isdir(MODEL_PATH))

if os.path.isdir(MODEL_PATH):
    print("모델 폴더 내부 :", os.listdir(MODEL_PATH))

print("=" * 60)

# ==========================================================
# 🧠 모델 로드
# ==========================================================

try:
    tokenizer = ElectraTokenizer.from_pretrained(
        MODEL_PATH,
        local_files_only=True
    )

    model = ElectraForSequenceClassification.from_pretrained(
        MODEL_PATH,
        local_files_only=True
    )

    model.eval()

    print("✅ KoElectra 모델이 성공적으로 로드되었습니다.")

except Exception:
    print("❌ 모델 로드 실패")
    traceback.print_exc()

    model = None
    tokenizer = None


# ==========================================================
# 예측
# ==========================================================

def predict_sentiment(text):

    if model is None:
        raise RuntimeError("모델이 로드되지 않았습니다.")

    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=128
    )

    with torch.no_grad():
        outputs = model(**inputs)

    prediction = torch.argmax(outputs.logits, dim=-1).item()

    return prediction


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


@app.route("/api/predict", methods=["POST"])
def predict():

    data = request.get_json()
    text = data.get("text", "")

    if not text.strip():
        return jsonify({
            "status": "empty",
            "result": 1
        })

    result = predict_sentiment(text)

    return jsonify({
        "status": "success",
        "result": result
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
