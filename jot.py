#!/usr/bin/python3

import sys
import os
import configparser
import json
import socket
import time
from datetime import datetime
from openai import OpenAI

now = datetime.now()
final_message = None
command = sys.argv[1]
content = " ".join(sys.argv[2:]).strip(
    "'"
)  # sys.argv[1:] excludes the script name from the args

# get config
config = configparser.ConfigParser()
config.read(os.path.expanduser("~/.jot"))
if "settings" not in config.keys():
    config.add_section("settings")


def saveConfig():
    with open(os.path.expanduser("~/.jot"), "w") as configfile:
        config.write(configfile)


def getOrCreateAssistant():
    if "assistant_id" not in config["settings"]:
        assistant = client.beta.assistants.create(
            name=socket.gethostname(),
            model=config.get("settings", "model").strip('"'),
            instructions=config.get("settings", "instructions"),
        )
        config["settings"]["assistant_id"] = assistant.id
        saveConfig()

    return config["settings"]["assistant_id"]


def getOrCreateThread():
    """
    Retrieves or creates a thread.

    Returns:
    - thread_id (str): The ID of the retrieved or created thread.

    Description:
    - If the 'thread_id' is not present in the 'config' settings, a new thread is created using the 'client.beta.threads.create()' method.
    - The 'thread_id' is then stored in the 'config' settings and saved using the 'saveConfig()' function.
    - Finally, the function returns the 'thread_id' from the 'config' settings.
    """
    if "thread_id" not in config["settings"]:
        thread = client.beta.threads.create()
        config["settings"]["thread_id"] = thread.id
        saveConfig()

    return config["settings"]["thread_id"]


def createMessageAndThread(content):
    """
    Creates a message and a thread.

    Args:
        content (str): The content of the message.

    Returns:
        str: The ID of the created thread.
        str: The ID of the created message.
    """
    thread_id = getOrCreateThread()
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=content,
    )
    return thread_id, message


def createNoteAndThread(content):
    """e
    Creates a note message and a thread.

    Args:
        content (str): The content of the note message.

    Returns:
        str: The ID of the created thread.
        str: The ID of the created message.
    """
    thread_id = getOrCreateThread()
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=f"{json.dumps([{'type':'note','datetime':str(now),'content': content}])}",
    )
    return thread_id, message


client = OpenAI()


if command in ["-q", "--query"]:
    thread_id, message = createMessageAndThread(content)

    run = client.beta.threads.runs.create(
        thread_id=message.thread_id, assistant_id=getOrCreateAssistant()
    )

    while True:
        this_run = client.beta.threads.runs.retrieve(
            thread_id=run.thread_id, run_id=run.id
        )

        if this_run.status == "completed":
            message = client.beta.threads.messages.list(thread_id=thread_id, limit=1)
            final_message = message.data[-1].content[-1].text.value
            break

        time.sleep(1)


if command in ["-n", "--note"]:
    thread_id, message = createNoteAndThread(content)

    run = client.beta.threads.runs.create(
        thread_id=message.thread_id, assistant_id=getOrCreateAssistant()
    )

    while True:
        this_run = client.beta.threads.runs.retrieve(
            thread_id=run.thread_id, run_id=run.id
        )

        if this_run.status == "completed":
            message = client.beta.threads.messages.list(thread_id=thread_id, limit=1)
            final_message = message.data[-1].content[-1].text.value
            break

        time.sleep(1)

if command in ["-l", "--list"]:
    messages = client.beta.threads.messages.list(getOrCreateThread(), order="asc")

    for message in messages:
        print(message.content[-1].text.value)

if final_message:
    print(final_message)
