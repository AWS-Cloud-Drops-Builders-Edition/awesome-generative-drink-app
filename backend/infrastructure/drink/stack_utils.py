import getpass
import os

import git
from infrastructure.drink.constants import SERVICE_NAME


def get_git_branch():
    try:
        repo = git.Repo(search_parent_directories=True)
        return repo.active_branch.name
    except git.InvalidGitRepositoryError:
        return "unknown-branch"


def generate_stack_name():
    username = getpass.getuser()
    git_branch = get_git_branch()
    environment = os.environ.get("ENVIRONMENT", "dev")
    return f"{username}-{git_branch}-{SERVICE_NAME}-{environment}"
