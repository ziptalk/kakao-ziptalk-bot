# server.py
from flask import Flask, request, jsonify
import sys
app = Flask(__name__)


@app.route('/keyboard')
def Keyboard():
    dataSend = {
    "Subject":"OSSP",
    "user":"corona_chatbot"
    }
    return jsonify(dataSend)

@app.route('/message', methods=['POST'])
def Message():

    content = request.get_json()
    content = content['userRequest']
    content = content['utterance']

    # if content == u"안녕":
    #     dataSend = {
    #         "version": "2.0",
    #         "template": {
    #             "outputs": [
    #                 {
    #                     "carousel": {
    #                         "type" : "basicCard",
    #                         "items": [
    #                             {
    #                                 "title" : "",
    #                                 "description" : "안녕하세요"
    #                             }
    #                         ]
    #                     }
    #                 }
    #             ]
    #         }
    #     }

    if content == u"시작하기":
        dataSend = {
            "message": {
                "text": "아직 개발중이라 대답을 잘 못해도 이해해줘^^;"
            }
        }
    elif content == u"도움말":
        dataSend = {
            "message": {
                "text": "이제 곧 정식 버전이 출시될거야. 조금만 기다려~~~"
            }
        }
    elif u"안녕" in content:
        dataSend = {
            "message": {
                "text": "안녕~~ 반가워 ㅎㅎ"
            }
        }
    else:
        dataSend = {
            "message": {
                "text": "나랑 놀자 ㅋㅋㅋ"
            }
        }

    return jsonify(dataSend)

if __name__ == "__main__":
    app.run(host='0.0.0.0') # Flask 기본포트 5000번