from utils.Utils import toNpArray, saveNpArrayToFile, printCoordsArray
from settings import AgentType, Mode, vr
from settings import pathToDataR, pathToDataF, pathToLabelR, pathToLabelF
from field.Field import Field



def generateTrainingDataSet(args):
    trainDataR = []
    trainLabelsR = []
    trainDataF = []
    trainLabelsF = []

    width = 150
    height = 150
    countR = int(round(height * width / 25 * 3)) # avg 3 Rabits per each 5x5 cells square
    countF = int(round(height * width / 25 * 1)) # avg 1 Fox per each 5x5 cells square 
    field = Field(width, height, countR, countF, vr, Mode.DataGeneration)

    while True:    
        agent, data, label = field.step()
        trainData = trainDataR if agent==AgentType.Rabit else trainDataF
        trainLabels = trainLabelsR if agent==AgentType.Rabit else trainLabelsF

        c=0
        for i in range(len(data)):
            if data[i] not in trainData:
                trainData.append(data[i])
                trainLabels.append(label[i])
            else:
                c += 1
        if(agent==AgentType.Fox and c > countF/4 or len(trainDataF)>10000):
            break

        if(field.aliveRabitsCount<countR/4 or field.aliveFoxesCount<countF/4):  # Restart the world if there are less then 1/4 of rabits or foxes  
            field = Field(width, height, countR, countF, vr, Mode.DataGeneration)

        
    trainDataR = toNpArray(trainDataR)
    trainLabelsR = toNpArray(trainLabelsR)
    trainDataF = toNpArray(trainDataF)
    trainLabelsF = toNpArray(trainLabelsF)

    saveNpArrayToFile(pathToDataR, trainDataR)
    saveNpArrayToFile(pathToLabelR, trainLabelsR)
    saveNpArrayToFile(pathToDataF, trainDataF)
    saveNpArrayToFile(pathToLabelF, trainLabelsF)

    return