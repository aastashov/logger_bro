class Singleton:
    def __new__(cls, *args, **kwargs):
        it = getattr(cls, "__it__", None)
        if it is not None:
            return it

        cls.__it__ = it = object.__new__(cls)
        it._init(*args, **kwargs)
        return it

    def _init(self, *args, **kwargs):
        pass
