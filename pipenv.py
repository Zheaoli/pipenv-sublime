import os

import sublime
import sublime_plugin

from .vendor import requests
from .vendor import parse
from .vendor import pipenvlib


TEMPLATE = "<a href='{0}'>{0}</a><br/>"

def plugin_loaded():
    pass


class InstallHandler(sublime_plugin.ListInputHandler):
    """docstring for ClassName"""

    def __init__(self):
        super(InstallHandler, self).__init__()

    def _yield_packages(self):
        sublime.status_message("Fetching Package names from PyPi…")
        r = requests.get('https://pypi.python.org/simple/')
        for result in parse.findall(TEMPLATE, r.text):
            yield result[0]

    def list_items(self):
        return [p for p in self._yield_packages()]

    def next_input(self, *args):
        return None

    def placeholder(self):
        return "package-name"

    def description(self, *args):
        return "Package to install."


class pipenv_install(sublime_plugin.WindowCommand):
    """docstring for PipenvMenu"""

    def __init__(self, text):
        super(pipenv_install, self).__init__(text)

    def is_enabled(self):
        return True

    def description(self):
        return "Pipenv is awesome"

    def input(self, *args):
        return InstallHandler()

    def run(self, install_handler):
        # The package to install.
        package = install_handler

        # The home directory for the current file name.
        home = os.path.dirname(sublime.active_window().active_view().file_name())
        p = pipenvlib.PipenvProject(home)

        # Update package status.
        sublime.status_message("Installing {} with Pipenv…".format(package))

        sublime.run_command('show_panel', {'panel': 'console'})
        print()
        print(p._run('install {}'.format(package)).out)
        # Show a new window.

        # Print the output of the installation.



if sublime.version() < '3000':
    plugin_loaded()
