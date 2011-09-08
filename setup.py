import os, sys

from setuptools import setup

###########################################################################
# Global configuration.
###########################################################################

global_options = dict(
    name = "DropboxURI",
    version = "0.1",
    description = "Utility for sharing URIs for items in shared Dropbox folders.",
    author = "Babar K. Zafar",
    author_email = "babar.zafar@gmail.com",
    url = "https://github.com/bkz",
    long_description = "n/a",
)

###########################################################################
# Target OSX.
###########################################################################

def build_darwin():
    import py2app

    sys.argv.append('py2app')

    plist = dict(
       CFBundleURLTypes = [
            dict(CFBundleURLSchemes = ["dropbox"],
                 CFBundleURLName = "Open dropbox files via uri.")
        ],
    )

    setup(
        app=["main.py"],
        options = {
            "py2app": {
                "argv_emulation" : True,
                "iconfile"       : "dropbox.icns",
                "plist"          : plist,
            }
        },
        **global_options
    )


###########################################################################
# Target Windows.
###########################################################################

def build_windows():
    import py2exe

    sys.argv.append('py2exe')

    setup(
        windows = [{"dest_base": "dropbox", "script": "main.py"}],
        data_files = [("", ["dropbox.ico", "platform.dll"])],
        zipfile = None,
        options = {
            "py2exe" : {
                "compressed"   : True,
                "bundle_files" : 2,
                "excludes"     : ["Tkconstants", "Tkinter", "tcl"],
                "dll_excludes" : ["w9xpopen.exe"],
                "dist_dir"     : 'bin',
            }
        },
        **global_options
    )


###########################################################################
# Trigger platform specific build.
###########################################################################

if sys.platform == "darwin":
    build_darwin()
elif sys.platform == "win32":
    build_windows()
else:
    raise NotImplementedError("Unsupported platform")


###########################################################################
# The End.
###########################################################################
