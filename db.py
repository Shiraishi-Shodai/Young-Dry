from flask import Flask
from flask import render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app2 = Flask(__name__, template_folder="template")
app2.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///chat.db'
db = SQLAlchemy(app2)

# 
class Users(db.Model):
    __tablename__ = "users"
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    password = db.Column(db.String(50), nullable=False)

# dbの作成
def cre():
    db.create_all()

def insert(password):
    user = Users(password=password)
    db.session.add(user)
    db.session.commit()

# 特定の行を削除
def delete_user(id):
    user = getUser(id)
    # print(user)
    if user is not None:
        db.session.delete(user)
        db.session.commit()

# ユーザーを取得
def getUser(user_id):
    user = db.session.query(Users).filter_by(user_id=user_id).first()
    return user

# ログインチェック
# def isLogin(user):
#     if user.
    

# このファイルを直接実行しているかを判断
if __name__ == '__main__':
    app2.run(port=8000,debug=True) #Flaskを実行