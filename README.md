[![Pylint](https://github.com/kyager/jot/actions/workflows/pylint.yml/badge.svg)](https://github.com/kyager/jot/actions/workflows/pylint.yml)

# Jot

Just a simple script for working with the OpenAI Assistant API.

## Commands

| Command | Description |
| ------- | ----------- |
| `jot -q [content]` | Sends a query to the assistant. |
| `jot -t [template_name]` | Wraps your query in a custom template prompt |
| `jot -f [file_path]` | Attaches a file to the assistant. |
| `jot -i [instructions]` | Updates the assistants instructions. |

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
personality = your personal assistant

[logging]
level = INFO
path = ~/.jot_log
```
