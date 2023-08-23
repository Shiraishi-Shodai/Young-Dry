# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# 必要なものをインポート

from flask import Flask
from flask import render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import requests
import os

app = Flask(__name__, template_folder="template")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
db = SQLAlchemy(app)

class Users(db.Model):
    __tablename__ = "users"
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    password = db.Column(db.String(50), nullable=False)

# dbの作成
def cre():
    db.create_all()
# 行を追加
def insert(password):
    user = Users(password=password)
    db.session.add(user)
    db.session.commit()

# 特定の行を削除
def delete_user(user_id):
    user = getUser(user_id)
    print(user)
    if user is not None:
        db.session.delete(user)
        db.session.commit()

# user_idに該当するユーザー情報を取得
def getUser(user_id):
    user = db.session.query(Users).filter_by(user_id=user_id).first()
    return user

# ログインチェック
def isLogin(user_id:str, password:str)-> bool:

# idが数字かどうか
    if user_id.isdecimal() == False:
        return False
    user = getUser(user_id)
    # データベースにユーザー情報が格納されているか
    if user is None:
        return False
        # パスワードが正しいか
    elif user.password != password:
        return False
    return True
        
# ボタンの種類
buttonObj = {
    "服の種類" : ["ハイブランド", "その他"],
    "繊維の種類" : ["ウール", "アクリル", "シルク", "麻", "ヤク", "キャメル", "モヘヤ", "アンゴラ", "ナイロン",  "ポリウレタン", "その他"],
    "色" : ["ツートーン", "その他"],
    "その他不具合" : ["ほつれ", "虫穴", "破れ", "その他",]
}

# チャット履歴
array = []

# 選択した値を格納する
choice = []
# 注意を格納
attention = []

keys = list(buttonObj.keys())
values = list(buttonObj.values())

# 次のキーと値を取得
def getNextKeyValue(target_key):
    if target_key in keys:
        target_index = keys.index(target_key)
        if target_index + 1 < len(keys):
            next_key = keys[target_index + 1]
            next_value = values[target_index + 1]
            # print("次のキー:", next_key)
            # print("次の値:", next_value)
            return next_key, next_value
        else:
            print("指定したキーの次のキーはありません")
            return "指定したキーの次のキーはありません"
    else:
        print("指定したキーが辞書に存在しません")
        return "指定したキーが辞書に存在しません"


# 回答データ
def find_answer(key, question):
    
    match key:
        case "服の種類":
            if question == "ハイブランド":
                return "ハイブランドの場合はハイクオリティをおすすめ"
            else:
                return "ハイブランドでない場合はスタンダード洗いをおすすめ"
        case "繊維の種類":
            if question in buttonObj["繊維の種類"]:
                return "基本的には洗える"
            elif question == "ポリウレタン":
                return "３年経過で劣化の可能性高い、剥離了解取れない場合洗うことは不可"
            else:
                return "回答なし"
        case "色":
            if question == "ツートーン":
                return "注意が必要、洗うことはOK。例えば、白と真っ赤といった二色の組み合わせは白へ濃い色が色移りする可能性あり"
            else:
                return "基本的には洗える"
        case "その他不具合":
            if question in buttonObj["その他不具合"]:
                return "更に広がる可能性があり、了解していただけないと洗うことは不可"
        case _:
            pass

def lineNotify(question, image):
    print('通知が行きます')
    lineNotifyToken = "nUtnR5VPF8YdNverJfbzS46bS5OvLsbsfQtbmppVgTU"
    lineNotifyAPI = "https://notify-api.line.me/api/notify"
    headers = {"Authorization": f"Bearer {lineNotifyToken}"}
    
    # print(header)
    data = {
        "message": question,
        # "image": image
        }
    
    # img_data = open("static/img/tesserat_test.png", encoding="utf-8")
    # os.chdir("static/img/")
    with open(image, "rb") as image_file:
        # print("画像タイプ" + type(image_file))
        files = {"imageFile" : image_file}
        print(f'ファイルです{files}')
    
    # print(data)
        res = requests.post(lineNotifyAPI, headers=headers,data=data, files=files)
        print(f'送信チェック:{res}')
    
@app.route('/', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        # cre()
        # insert(password="user1")
        return render_template('login.html')

    user_id = request.form["user_id"]
    password = request.form["password"]
    flag = isLogin(user_id, password)
    
    # ログイン可能ならchat画面へ、そうでないならログイン画面へ
    if flag:
        return redirect('/chat')
    else:
        return render_template("login.html", error="error")

@app.route('/chat', methods=['GET', 'POST']) #ルートからのパスを設定
def index():
    global choice, attention
    if request.method == 'GET':
        choice = []
        attention = []
        return render_template('main.html', key="服の種類", data = buttonObj["服の種類"], array=array)
    
    key = request.form["buttonType"]
    # 選択した値を取得
    question = request.form['select']
    # 選択したものを追加
    choice.append(question)
    # # quesitonをキーとし、対応する回答を取得
    answer = find_answer(key, question)
    # 注意を追加
    attention.append(question + ":" + answer)
    
    if key == "その他不具合":
        # # array配列に辞書を追加
        array.append({
            tuple(choice): attention
        })
        return redirect("/chat")
    
    key, value = getNextKeyValue(key)
    # question,answerをmain.htmlに渡し、main.htmlを表示する
    return render_template('main.html', key=key, data = value, choice=choice, attention=attention, array=array)

@app.route('/inquiry', methods=["GET", "POST"])
def inquiry():
    if request.method == "GET":
        return render_template("inquiry.html")
    
    question = request.form["question"]
    image = request.form["image"]
    print(f'リクエスト: {request}')
    print(f'fileからのでーた:{image}')
    lineNotify(question, image)
    return render_template("inquiry.html", send="send")

# Flaskで必要なもの、port=8000番
# このファイルを直接実行しているかを判断
if __name__ == '__main__':
    app.run(port=8000,debug=True) #Flaskを実行