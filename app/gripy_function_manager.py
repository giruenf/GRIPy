from six import add_metaclass


class GripyFunctionManager(type):

    def __init__(cls, name, bases, dct):
        super(GripyFunctionManager, cls).__init__(name, bases, dct)


@add_metaclass(GripyFunctionManager)
class FunctionManager(object):
    _registered = {}
    _with_classes = {}

    @classmethod
    def _register(cls, func, *types, **kwtypes):
        """
        Decorator based on @accept found in:
            http://wiki.python.org/moin/PythonDecoratorLibrary
        """
        try:
            def decorator(f):
                def newfunc(*args, **kwargs):
                    if len(args) != len(types):
                        raise TypeError(
                            'Wrong number of arguments. len(args): {}, len(types): {}'.format(len(args), len(types)))
                    for i, t in enumerate(map(type, args)):
                        if types[i] != type(args[i]):
                            raise TypeError('Wrong type given in args[{}]'.format(i))
                    if kwargs:
                        for k, v in kwargs.items():
                            if kwtypes[k] != type(v):
                                raise TypeError('Wrong type given in key {}'.format(k))
                    return f(*args, **kwargs)

                newfunc.__name__ = f.__name__
                return newfunc

            return decorator(func)
        except:
            raise

    @classmethod
    def register_function(cls, func, friendly_name=None, *args, **kwargs):
        try:
            name = func.__name__
        except:
            name = ''
        if not friendly_name:
            friendly_name = name
        func = cls._register(func, *args, **kwargs)
        func = staticmethod(func)
        setattr(cls, name, func)
        cls._registered[func] = {'name': name,
                                 'friendly_name': friendly_name,
                                 'function': func,
                                 'args': args,
                                 'kwargs': kwargs
                                 }
        for class_ in list(args) + list(kwargs.values()):
            if class_ not in cls._with_classes.keys():
                cls._with_classes[class_] = [func]
            else:
                cls._with_classes[class_].append(func)

    @classmethod
    def functions_available_for_class(cls, class_):
        try:
            return [cls._registered.get(f) for f in cls._with_classes[class_]]
        except KeyError:
            return []
