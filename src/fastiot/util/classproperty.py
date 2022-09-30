def classproperty(fn):
    return classmethod(property(fget=fn))
