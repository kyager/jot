[![Pylint](https://github.com/kyager/jot/actions/workflows/pylint.yml/badge.svg)](https://github.com/kyager/jot/actions/workflows/pylint.yml)

# Jot

Just a simple script for woring with the OpenAI Assistant API.

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