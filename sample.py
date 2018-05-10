# -*- coding: utf-8 -*-
"""
Sample code for using ciscosparkbot
"""
import os
from ciscosparkbot import SparkBot
from ciscosparkbot.models import Response

__author__ = "imapex"
__author_email__ = "CiscoSparkBot@imapex.io"
__copyright__ = "Copyright (c) 2016 Cisco Systems, Inc."
__license__ = "Apache 2.0"

# Retrieve required details from environment variables
bot_email = os.getenv("SPARK_BOT_EMAIL")
spark_token = os.getenv("SPARK_BOT_TOKEN")
bot_url = os.getenv("SPARK_BOT_URL")
bot_app_name = os.getenv("SPARK_BOT_APP_NAME")


def do_something(incoming_msg):
    """
    Sample function to do some action.
    :param incoming_msg: The incoming message object from Spark
    :return: A text or markdown based reply
    """
    return "i did what you said - {}".format(incoming_msg.text)


def ret_message(incoming_msg):
    m = Response()
    u = 'https://sayingimages.com/wp-content/uploads/'
    u = u + 'aaaaaalll-righty-then-alrighty-meme.jpg'
    m.files = u
    return m


# Create a new bot
bot = SparkBot(bot_app_name, spark_bot_token=spark_token,
               spark_bot_url=bot_url, spark_bot_email=bot_email, debug=True)


# Add new command
bot.add_command('/dosomething', 'help for do something', do_something)
bot.add_command('/demo', 'sampel that allows spark message to be returned',
                ret_message)

# Run Bot
bot.run(host='0.0.0.0', port=5000)
