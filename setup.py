import sys

from distutils.core import setup

if sys.platform == "win32":
    import py2exe
    sys.argv.append('py2exe')

    setup(
        name = "Dropbox Copy URI",
        version = "0.1",
        description = "Utility for sharing URIs for items in shared Dropbox folders.",
        author = "Babar K. Zafar",
        author_email = "babar.zafar@gmail.com",
        url = "https://github.com/bkz",
        long_description = "n/a",
        console = [{"dest_base": "dropbox", "script": "main.py"}],
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
    )
else:
    raise RuntimeError("Unsupported platform")
