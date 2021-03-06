#!/usr/bin/env python

import os

os.environ["DJANGO_SETTINGS_MODULE"] = "pyrm.settings"

from django.core.management import execute_manager

from pyrm import settings

if __name__ == "__main__":
    execute_manager(settings)
