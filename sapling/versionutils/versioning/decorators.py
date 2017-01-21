from functools import wraps


def require_instance(historyManagerFunction):
    @wraps(historyManagerFunction)
    def _require_instance(*args, **kwargs):
        self = args[0]
        if not self.instance:
            raise TypeError("This method must be called via an instance of "
                            "the model rather than from the class.")
        return historyManagerFunction(*args, **kwargs)
    return _require_instance
