from flask import Flask, request, jsonify
from ciscosparkapi import CiscoSparkAPI
from ciscosparkapi.exceptions import ciscosparkapiException
import os
import sys
import json


class Bot(object):
    pass


class SparkBot(Flask):

    def __init__(self, spark_bot_name, spark_bot_token=None,
                 spark_bot_email=None, spark_bot_url=None, debug=False):

        super(SparkBot, self).__init__(spark_bot_name)

        if None in (spark_bot_name, spark_bot_token, spark_bot_email, spark_bot_token):
            raise ValueError("SparkBot requires spark_bot_name, spark_bot_token, spark_bot_email, spark_bot_url!!!")
        self.DEBUG = debug
        self.spark_bot_name = spark_bot_name
        self.spark_bot_token = spark_bot_token
        self.spark_bot_email = spark_bot_email
        self.spark_bot_url = spark_bot_url

        self.spark = CiscoSparkAPI(access_token=spark_bot_token)

        # A dictionary of commands this bot listens to
        # Each key in the dictionary is a command, with associated help text and callback function
        self.commands = {"/echo":
                             {"help": "Reply back with the same message sent.",
                              "callback": self.send_echo},
                         "/help":
                             {"help": "Get help.",
                              "callback": self.send_help}
                         }

        # Urls, see SparkBot.add_command
        self.add_url_rule('/health', 'health', self.health)
        self.add_url_rule('/config', 'config', self.config_bot)
        self.add_url_rule('/', 'index', self.process_incoming_message, methods=['POST'])
        self.spark_setup(self.spark_bot_email, self.spark_bot_token)

    def add_command(self, command, help, callback):
        """
        add a command to this bot
        :return:
        """
        self.commands[command] = {"help": help, "callback": callback}

    # Not strictly needed for most bots, but this allows for requests to be sent
    def after_request(self, response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,Key')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')
        return response

    # Entry point for Spark Webhooks
    def process_webhook(self):
        if self.DEBUG:
            sys.stderr.write(request)
        # Check if the Spark connection has been made
        if self.spark is None:
            sys.stderr.write("Bot not ready.  \n")
            return "Spark Bot not ready.  "

        post_data = request.get_json(force=True)
        if self.DEBUG:
            sys.stderr.write("Webhook content:" + "\n")
            sys.stderr.write(str(post_data) + "\n")

        # Take the posted data and send to the processing function
        msg = self.process_incoming_message(post_data)
        return jsonify({"message": msg})

    def config_bot(self):
        if request.method == "POST":
            post_data = request.get_json(force=True)
            # Verify that a token and email were both provided
            if "SPARK_BOT_TOKEN" not in post_data.keys() or "SPARK_BOT_EMAIL" not in post_data.keys():
                return "Error: POST Requires both 'SPARK_BOT_TOKEN' and 'SPARK_BOT_EMAIL' to be provided."

            # Setup Spark
            self.spark_setup(post_data["SPARK_BOT_EMAIL"], post_data["SPARK_BOT_TOKEN"])

        # Return the config detail to API requests
        config_data = dict(SPARK_BOT_EMAIL=self.spark_bot_email,
                           SPARK_BOT_TOKEN="nice try!",
                           SPARK_BOT_URL=self.spark_bot_url,
                           SPARK_BOT_NAME=self.spark_bot_name)

        return json.dumps(config_data)

    # Quick REST API to have bots send a message to a user
    def message_email(self, email):
        """
        Kickoff a 1 on 1 chat with a given email
        :param email:
        :return:
        """
        # Check if the Spark connection has been made
        if self.spark is None:
            sys.stderr.write("Bot not ready.  \n")
            return "Spark Bot not ready.  "

        # send_message_to_email(email, "Hello!")
        self.spark.messages.create(toPersonEmail=email, markdown="Hello!")
        return "Message sent to " + email
        self.route

    def setup_webhook(self, name, targeturl):
        # Get a list of current webhooks
        webhooks = spark.webhooks.list()

        # Look for a Webhook for this bot_name
        # Need try block because if there are NO webhooks it throws an error

        webhook = None
        wh = None
        # webhooks is a generator
        for h in webhooks:
            if h.name == name:
                sys.stderr.write("Found existing webhook.  Updating it.\n")
                wh = h

        if wh is None:
        # we reached the end of the generator w/o finding a matching webhook
            sys.stderr.write("Creating new webhook.\n")
            wh = spark.webhooks.create(name=name, targetUrl=targeturl, resource="messages", event="created")

        # if we have an existing webhook update it, here is a better place to worry about exceptions
        else:
            try:
                wh = spark.webhooks.update(webhookId=wh.id, name=name, targetUrl=targeturl)

            # https://github.com/CiscoDevNet/ciscosparkapi/blob/master/ciscosparkapi/api/webhooks.py#L237
            except Exception as e:
                sys.stderr.write("Encountered an error updating webhook: {}".format(e))

        return wh

    def process_incoming_message(self):
        post_data = request.json
        # Determine the Spark Room to send reply to
        room_id = post_data["data"]["roomId"]

        # Get the details about the message that was sent.
        message_id = post_data["data"]["id"]
        message = self.spark.messages.get(message_id)
        if self.DEBUG:
            sys.stderr.write("Message content:" + "\n")
            sys.stderr.write(str(message) + "\n")

        # First make sure not processing a message from the bots
        if message.personEmail in self.spark.people.me().emails:
            if self.DEBUG:
                sys.stderr.write("Ignoring message from ourself" + "\n")
            return ""

        # Log details on message
        sys.stderr.write("Message from: " + message.personEmail + "\n")

        # Find the command that was sent, if any
        command = ""
        for c in self.commands.items():
            if message.text.find(c[0]) != -1:
                command = c[0]
                sys.stderr.write("Found command: " + command + "\n")
                # If a command was found, stop looking for others
                break

        reply = ""
        # Take action based on command
        # If no command found, send help
        if command in ["", "/help"]:
            reply = self.send_help(post_data)
        elif command in ["/echo"]:
            reply = self.send_echo(message)
        else:
            reply = self.commands[command]["callback"](message)

        # send_message_to_room(room_id, reply)
        self.spark.messages.create(roomId=room_id, markdown=reply)
        return reply

    def health(self):
        return "I'm Alive"

    # Sample command function that just echos back the sent message
    def send_echo(self, incoming):
        # Get sent message
        message = self.extract_message("/echo", incoming.text)
        return message

    # Construct a help message for users.
    def send_help(self, post_data):
        message = "Hello!  "
        message = message + "I understand the following commands:  \n"
        for c in self.commands.items():
            message = message + "* **%s**: %s \n" % (c[0], c[1]["help"])
        return message

    # Return contents following a given command
    def extract_message(self, command, text):
        cmd_loc = text.find(command)
        message = text[cmd_loc + len(command):]
        return message

    # Setup the Spark connection and WebHook
    def spark_setup(self, email, token):
        # Update the global variables for config details
        globals()["spark_token"] = self.spark_bot_token
        globals()["bot_email"] = self.spark_bot_email

        sys.stderr.write("Spark Bot Email: " + bot_email + "\n")
        sys.stderr.write("Spark Token: REDACTED\n")

        # Setup the Spark Connection
        globals()["spark"] = CiscoSparkAPI(access_token=self.spark_bot_token)
        globals()["webhook"] = self.setup_webhook(self.spark_bot_name, self.spark_bot_url)
        sys.stderr.write("Configuring Webhook. \n")
        sys.stderr.write("Webhook ID: " + globals()["webhook"].id + "\n")


if __name__ == '__main__':
    # Entry point for bots
    # Retrieve needed details from environment for the bots
    bot_email = os.getenv("SPARK_BOT_EMAIL")
    spark_token = os.getenv("SPARK_BOT_TOKEN")
    bot_url = os.getenv("SPARK_BOT_URL")
    bot_app_name = os.getenv("SPARK_BOT_APP_NAME")

    # bot_url and bot_app_name must come in from Environment Variables
    if bot_url is None or bot_app_name is None:
            sys.exit("Missing required argument.  Must set 'SPARK_BOT_URL' and 'SPARK_BOT_APP_NAME' in ENV.")

    # Write the details out to the console
    sys.stderr.write("Spark Bot URL (for webhook): " + bot_url + "\n")
    sys.stderr.write("Spark Bot App Name: " + bot_app_name + "\n")

    # Placeholder variables for spark connection objects
    spark = None
    webhook = None

    # Check if the token and email were set in ENV - TODO move this up to validate earlier
    bot = SparkBot(bot_app_name, spark_bot_token=spark_token,
                   spark_bot_url=bot_url, spark_bot_email=bot_email)



    bot.run(host='0.0.0.0', port=5000)
