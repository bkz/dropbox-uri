import os, sys
import logging
import sqlite3

import platform

PROGRAM_TITLE = "Copy Dropbox URI"
PROTOCOL_URI_PREFIX = "dropbox:"

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
                platform.explore_path(filename)
                break
    else:
        raise DropboxWarning("Could not locate shared file")


def encode_dropbox_uri(namespace, path):
    data = u"%s|%s" % (namespace, path)
    return PROTOCOL_URI_PREFIX + uri_b64encode(data.encode("utf-8"))


###########################################################################
# Dropbox URI creation/lookup.
###########################################################################

def main(rootdir, is_frozen, script_path):
    try:
        if "/install" in sys.argv:
            if not platform.is_admin():
                raise DropboxWarning("Need admin right to install program")
            platform.install(rootdir, is_frozen, script_path)
            sys.exit(0)
        if "/uninstall" in sys.argv:
            if not platform.is_admin():
                raise DropboxWarning("Need admin right to uninstall program")
            platform.uninstall(rootdir)
            sys.exit(0)

        shared_folders = get_dropbox_shared_folders()

        clipboard_html, clipboard_text = [], []

        for arg in platform.get_argv(script_path):
            if arg.startswith(PROTOCOL_URI_PREFIX):
                explore_dropbox(shared_folders, arg)
                continue
            if not os.path.exists(arg):
                continue
            for (namespace, shared_path) in shared_folders:
                if arg.lower().startswith(shared_path):
                    rel_path = arg[len(shared_path):]
                    uri = encode_dropbox_uri(namespace, rel_path)
                    clipboard_html.append(u"<a href='%s'>%s</a>" % (uri, rel_path))
                    clipboard_text.append(uri)
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


###########################################################################
# The End.
###########################################################################
