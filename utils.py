# Third party imports
import lockfile
def wait_for_file(filepath):
    """
    This function waits for a file to be available before proceeding.

    Args:
        filepath: Path to the file to wait for
    """
    lock = lockfile.FileLock(filepath)
    while not lock.i_am_locking():
        try:
            lock.acquire(timeout=1)  # wait for 1 second
        except lockfile.LockTimeout:
            pass
    return True