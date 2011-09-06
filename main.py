import os, sys
import logging
import logging.handlers

###########################################################################
# Application entry-point.
###########################################################################

def setup_logfile(rootdir, is_frozen, logname):
    logging.getLogger().setLevel(logging.DEBUG)
    if not is_frozen:
        logging.getLogger().addHandler(logging.StreamHandler())
    filelogger = logging.handlers.RotatingFileHandler(
        os.path.join(rootdir, logname), maxBytes=512*1024)
    filelogger.setFormatter(logging.Formatter("%(asctime)s : %(message)s"))
    logging.getLogger().addHandler(filelogger)


if __name__ == '__main__':
    try:
        is_frozen = hasattr(sys, "frozen")
        if is_frozen:
            rootdir = os.path.abspath(os.path.dirname(sys.executable))
        else:
            rootdir = os.path.abspath(os.path.dirname(__file__))

        rootdir = unicode(rootdir, encoding=sys.getfilesystemencoding())

        if is_frozen:
            script_path = None
        else:
            script_path = os.path.join(rootdir, sys.argv[0])

        setup_logfile(rootdir, is_frozen, 'debug.log')

        os.chdir(rootdir)

        import dropbox

        dropbox.main(rootdir, is_frozen, script_path)
    finally:
        pass


###########################################################################
# The End.
###########################################################################
