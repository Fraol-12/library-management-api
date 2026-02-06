import os

# ruff: noqa: F403,F405

from .base import *

DEBUG = True
SECRET_KEY = os.getenv("SECRET_KEY")  # or a dev-only insecure key
ALLOWED_HOSTS = ["*"]  # permissive for local
