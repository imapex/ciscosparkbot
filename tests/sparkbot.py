import unittest
from ciscosparkbot import SparkBot
import requests_mock
from .spark_mock import MockSparkAPI


class SparkBotTests(unittest.TestCase):

    @requests_mock.mock()
    def setUp(self, m):
        m.get('https://api.ciscospark.com/v1/webhooks',
              json=MockSparkAPI.list_webhooks())
        m.post('https://api.ciscospark.com/v1/webhooks',
               json=MockSparkAPI.create_webhook())
        bot_email = "test@test.com"
        spark_token = "somefaketoken"
        bot_url = "http://fakebot.com"
        bot_app_name = "testbot"
        # Create a new bot
        bot = SparkBot(bot_app_name,
                       spark_bot_token=spark_token,
                       spark_bot_url=bot_url,
                       spark_bot_email=bot_email,
                       debug=True)

        # Add new command
        bot.add_command('/dosomething',
                        'help for do something',
                        self.do_something)
        bot.testing = True
        self.app = bot.test_client()

    def do_something(self, incoming_msg):
        """
        Sample function to do some action.
        :param incoming_msg: The incoming message object from Spark
        :return: A text or markdown based reply
        """
        return "i did what you said - {}".format(incoming_msg.text)

    @requests_mock.mock()
    def test_webhook_already_exists(self, m):
        m.get('https://api.ciscospark.com/v1/webhooks',
              json=MockSparkAPI.list_webhooks_exist())
        m.post('https://api.ciscospark.com/v1/webhooks',
               json=MockSparkAPI.create_webhook())

        bot_email = "test@test.com"
        spark_token = "somefaketoken"
        bot_url = "http://fakebot.com"
        bot_app_name = "testbot"
        # Create a new bot
        bot = SparkBot(bot_app_name,
                       spark_bot_token=spark_token,
                       spark_bot_url=bot_url,
                       spark_bot_email=bot_email,
                       debug=True)

        # Add new command
        bot.add_command('/dosomething',
                        'help for do something',
                        self.do_something)
        bot.testing = True
        self.app = bot.test_client()

    @requests_mock.mock()
    def test_spark_setup(self, m):
        m.get('https://api.ciscospark.com/v1/webhooks',
              json=MockSparkAPI.list_webhooks())
        m.post('https://api.ciscospark.com/v1/webhooks',
               json=MockSparkAPI.create_webhook())

    def test_health_endpoint(self):
        resp = self.app.get('/health')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b"I'm Alive", resp.data)

    @requests_mock.mock()
    def test_process_incoming_message_send_help(self, m):
        m.get('//api.ciscospark.com/v1/people/me', json=MockSparkAPI.me())
        m.get('//api.ciscospark.com/v1/messages/incoming_message_id',
              json=MockSparkAPI.get_message_help())
        m.post('//api.ciscospark.com/v1/messages', json={})
        resp = self.app.post('/',
                             data=MockSparkAPI.incoming_msg(),
                             content_type="application/json")
        self.assertEqual(resp.status_code, 200)
        print(resp.data)
        self.assertIn(b'I understand the following commands', resp.data)

    @requests_mock.mock()
    def test_process_incoming_message_match_command(self, m):
        m.get('//api.ciscospark.com/v1/people/me', json=MockSparkAPI.me())
        m.get('//api.ciscospark.com/v1/messages/incoming_message_id',
              json=MockSparkAPI.get_message_dosomething())
        m.post('//api.ciscospark.com/v1/messages', json={})
        resp = self.app.post('/',
                             data=MockSparkAPI.incoming_msg(),
                             content_type="application/json")
        self.assertEqual(resp.status_code, 200)
        print(resp.data)
        # self.assertIn(b'I understand the following commands', resp.data)

    @requests_mock.mock()
    def test_process_incoming_message_from_bot(self, m):
        m.get('//api.ciscospark.com/v1/people/me', json=MockSparkAPI.me())
        m.get('//api.ciscospark.com/v1/messages/incoming_message_id',
              json=MockSparkAPI.get_message_from_bot())
        m.post('//api.ciscospark.com/v1/messages', json={})
        resp = self.app.post('/',
                             data=MockSparkAPI.incoming_msg(),
                             content_type="application/json")
        self.assertEqual(resp.status_code, 200)
        print(resp.data)

    def tearDown(self):
        pass
