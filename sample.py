import os
from ciscosparkbot import SparkBot

bot_email = os.getenv("SPARK_BOT_EMAIL")
spark_token = os.getenv("SPARK_BOT_TOKEN")
bot_url = os.getenv("SPARK_BOT_URL")
bot_app_name = os.getenv("SPARK_BOT_APP_NAME")

def do_something(incoming_msg):
    return "i did what you said - {}".format(incoming_msg.text)

bot = SparkBot(bot_app_name, spark_bot_token=spark_token,
               spark_bot_url=bot_url, spark_bot_email=bot_email, debug=True)

bot.add_command('dosomething', 'help for do something', do_something)
bot.run(host='0.0.0.0', port=5000)
