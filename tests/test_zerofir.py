import sys
import unittest
from typing import Any, Dict, List, Optional

from zerofir import Zerofir, Attribute


class Component(Zerofir):
    id: int


class User(Zerofir):
    id: int
    name: str = ""


class Cart(Zerofir):
    type: Attribute(str, key='__type')
    id: int = 0
    user: User
    components: List[Component]


class ZerofirTestCase(unittest.TestCase):
    """ Тест """

    def test_make(self):
        """ Создание объекта """
        class Man(Zerofir):
            id: int
            name: str = "Lisp"
            range: list[int]
            seek: List[int]

        man = Man(
            id=10, 
            range=[1,2,3],
            seek=[5,6],
        )
        
        self.assertEqual(man.id, 10)
        self.assertEqual(man.name, "Lisp")
        self.assertEqual(man.range, [1,2,3])
        self.assertEqual(man.seek, [5,6])
    
    def test_validation(self):
        """ Проверка типов """
    
        class Man(Zerofir):
            id: int
            
        man = Man(id=10)
    
        with self.assertRaises(TypeError):
            man.id = "10"


    def test_serialize(self):
        """ Сериализация """
        
        cart = Cart.from_struct({
            '__type': 'restrict',
            'user': {
                'id': 45,
                'name': "San",
            },
            'components': [
                {'id': 1},
                {'id': 2},
            ],
        })
        
        self.assertEqual(cart.id, 0)
        self.assertEqual(cart.type, 'default')
        self.assertEqual(len(cart.components), 2)

    # def test_constructor_params(self):
        # """ Конструктор, нормальные параметры """

    # def test_constructor_kw(self):
        # """ Конструктор принимает параметры из словаря """


        # kw = {
            # '__type': 'default', 
            # components: [
                # {'id': 1},
                # {'id': 2},
            # ],
        # }
        # cart = Cart(**kw)

        # #self.assertRaises()
       
    # def test_constructor_many_params(self):
        # """ Конструктор """



if __name__ == '__main__':
    unittest.main()
