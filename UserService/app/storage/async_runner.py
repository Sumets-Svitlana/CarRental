from functools import wraps

from starlette.concurrency import run_in_threadpool


def run_async(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        return await run_in_threadpool(func, *args, **kwargs)

    return wrapper
