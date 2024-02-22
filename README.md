[![Pylint](https://github.com/kyager/jot/actions/workflows/pylint.yml/badge.svg)](https://github.com/kyager/jot/actions/workflows/pylint.yml)

# Jot

Just a simple script for woring with the OpenAI Assistant API.

## Commands

| Command | Description |
| ------- | ----------- |
| `jot --query "Text"` | Sends a query to the assistant. |
| `jot --note "Text"` | Sends a JSON formatted note to the assistant. |
| `jot --file [file_path]` | Attaches a file to the assistant. |
| `jot --instructions "Text"` | Updates the assistants instructions. |

## OpenAI Setup
You will need an API key, which can be acquired here: https://platform.openai.com/api-keys.

Then add the key to your environment variables.

`export OPENAI_API_KEY="sk-ABC123"`

## Configuration
Needs to be placed in `~/.jot`
```.jot
[settings]
instructions = You are a helpful assistant
model = gpt-3.5-turbo-0125
thread_id = 
assistant_id = 
hide_responses = false

[logging]
level = INFO
path = ~/.jot_log
```
