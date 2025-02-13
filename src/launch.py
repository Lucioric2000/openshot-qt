#!/usr/bin/env python3

"""
 @file
 @brief This file is used to launch OpenShot
 @author Jonathan Thomas <jonathan@openshot.org>
 @author Noah Figg <eggmunkee@hotmail.com>

 @mainpage OpenShot Video Editor 2.0

 Welcome to the OpenShot Video Editor 2.0 PyQt5 documentation. OpenShot was developed to
 make high-quality video editing and animation solutions freely available to the world. With a focus
 on stability, performance, and ease-of-use, we believe OpenShot is the best cross-platform,
 open-source video editing application in the world!

 This documentation is auto-generated by Doxygen, using the doxypy Python filter. If you are
 interested in how OpenShot Video Editor is designed, feel free to dive in, because this
 documentation was built just for you. If you are not a developer, please feel free to visit
 our main website (http://www.openshot.org/download/), and download a copy today for Linux, Mac, or Windows.

 @section LICENSE

 Copyright (c) 2008-2018 OpenShot Studios, LLC
 (http://www.openshotstudios.com). This file is part of
 OpenShot Video Editor (http://www.openshot.org), an open-source project
 dedicated to delivering high quality video editing and animation solutions
 to the world.

 OpenShot Video Editor is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 OpenShot Video Editor is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with OpenShot Library.  If not, see <http://www.gnu.org/licenses/>.
 """

import sys
import os.path
import argparse

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication

try:
    # This apparently has to be done before loading QtQuick
    # (via QtWebEgine) AND before creating the QApplication instance
    QApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    from OpenGL import GL  # noqa
except (ImportError, AttributeError):
    pass

try:
    # QtWebEngineWidgets must be loaded prior to creating a QApplication
    # But on systems with only WebKit, this will fail (and we ignore the failure)
    from PyQt5 import QtWebEngineWidgets
    WebEngineView = QtWebEngineWidgets.QWebEngineView
except ImportError:
    pass

try:
    # Enable High-DPI resolutions
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
except AttributeError:
    pass  # Quietly fail for older Qt5 versions

try:
    from classes import info, exceptions
except ImportError:
    import openshot_qt
    sys.path.append(openshot_qt.OPENSHOT_PATH)
    from classes import info, exceptions

# Initialize sentry exception tracing
exceptions.init_sentry_tracing()

# Global holder for QApplication instance
app = None


def main():
    """"Initialize settings (not implemented) and create main window/application."""

    global app

    # Configure argument handling for commandline launches
    parser = argparse.ArgumentParser(description='OpenShot version ' + info.SETUP['version'])
    parser.add_argument(
        '-l', '--lang', action='store',
        help='language code for interface (overrides '
             'preferences and system environment)')
    parser.add_argument(
        '--list-languages', dest='list_languages',
        action='store_true',
        help='List all language codes supported by OpenShot')
    parser.add_argument(
        '--path', dest='py_path', action='append',
        help='Additional locations to search for modules '
             '(PYTHONPATH). Can be used multiple times.')
    parser.add_argument(
        '--test-models', dest='modeltest',
        action='store_true',
        help="Load Qt's QAbstractItemModelTester into data models "
        '(requires Qt 5.11+)')
    parser.add_argument(
        '-b', '--web-backend', action='store',
        choices=['auto', 'webkit', 'webengine'], default='auto',
        help="Web backend to use for Timeline")
    parser.add_argument(
        '-d', '--debug', action='store_true',
        help='Enable debugging output')
    parser.add_argument(
        '--debug-file', action='store_true',
        help='Debugging output (logfile only)')
    parser.add_argument(
        '--debug-console', action='store_true',
        help='Debugging output (console only)')
    parser.add_argument('-V', '--version', action='store_true')
    parser.add_argument(
        'remain', nargs=argparse.REMAINDER, help=argparse.SUPPRESS)

    args, extra_args = parser.parse_known_args()

    # Display version and exit (if requested)
    if args.version:
        print(info.SETUP['version'])
        sys.exit()

    # Set up debugging log level to requested streams
    if args.debug or args.debug_file:
        info.LOG_LEVEL_FILE = 'DEBUG'
    if args.debug or args.debug_console:
        info.LOG_LEVEL_CONSOLE = 'DEBUG'

    if args.list_languages:
        from classes.language import get_all_languages
        print("Supported Languages:")
        for code, lang in get_all_languages():
            print("  {:>12}  {}".format(code, lang))
        sys.exit()

    if args.py_path:
        for p in args.py_path:
            try:
                if os.path.exists(os.path.realpath(p)):
                    sys.path.insert(0, os.path.realpath(p))
                    print("Added {} to PYTHONPATH".format(os.path.realpath(p)))
                else:
                    print("{} does not exist".format(os.path.realpath(p)))
            except TypeError as ex:
                print("Bad path {}: {}".format(p, ex))
                continue

    if args.modeltest:
        info.MODEL_TEST = True
        # Set default logging rules, if the user didn't
        if os.getenv('QT_LOGGING_RULES') is None:
            os.putenv('QT_LOGGING_RULES', 'qt.modeltest.debug=true')
    if args.web_backend:
        info.WEB_BACKEND = args.web_backend.lower()
    if args.lang:
        if args.lang in info.SUPPORTED_LANGUAGES:
            info.CMDLINE_LANGUAGE = args.lang
        else:
            print("Unsupported language '{}'! (See --list-languages)".format(args.lang))
            sys.exit(-1)

    # Normal startup, print module path and lauch application
    print("Loaded modules from: %s" % info.PATH)

    # Create Qt application, pass any unprocessed arguments
    from classes.app import OpenShotApp

    argv = [sys.argv[0]]
    argv.extend(extra_args)
    argv.extend(args.remain)
    try:
        app = OpenShotApp(argv)
    except Exception:
        app.show_errors()

    # Setup Qt application details
    app.setApplicationName('openshot')
    app.setApplicationVersion(info.SETUP['version'])
    try:
        # Qt 5.7+ only
        app.setDesktopFile("org.openshot.OpenShot")
    except AttributeError:
        pass

    # Launch GUI and start event loop
    app.gui()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
