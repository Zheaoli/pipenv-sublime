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

    def initial_text(self, *args):
        return ""

class pipenv_install(sublime_plugin.WindowCommand):

    def __init__(self, text):
        super(pipenv_install, self).__init__(text)

    def is_enabled(self):
        open_files = [view.file_name() for view in sublime.active_window().views()]

        for o_f in open_files:
            o_f = os.path.abspath(o_f)
            dirname = os.path.dirname(o_f)
            dirname = os.path.sep.join([dirname, '..', '..'])

            for root, dirs, files in os.walk(dirname, followlinks=True):
                if 'Pipfile' in files:
                    return True

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

        # Show the console.
        sublime.active_window().active_view().window().run_command('show_panel', {'panel': 'console'})

        # Run the install command.
        c = p.run('install {}'.format(package), block=False)

        # Update the status bar.
        sublime.status_message("Waiting for {!r} to install…".format(package))

        # Block on subprocess…
        c.block()

        # Print results to console.
        print(c.out)

        # Assure that the intallation was successful.
        try:
            # Ensure installation was successful.
            assert c.return_code == 0

            # Update the status bar.
            sublime.status_message("Success installing {!r}!".format(package))

            # Open the Pipfile.
            sublime.active_window().active_view().window().open_file('Pipfile')

            # Hide the console.
            sublime.active_window().active_view().window().run_command('hide_panel', {'panel': 'console'})
        except AssertionError:
            # Update the status bar.
            sublime.status_message("Error installing {!r}!".format(package))

            # Report the error.
            print(c.err)


class UninstallHandler(sublime_plugin.ListInputHandler):

    def __init__(self):
        super(UninstallHandler, self).__init__()

    def list_items(self):
        home = os.path.dirname(sublime.active_window().active_view().file_name())
        p = pipenvlib.PipenvProject(home)

        return list(set([p.name for p in p.packages + p.dev_packages]))

    def initial_text(self, *args):
        return ""


class pipenv_uninstall(sublime_plugin.WindowCommand):

    def __init__(self, text):
        super(pipenv_uninstall, self).__init__(text)

    def is_enabled(self):
        open_files = [view.file_name() for view in sublime.active_window().views()]

        for o_f in open_files:
            o_f = os.path.abspath(o_f)
            dirname = os.path.dirname(o_f)
            dirname = os.path.sep.join([dirname, '..', '..'])

            for root, dirs, files in os.walk(dirname, followlinks=True):
                if 'Pipfile' in files:
                    return True

    def input(self, *args):
        return UninstallHandler()

    def run(self, uninstall_handler):
        # The package to install.
        package = uninstall_handler

        # The home directory for the current file name.
        home = os.path.dirname(sublime.active_window().active_view().file_name())
        p = pipenvlib.PipenvProject(home)

        # Update package status.
        sublime.status_message("Un–installing {!r} with Pipenv…".format(package))

        # Show the console.
        sublime.active_window().active_view().window().run_command('show_panel', {'panel': 'console'})

        # Run the uninstall command.
        c = p.run('uninstall {}'.format(package), block=False)

        # Update the status bar.
        sublime.status_message("Waiting for {!r} to un–install…".format(package))

        # Block on subprocess…
        c.block()

        # Print results to console.
        print(c.out)

        # Assure that the intallation was successful.
        try:
            # Ensure installation was successful.
            assert c.return_code == 0

            # Update the status bar.
            sublime.status_message("Success un–installing {!r}!".format(package))

            # Open the Pipfile.
            sublime.active_window().active_view().window().open_file('Pipfile')

            # Hide the console.
            sublime.active_window().active_view().window().run_command('hide_panel', {'panel': 'console'})
        except AssertionError:
            # Update the status bar.
            sublime.status_message("Error un–installing {!r}!".format(package))

            # Report the error.
            print(c.err)


class pipenv_open_pipfile(sublime_plugin.WindowCommand):

    def __init__(self, text):
        super(pipenv_open_pipfile, self).__init__(text)

    def is_enabled(self):
        open_files = [view.file_name() for view in sublime.active_window().views()]

        for o_f in open_files:
            o_f = os.path.abspath(o_f)
            dirname = os.path.dirname(o_f)
            dirname = os.path.sep.join([dirname, '..', '..'])

            for root, dirs, files in os.walk(dirname, followlinks=True):
                if 'Pipfile' in files:
                    return True

    def input(self, *args):
        return UninstallHandler()

    def run(self, uninstall_handler):
        # The package to install.
        package = uninstall_handler

        # The home directory for the current file name.
        home = os.path.dirname(sublime.active_window().active_view().file_name())
        p = pipenvlib.PipenvProject(home)

        # Update package status.
        sublime.status_message("Un–installing {!r} with Pipenv…".format(package))

        # Show the console.
        sublime.active_window().active_view().window().run_command('show_panel', {'panel': 'console'})

        # Run the uninstall command.
        c = p.run('uninstall {}'.format(package), block=False)

        # Update the status bar.
        sublime.status_message("Waiting for {!r} to un–install…".format(package))

        # Block on subprocess…
        c.block()

        # Print results to console.
        print(c.out)

        # Assure that the intallation was successful.
        try:
            # Ensure installation was successful.
            assert c.return_code == 0

            # Update the status bar.
            sublime.status_message("Success un–installing {!r}!".format(package))

            # Open the Pipfile.
            sublime.active_window().active_view().window().open_file('Pipfile')

            # Hide the console.
            sublime.active_window().active_view().window().run_command('hide_panel', {'panel': 'console'})
        except AssertionError:
            # Update the status bar.
            sublime.status_message("Error un–installing {!r}!".format(package))

            # Report the error.
            print(c.err)

if sublime.version() < '3000':
    plugin_loaded()
