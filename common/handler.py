import os, sys

from linebot import LineBotApi, WebhookParser

from linebot.models import TextSendMessage, StickerSendMessage


class Handler:
    def __init__(self, db):
        self.db = db
        # get channel_secret and channel_access_token from your environment variable
        channel_secret = os.getenv('LINE_CHANNEL_SECRET', '2d3c68deba21ecdfdbf452f64b69cc32')
        channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', 'YUjOvrDZuw02TYxulA+z6jTfJ7pA5b5ipfDq8SqsZPuhUUgg7ageSBJ8B5zDaX7vfbqvbYbAfJqyivvYT5+jRI5Fmm4wSBr1IELF51fCRnaO1v4UOW6JInh6b6/sXVQ2xCkfNbKJ/2gZA15tYGca2AdB04t89/1O/w1cDnyilFU=')
        database_url = os.getenv('DATABASE_URL', 'postgres://hmrdcrywqbdvqj:f1219187293d8e10e69ee806cf6012787a696fb3539e0976db9f664db7112d38@ec2-23-22-156-110.compute-1.amazonaws.com:5432/d1774sms9m8gp5')

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
