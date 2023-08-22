from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer, ListTrainer

# チャットボット指定
bot = ChatBot(
    name='MyBot',
    tagger=MecabTagger,)

while True:
    try:
        a = input('入力してください')
        res = bot.get_response(a)
        print(f'結果: {res}')
    except(KeyboardInterrupt, EOFError, SystemError):
        break

# 訓練準備
# trainer = ChatterBotCorpusTrainer(chatbot)
# # 日本語で訓練
# trainer.train('chatterbot.corpus.japanese')
# res = chatbot.generate_response('出身はどちらですか')
# print(f'答えです{res}')