import streamlit as st
from functools import wraps
import time

def background_cache(ttl_hours=1):
    """
    Decorator that caches the result of a function for a specified number of hours.
    Uses Streamlit's cache_data with a background thread to avoid blocking the UI.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Create a unique cache key based on function name and arguments
            cache_key = f"{func.__name__}_{str(args)}_{str(kwargs)}"
            
            # Check if we have a cached result
            if cache_key in st.session_state:
                cached_result, timestamp = st.session_state[cache_key]
                # Check if cache is still valid
                if time.time() - timestamp < ttl_hours * 3600:
                    return cached_result
            
            # If no cache or expired, execute function
            result = func(*args, **kwargs)
            
            # Cache the result with timestamp
            st.session_state[cache_key] = (result, time.time())
            
            return result
        return wrapper
    return decorator 