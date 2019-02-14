
import os

vr = 4 # viewRadius: number of cell visible for estimating current situation 


fieldW = 150
fieldH = 100

RabitN = 600
FoxN = 200


pathToDataR = os.path.abspath(r"./trainingData/dataR.mat")
pathToDataF = os.path.abspath(r"./trainingData/dataF.mat")

pathToLabelR = os.path.abspath(r"./trainingData/labelR.mat")
pathToLabelF = os.path.abspath(r"./trainingData/labelF.mat")

class AgentType:
    Null = -1   # there is no agent
    Fox = 1
    Rabit = 2

class Mode:
    Initialization = -1
    Training = 0
    Visualization = 1
    DataGeneration = 2
    Reinforcement = 3