# !/usr/bin/env python3
# -*- coding:utf-8 -*-
# 必要なものをインポート

from flask import Flask, render_template, request, redirect


app = Flask(__name__, template_folder='template')   #Flaskのインスタンス化(デフォルトでmainになる)

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
                return "ハイクオリティをおすすめ"
            else:
                return "スタンダード洗いをおすすめ"
        case "繊維の種類":
            if question in ["ウール", "アクリル", "シルク", "麻", "ヤク", "キャメル", "モヘヤ", "アンゴラ", "ナイロン"]:
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
            if question in ["ほつれ", "虫穴", "破れ", "その他"]:
                return "いずれも更に広がる可能性があり、了解していただけないと洗うことは不可"
        case _:
            pass
            
        
    
#  リストを初期化する関数
def init(l: list) -> list:
    print(l)
    l = []
    print(l)
    return l

@app.route('/', methods=['GET', 'POST']) #ルートからのパスを設定
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
    # print(f'キー{key}: クエスチョン:{question}')
    # print(f'選択したもの{choice}')
    # # quesitonをキーとし、対応する回答を取得
    answer = find_answer(key, question)
    # print(answer)
    # 注意を追加
    # print(request.form["attention"])
    attention.append(question + ":" + answer)
    # print(f'注意{attention}')
    # print(answer)
    
    if key == "その他不具合":

        # # array配列に辞書を追加
        array.append({
            tuple(choice): attention
        })
        return render_template('main.html', array=array)
    
    key, value = getNextKeyValue(key)
    # question,answerをmain.htmlに渡し、main.htmlを表示する
    return render_template('main.html', key=key, data = value, choice=choice, attention=attention, array=array)

# Flaskで必要なもの、port=8000番
# このファイルを直接実行しているかを判断
if __name__ == '__main__':
    app.run(port=8000,debug=True) #Flaskを実行