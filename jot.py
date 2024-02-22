#!/usr/bin/python3

"""
This script provides an CLI interface for interacting with the OpenAI API.
"""

import sys
import os
import configparser
import json
import socket
import time
from datetime import datetime
from openai import OpenAI

NOW = datetime.now()
FINAL_MESSAGE = None
COMMAND = sys.argv[1]
CONTENT = " ".join(sys.argv[2:]).strip("'")
NAME = socket.gethostname()

config = configparser.ConfigParser()
config.read(os.path.expanduser("~/.jot"))
if "settings" not in config.keys():
    config.add_section("settings")


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
            model=config.get("settings", "model").strip('"'),
            instructions=config.get("settings", "instructions"),
        )
        config["settings"]["assistant_id"] = assistant.id
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

def build_message(content, template):
    """Builds a message using a specified template.

    Returns:
    object:run

    """
    thread_id = get_or_create_thread()
    assistant_id = get_or_create_assistant()

    if template == "message":
        templated_content = f"{content}"
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

    return message_run


client = OpenAI()

if COMMAND in ["-i", "--instructions"]:
    my_updated_assistant = client.beta.assistants.update(
      get_or_create_assistant(),
      instructions=CONTENT,
      name=NAME,
      model=config.get("settings", "model").strip('"'),
    )

    run = build_message(f"Ive updated your instructions to: {CONTENT}, I hope you enjoy!", None)

    while True:
        this_run = client.beta.threads.runs.retrieve(
            thread_id=run.thread_id, run_id=run.id
        )

        if this_run.status == "completed":
            message = client.beta.threads.messages.list(thread_id=run.thread_id, limit=1)
            FINAL_MESSAGE = message.data[-1].content[-1].text.value
            break

        time.sleep(1)

if COMMAND in ["-q", "--query"]:
    run = build_message(CONTENT, "message")

    while True:
        this_run = client.beta.threads.runs.retrieve(
            thread_id=run.thread_id, run_id=run.id
        )

        if this_run.status == "completed":
            message = client.beta.threads.messages.list(thread_id=run.thread_id, limit=1)
            FINAL_MESSAGE = message.data[-1].content[-1].text.value
            break

        time.sleep(1)


if COMMAND in ["-n", "--note"]:
    run = build_message(CONTENT, "note")

    while True:
        this_run = client.beta.threads.runs.retrieve(
            thread_id=run.thread_id, run_id=run.id
        )

        if this_run.status == "completed":
            message = client.beta.threads.messages.list(thread_id=run.thread_id, limit=1)
            FINAL_MESSAGE = message.data[-1].content[-1].text.value
            break

        time.sleep(1)

if COMMAND in ["-l", "--list"]:
    messages = client.beta.threads.messages.list(get_or_create_thread(), order="asc")

    for message in messages:
        print(message.content[-1].text.value)

if FINAL_MESSAGE:
    print(FINAL_MESSAGE)
