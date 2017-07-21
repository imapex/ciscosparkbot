# -*- coding: utf-8 -*-
"""
Cisco Spark Bot Class

Classes:
    SparkBot: Built from a Flask application, provides an easy to instantiate
        instance of a Spark Bot.  Handles requisite webhook registration and setup.
"""

from flask import Flask, request, jsonify
from ciscosparkapi import CiscoSparkAPI
from ciscosparkapi.exceptions import ciscosparkapiException
import os
import sys
import json

__author__ = "imapex"
__author_email__ = "CiscoSparkBot@imapex.io"
__copyright__ = "Copyright (c) 2016 Cisco Systems, Inc."
__license__ = "Apache 2.0"


class SparkBot(Flask):
    """An instance of a Cisco Spark Bot"""

    def __init__(self, spark_bot_name, spark_bot_token=None,
                 spark_bot_email=None, spark_bot_url=None, default_action="/help", debug=False):
        """
        Initialize a new SparkBot

        :param spark_bot_name: Friendly name for this Bot.  Used to register WebHook
        :param spark_bot_token: Spark Auth Token for Bot Account
        :param spark_bot_email: Spark Bot Email Address
        :param spark_bot_url: WebHook URL for this Bot
        :param default_action: What action to take if no command found. Defaults to /help
        :param debug: boolean value for debut messages
        """

        super(SparkBot, self).__init__(spark_bot_name)

        # Verify required parameters provided
        if None in (spark_bot_name, spark_bot_token, spark_bot_email, spark_bot_token):
            raise ValueError("SparkBot requires spark_bot_name, spark_bot_token, spark_bot_email, spark_bot_url!!!")

        self.DEBUG = debug
        self.spark_bot_name = spark_bot_name
        self.spark_bot_token = spark_bot_token
        self.spark_bot_email = spark_bot_email
        self.spark_bot_url = spark_bot_url
        self.default_action = default_action

        # Create Spark API Object for interacting with Spark
        self.spark = CiscoSparkAPI(access_token=spark_bot_token)

        # A dictionary of commands this bot listens to
        # Each key in the dictionary is a command, with associated help text and callback function
        # By default supports 2 command, /echo and /help
        self.commands = {"/echo":
                             {"help": "Reply back with the same message sent.",
                              "callback": self.send_echo},
                         "/help":
                             {"help": "Get help.",
                              "callback": self.send_help}
                         }

        # Flask Application URLs
        self.add_url_rule('/health', 'health', self.health)   # Basic Health Check for Flask Application
        self.add_url_rule('/config', 'config', self.config_bot)   # Endpoint to enable dynamically configuring account
        self.add_url_rule('/', 'index', self.process_incoming_message, methods=['POST'])   # Spark WebHook Target

        # Setup the Spark WebHook and connections.
        self.spark_setup()

    # *** Bot Setup and Core Processing Functions

    def spark_setup(self):
        """
        Setup the Spark Connection and WebHook
        :return:
        """
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

    # noinspection PyMethodMayBeStatic
    def setup_webhook(self, name, targeturl):
        """
        Setup Spark WebHook to send incoming messages to this bot.
        :param name: Name of the WebHook
        :param targeturl: Target URL for WebHook
        :return: WebHook
        """
        # Get a list of current webhooks
        webhooks = spark.webhooks.list()

        # Look for an Existing Webhook with this name, if found update it
        wh = None
        # webhooks is a generator
        for h in webhooks:
            if h.name == name:
                sys.stderr.write("Found existing webhook.  Updating it.\n")
                wh = h

        # No existing webhook found, create new one
        # we reached the end of the generator w/o finding a matching webhook
        if wh is None:
            sys.stderr.write("Creating new webhook.\n")
            wh = spark.webhooks.create(name=name, targetUrl=targeturl, resource="messages", event="created")

        # if we have an existing webhook update it
        else:
            # Need try block because if there are NO webhooks it throws an error
            try:
                wh = spark.webhooks.update(webhookId=wh.id, name=name, targetUrl=targeturl)
                # https://github.com/CiscoDevNet/ciscosparkapi/blob/master/ciscosparkapi/api/webhooks.py#L237
            except Exception as e:
                sys.stderr.write("Encountered an error updating webhook: {}".format(e))

        return wh

    # ToDo - fix the "POST" method to allow reconfigure
    def config_bot(self):
        """
        Method to check and change the Bot Token and Email on the fly.
        :return: Configuration Data for Bot
        """
        # if request.method == "POST":
        #     post_data = request.get_json(force=True)
        #     # Verify that a token and email were both provided
        #     if "SPARK_BOT_TOKEN" not in post_data.keys() or "SPARK_BOT_EMAIL" not in post_data.keys():
        #         return "Error: POST Requires both 'SPARK_BOT_TOKEN' and 'SPARK_BOT_EMAIL' to be provided."
        #
        #     # Setup Spark
        #     self.spark_setup(post_data["SPARK_BOT_EMAIL"], post_data["SPARK_BOT_TOKEN"])

        # Return the config detail to API requests
        config_data = dict(SPARK_BOT_EMAIL=self.spark_bot_email,
                           SPARK_BOT_TOKEN="--Redacted--",
                           SPARK_BOT_URL=self.spark_bot_url,
                           SPARK_BOT_NAME=self.spark_bot_name)

        return json.dumps(config_data)

    def process_webhook(self):
        """
        Main entry point for incoming WebHooks
        :return: Message reply to send
        """

        if self.DEBUG:
            sys.stderr.write(request)
        # Check if the Spark connection has been made
        if self.spark is None:
            sys.stderr.write("Bot not ready.  \n")
            return "Spark Bot not ready.  "

        # Retrieve contents of the WebHook
        post_data = request.get_json(force=True)
        if self.DEBUG:
            sys.stderr.write("Webhook content:" + "\n")
            sys.stderr.write(str(post_data) + "\n")

        # Take the posted data and send to the processing function
        msg = self.process_incoming_message()
        return jsonify({"message": msg})

    # Not strictly needed for most bots, but this allows for requests to be sent
    def after_request(self, response):
        """
        Add additional headers for API
        :param response:
        :return:
        """
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,Key')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')
        return response

    # noinspection PyMethodMayBeStatic
    def health(self):
        """
        Flask App Health Check to verify Web App is up.
        :return:
        """
        return "I'm Alive"

    def process_incoming_message(self):
        """
        Process an incoming message, determine the command and action,
        and determine reply.
        :return:
        """

        # Get the webhook data
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
        # Needed to avoid the bot talking to itself
        if message.personEmail in self.spark.people.me().emails:
            if self.DEBUG:
                sys.stderr.write("Ignoring message from our self" + "\n")
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

        # Build the reply to the user
        reply = ""

        # Take action based on command
        # If no command found, send the default_action
        if command in [""] and self.default_action:
            # noinspection PyCallingNonCallable
            reply = self.commands[self.default_action]["callback"](message)
        elif command in self.commands.keys():
            # noinspection PyCallingNonCallable
            reply = self.commands[command]["callback"](message)
        else:
            pass

        # send_message_to_room(room_id, reply)
        if reply:
            self.spark.messages.create(roomId=room_id, markdown=reply)
        return reply

    def add_command(self, command, help_message, callback):
        """
        Add a new command to the bot
        :param command: The command string, example "/status"
        :param help_message: A Help string for this command
        :param callback: The function to run when this command is given
        :return:
        """
        self.commands[command] = {"help": help_message, "callback": callback}

    # noinspection PyMethodMayBeStatic
    def extract_message(self, command, text):
        """
        Return message contents following a given command.
        :param command: Command to search for.  Example "/echo"
        :param text: text to search within.
        :return:
        """
        cmd_loc = text.find(command)
        message = text[cmd_loc + len(command):]
        return message

    # *** Default Commands included in Bot

    def send_help(self, post_data):
        """
        Construct a help message for users.
        :param post_data:
        :return:
        """
        message = "Hello!  "
        message += "I understand the following commands:  \n"
        for c in self.commands.items():
            message += "* **%s**: %s \n" % (c[0], c[1]["help"])
        return message

    def send_echo(self, post_data):
        """
        Sample command function that just echos back the sent message
        :param post_data:
        :return:
        """
        # Get sent message
        message = self.extract_message("/echo", post_data.text)
        return message

        # def message_email(self, email):
        #     """
        #     Kickoff a 1 on 1 chat with a given email
        #     :param email:
        #     :return:
        #     """
        #     # Check if the Spark connection has been made
        #     if self.spark is None:
        #         sys.stderr.write("Bot not ready.  \n")
        #         return "Spark Bot not ready.  "
        #
        #     # send_message_to_email(email, "Hello!")
        #     self.spark.messages.create(toPersonEmail=email, markdown="Hello!")
        #     return "Message sent to " + email
        #     self.route


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
