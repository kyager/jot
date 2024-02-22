#!/usr/bin/python3

import sys
import os
import configparser
import json
import socket
import time
import openai
from datetime import datetime
from openai import OpenAI

NOW = datetime.now()
FINAL_MESSAGE = None
COMMAND = sys.argv[1]
CONTENT = " ".join(sys.argv[2:]).strip("'")

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
    if "thread_id" not in config["settings"]:
        thread = client.beta.threads.create()
        config["settings"]["thread_id"] = thread.id
        saveConfig()

    return config["settings"]["thread_id"]


def createMessageAndThread(content):
    thread_id = getOrCreateThread()
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=content,
    )
    return thread_id, message


def createNoteAndThread(content):
    thread_id = getOrCreateThread()
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=f"{json.dumps([{'type':'note','datetime':str(NOW),'content': content}])}",
    )
    return thread_id, message


client = OpenAI()


if COMMAND in ["-q", "--query"]:
    thread_id, message = createMessageAndThread(CONTENT)

    run = client.beta.threads.runs.create(
        thread_id=message.thread_id, assistant_id=getOrCreateAssistant()
    )

    while True:
        this_run = client.beta.threads.runs.retrieve(
            thread_id=run.thread_id, run_id=run.id
        )

        if this_run.status == "completed":
            message = client.beta.threads.messages.list(thread_id=thread_id, limit=1)
            FINAL_MESSAGE = message.data[-1].content[-1].text.value
            break

        time.sleep(1)


if COMMAND in ["-n", "--note"]:
    thread_id, message = createNoteAndThread(CONTENT)

    run = client.beta.threads.runs.create(
        thread_id=message.thread_id, assistant_id=getOrCreateAssistant()
    )

    while True:
        this_run = client.beta.threads.runs.retrieve(
            thread_id=run.thread_id, run_id=run.id
        )

        if this_run.status == "completed":
            message = client.beta.threads.messages.list(thread_id=thread_id, limit=1)
            FINAL_MESSAGE = message.data[-1].content[-1].text.value
            break

        time.sleep(1)

if COMMAND in ["-l", "--list"]:
    messages = client.beta.threads.messages.list(getOrCreateThread(), order="asc")

    for message in messages:
        print(message.content[-1].text.value)

if FINAL_MESSAGE:
    print(FINAL_MESSAGE)
