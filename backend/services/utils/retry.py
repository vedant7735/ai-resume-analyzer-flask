import time
import functools
import random

def retry_on_exception(retries=3, initial_delay=1.0, backoff_factor=2.0, exception_types=(Exception,)):
    """
    A simple decorator to retry a function call with exponential backoff.
    Only retries for specified exception types.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None
            for attempt in range(retries + 1):
                try:
                    return func(*args, **kwargs)
                except exception_types as e:
                    last_exception = e
                    if attempt == retries:
                        break
                    
                    # Add jitter to the delay
                    sleep_time = delay * (0.8 + 0.4 * random.random())
                    print(f"[Retry] Attempt {attempt + 1} failed with {type(e).__name__}: {e}. Retrying in {sleep_time:.2f}s...")
                    time.sleep(sleep_time)
                    delay *= backoff_factor
            
            print(f"[Retry] All {retries + 1} attempts failed.")
            raise last_exception
        return wrapper
    return decorator
