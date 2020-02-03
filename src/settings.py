
import os




fieldW = 150
fieldH = 100

RabitN = 600
FoxN = 200

vr = 4 # viewRadius: number of cell visible for estimating current situation
mr = 1 # move radius: how far the agent can step from curent position

RandomizationEnabled = False

def setDieOfHunger(value):
    global dieOfHunger
    dieOfHunger = value

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


# randomMoveP = 0.25 # the probability that the Agent will move in a random direction


# lblShape = mr*2 + 1 # label will be an array of shape [lblShape, lblShape] 
# moveDirections = lblShape**2 # number of ways an Agent can move from his current pozition (including staying on the same place)




# trainingDataDir = os.path.abspath(r"./trainingData")
# if not os.path.exists(trainingDataDir):
#     os.makedirs(trainingDataDir)
# pathToDataR = os.path.join(trainingDataDir, "dataR.mat")
# pathToDataF = os.path.join(trainingDataDir, "dataF.mat")

# pathToLabelR = os.path.join(trainingDataDir, "labelR.mat")
# pathToLabelF = os.path.join(trainingDataDir, "labelF.mat")

