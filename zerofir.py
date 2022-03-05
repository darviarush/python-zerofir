""" zerofir — классы данных с валидацией и сериализацией """

import inspect
from types import GenericAlias
from typing import Any, Dict, List, Optional

from strongtyping.strong_typing_utils import check_type, get_origins


NOT_DEFAULT = object()


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

        print("%s type (%s): %s." % (self.error_prefix, type(_type), _type))

        if not check_type(value, self.type):
            raise TypeError("%sType maybe %s, but %s." % (self.error_prefix, self.type, type(value)))


class Zerofir:
    """ Базовый класс для создания дата-классов """
    
    @classmethod
    def __initialize__(cls):
        """ Инициализирует атрибуты класса """
        if not cls.__annotations__ or not len(cls.__annotations__):
            raise TypeError("In %s dataclass not fields." % cls.__name__)

        attributes = {}

        for k, _type in cls.__annotations__.items():
            #print("%s.%s: %s" % (cls.__name__, k, _type))

            if isinstance(_type, Attribute):
                attr = _type
            else:
                attr = Attribute(_type)
                if hasattr(cls, k):
                    attr.default = getattr(cls, k)
                if attr.key is None:
                    attr.key = k

            attr.error_prefix = "%s.%s: " % (cls.__name__, k)
            attributes[k] = attr

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
        print("get: %s" % k)
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

        attributes = cls.__zerofir__
        kw = {}
        for k, attr in attributes.items():
            if attr.default is NOT_DEFAULT or attr.key in data:
                val = data[attr.key]

                type_name, x = get_origins(attr.type)

                print(">>> %s.%s [%s] = [%s] %s:%s x=%s:%s" % (cls.__name__, k, attr.type, val, type_name, type(type_name), x, type(x)))

                if inspect.isclass(attr.type) and issubclass(attr.type, Zerofir):
                    kw[k] = attr.type.from_struct(val)
                else:
                    kw[k] = val

        return cls(**kw)

    def to_struct(self):
        """ Метод сериализует объект в структуру """
        
        def structured(val):
            if isinstance(val, Zerofir):
                val = val.to_struct()
            elif isinstance(val, (list, tuple)):
                val = map(structured, val)
            elif isinstance(val, dict):
                val = { structured(k): structured(v) for k, v in val.items() }
            elif isinstance(val, set):
                val = set(map(structured, list(val)))
                
            return val
        
        attributes = self.__class__.__zerofir__
        data = []
        for k, attr in attributes.items():
            val = getattr(self, k)
            val = structured(val)
            data[attr.key] = val
            
        return data