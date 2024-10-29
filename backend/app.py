#!/usr/bin/env python3
import os
import subprocess
import getpass

import aws_cdk as cdk

from backend.backend_stack import BackendStack
from backend.constants import SERVICE_NAME

def get_git_branch():
    try:
        return subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).decode('utf-8').strip()
    except:
        return 'unknown-branch'

def generate_stack_name():
    username = getpass.getuser()
    git_branch = get_git_branch()
    environment = os.environ.get('ENVIRONMENT', 'dev')
    return f"{username}-{git_branch}-{SERVICE_NAME}-{environment}"

app = cdk.App()
stack_name = generate_stack_name()
BackendStack(app, stack_name)

app.synth()