import os, sys
from setuptools import setup

import py2app
sys.argv.append('py2app')

###########################################################################
# Global configuration.
###########################################################################

AUTHOR_EMAIL  = "babar.zafar@gmail.com"
AUTHOR_NAME   = "Babar K. Zafar"
AUTHOR_URL    = "http://www.sharedropbox.com/"
ICON_FILE     = "dropbox.icns"
MAIN_SCRIPT   = "main.py"
PRODUCT_NAME  = "DropboxURI"
VERSION       = "0.1"

###########################################################################
# Target OSX.
###########################################################################

plist = dict(
   CFBundleURLTypes = [
        dict(CFBundleURLSchemes = ["dropbox"],
             CFBundleURLName = "Open dropbox files via uri.")
    ],
)

setup(
    app=[MAIN_SCRIPT],
    options = {
        "py2app": {
            "argv_emulation" : True,
            "resources"      : ["automator/Copy Dropbox URI.workflow"],
            "iconfile"       : ICON_FILE,
            "plist"          : plist,
        }
    },
    name         = PRODUCT_NAME,
    version      = VERSION,
    author       = AUTHOR_NAME,
    author_email = AUTHOR_EMAIL,
    url          = AUTHOR_URL
)


###########################################################################
# The End.
###########################################################################
