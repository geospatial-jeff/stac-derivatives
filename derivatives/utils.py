import inspect

def get_methods(obj):
    return [x[0] for x in inspect.getmembers(obj, predicate=inspect.ismethod)]