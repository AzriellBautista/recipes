# A class whose attributes cannot be modified after initialization
class FrozenClass:
    """A class whose attributes cannot be modified after initialization
    
    Attributes of the classes that inherit from this class cannot be modified 
    after initialization. This is useful for preventing accidental modifications 
    of attributes that are intended to be read-only. 
    
    Notes: 
        super().__init__() must be called in the subclass's __init__() method, 
        after the subclass's attributes have been initialized.
    
    Attrs:
        _initd (bool): Whether the class has been initialized
    """
    __slots__ = ("_initd",)

    def __init__(self):
        self._initd = True

    def __setattr__(self, attr, value):
        # If the class has been initialized, raise an AttributeError
        # indicating that an attribute cannot be modified
        if getattr(self, '_initd', False):
            raise AttributeError(f"Cannot change `{attr}` attribute of `{self.__class__.__name__}` after initialization")
        super().__setattr__(attr, value)