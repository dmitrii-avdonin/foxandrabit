import unittest
from mock import patch
import mock
# from actions.reinforcement import reinforcement
from settings import Mode
from field.Field import Field
import utils.Utils
import actions.reinforcement


def loadFromFile(fileName):
    return fileName

class TestStringMethods(unittest.TestCase):

    def setUp(self):
        self.width = 50
        self.height = 40
        self.countR = 10
        self.countF = 10
        self.vr = 2        
        # with patch('field.Field') as mock:
        #     insnstance = mock.return_value
        #     insnstance.step.return_value  = ("first", "second")
        #     f = Field(self.width, self.height, self.countR, self.countF, self.vr, Mode.Reinforcement)
        #     a, b, c, d, e = f.step()
        #     print("==========================" + str(a))


    @mock.patch('utils.Utils.loadNpArrayFromFile', side_effect=loadFromFile)
    @mock.patch('actions.reinforcement.loadNpArrayFromFile', side_effect=loadFromFile)
    def test_mockModuleFunction(self, mock_load, mock_loadInReinf):
        self.assertEqual(utils.Utils.loadNpArrayFromFile("asdf"), 'asdf')
        actions.reinforcement.reinforcement([3])

    @patch.object(Field, 'step', return_value = ("a", "b", "c", "d", "e"))
    @patch.object(Field, 'aliveRabitsCount', return_value = 555)
    def test_patchMultipleMethods(self, mock_step, mock_aliveRabitsCount):
        f = Field(self.width, self.height, self.countR, self.countF, self.vr, Mode.Reinforcement)
        a, b, c, d, e = f.step()
        count = f.aliveRabitsCount()
        self.assertEqual(a, 'a')
        self.assertEqual(count, 555)


    @patch.object(Field, 'step')
    def test_patchOneMethod(self, stepMock):
        stepMock.return_value = ("a", "b", "c", "d", "e")
        a, b, c, d, e = Field(self.width, self.height, self.countR, self.countF, self.vr, Mode.Reinforcement).step()
        self.assertEqual(a, 'a')

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