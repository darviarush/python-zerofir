""" zerofir — классы данных с валидацией и сериализацией """

from typing import Any, Dict, List, Optional


NOT_DEFAULT = object()


class Attribute:
    """ Атрибут для дополнительных опций """
    
    def __init__(self, type, name=None):
        self.type = type
        self.default = NOT_DEFAULT
        self.name = name
        
    def check(self, value):
        """ Валидирует значение """
        _type = self.type
        
        print("type: %s." % _type)
        
        if _type is Any:
            return
                
        if type(value) is _type:
            return

        raise TypeError("Type maybe %s, but %s." % (self.type, type(value)))


class Zerofir:
    """ Базовый класс для создания дата-классов """
    
    def __init__(self, **kw):
        """ С помощью конструктора можно установить свойства класса """
        
        # Первый экземпляр — инициализируем
        cls = self.__class__
        
        if not hasattr(cls, '__zerofir__'):
            if not cls.__annotations__ or not len(cls.__annotations__):
                raise TypeError("In %s dataclass not fields." % cls.__name__)
        
            attributes = {}
            
            for k, _type in cls.__annotations__.items():
                print("%s.%s: %s" % (cls.__name__, k, _type))
               
                if isinstance(_type, Attribute):
                    attr = _type
                else:
                    attr = Attribute(_type)
                    if hasattr(cls, k):
                        attr.default = getattr(cls, k)
                    if attr.name is None:
                        attr.name = k

                attributes[k] = attr
            
            cls.__zerofir__ = attributes
            
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
        fields = set(attributes)
        unnecessary = args - fields
        if unnecessary:
            raise KeyError("Unnecessary arguments: %s." % ", ".join(list(unnecessary)))

    def __getattr__(self, k):
        print("get: %s" % k)
        return self.__dict__[k]

    def __setattr__(self, k, val):
        attr = self.__class__.__zerofir__[k]
        attr.check(val)
        self.__dict__[k] = val

    def __delattr__(self, k):
        del self.__dict__[k]
    
    @classmethod
    def from_struct(cls, data):
        """ Метод восстанавливает объект из структуры """
        attributes = cls.__zerofir__
        kw = {}
        for k, attr in attributes.items():
            val = data[k]
            
            print("%s.%s :%s = %s" % (cls.__name__, k, attr.type, val))
            
            if issubclass(attr.type, Zerofir):
                kw[k] = attr.type.from_struct(val)
            else:
                kw[k] = val
        return cls(**kw)

    def to_struct(self):
        """ Метод сериализует объект в структуру """
        attributes = self.__class__.__zerofir__
        data = []
        for k, _type in annotations.items():
            val = getattr(self, k)
            if issubclass(_type, Zerofir):
                val = val.to_struct()
            #elif hasinstance(val):
            data[k] = val
        return data