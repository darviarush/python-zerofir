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
    __type: str
    id: int = 0
    user: User
    components: List[Component]


class ZerofirTestCase(unittest.TestCase):
    """ Тест """

    def test_make(self):
        """ Создание объекта """
        class Man(Zerofir):
            id: int
            name: str = ""

        man = Man(id=10, name="Lisp")
        self.assertEqual(man.id, 10)
        self.assertEqual(man.name, "Lisp")
        
        with self.assertRaises(TypeError):
            man.id = "10"


    # def test_serialize(self):
        # """ Сериализация и десериализация """
        
        # cart = Cart.from_struct({
            # '__type': 'restrict',
            # 'user': {
                # 'id': 45,
                # 'name': "San",
            # },
            # 'components': [
                # {'id': 1},
                # {'id': 2},
            # ],
        # })
        
        # self.assertEqual(cart.id, 0)
        # self.assertEqual(cart.__type, 'default')
        # self.assertEqual(len(cart.components), 2)

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
