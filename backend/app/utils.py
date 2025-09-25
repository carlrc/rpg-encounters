import os
from functools import lru_cache


@lru_cache()
def get_or_throw(env_var: str) -> str:
    value = os.getenv(env_var)
    if not value:
        raise RuntimeError(f"Could not retrieve env var {env_var}")
    else:
        return value
