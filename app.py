import os
import zipfile
import gdown
import torch
from flask import Flask, render_template, request, jsonify
from transformers import ElectraForSequenceClassification, ElectraTokenizer

# ==========================================================
# 📥 구글 드라이브에서 KoElectra 모델 자동 다운로드 및 압축 해제
# ==========================================================
MODEL_PATH = "./koelectra_model"

# 모델 폴더가 없는 경우에만 구글 드라이브에서 다운로드 및 압축 해제 실행
if not os.path.exists(MODEL_PATH):
    print("📢 [모델 감지] 로컬 모델 폴더가 존재하지 않아 구글 드라이브에서 다운로드를 시작합니다...")

    file_id = '1M4rnWBmhZwSTCN7rZP5-4k2TU1TZnoOm'
    url = f'https://drive.google.com/uc?id={file_id}'
    output = 'koelectra_model.zip'

    try:
        # 구글 드라이브 대용량 파일 다운로드 (gdown 활용)
        gdown.download(url, output, quiet=False, remaining_ok=True)

        # 다운로드받은 zip 파일 압축 해제
        print("📦 다운로드 완료. 압축을 해제합니다...")
        with zipfile.ZipFile(output, 'r') as zip_ref:
            # zip 안에 'koelectra_model' 폴더가 포함되어 있는지 확인 후 압축 해제 경로 지정
            zip_ref.extractall(".")

            # 압축 해제 후 다운로드받은 원본 zip 파일은 서버 용량 확보를 위해 삭제
        os.remove(output)
        print("✅ 모델 다운로드 및 압축 해제가 완료되었습니다!")

    except Exception as e:
        print(f"❌ 모델 자동 다운로드 중 오류 발생: {e}")
        print("⚠️ 수동 다운로드나 구글 드라이브 링크 및 권한(링크가 있는 모든 사용자 공개)을 다시 확인해 주세요.")

app = Flask(__name__)

# ==========================================================
# 🧠 KoElectra 모델 로드 설정 (실제 모델 폴더명과 맞추어 설정)
# ==========================================================

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
