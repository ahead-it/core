map = {}

def _add_tomap(func, attribute):
    fn = func.__module__ + '/' + func.__qualname__
    if fn not in map:
        map[fn] = []
    map[fn].append(attribute)

def PublicMethod(func):
    """
    Define a method callable without authentication 
    """
    _add_tomap(func, 'public')
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

