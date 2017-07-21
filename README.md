# ciscosparkbot

A flask based Bot for Cisco spark

# Prerequisites

If you don't already have a Cisco Spark account, go ahead and register for one.  They are free.
You'll need to start by adding your bot to the Cisco Spark website.

[https://developer.ciscospark.com/add-app.html](https://developer.ciscospark.com/add-app.html)

![add-app](images/newapp.png)

1. Click create bot

![add-bot](images/newbot.png)

2. Fill out all the details about your bot, including a publicly hosted avatar image.  A sample avatar is available at [http://cs.co/devnetlogosq](http://cs.co/devnetlogosq).

![enter-details](images/enterdetails.png)

3. Click "Add Bot", make sure to copy your access token, you will need this in a second

![copy-token](images/copytoken.png)

# Installation

Create a virtualenv and install the module

```
virtualenv venv
source venv/bin/activate
pip install ciscosparkbot
```

# Usage

The easiest way to use this module is to set a few environment variables

```
export SPARK_BOT_URL=https://mypublicsite.io
export SPARK_BOT_TOKEN=<your bots token>
export SPARK_BOT_EMAIL=<your bots email?
export SPARK_BOT_APP_NAME=<your bots name>
```

A [sample script](sample.py) is also provided for your convenience

```
# -*- coding: utf-8 -*-
"""
Sample code for using ciscosparkbot
"""

import os
from ciscosparkbot import SparkBot

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

# Create a new bot
bot = SparkBot(bot_app_name, spark_bot_token=spark_token,
               spark_bot_url=bot_url, spark_bot_email=bot_email, debug=True)

# Add new command
bot.add_command('/dosomething', 'help for do something', do_something)

# Run Bot
bot.run(host='0.0.0.0', port=5000)
```

# ngrok

ngrok will make easy for you to develop your code with a live bot.

You can find installation instructions here: https://ngrok.com/download

After you've installed ngrok, in another window start the service


`ngrok http 5000`


You should see a screen that looks like this:

```
ngrok by @inconshreveable                                                                                                                                 (Ctrl+C to quit)

Session Status                online
Version                       2.2.4
Region                        United States (us)
Web Interface                 http://127.0.0.1:4040
Forwarding                    http://this.is.the.url.you.need -> localhost:5000
Forwarding                    https://this.is.the.url.you.need -> localhost:5000

Connections                   ttl     opn     rt1     rt5     p50     p90
                              2       0       0.00    0.00    0.77    1.16

HTTP Requests
-------------

POST /                         200 OK
```

Make sure and update your environment with this url:

```
export SPARK_BOT_URL=https://this.is.the.url.you.need

```

Now launch your bot!!


```
python sample.py
```