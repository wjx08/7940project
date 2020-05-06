from __future__ import unicode_literals

import os
import sys
import redis

from argparse import ArgumentParser

from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    StickerMessage, StickerSendMessage
)

line_bot_api = LineBotApi('YUjOvrDZuw02TYxulA+z6jTfJ7pA5b5ipfDq8SqsZPuhUUgg7ageSBJ8B5zDaX7vfbqvbYbAfJqyivvYT5+jRI5Fmm4wSBr1IELF51fCRnaO1v4UOW6JInh6b6/sXVQ2xCkfNbKJ/2gZA15tYGca2AdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('2d3c68deba21ecdfdbf452f64b69cc32')

app = Flask(__name__)

from linebot.utils import PY3

words = ''
save = False

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)

# obtain the port that heroku assigned to this app.
heroku_port = os.getenv('PORT', None)

if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)


@app.route('/')
def index():
    return 'Welcome to Line Bot!'

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global words
    global save

    _id = event.source.user_id
    profile = line_bot_api.get_profile(_id) 
    
    _name = profile.display_name
    print("大頭貼：", profile.picture_url)
    print("狀態消息：", profile.status_message)

    txt=event.message.text

    if (txt=='Hi') or (txt=="你好"):
        reply = f'{_name}Hi！正值疫情期間，希望你能保重身體，注意健康。多通風，勤洗手。'
    elif '日記本' in txt:
        if words != '':
            reply = f'你的悄悄話是：\n\n{words}'
        else:
            reply = '今天過得怎麽樣呢？'
            save = True
    elif save:
        words = txt
        save = False
        reply = '日記本上鎖！我會好好幫你保存的！'
    else:
        reply = txt

    msg = TextSendMessage(reply)
    line_bot_api.reply_message(event.reply_token, msg)

@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        StickerSendMessage(
            package_id=event.message.package_id, 
            sticker_id=event.message.sticker_id)
    )

if __name__ == "__main__":
    arg_parser = ArgumentParser(
        usage='Usage: python ' + __file__ + ' [--port <port>] [--help]'
    )
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()

    app.run(host='0.0.0.0', debug=options.debug, port=heroku_port)
