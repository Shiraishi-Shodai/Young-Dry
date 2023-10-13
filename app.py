# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# 必要なものをインポート

from flask import Flask
from flask import render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
import os
import requests

app = Flask(__name__, template_folder="template")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
app.config['SQLALCHEMY_ECHO']=True #sql文等のログを出力
# ログイン状態を管理する秘密鍵を定義
app.config["SECRET_KEY"] = os.urandom(24)
# DBを操作するためのインスタンスを生成し、dbに格納
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String(50), nullable=True, unique=True) #null,重複を許可しない
    password = db.Column(db.String(25))
    
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
    
    files = {"imageFile" : image}
    print(f'ファイルです{files}')

# print(data)
    res = requests.post(lineNotifyAPI, headers=headers,data=data, files=files)
    print(f'送信チェック:{res}')

@login_manager.user_loader
def load_user(id):
    user = User.query.filter_by(id=id).first()
    return user
    
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User(username=username, password=generate_password_hash(password, method="sha256"))        
        db.session.add(user)
        db.session.commit()
        return redirect("/login")
    else:
        return render_template("signup.html")

@app.route("/login", methods=["POST", "GET"])
def login():
        if request.method == "POST":
            username = request.form["username"]
            password = request.form["password"]
            user = User.query.filter_by(username=username).first()

            if check_password_hash(user.password, password):
                login_user(user)
                return redirect("/chat")
            else:
                return redirect("/")
        else:
            return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return render_template("logout.html")

@app.route('/chat', methods=['GET', 'POST']) #ルートからのパスを設定
@login_required
def chat():
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
@login_required
def inquiry():
    if request.method == "GET":
        return render_template("inquiry.html")
    question = request.form["question"]
    print(f'クエスチョン: {question}')
    image = request.files["image"]
    print(f'fileからのデータ:{image}')
    lineNotify(question, image)
    return render_template("inquiry.html", send="send")

@login_manager.unauthorized_handler
def unauthorized():
    return redirect("/")

# Flaskで必要なもの、port=8000番
# このファイルを直接実行しているかを判断
if __name__ == '__main__':
    app.run(port=8000,debug=True) #Flaskを実行