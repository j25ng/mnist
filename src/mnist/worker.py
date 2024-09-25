from rightnow.time import now
from mnist.model.manager import get_model_path
from mnist.db import select, dml
from keras.models import load_model
from PIL import Image
import numpy as np
import requests
import random
import os

def get_job_img_task():
    sql = """
    SELECT
    num, label, file_name, file_path
    FROM image_processing
    WHERE prediction_result IS NULL
    ORDER BY num
    LIMIT 1
    """
    r = select(sql, 1)

    if len(r) > 0:
        return r[0]
    else:
        return None

# 사용자 이미지 불러오기 및 전처리
def preprocess_image(image_path):
    img = Image.open(image_path).convert('L')  # 흑백 이미지로 변환
    img = img.resize((28, 28))  # 크기 조정

    # 흑백 반전
    # img = 255 - np.array(img)  # 흑백 반전
    img = np.array(img)
    img = img.reshape(1, 28, 28, 1)  # 모델 입력 형태에 맞게 변형
    img = img / 255.0  # 정규화
    return img

def predict_digit(image_path, model):
    # 모델 로드
    model = load_model(get_model_path(model))  # 학습된 모델 파일 경로
    
    img = preprocess_image(image_path)
    prediction = model.predict(img)
    digit = np.argmax(prediction)
    return digit

def prediction(file_path, model, num):
    sql = """UPDATE image_processing
    SET prediction_result=%s,
        prediction_model=%s,
        prediction_time=%s
    WHERE num=%s
    """
    presult = predict_digit(file_path, model) 
    dml(sql, presult, model, now(), num)
    return presult

def send_line_noti(file_name, label, presult):
    api = "https://notify-api.line.me/api/notify"
    token = os.getenv('LINE_NOTI_TOKEN', 'NULL')
    h = {'Authorization':'Bearer ' + token}

    if int(label) == int(presult):
        r = "성공"
    else:
        r = "실패"

    msg = {
            "message" : f"{file_name} : {label} => {presult} 예측{r}"
    }

    requests.post(api, headers=h, data=msg)
    print("SEND LINE NOTI")

def run():
    """image_processing 테이블을 읽어서 가장 오래된 요청 하나씩을 처리"""
    # STEP 1
    # image_processing 테이블의 prediction_result IS NULL 인 ROW 1 개 조회 - num 가져오기 
    job = get_job_img_task()

    if job is None:
        print(f"{now()} - job is None")
        return

    num = job['num']
    file_name = job['file_name']
    file_path = job['file_path']
    label = job['label']

    # STEP 2
    # RANDOM 으로 0 ~ 9 중 하나 값을 prediction_result 컬럼에 업데이트
    # 동시에 prediction_model, prediction_time 도 업데이트
    model = os.getenv('MODEL', 'mnist240924.keras')
    presult = prediction(file_path, model, num)

    # STEP 3
    # LINE 으로 처리 결과 전송
    send_line_noti(file_name, label, presult)

    print(now())
