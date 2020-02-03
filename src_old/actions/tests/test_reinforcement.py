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
countR = 15
countF = 10

_DataR = []
_DataF = []
_LabelR = []
_LabelF = []
defaultLabel = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]
def prepareTestData():
    global _DataR, _DataF, _LabelR, _LabelF, defaultLabel
    for i in range(100):
        _DataR.append([[1],[i]])
    _DataR = toNpArray(_DataR)

    for i in range(100):
        _DataF.append([[2],[i]])
    _DataF = toNpArray(_DataF)

    for i in range(100):
        _LabelR.append(defaultLabel.copy())
    _LabelR = toNpArray(_LabelR)

    for i in range(100):
        _LabelF.append(defaultLabel.copy())
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
fieldStep = 1
def fieldStep_mock():
    global currentAgent, fieldStep
    if currentAgent==AgentType.Rabit:
        currentAgent=AgentType.Fox
        agentsCount = countF
    else:
        currentAgent=AgentType.Rabit
        agentsCount = countR

    data = [[[fieldStep], [i]] for i in range(agentsCount)]
    labels = []
    for i in range(agentsCount):
        labels.append(defaultLabel.copy())

    agentsFeedback = [i%2 for i in range(agentsCount)]
    moves = [0 for i in range(agentsCount)]
    fieldStep += 1
    return (currentAgent, data, labels, agentsFeedback, moves)

_EDataR = []
_EDataF = []
_ELabelR = []
_ELabelF = []
def saveNpArrayToFile_mock(pathToFile, npArray):
    global _EDataR, _EDataF, _ELabelR, _ELabelF
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


class TestStringMethods(unittest.TestCase):
    global width, height, countR, countF
    
    def setUp(self):
        pass

    @mock.patch('actions.reinforcement.loadNpArrayFromFile', side_effect=loadNpArrayFromFile_mock)
    @patch.object(Field, 'step', side_effect = fieldStep_mock)
    @mock.patch('actions.reinforcement.saveNpArrayToFile', side_effect=saveNpArrayToFile_mock)
    def test_checkNewStatesAdded(self, mock_loadFile, mock_step, mock_saveToFile):
        global fieldStep, countR, countF
        fieldStep = 3
        stepsCount = 20
        actions.reinforcement.reinforcement([stepsCount, width, height, countR, countF])
        rabitSteps = stepsCount // 2 + stepsCount % 2 #rabits move first
        foxSteps = stepsCount // 2 #foxes move second
        self.assertEqual(len(_EDataR),len(_DataR) + countR * rabitSteps)
        self.assertEqual(len(_EDataF),len(_DataF) + countF * foxSteps)
        print("Stop")



    @mock.patch('actions.reinforcement.loadNpArrayFromFile', side_effect=loadNpArrayFromFile_mock)
    @patch.object(Field, 'step', side_effect = fieldStep_mock)
    @mock.patch('actions.reinforcement.saveNpArrayToFile', side_effect=saveNpArrayToFile_mock)
    def test_checkExistingStatesUpdated(self, mock_loadFile, mock_step, mock_saveToFile):
        global fieldStep, countR, countF, defaultLabel, _DataR, _DataF, _EDataR, _EDataF
        fieldStep = 1
        stepsCount = 8
        actions.reinforcement.reinforcement([stepsCount, width, height, countR, countF])

        for i in range(len(_DataR)):
            if(i<countR and i%2==1):
                self.assertTrue((_ELabelR[i]!=toNpArray(defaultLabel)).any())
            else:
                self.assertTrue((_ELabelR[i]==toNpArray(defaultLabel)).all())
                

if __name__ == '__main__':
    unittest.main()