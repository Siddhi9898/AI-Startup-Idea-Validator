"""
Timeout Utilities
--------------------
Wraps any potentially slow/hanging call (LLM calls, search calls)
with a hard timeout, so low/no internet connectivity never causes
an infinite loop or unresponsive UI (fixes P5 and P10 together -
the "stop not working" and "infinite loop on low internet" issues
are really the same root cause: nothing had a timeout before).
"""

import concurrent.futures


class OperationTimedOut(Exception):
    pass


def run_with_timeout(func, args=(), kwargs=None, timeout_seconds: float = 15.0):
    """
    Runs func(*args, **kwargs) with a hard timeout. If it doesn't
    complete in time, raises OperationTimedOut instead of hanging
    forever. This is what makes Streamlit's stop button (and any
    future explicit stop control) actually able to interrupt work,
    since the pipeline will never block indefinitely on one call.
    """
    kwargs = kwargs or {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(func, *args, **kwargs)
        try:
            return future.result(timeout=timeout_seconds)
        except concurrent.futures.TimeoutError:
            raise OperationTimedOut(
                f"This step took longer than {timeout_seconds} seconds - likely a slow or "
                f"unstable internet connection. Please check your connection and try again."
            )
