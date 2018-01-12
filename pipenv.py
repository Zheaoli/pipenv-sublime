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


class UninstallHandler(sublime_plugin.ListInputHandler):
    """docstring for ClassName"""

    def __init__(self):
        super(InstallHandler, self).__init__()

    def _return_packages(self):
        home = os.path.basename(sublime.View().file_name())
        print(sublime.current.file_name)

        p = pipenvlib.PipenvProject(home)
        return [p.name for p in (p.dev_packages + p.packages)]


    def list_items(self):
        return [p for p in self._return_packages()]

    def next_input(self, *args):
        return None

    def placeholder(self):
        return "package-name"

    def description(self, *args):
        return "Package to uninstall."


class pipenv_install(sublime_plugin.WindowCommand):
    """docstring for PipenvMenu"""

    def __init__(self, text):
        super(pipenv_install, self).__init__(text)

    def is_enabled(self):
        return True

    def description(self):
        return "Pipenv is awesome"

    def input(self, *args):
        return UninstallHandler()

    def run(self, install_handler):
        # The package to install.
        package = install_handler

        # The home directory for the current file name.
        home = os.path.basename(sublime.View().file_name())
        print(sublime.current.file_name)

        p = pipenvlib.PipenvProject(home)
        print(p._run('install {}', package))


class pipenv_uninstall(sublime_plugin.WindowCommand):
    """docstring for PipenvMenu"""

    def __init__(self, text):
        super(pipenv_uninstall, self).__init__(text)

    def is_enabled(self):
        return True

    def description(self):
        return "Pipenv is awesome"

    def input(self, *args):
        return UninstallHandler()

    def run(self, uninstall_handler=None):
        # The package to install.
        package = uninstall_handler

        # The home directory for the current file name.
        home = os.path.basename(sublime.Window.active_view(sublime.active_window()).file_name())

        p = pipenvlib.PipenvProject(home)
        print(p.packages + p.dev_packages)


if sublime.version() < '3000':
    plugin_loaded()
