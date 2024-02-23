[![Pylint](https://github.com/kyager/jot/actions/workflows/pylint.yml/badge.svg)](https://github.com/kyager/jot/actions/workflows/pylint.yml)

# Jot

Just a simple script for working with the OpenAI Assistant API.

```
usage: jot [-h] [-o {json,text}] {image,moderate,assist,attach,instructions} prompt

positional arguments:
  {image,moderate,assist,attach,instructions}
                        The type of model to use.
  prompt                Your prompt.

options:
  -h, --help            show this help message and exit
  -o {json,text}        Specifies the output type
```

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
image_model = dall-e-3
image_size = 1024x1024
thread_id = 
assistant_id = 

[logging]
level = INFO
path = ~/.jot_log
```
