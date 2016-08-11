import sys
def log(str):

    # This function was used during development to have a live debug log of the client networking and logging
    # screen rendering while the terminal window was being used as a Curses screen
    
    # If the standard-error stream is not re-directed though these logging messages will appear on screen and
    # interfere with the curses library's ability to use the terminal window as a rendering pallet

    # Therefore logging is disabled and easily re-enabled by allowing our functions to call this ineffectual function
    # in release builds.

    pass
    # sys.stderr.write(str)
    # sys.stderr.flush()