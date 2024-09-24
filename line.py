import os
import requests

def send_line_noti(file_name, presult):
    api = "https://notify-api.line.me/api/notify"
    token = os.getenv('LINE_NOTI_TOKEN', 'NULL')
    h = {'Authorization':'Bearer ' + 'C5bEOM560c3dqyXYlrBkJEGIgR9gqhUmOc0wVsnpvBK'}
    msg = {
       "message" : f"{file_name} => {presult}"
    }
    requests.post(api, headers=h , data=msg)
    print("SEND LINE NOTI")

send_line_noti("file", "result")
