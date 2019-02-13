import unittest
from mock import patch
import mock
# from actions.reinforcement import reinforcement
import numpy as np
from settings import Mode, vr, AgentType, pathToDataR, pathToDataF, pathToLabelR, pathToLabelF
from field.Field import Field
from utils.Utils import toNpArray
import utils.Utils
import actions.reinforcement


width = 50
height = 40
countR = 10
countF = 10

_DataR = []
_DataF = []
_LabelR = []
_LabelF = []

def prepareTestData():
    global _DataR, _DataF, _LabelR, _LabelF
    for i in range(100):
        _DataR.append([[1],[i]])
    _DataR = toNpArray(_DataR)

    for i in range(100):
        _DataF.append([[2],[i]])
    _DataF = toNpArray(_DataF)

    for i in range(100):
        _LabelR.append([[0.1],[0.2],[0.3],[0.4],[0.5],[0.6],[0.7],[0.8],[0.9]])
    _LabelR = toNpArray(_LabelR)

    for i in range(100):
        _LabelF.append([[0.1],[0.2],[0.3],[0.4],[0.5],[0.6],[0.7],[0.8],[0.9]])
    _LabelF = toNpArray(_LabelF)


prepareTestData()

def loadNpArrayFromFile_mock(fileName):
    switcher = {
        pathToDataR: np.array(_DataR, copy=True),
        pathToDataF: np.array(_DataF, copy=True),
        pathToLabelR: np.array(_LabelR, copy=True),
        pathToLabelF: np.array(_LabelF, copy=True)
    }
    result = switcher.get(fileName)
    if(result is None):        
        raise ValueError('Uncnown file name: ' + fileName)

    return result

currentAgent = AgentType.Fox
def fieldStep_mock():
    global currentAgent
    if currentAgent==AgentType.Rabit:
        currentAgent=AgentType.Fox
        agentsCount = countF
    else:
        currentAgent=AgentType.Rabit
        agentsCount = countR

    data = [[[3], [i]] for i in range(agentsCount)]
    labels = []
    for i in range(agentsCount):
        labels.append([[0.1],[0.2],[0.3],[0.4],[0.5],[0.6],[0.7],[0.8],[0.9]])

    agentsFeedback = [0 for i in range(agentsCount)]
    moves = [0 for i in range(agentsCount)]
    return (currentAgent, data, labels, agentsFeedback, moves)

_EDataR = []
_EDataF = []
_ELabelR = []
_ELabelF = []

def saveNpArrayToFile_mock(pathToFile, npArray):
    if pathToFile==pathToDataR:
        _EDataR = npArray
    elif pathToFile==pathToDataF:
        _EDataF = npArray
    elif pathToFile==pathToLabelR:
        _ELabelR = npArray
    elif pathToFile==pathToLabelF:
        _ELabelF = npArray
    else:
        raise ValueError('Uncnown file name: ' + pathToFile)
    return

def loadFromFile(fileName):
    return fileName

class TestStringMethods(unittest.TestCase):
    global width, height, countR, countF
    
    def setUp(self):
        pass

    @mock.patch('actions.reinforcement.loadNpArrayFromFile', side_effect=loadNpArrayFromFile_mock)
    @patch.object(Field, 'step', side_effect = fieldStep_mock)
    @mock.patch('actions.reinforcement.saveNpArrayToFile', side_effect=loadNpArrayFromFile_mock)
    def test_reinforce(self, mock_loadFile, mock_step, mock_saveToFile):
        actions.reinforcement.reinforcement([5, width, height, countR, countF])
        print("Stop")




    @mock.patch('utils.Utils.loadNpArrayFromFile', side_effect=loadFromFile)
    @mock.patch('actions.reinforcement.loadNpArrayFromFile', side_effect=loadFromFile)
    def test_mockModuleFunction(self, mock_load, mock_loadInReinf):
        self.assertEqual(utils.Utils.loadNpArrayFromFile("asdf"), 'asdf')
        #actions.reinforcement.reinforcement([3])

    @patch.object(Field, 'step', return_value = ("a", "b", "c", "d", "e"))
    @patch.object(Field, 'aliveRabitsCount', return_value = 555)
    def test_patchMultipleMethods(self, mock_step, mock_aliveRabitsCount):
        f = Field(width, height, countR, countF, vr, Mode.Reinforcement)
        a, b, c, d, e = f.step()
        count = f.aliveRabitsCount()
        self.assertEqual(a, 'a')
        self.assertEqual(count, 555)


    @patch.object(Field, 'step')
    def test_patchOneMethod(self, stepMock):
        stepMock.return_value = ("a", "b", "c", "d", "e")
        a, b, c, d, e = Field(width, height, countR, countF, vr, Mode.Reinforcement).step()
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