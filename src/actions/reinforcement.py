from utils.Utils import toNpArray, saveNpArrayToFile, printCoordsArray
from settings import AgentType, Mode, vr
from settings import pathToDataR, pathToDataF, pathToLabelR, pathToLabelF
from field.Field import Field



def reinforcement(args):

    targetStepsCount = int(args[0])

    trainDataR = []
    trainLabelsR = []
    trainDataF = []
    trainLabelsF = []

    width = 150
    height = 150
    countR = int(round(height * width / 25 * 3)) # avg 3 Rabits per each 5x5 cells square
    countF = int(round(height * width / 25 * 1)) # avg 1 Fox per each 5x5 cells square 
    field = Field(width, height, countR, countF, vr, Mode.DataGeneration)

    dataQueueR = []
    labelQueueR = [] 
    dataQueueF = []
    labelQueueF = [] 

    stepsCount = 0
    while stepsCount < targetStepsCount:
        agent, data, label, agentsFeedback = field.step()

        if(agent == AgentType.Rabit):
            dataQueue = dataQueueR
            labelQueue = labelQueueR
            trainData = trainDataR
            trainLabels = trainLabelsR
        else:
            dataQueue = dataQueueF
            labelQueue = labelQueueF
            trainData = trainDataF
            trainLabels = trainLabelsF


        dataQueue.append(data)
        labelQueue.append(label)


        if(len(dataQueue)>=vr):
            oldestData = dataQueue.pop(0)
            oldestLabel = labelQueue.pop(0)
            for i in range(len(oldestData)):
                if oldestData[i] not in trainData:
                    trainData.append(oldestData[i])
                    trainLabels.append(oldestLabel[i])
                else:
                    trainLabels[i] = oldestLabel[i]

        if(field.aliveRabitsCount<countR/4 or field.aliveFoxesCount<countF/4):  # Restart the world if there are less then 1/4 of rabits or foxes  
            field = Field(width, height, countR, countF, vr, Mode.DataGeneration)

        stepsCount += 1
#====================================================================================================
        
    trainDataR = toNpArray(trainDataR)
    trainLabelsR = toNpArray(trainLabelsR)
    trainDataF = toNpArray(trainDataF)
    trainLabelsF = toNpArray(trainLabelsF)

    saveNpArrayToFile(pathToDataR, trainDataR)
    saveNpArrayToFile(pathToLabelR, trainLabelsR)
    saveNpArrayToFile(pathToDataF, trainDataF)
    saveNpArrayToFile(pathToLabelF, trainLabelsF)

    return