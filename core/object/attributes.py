from functools import wraps


def PublicMethod(func):
    """
    Define a method callable without authentication 
    """
    func.__dict__['_ispublic'] = True

    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

