from __future__ import unicode_literals

import os
import sys
from argparse import ArgumentParser

import psycopg2
from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookParser
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, ImageMessage, VideoMessage, FileMessage, StickerMessage,
    StickerSendMessage
)


class Postgre:
    conn = None
    cur = None

    def __init__(self):
        self.conn = psycopg2.connect(database="d1774sms9m8gp5", user="hmrdcrywqbdvqj",
                                     password="f1219187293d8e10e69ee806cf6012787a696fb3539e0976db9f664db7112d38",
                                     host="ec2-23-22-156-110.compute-1.amazonaws.com", port="5432")
        self.cur = self.conn.cursor()

    def query(self, sql, params=None):
        res = None
        try:
            self.cur.execute(sql, params)
            res = self.cur.fetchall()
        except Exception:
            print("error happened when query")
        return res

    def close(self):
        self.cur.close()
        self.conn.close()


class App:
    app = None

    def __init__(self):
        self.app = Flask(__name__)
        self.db = Postgre()
        # get channel_secret and channel_access_token from your environment variable
        channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
        channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
        database_url = os.getenv('DATABASE_URL', None)

        # obtain the port that heroku assigned to this app.
        self.heroku_port = os.getenv('PORT', None)
        if channel_secret is None:
            print('Specify LINE_CHANNEL_SECRET as environment variable.')
            sys.exit(1)
        if channel_access_token is None:
            print('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
            sys.exit(1)
        if database_url is None:
            print('Specify DATABASE_URL as environment variable.')
            sys.exit(1)
        self.line_bot_api = LineBotApi(channel_access_token)
        self.parser = WebhookParser(channel_secret)

    @app.route("/callback", methods=['POST'])
    def callback(self):
        signature = request.headers['X-Line-Signature']

        # get request body as text
        body = request.get_data(as_text=True)
        self.app.logger.info("Request body: " + body)

        # parse webhook body
        events = None
        try:
            events = self.parser.parse(body, signature)
        except InvalidSignatureError:
            abort(400)

        # if event is MessageEvent and message is TextMessage, then echo text
        for event in events:
            if not isinstance(event, MessageEvent):
                continue
            if isinstance(event.message, TextMessage):
                self.handle_text_message(event)
            if isinstance(event.message, StickerMessage):
                self.handle_sticker_message(event)
            if isinstance(event.message, ImageMessage):
                self.handle_image_message(event)
            if isinstance(event.message, VideoMessage):
                self.handle_video_message(event)
            if isinstance(event.message, FileMessage):
                self.handle_file_message(event)

            if not isinstance(event, MessageEvent):
                continue
            if not isinstance(event.message, TextMessage):
                continue

        return 'OK'

    # Handler function for Text Message
    def handle_text_message(self, event):
        # print(event.message.text)
        # msg = 'You said: "' + event.message.text + '" '
        msg = self.db.query("SELECT confirmedcases FROM region WHERE rname = 'event'")
        if msg is not None:
            self.line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="The number of confirmed cases in this city is" + msg)
            )
        else:
            self.line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="You may enter another region.")
            )

    # Handler function for Sticker Message
    def handle_sticker_message(self, event):
        self.line_bot_api.reply_message(
            event.reply_token,
            StickerSendMessage(
                package_id=event.message.package_id,
                sticker_id=event.message.sticker_id)
        )

    # Handler function for Image Message
    def handle_image_message(self, event):
        self.line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="Nice image!")
        )

    # Handler function for Video Message
    def handle_video_message(self, event):
        self.line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="Nice video!")
        )

    # Handler function for File Message
    def handle_file_message(self, event):
        self.line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="Nice file!")
        )


if __name__ == "__main__":
    arg_parser = ArgumentParser(usage='Usage: python ' + __file__ + ' [--port <port>] [--help]')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()
    line_bot = App()
    line_bot.app.run(host='0.0.0.0', debug=options.debug, port=line_bot.heroku_port)
