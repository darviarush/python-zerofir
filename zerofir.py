""" zerofir — классы данных с валидацией и сериализацией """
from data_printer import p

import inspect
from typing import ForwardRef, List, Optional

from strongtyping.strong_typing_utils import check_type


class NotDefault:
    def __str__(self):
        return "NOT_DEFAULT!"

# Атрибут обязателен, если значение его свойства default именно такое
NOT_DEFAULT = NotDefault()


class Attribute:
    """ Атрибут для дополнительных опций """

    def __init__(self, type, key=None, error_prefix=""):
        self.type = type
        self.default = NOT_DEFAULT
        self.key = key
        self.error_prefix = error_prefix

    def check(self, value):
        """ Валидирует значение """
        _type = self.type

        if not check_type(value, self.type, mro=False):
            raise TypeError("%sType maybe %s, but %s." % (self.error_prefix, self.type, type(value)))


class Zerofir:
    """ Базовый класс для создания дата-классов """
    
    @classmethod
    def __initialize__(cls):
        """ Инициализирует атрибуты класса """
        if not cls.__annotations__ or not len(cls.__annotations__):
            raise TypeError("In %s dataclass not fields." % cls.__name__)

        def resolve_forwards(_type):
            """ Замена атрибутов """
            p("%s -> %s" % (_type, hasattr(_type, '__forward_arg__')))
            #print("!!! %s" % _type)
            

            if hasattr(_type, '__forward_arg__'):
                print('__forward_arg__=%s' % _type.__forward_arg__)
                print('__forward_code__=%s' % _type.__forward_code__)
                print('__forward_evaluated__=%s' % _type.__forward_evaluated__)
                print('__forward_value__=%s' % _type.__forward_value__)
                print('__forward_is_argument__=%s' % _type.__forward_is_argument__)
                print('__forward_is_class__=%s' % _type.__forward_is_class__)
                print('__forward_module__=%s' % _type.__forward_module__)

            if hasattr(_type, "__args__"):
                print("is_args!")
                #_type.__args__ = tuple([ resolve_forwards(t) for t in _type.__args__])
            return _type


        attributes = {}

        for k, _type in cls.__annotations__.items():

            if isinstance(_type, Attribute):
                attr = _type
            else:
                attr = Attribute(_type)
                if hasattr(cls, k):
                    attr.default = getattr(cls, k)
                if attr.key is None:
                    attr.key = k

            attr.error_prefix = "%s.%s: " % (cls.__name__, k)
            
            attr.type = resolve_forwards(attr.type)
            
            attributes[k] = attr
            
            # if k == 'base':
                # t = attr.type
                # f = t.__args__[0]
                # print(isinstance(t, ForwardRef))
                # # p({
                    # # '__forward_arg__': attr.type.__forward_arg__,
                    # # '__forward_code__': attr.type.__forward_code__,
                    # # '__forward_evaluated__': attr.type.__forward_evaluated__,
                    # # '__forward_value__': attr.type.__forward_value__,
                    # # '__forward_is_argument__': attr.type.__forward_is_argument__,
                    # # '__forward_is_class__': attr.type.__forward_is_class__,
                    # # '__forward_module__': attr.type.__forward_module__,
                # # })

        cls.__zerofir__ = attributes
    
    def __init__(self, **kw):
        """ С помощью конструктора можно установить свойства класса """

        # Первый экземпляр — инициализируем
        cls = self.__class__

        if not hasattr(cls, '__zerofir__'):
            cls.__initialize__()

        # Устанавливаем свойства:
        for k, attr in cls.__zerofir__.items():
            if k in kw:
                setattr(self, k, kw[k])
            elif attr.default is NOT_DEFAULT:
                raise KeyError("%s.%s required." % (cls.__name__, k))
            else:
                setattr(self, k, attr.default)

        # Проверяем, что у нас нет лишних аргументов:
        args = set(kw.keys())
        fields = set(cls.__zerofir__)
        unnecessary = args - fields
        if unnecessary:
            raise KeyError("Unnecessary arguments: %s." % ", ".join(list(unnecessary)))

    def __getattr__(self, k):
        if k not in self.__class__.__zerofir__:
            raise AttributeError("'%s' object has no attribute '%s'" % (self.__class__.__name__, k))
        return self.__dict__[k]

    def __setattr__(self, k, val):
        if k not in self.__class__.__zerofir__:
            raise AttributeError("'%s' object has no attribute '%s'" % (self.__class__.__name__, k))
        attr = self.__class__.__zerofir__[k]
        attr.check(val)
        self.__dict__[k] = val

    def __delattr__(self, k):
        if k not in self.__class__.__zerofir__:
            raise AttributeError("%s" % k)
        del self.__dict__[k]
    
    @classmethod
    def from_struct(cls, data):
        """ Метод восстанавливает объект из структуры """
        if not hasattr(cls, '__zerofir__'):
            cls.__initialize__()

        def unstructured(val, type_val):
            if inspect.isclass(type_val) and issubclass(type_val, Zerofir):
                return type_val.from_struct(val)
            if hasattr(attr.type, "__args__"):
                origin = attr.type.__origin__
                if origin in (list, tuple):
                    type_in = attr.type.__args__[0]
                    return [ unstructured(v, type_in) for v in val ]
            return val

        attributes = cls.__zerofir__
        kw = {}
        for k, attr in attributes.items():
            if attr.default is NOT_DEFAULT or attr.key in data:
                val = data[attr.key]
                kw[k] = unstructured(val, attr.type)

        return cls(**kw)

    def to_struct(self):
        """ Метод сериализует объект в структуру """
        
        def structured(val):
            if isinstance(val, Zerofir):
                val = val.to_struct()
            elif isinstance(val, (list, tuple, set)):
                val = [ structured(v) for v in val]
            elif isinstance(val, dict):
                val = { structured(k): structured(v) for k, v in val.items() }
                
            return val
        
        attributes = self.__class__.__zerofir__
        data = {}
        for k, attr in attributes.items():
            val = getattr(self, k)
            val = structured(val)
            data[attr.key] = val
            
        return data