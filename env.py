'''This module contains functions to set environment variables.'''

import os
from dotenv import load_dotenv

load_dotenv()

def set_env_variable(key, value):
    '''Set an environment variable.'''
    with open('.env', 'r', encoding='utf-8') as file:
        lines = file.readlines()

    with open('.env', 'w', encoding='utf-8') as file:
        found = False
        for line in lines:
            if line.startswith(f"{key}="):
                file.write(f"{key}={value}\n")
                found = True
            else:
                file.write(line)

        if not found:
            file.write(f"\n{key}={value}\n")

    os.environ[key] = value
