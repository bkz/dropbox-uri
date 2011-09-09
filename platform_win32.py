import os, sys

###########################################################################
# Wrap shared library interfacting with OS.
###########################################################################

from ctypes import CDLL, c_int, c_wchar_p

shared_lib = "platform.dll"

_set_clipboard_html = CDLL(shared_lib).set_clipboard_html
_set_clipboard_html.restype = c_int
_set_clipboard_html.argtypes = [
    c_wchar_p, # html
    c_wchar_p] # text

_create_shortcut = CDLL(shared_lib).create_shortcut
_create_shortcut.restype = c_int
_create_shortcut.argtypes = [
    c_wchar_p, # source
    c_wchar_p, # destination
    c_wchar_p, # working_dir
    c_wchar_p, # arguments
    c_wchar_p, # description
    c_wchar_p, # icon
    c_int]     # icon_index

_get_unicode_argc = CDLL(shared_lib).get_unicode_argc
_get_unicode_argc.restype = c_int
_get_unicode_argc.argtypes = []

_get_unicode_argv = CDLL(shared_lib).get_unicode_argv
_get_unicode_argv.restype = c_wchar_p
_get_unicode_argv.argtypes = [c_int] # index

_explore_path = CDLL(shared_lib).explore_path
_explore_path.restype = c_int
_explore_path.argtypes = [c_wchar_p] # filename

_show_info_message = CDLL(shared_lib).show_info_message
_show_info_message.restype = c_int
_show_info_message.argtypes = [
    c_wchar_p, # title
    c_wchar_p] # message

_show_warning_message = CDLL(shared_lib).show_warning_message
_show_warning_message.restype = c_int
_show_warning_message.argtypes = [
    c_wchar_p, # title
    c_wchar_p] # message

_show_error_message = CDLL(shared_lib).show_error_message
_show_error_message.restype = c_int
_show_error_message.argtypes = [
    c_wchar_p, # title
    c_wchar_p] # message

_is_admin = CDLL(shared_lib).is_admin
_is_admin.restype = c_int
_is_admin.argtypes = []

def create_shortcut(source, destination, workdir=None, args=None, tooltip=None, iconpath=None, iconindex=0):
    """
    Create a shortcut link to launch the executable or script ``source``. The
    shortcut will be saved to ``destination`` which should be a fully qualified
    path to a .lnk file (ex: C:\Users\Default\Desktop\Hello World.lnk). One can
    optionally specify a ``workdir`` and additional ``args`` (whitespace
    delimited string) needed to launch the application. A descriptive
    ``tooltip`` can also be set which the user is shown when he/she hovers over
    the shortcut. Custom icons be assigned using a combination of ``iconpath``
    which points to the .ico file and ``iconindex`` can be set if the .ico
    contains more than one icon. Returns True if short was successfully
    created. (Hint: To create a shortcut to launch a Python script set the
    source to the Python interpreter and pass the script an argument while also
    setting a correct working directory if needed.)
    """
    if not os.path.exists(source):
        raise RuntimeError("Missing source for shortcur link: %s" % source)
    if not destination.endswith(".lnk"):
        raise RuntimeError("Malformed shortcut link: %s" % destination)
    linkpath = os.path.split(destination)[0]
    if not os.path.exists(linkpath):
        os.makedirs(linkpath)
    ret = _create_shortcut(source, destination, workdir, args, tooltip, iconpath, iconindex)
    return (ret > 0) and os.path.exists(linkpath)


###########################################################################
# Lookup system folders.
###########################################################################

from ctypes import windll, wintypes, c_int

# These constants were imported from shlobj.h

CSIDL_APPDATA                  = 0x1a   # C:\Users\%USERNAME%\AppData\Roaming
CSIDL_COMMON_APPDATA           = 0x23   # C:\ProgramData
CSIDL_COMMON_DESKTOPDIRECTORY  = 0x19   # C:\Users\Public\Desktop
CSIDL_COMMON_DOCUMENTS         = 0x2e   # C:\Users\Public\Documents
CSIDL_COMMON_FAVORITES         = 0x1f   # C:\Users\%USERNAME%\Favorites
CSIDL_COMMON_MUSIC             = 0x35   # C:\Users\Public\Music
CSIDL_COMMON_PICTURES          = 0x36   # C:\Users\Public\Pictures
CSIDL_COMMON_PROGRAMS          = 0x17   # C:\ProgramData\Microsoft\Windows\Start Menu\Programs
CSIDL_COMMON_STARTMENU         = 0x16   # C:\ProgramData\Microsoft\Windows\Start Menu
CSIDL_COMMON_STARTUP           = 0x18   # C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup
CSIDL_COMMON_VIDEO             = 0x37   # C:\Users\Public\Videos
CSIDL_COOKIES                  = 0x21   # C:\Users\%USERNAME%\AppData\Roaming\Microsoft\Windows\Cookies
CSIDL_DESKTOPDIRECTORY         = 0x10   # C:\Users\%USERNAME%\Desktop
CSIDL_FAVORITES                = 0x6    # C:\Users\%USERNAME%\Favorites
CSIDL_FONTS                    = 0x14   # C:\Windows\Fonts
CSIDL_HISTORY                  = 0x22   # C:\Users\%USERNAME%\AppData\Local\Microsoft\Windows\History
CSIDL_INTERNET_CACHE           = 0x20   # C:\Users\%USERNAME%\AppData\Local\Microsoft\Windows\Temporary Internet Files
CSIDL_LOCAL_APPDATA            = 0x1c   # C:\Users\%USERNAME%\AppData\Local
CSIDL_MYDOCUMENTS              = 0x5    # C:\Users\%USERNAME%\Documents
CSIDL_MYMUSIC                  = 0xd    # C:\Users\%USERNAME%\Music
CSIDL_MYPICTURES               = 0x27   # C:\Users\%USERNAME%\Pictures
CSIDL_MYVIDEO                  = 0xe    # C:\Users\%USERNAME%\Videos
CSIDL_PERSONAL                 = 0x5    # C:\Users\%USERNAME%\Documents
CSIDL_PROFILE                  = 0x28   # C:\Users\%USERNAME%
CSIDL_PROGRAM_FILES            = 0x26   # C:\Program Files (x86)
CSIDL_PROGRAM_FILESX86         = 0x2a   # C:\Program Files (x86)
CSIDL_PROGRAM_FILES_COMMON     = 0x2b   # C:\Program Files (x86)\Common Files
CSIDL_PROGRAM_FILES_COMMONX86  = 0x2c   # C:\Program Files (x86)\Common Files
CSIDL_SENDTO                   = 0x09   # C:\Users\%USERNAME%\AppData\Roaming\Microsoft\Windows\SendTo
CSIDL_SYSTEM                   = 0x25   # C:\Windows\system32
CSIDL_SYSTEMX86                = 0x29   # C:\Windows\SysWOW64
CSIDL_WINDOWS                  = 0x24   # C:\Windows

