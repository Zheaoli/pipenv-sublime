import os

import sublime
import sublime_plugin

from .vendor import requests
from .vendor import parse
from .vendor import pipenvlib


TEMPLATE = "<a href='{0}'>{0}</a><br/>"
ALL_PACKAGES = list()

def plugin_loaded():
    pass

class InstallHandler(sublime_plugin.ListInputHandler):
    """docstring for ClassName"""

    def __init__(self):
        super(InstallHandler, self).__init__()

    def _yield_packages(self):
        # Set the status message.
        sublime.status_message("Fetching all available packages from PyPi (just a sec!)…")

        # Make the HTTP Request.
        r = requests.get('https://pypi.python.org/simple/')
        sublime.status_message("")

        # Yield results.
        for result in parse.findall(TEMPLATE, r.text):
            yield result[0]

    @property
    def _all_packages(self):
        return ALL_PACKAGES

    @_all_packages.setter
    def function(self, value):
        global ALL_PACKAGES
        ALL_PACKAGES = value

    @property
    def all_packages(self):
        if self._all_packages:
            return self._all_packages

        for package in self._yield_packages():
            self._all_packages.append(package)

        # List special packages first, because I can.
        kr_packages = (
            'requests', 'requests-html', 'maya', 'records', 'httpbin', 'crayons',
            'delegator.py', 'tablib', 'background', 'clint', 'xerox'
        )
        # Special shout-outs.
        kr_favorites = ('django', 'flask', 'docopt', 'parse', 'apistar')
        kr_favorites = list(kr_packages + kr_favorites)

        # Reverse order.
        kr_favorites.reverse()

        for kr_package in kr_favorites:
            package = self._all_packages.pop(self._all_packages.index(kr_package))
            self._all_packages.insert(0, package)

        return self._all_packages

    def list_items(self):
        return self.all_packages

    def next_input(self, *args):
        return None

    def placeholder(self):
        # return "package-name"
        pass

    def description(self, *args):
        # return "Package to install."
        pass


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
        sublime.status_message("Installing {!r} with Pipenv…".format(package))

        sublime.run_command('show_panel', {'panel': 'console'})
        print()
        c = p._run('install {}'.format(package))
        # sublime.status_message("Waiting for {!r} to install…".format(package))
        # c.block()

        assert c.return_code == 0
        sublime.status_message("Success installing {!r}!".format(package))

        sublime.active_window().active_view().window().open_file('Pipfile')
        # sublime.open('Pipfile')
        # Show a new window.


        # Print the output of the installation.


if sublime.version() < '3000':
    plugin_loaded()
