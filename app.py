import os
import torch
from flask import Flask, render_template, request, jsonify
from transformers import ElectraForSequenceClassification, ElectraTokenizer

app = Flask(__name__)

# ==========================================================
# 🧠 KoElectra 모델 로드 설정 (실제 모델 폴더명과 맞추어 설정)
# ==========================================================
MODEL_PATH = "./koelectra_model"

try:
    tokenizer = ElectraTokenizer.from_pretrained(MODEL_PATH)
    model = ElectraForSequenceClassification.from_pretrained(MODEL_PATH)
    model.eval()
    print("✅ KoElectra 모델이 성공적으로 로드되었습니다.")
except Exception as e:
    print(f"❌ 모델 로드 중 오류 발생: {e}")
    print("⚠️ 모델 없이 테스트하기 위해 더미 필터링 모드로 안전하게 자동 전환합니다.")
    model = None
    tokenizer = None


def predict_sentiment(text):
    if model is None or tokenizer is None:
        return 1  # 에러 방지용 기본 통과 처리

    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=128)
    with torch.no_grad():
        outputs = model(**inputs)
        logits = outputs.logits
        # 0: abnormal (비속어/부적절), 1: normal (정상) 가정
        prediction = torch.argmax(logits, dim=-1).item()
    return prediction


# ==========================================================
# 🌐 Flask 라우팅 설정
# ==========================================================

@app.route('/')
def index():
    # 이제 첫 인트로 및 신분 선택 화면을 띄워줍니다.
    return render_template('index.html')


@app.route('/student')
def student_view():
    return render_template('student.html')


@app.route('/teacher')
def teacher_view():
    return render_template('teacher.html')


@app.route('/api/predict', methods=['POST'])
def predict():
    data = request.get_json()
    text = data.get('text', '')

    if not text.strip():
        return jsonify({'status': 'empty', 'result': 1})

    result = predict_sentiment(text)
    return jsonify({
        'status': 'success',
        'result': result  # 0(abnormal) 또는 1(normal)
    })


from flask import send_from_directory

@app.route('/firebase-messaging-sw.js')
def serve_service_worker():
    return send_from_directory('.', 'firebase-messaging-sw.js', mimetype='application/javascript')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003, debug=True)

