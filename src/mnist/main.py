from typing import Annotated
from fastapi import FastAPI, File, UploadFile
from rightnow.time import now
from mnist.db import get_conn, select, dml
import pymysql
import uuid
import os

app = FastAPI()

@app.post("/files/")
async def file_list():
    conn = get_conn()

    with conn:
        with conn.cursor() as cursor:
            sql = "SELECT * FROM image_processing WHERE prediction_time IS NULL ORDER BY num"
            cursor.execute(sql)
            result = cursor.fetchall()
        
    return result

@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile, label: Annotated[str, Form()]):
    # 파일 저장
    img = await file.read()
    file_name = file.filename
    file_ext = file.content_type.split('/')[-1]

    upload_dir = os.getenv('UPLOAD_DIR', '/home/j25ng/code/mnist/img')
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    file_full_path = os.path.join(upload_dir,
            f"{uuid.uuid4()}.{file_ext}")

    with open(file_full_path, 'wb') as f:
        f.write(img)

    # 파일 저장 경로 DB INSERT
    # tablename : image_processing
    # 컬럼 정보 : num (초기 인서트, 자동 증가)
    # 컬럼 정보 : 파일이름, 파일경로, 요청시간(초기 인서트), 요청 사용자
    # 컬럼 정보 : 예측모델, 예측결과, 예측시간(추후 업데이트)
    sql = "INSERT INTO image_processing(file_name, file_path, label, request_time, request_user) VALUES(%s, %s, %s, %s, %s)"

    insert_row = dml(sql, file_name, file_full_path, label, now(), 'n16')

    return {
            "filename": file.filename,
            "content_type": file.content_type,
            "file_full_path": file_full_path,
            "insert_row_cont": insert_row
            }

@app.get("/all")
def all():
    sql = "SELECT * FROM image_processing"
    result = select(query=sql, size=-1)
    return result

@app.get("/one")
def one():
    sql = """SELECT * FROM image_processing 
    WHERE prediction_time IS NULL ORDER BY num LIMIT 1"""
    result = select(query=sql, size=1)
    return result

@app.get("/many/")
def many(size: int = -1):
    sql = "SELECT * FROM image_processing WHERE prediction_time IS NULL ORDER BY num"
    result = select(sql, size)

    return result
