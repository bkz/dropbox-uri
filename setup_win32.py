import os, sys
import subprocess
import shutil
from setuptools import setup

import py2exe
sys.argv.append('py2exe')

###########################################################################
# Configuration.
###########################################################################

AUTHOR_EMAIL  = "babar.zafar@gmail.com"
AUTHOR_NAME   = "Babar K. Zafar"
AUTHOR_URL    = "http://www.sharedropbox.com/"
COPYRIGHT     = "Copyright (C) Babar K. Zafar"
DEST_BASE     = "dropbox-uri"
DIST_DIR      = "dist"
ICON_FILE     = "dropbox.ico"
INSTALLER_EXE = "dropbox-uri.exe"
MAIN_SCRIPT   = "main.py"
PRODUCT_NAME  = "DropboxURI"
VERSION       = "0.1"
VERSIONSTRING = "%s %s" % (PRODUCT_NAME, VERSION)

###########################################################################
# NSIS silent installer template.
###########################################################################

NSIS_SCRIPT = """\
!define DistDir '%(DIST_DIR)s'
!define PythonExe '%(DEST_BASE)s.exe'

OutFile ${PythonExe}

Name '%(AUTHOR_NAME)s'
Icon '%(ICON_FILE)s'
RequestExecutionLevel admin
SetCompressor 'lzma' ; Off
SilentInstall silent

Section
    InitPluginsDir
    SetOutPath '$LOCALAPPDATA\DropboxURI\%(VERSION)s'
    File /r '${DistDir}\*.*'
    Exec '"$LOCALAPPDATA\DropboxURI\%(VERSION)s\${PythonExe}" /install'
SectionEnd
"""


###########################################################################
# Preprare build envrionment.
###########################################################################

for n in range(5):
    try:
        if os.path.exists(DIST_DIR):
            shutil.rmtree(DIST_DIR)
        os.makedirs(DIST_DIR)
        break
    except (IOError, OSError):
        pass
else:
    assert(0)


###########################################################################
# Generate standalone executable using Py2exe.
###########################################################################

setup(
    windows = [{
        "dest_base"       : DEST_BASE,
        "script"          : MAIN_SCRIPT,
        "other_resources" : [(u"VERSIONTAG", 1, VERSIONSTRING)],
        "icon_resources"  : [(1, ICON_FILE)],
        "copyright"       : COPYRIGHT,
    }],

    zipfile = None,

    data_files = [
        ("", [ICON_FILE, "platform.dll"]),
    ],

    options = {
        "py2exe" : {
            "packages"     : [],
            "excludes"     : ["Tkconstants", "Tkinter", "tcl", "psycopg2"],
            "compressed"   : False,
            "bundle_files" : 2,
            "dll_excludes" : ["w9xpopen.exe"],
            "dist_dir"     : DIST_DIR,
        }
    },

    name         = PRODUCT_NAME,
    version      = VERSION,
    author       = AUTHOR_NAME,
    author_email = AUTHOR_EMAIL,
    url          = AUTHOR_URL
)

if os.path.exists("setup.nsi"):
    os.remove("setup.nsi")

open("setup.nsi", "wt").write(
    NSIS_SCRIPT % {
        "DIST_DIR"    : DIST_DIR,
        "DEST_BASE"   : DEST_BASE,
        "AUTHOR_NAME" : AUTHOR_NAME,
        "ICON_FILE"   : ICON_FILE,
        "VERSION"     : VERSION,
        })


###########################################################################
# Build bundle/installer using NSIS.
###########################################################################

if os.path.exists(INSTALLER_EXE):
    os.remove(INSTALLER_EXE)

subprocess.call("makensis.exe setup.nsi")

os.rename(DEST_BASE + ".exe", INSTALLER_EXE)


###########################################################################
# The End.
###########################################################################
