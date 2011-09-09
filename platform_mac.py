import os, sys
import logging
import subprocess
import shutil

###########################################################################
# Helper scripts.
###########################################################################

FINDER_SELECT_SCRIPT = """\
on run {filename}
    set filepath to POSIX file filename
    tell application "Finder"
        reveal filepath
        activate
    end tell
end run
"""

ALERT_DIALOG_SCRIPT = """\
tell application "Finder"
    delay 0
    activate
    display dialog "%(message)s" with title "%(title)s" buttons {"OK"} default button 1 with icon %(icon)s giving up after %(timeout)d
end tell
"""

###########################################################################
# Utilities.
###########################################################################

def show_message_box(title, message, icon=1, timeout=30):
    """
    Display a simple alert dialog with ``title`` and ``message`` and an
    optional icon ('stop' or 'caution') and ``timeout`` limit in seconds.
    """
    p = subprocess.Popen(["osascript", "-"], stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate(ALERT_DIALOG_SCRIPT %
                                   dict(title=title.replace('"', '\\"'),
                                        message=message.replace('"', '\\"'),
                                        icon=icon, timeout=timeout))


###########################################################################
# Module public interface..
###########################################################################

def get_dropbox_dbfile(filename):
    """
    Locate Dropbox SQLite database ``filename`` in users home folder.
    """
    return os.path.normpath(os.path.join(os.path.expanduser("~/.dropbox"), filename))


def set_clipboard_html(html, text):
    """
    Set global clipboard content to `html` (encoded as raw HTML text) as well
    as `text` which is intended to be a unicode fallback for handlers which
    don't support HTML clipboard content.
    """
    p = subprocess.Popen("textutil -stdin -inputencoding utf-8 -format html -convert rtf -encoding utf-8 -stdout",
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, shell=True)
    stdout, stderr = p.communicate(html.encode("utf-8"))

    rtf = stdout.decode("utf-8")

    p = subprocess.Popen("pbcopy",
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, shell=True)
    stdout, stderr = p.communicate(rtf.encode("utf-8"))



def get_argv(script=None):
    """
    Return sys.argv like list with command-line options fetched as unicode
    bypassing all Python layers. This is needed to interface with OS in order
    to handle unicode (UTF-8, UTF-16) filenames correctly. In order to mimic
    sys.argv we'll filter out the sys.executable and optionally any `script`
    file if needed (most likely you'll want to ignore __file__ and only deal
    with real arguments).
    """
    if script:
        script = os.path.abspath(os.path.normpath(script))
    argv = []
    for i in range(len(sys.argv)):
        a = sys.argv[i].decode(sys.getfilesystemencoding())
        if os.path.exists(a):
            a = os.path.abspath(os.path.normpath(a))
            if a == script:
                continue
        if a.endswith(sys.executable):
            continue
        argv.append(a)
    return argv


def explore_path(filename):
    """
    Open the OS file browser and navigate/select the `filename` resource.
    """
    filename = filename.encode(sys.getfilesystemencoding())
    p = subprocess.Popen(["osascript", "-", filename],
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    stdout, stderr = p.communicate(FINDER_SELECT_SCRIPT)


def show_info_message(title, message):
    """
    Show simple modal OS specific messagebox/dialog with info message.
    """
    logging.debug("Info %s" % message.encode("utf-8"))
    show_message_box(title, message)


def show_warning_message(title, message):
    """
    Show simple modal OS specific messagebox/dialog with warning message.
    """
    logging.debug("Warning %s" % message.encode("utf-8"))
    show_message_box(title, message, icon="caution")


def show_error_message(title, message):
    """
    Show simple modal OS specific messagebox/dialog with error message.
    """
    logging.debug("Error %s" % message.encode("utf-8"))
    show_message_box(title, message, icon="stop")


def is_admin():
    """
    Returns True if process is running with admin privileges (UAC or root).
    """
    return os.getuid() == 0


###########################################################################
# Platform specific setup actions (bootstrap Automator).
###########################################################################

MIN_OSX_VER = 10.6

from platform import mac_ver

def setup(title, rootdir, is_frozen, script_path=None):
    if is_frozen:
        app = os.path.abspath(os.path.join(rootdir, "../../"))
        target = os.path.join(os.path.expanduser("~/Library/Services/Copy Dropbox URI.workflow"))
        workflow_script = os.path.join(target, "Contents/document.wflow")
        # Pass 1: check if workflow exists and points to correct .app
        if os.path.exists(target):
            if open(workflow_script, "rt").read().find(app) == -1:
                logging.debug("Automator workflow path incorrect, deleting")
                shutil.rmtree(target)
            else:
                logging.debug("Automator workflow up-to-date")
        # Pass 2: possible install or re-install workflow if out-of-date
        if not os.path.exists(target):
            osx_ver = float(".".join(mac_ver()[0].split(".")[:2])) # "x.y.z" -> float(x.y)
            if osx_ver >= MIN_OSX_VER:
                logging.debug("Installing Automator workflow on %s" % osx_ver)
                source = os.path.join(rootdir, "../Resources/Copy Dropbox URI.workflow")
                shutil.copytree(source, target)
                # Patch the workflow script to point to the correct .app
                logging.debug("Patching workflow -> %s" % app.encode("utf-8"))
                content = open(workflow_script, "rt").read()
                open(workflow_script, "wt").write(content.replace("/Applications/DropboxURI.app", app))
                show_info_message(title, "Successfully installed plugin!")
            else:
                show_error_message("Sorry, Mac OS X %s is not supported!" % osx_ver)


###########################################################################
# The End.
###########################################################################
