


vr = 2 # viewRadius: number of cell visible for estimating current situation 


fieldW = 150
fieldH = 100

RabitN = 600
FoxN = 200


pathToDataR = "./trainingData/dataR.csv"
pathToDataF = "./trainingData/dataF.csv"

pathToLabelR = "./trainingData/labelR.csv"
pathToLabelF = "./trainingData/labelF.csv"

class AgentType:
    Null = -1   # there is no agent
    Fox = 1
    Rabit = 2

class Mode:
    Training = 0
    Visualization = 1
    DataGeneration = 2    