import unittest
from mock import patch
# from actions.reinforcement import reinforcement
# from settings import Mode
# from field.Field import Field


class TestStringMethods(unittest.TestCase):

    # def setUp(self):
    #     self.width = 50
    #     self.height = 40
    #     self.countR = 100
    #     self.countF = 100
    #     self.vr = 2        
    #     # with patch('field.Field') as mock:
    #     #     insnstance = mock.return_value
    #     #     insnstance.step.return_value  = ("first", "second")
    #     #     f = Field(self.width, self.height, self.countR, self.countF, self.vr, Mode.Reinforcement)
    #     #     a, b, c, d, e = f.step()
    #     #     print("==========================" + str(a))


    # @patch('field.Field.Field', autospec='testField')
    # def test_reinforce(self, fieldMock):
    #     instance = fieldMock.return_value
    #     instance.return_value.step = ("a", "b", "c", "d", "e")
    #     a, b, c, d, e = Field(self.width, self.height, self.countR, self.countF, self.vr, Mode.Reinforcement).step()
    #     self.assertEqual(a, 'a')

    def test_upper(self):
        print("I'm here")
        self.assertEqual('foo'.upper(), 'FOO')

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)

if __name__ == '__main__':
    unittest.main()