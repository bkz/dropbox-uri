import os, sys
import logging
import sqlite3
import re

PROGRAM_TITLE = "Share Dropbox"
PROTOCOL_URI_PREFIX = "dropbox:"

###########################################################################
# Platform abstraction layer.
###########################################################################

if sys.platform == "win32":
    import platform_win32 as platform
elif sys.platform == "darwin":
    import platform_mac as platform
else:
    raise NotImplementedError("Unsupported platform")


###########################################################################
# Exceptions
###########################################################################

class DropboxWarning(RuntimeError):
    """
    Generic warning intended to be displayed via UI.
    """
    pass


###########################################################################
# Utilities.
###########################################################################

def get_dropbox_shared_folders():
    local_ns = get_dropbox_root_ns()
    local_path = get_dropbox_path()
    con = sqlite3.connect(platform.get_dropbox_dbfile("filecache.db"))
    con.row_factory = sqlite3.Row
    return [(unicode(row["target_ns"]),
             os.path.normpath(row["server_path"].replace("%s:" % local_ns, local_path).lower()))
            for row in con.execute("SELECT * FROM mount_table")]


def get_dropbox_config(key):
    con = sqlite3.connect(platform.get_dropbox_dbfile("config.db"))
    return con.execute("SELECT * FROM config WHERE config.key=?", (key,)).fetchone()[1]


def get_dropbox_root_ns():
    return unicode(get_dropbox_config('root_ns'))


def get_dropbox_path():
    return os.path.normpath(get_dropbox_config('dropbox_path'))


###########################################################################
# Padding-less base64 encoding.
###########################################################################

from base64 import urlsafe_b64encode, urlsafe_b64decode

def uri_b64encode(s):
     return urlsafe_b64encode(s).strip('=')

def uri_b64decode(s):
     return urlsafe_b64decode(s + '=' * (4 - len(s) % 4))


###########################################################################
# Dropbox URI handling (for protocol handler).
###########################################################################

def explore_dropbox(shared_folders, uri):
    data = uri[len(PROTOCOL_URI_PREFIX):]
    uri_namespace, uri_path = uri_b64decode(data.encode("ascii")).decode("utf-8").split("|")
    for (namespace, shared_path) in shared_folders:
        if namespace == uri_namespace:
            filename = os.path.join(shared_path, uri_path[1:])
            if os.path.exists(filename):
                logging.debug("Exploring: %s" % filename.encode("utf-8"))
                platform.explore_path(filename)
                break
    else:
        raise DropboxWarning("Could not locate shared file: %s" % filename.encode("utf-8"))


def encode_dropbox_uri(namespace, path):
    data = u"%s|%s" % (namespace, path)
    return uri_b64encode(data.encode("utf-8"))


def is_valid_dropbox_uri(arg):
    if arg.startswith(PROTOCOL_URI_PREFIX):
        uri = arg[len(PROTOCOL_URI_PREFIX):]
        return re.match(r"^[a-z0-9_\-]+$", uri, re.I) != None
    else:
        return False


###########################################################################
# Dropbox URI creation/lookup.
###########################################################################

def main(rootdir, is_frozen, script_path):
    try:
        platform.setup(PROGRAM_TITLE, rootdir, is_frozen, script_path)

        shared_folders = get_dropbox_shared_folders()

        clipboard_html, clipboard_text = [], []

        for arg in platform.get_argv(script_path):
            if is_valid_dropbox_uri(arg):
                explore_dropbox(shared_folders, arg)
                continue
            if not os.path.exists(arg):
                logging.debug("Invalid argument: %s" % arg.encode("utf-8"))
                continue
            for (namespace, shared_path) in shared_folders:
                if arg.lower().startswith(shared_path):
                    rel_path = arg[len(shared_path):]
                    uri = encode_dropbox_uri(namespace, rel_path)
                    clipboard_html.append(u"<a href='http://www.sharedropbox.com/%s'>%s</a>" % (uri, rel_path))
                    clipboard_text.append("http://www.sharedropbox.com/%s" % uri)
                    break
            else:
                raise DropboxWarning("You can only link to items in shared folders")

        if clipboard_html:
            platform.set_clipboard_html(
                "<br>".join(clipboard_html),
                "\n".join(clipboard_text))

    except DropboxWarning, e:
        platform.show_warning_message(PROGRAM_TITLE, str(e) + "!")
    except (KeyboardInterrupt, SystemExit):
        pass
    except:
        import traceback
        stacktrace = traceback.format_exc()
        platform.show_error_message(PROGRAM_TITLE, stacktrace)
        logging.exception("Unhandled exception")


###########################################################################
# The End.
###########################################################################
