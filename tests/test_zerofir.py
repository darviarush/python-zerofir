import sys
import unittest
from typing import List, Optional
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
            base: Optional['Man'] = None

        man1 = Man(id=10, range=[])

        man = Man(
            id=10, 
            range=[1,2,3],
            base=man1,
        )
        
        self.assertEqual(man.id, 10)
        self.assertEqual(man.name, "Lisp")
        self.assertEqual(man.range, [1,2,3])
        self.assertEqual(man.base, None)
    
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
        self.assertEqual(cart.type, 'restrict')
        self.assertEqual(len(cart.components), 2)
        
    def test_unserialize(self):
        """ Десериализация """
        cart = Cart(
            type='restrict',
            user=User(id=45, name="San"),
            components=[
                Component(id=1),
                Component(id=2),
            ],
        )
                
        self.assertEqual(cart.to_struct(), {
            '__type': 'restrict',
            'id': 0,
            'user': {
                'id': 45,
                'name': "San",
            },
            'components': [
                {'id': 1},
                {'id': 2},
            ],
        })


if __name__ == '__main__':
    unittest.main()
