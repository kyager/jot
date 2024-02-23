#!/usr/bin/python3

"""
This script provides an CLI interface for interacting with the OpenAI API.
"""
import os
import configparser
import json
import socket
import time
import logging
import argparse
from datetime import datetime
from openai import OpenAI

NOW = datetime.now()
FINAL_MESSAGE = None
NAME = socket.gethostname()

PARSER = argparse.ArgumentParser()
PARSER.add_argument("-q", "--query", help = "Sends a query the assistant.")
PARSER.add_argument("-f", "--file", help = "Attaches a file to your assistant.")
PARSER.add_argument("-i", "--instructions", help = "Updates your assistants instructions.")
PARSER.add_argument(
    "-t",
    "--template",
    help = "Specifies a custom template for your queries",
    default = "message"
)

config = configparser.ConfigParser()
config.read(os.path.expanduser("~/.jot"))
if "settings" not in config.keys():
    config.add_section("settings")

logging.basicConfig(
    filename=os.path.expanduser(config["logging"]["path"]),
    encoding='utf-8',
    level=config["logging"]["level"]
    )

def save_config():
    """Saves the open configuration file"""
    with open(os.path.expanduser("~/.jot"), "w", encoding="utf-8") as configfile:
        config.write(configfile)

def get_or_create_assistant():
    """Checks the config for an assistant id, and creates one if not.

    Returns:
        string:assistant_id

   """
    if "assistant_id" not in config["settings"]:
        assistant = client.beta.assistants.create(
            name=NAME,
            model=config.get("settings", "model"),
            instructions=config.get("settings", "instructions"),
        )
        config["settings"]["assistant_id"] = assistant.id
        logging.info(assistant)
        save_config()

    return config["settings"]["assistant_id"]


def get_or_create_thread():
    """Checks the config for an thread id, and creates one if not.

    Returns:
    string:thread_id

   """
    if "thread_id" not in config["settings"]:
        thread = client.beta.threads.create()
        config["settings"]["thread_id"] = thread.id
        save_config()

    return config["settings"]["thread_id"]

def attach_file(file):
    """Uploads a file and attaches it to your current assistant"""
    created_file = client.files.create(
        file=file,
        purpose="assistants"
    )

    logging.debug(created_file)

    assistant_file = client.beta.assistants.files.create(
        assistant_id=get_or_create_assistant(),
        file_id=created_file.id
    )

    logging.info(assistant_file)

    return assistant_file

def personalize(content):
    """Wraps the content in a personality prompt for fun"""
    return f"Respond in the personality of a {config['settings']['personality']}: {content}"

def send_message(content, template, interval = 1):
    """Builds a message and then sends it to the assistant, then checks at the specified
    interval for a response.
    """
    thread_id = get_or_create_thread()
    assistant_id = get_or_create_assistant()

    if template == "message":
        templated_content = personalize(content)
    elif template == "note":
        templated_content = json.dumps([{
            'type':'note',
            'datetime':str(NOW),
            'content': content
        }])
    else:
        templated_content = content

    built_message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=templated_content,
    )

    message_run = client.beta.threads.runs.create(
        thread_id=built_message.thread_id, assistant_id=assistant_id
    )

    while True:
        this_run = client.beta.threads.runs.retrieve(
            thread_id=message_run.thread_id, run_id=message_run.id
        )

        if this_run.status == "completed":
            this_message = client.beta.threads.messages.list(
                thread_id=message_run.thread_id,
                limit=1
            )
            logging.debug(this_run)
            break

        time.sleep(interval)

    logging.debug(this_message)
    logging.info(this_message.data[0].content[0].text.value)

    if config["settings"]["hide_responses"] == "false":
        print(this_message.data[0].content[0].text.value)

try:
    # Parsing argument
    args = PARSER.parse_args()

    client = OpenAI()

    if args.query:
        send_message(args.query, args.template, 1)

    if args.instructions:
        my_updated_assistant = client.beta.assistants.update(
            get_or_create_assistant(),
            instructions=args.instructions,
            name=NAME,
            tools=[{"type": "retrieval"}],
            model=config.get("settings", "model"),
        )

        send_message(f"Ive updated your instructions to: {args.instructions}!", None, 1)

    if args.file:
        with open(args.file, 'rb') as file_to_open:
            logging.info(attach_file(file_to_open))

except argparse.ArgumentError as err:
    logging.error(err)
    print (str(err))