SHGetFolderPath = windll.shell32.SHGetFolderPathW
SHGetFolderPath.argtypes = [
    wintypes.HWND,
    c_int,
    wintypes.HANDLE,
    wintypes.DWORD,
    wintypes.LPCWSTR]

def _get_system_path(csidl):
    path = wintypes.create_unicode_buffer(wintypes.MAX_PATH)
    result = SHGetFolderPath(0, csidl, 0, 0, path)
    return path.value


###########################################################################
# Module public interfance.
###########################################################################

def get_dropbox_dbfile(filename):
    """
    Locate Dropbox SQLite database ``filename`` application data folder.
    """
    if sys.platform == "win32":
        db_path = os.path.expandvars("%APPDATA%/Dropbox")
        db_path = os.path.normpath(os.path.join(db_path, filename))
    else:
        NotImplementedError("Platform not supported")
    if not os.path.exists(db_path):
        raise IOError("Could not locate Dropbox DB %s" % fileame)
    return db_path


def set_clipboard_html(html, text):
    """
    Set global clipboard content to `html` (encoded as raw HTML text) as well
    as `text` which is intended to be a unicode fallback for handlers which
    don't support HTML clipboard content.
    """
    return _set_clipboard_html(html, text)


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
    for i in range(_get_unicode_argc()):
        a = _get_unicode_argv(i)
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
    return _explore_path(filename)


def show_info_message(title, message):
    """
    Show simple modal OS specific messagebox/dialog with info message.
    """
    return _show_info_message(title, message)


def show_warning_message(title, message):
    """
    Show simple modal OS specific messagebox/dialog with warning message.
    """
    return _show_warning_message(title, message)


def show_error_message(title, message):
    """
    Show simple modal OS specific messagebox/dialog with error message.
    """
    return _show_error_message(title, message)


def is_admin():
    """
    Returns True if process is running with admin privileges (UAC).
    """
    return _is_admin()


###########################################################################
# Platform specific install/uninstall actions (requires admin rights).
###########################################################################

def install(rootdir, is_frozen, script_path=None):
    sendto = _get_system_path(CSIDL_SENDTO)
    create_shortcut(
        os.path.abspath(sys.executable),
        os.path.join(sendto, "Copy Dropbox URI.lnk"),
        args=script_path,
        tooltip="Copy Dropbox URI",
        workdir=rootdir,
        iconpath=os.path.join(rootdir, "dropbox.ico"))

    import _winreg
    root = _winreg.CreateKey(_winreg.HKEY_CLASSES_ROOT, "dropbox")
    _winreg.SetValueEx(root, "URL Protocol", 0, _winreg.REG_SZ, "")
    _winreg.SetValue(root, "DefaultIcon", _winreg.REG_SZ, os.path.join(rootdir, "dropbox.ico"))
    _winreg.SetValue(root, "shell\\open\\command", _winreg.REG_SZ,
                     '"%s"%s%%1' % (os.path.abspath(sys.executable),
                                       ' "%s" ' % script_path if script_path else ' '))
    _winreg.CloseKey(root)


def uninstall(rootdir):
    sendto = _get_system_path(CSIDL_SENDTO)
    shortcut = os.path.join(sendto, "Copy Dropbox URI.lnk")
    if os.path.exists(shortcut):
        os.remove(shortcut)


def setup(title, rootdir, is_frozen, script_path=None):
    if "/install" in sys.argv:
        if is_admin():
            install(rootdir, is_frozen, script_path)
            show_info_message(title, "Successfully installed plugin!")
        else:
            show_error_message(title, "Need admin rights to install")
        sys.exit(0)
    if "/uninstall" in sys.argv:
        if is_admin():
            uninstall(rootdir)
            show_info_message(title, "Successfully uninstalled plugin!")
        else:
            show_error_message(title, "Need admin rights to uninstall")
        sys.exit(0)


###########################################################################
# The End.
###########################################################################
