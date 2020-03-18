from __future__ import unicode_literals
from argparse import ArgumentParser
from common import db, handler
from flask import Flask, request, abort
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, ImageMessage, VideoMessage, FileMessage, StickerMessage
)

app = Flask(__name__)
db = db.Postgre()
handler = handler.Handler(db)


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # parse webhook body
    events = None
    try:
        events = handler.parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if isinstance(event.message, TextMessage):
            handler.handle_text_message(event)
        if isinstance(event.message, StickerMessage):
            handler.handle_sticker_message(event)
        if isinstance(event.message, ImageMessage):
            handler.handle_image_message(event)
        if isinstance(event.message, VideoMessage):
            handler.handle_video_message(event)
        if isinstance(event.message, FileMessage):
            handler.handle_file_message(event)
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue
    return 'OK'


if __name__ == "__main__":
    arg_parser = ArgumentParser(usage='Usage: python ' + __file__ + ' [--port <port>] [--help]')
    arg_parser.add_argument('-d', '--debug', default=False, help='debug')
    options = arg_parser.parse_args()
    app.run(host='0.0.0.0', debug=options.debug, port=handler.heroku_port)
