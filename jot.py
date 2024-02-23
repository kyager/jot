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
import webbrowser
from datetime import datetime
from openai import OpenAI

NOW = datetime.now()
FINAL_MESSAGE = None
NAME = socket.gethostname()

PARSER = argparse.ArgumentParser()
PARSER.add_argument(
    "type",
    help="The type of model to use.",
    choices=["image", "moderate", "assist", "attach", "instructions"],
)
PARSER.add_argument(
    "prompt",
    help="Your prompt.",
)
PARSER.add_argument(
    "-o",
    help="Specifies the output type",
    choices=["json", "text"],
    default="text",
)

config = configparser.ConfigParser()
config.read(os.path.expanduser("~/.jot"))
if "settings" not in config.keys():
    config.add_section("settings")

logging.basicConfig(
    filename=os.path.expanduser(config["logging"]["path"]),
    encoding="utf-8",
    level=config["logging"]["level"],
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


def add_tools(assistant_id, tools):
    """Adds the specified tools to your current assistant"""
    client.beta.assistants.update(assistant_id=assistant_id, tools=tools)


def remove_tools(assistant_id):
    """Removes all tools from your current assistant"""
    client.beta.assistants.update(assistant_id=assistant_id, tools=[])


def attach_file(file):
    """Uploads a file and attaches it to your current assistant"""
    created_file = client.files.create(file=file, purpose="assistants")

    add_tools(get_or_create_assistant(), [{"type": "code_interpreter"}])
    assistant_file = client.beta.assistants.files.create(
        assistant_id=get_or_create_assistant(), file_id=created_file.id
    )
    remove_tools(get_or_create_assistant())

    return assistant_file


def send_message(content, interval=1):
    """Builds a message and then sends it to the assistant, then checks at the specified
    interval for a response.
    """
    thread_id = get_or_create_thread()
    assistant_id = get_or_create_assistant()

    # If it looks like we're trying to use a file, ensure the needed tools are added
    if "file-" in content:
        add_tools(assistant_id, [{"type": "code_interpreter"}])

    built_message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=content,
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
                thread_id=message_run.thread_id, limit=1
            )
            logging.debug(this_run)
            break

        time.sleep(interval)

    if "file-" in content:
        remove_tools(assistant_id)

    return this_message.data[0].content[0]


try:
    args = PARSER.parse_args()

    if args.type == "image":
        client = OpenAI()
        image = client.images.generate(
            model=config["settings"]["image_model"],
            prompt=args.prompt,
            n=1,
            size=str(config["settings"]["image_size"]),
        )

        if args.o == "text":
            webbrowser.open(image.data[0].url)
            print(image.data[0].revised_prompt)

        elif args.o == "json":
            print(json.dumps(image.data[0].__dict__))

    if args.type == "moderate":
        client = OpenAI()
        response = client.moderations.create(input=args.prompt)

        if args.o == "text":
            for category, mod in response.results[0].categories:
                print(f"{category.title().replace('_', ' ')}: {mod}")
        elif args.o == "json":
            print(json.dumps(response.results[0].categories.__dict__))

    if args.type == "assist":
        client = OpenAI()
        response = send_message(args.prompt, 1)

        if args.o == "text":
            print(response.text.value)
        elif args.o == "json":
            print(json.dumps(response.text.__dict__))

    if args.type == "instructions":
        client = OpenAI()
        my_updated_assistant = client.beta.assistants.update(
            get_or_create_assistant(), instructions=args.prompt
        )

        if args.o == "json":
            print(json.dumps(my_updated_assistant.__dict__))

    if args.type == "attach":
        client = OpenAI()
        with open(args.prompt, "rb") as file_to_open:
            attached_file = attach_file(file_to_open)

        if args.o == "text":
            print(attached_file.id)
        elif args.o == "json":
            print(json.dumps(attached_file.__dict__))

except argparse.ArgumentError as err:
    logging.error(err)
    print(str(err))
