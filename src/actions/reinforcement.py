from utils.Utils import toNpArray, saveNpArrayToFile, printCoordsArray, loadNpArrayFromFile, printCoordsArray
from settings import AgentType, Mode, vr
from settings import pathToDataR, pathToDataF, pathToLabelR, pathToLabelF
from field.Field import Field
import time
import numpy as np
from functools import reduce
from utils.myBst import MyBST



class VarStore:
    def __init__(self, trainData, trainLabels, mWight, count, bst):
        self.dataQ = []
        self.labelQ = []
        self.agntMoveDirsArray = None
        self.trainData = trainData
        self.trainLabels = trainLabels
        self.mWight = mWight
        self.agentsCount = count
        self.bst = bst

def parseArgs(args):    
    targetStepsCount = 10
    width = 150
    height = 150
    countR = int(round(height * width / 25 * 3)) # avg 3 Rabits per each 5x5 cells square
    countF = int(round(height * width / 25 * 1)) # avg 1 Fox per each 5x5 cells square 

    argsCount = len(args)
    if(argsCount>0):
        targetStepsCount = args[0]

    if(argsCount>=3):
        width = args[1]
        height = args[2]

    if(argsCount>=5):
        countR = args[3]
        countF = args[4]
    
    return (targetStepsCount, width, height, countR, countF)



def reinforcement(args):

    targetStepsCount, width, height, countR, countF = parseArgs(args)

    # loading existing training data from files
    _dataR = loadNpArrayFromFile(pathToDataR)
    _labelR = loadNpArrayFromFile(pathToLabelR)
    _dataF = loadNpArrayFromFile(pathToDataF)
    _labelF = loadNpArrayFromFile(pathToLabelF)

    # converting to lists
    trainDataR = [a for a in _dataR]
    trainLabelsR = [a for a in _labelR]
    trainDataF = [a for a in _dataF]
    trainLabelsF = [a for a in _labelF]

    bstR = MyBST()
    bstR.insertList(trainDataR)

    bstF = MyBST()
    bstF.insertList(trainDataF)

    field = Field(width, height, countR, countF, vr, Mode.Reinforcement)

    decrees = 1.2   # the rate increment is decreasing if we go one step back
    increment = 0.01 # the amout by wich we encrease the label

    vWeight = np.zeros(vr)
    inc = increment
    for i in range(vr):
        vWeight[i] = inc
        inc = inc/decrees

    mWightR =  np.repeat(vWeight[None], countR, 0).T # matrix of weigths Rabits
    mWightF =  np.repeat(vWeight[None], countF, 0).T # matrix of weigths

    moveDirsCount = 9 # number of directions where agent can move (or stay insme place)

    stores=[
        VarStore(trainDataF, trainLabelsF, mWightF, countF, bstF),
        VarStore(trainDataR, trainLabelsR, mWightR, countR, bstR),
    ]

    updatesCount = 0
    stepsCount = 0    
    timeList = []
    while stepsCount < targetStepsCount:
        agent, data, label, agentsFeedback, moves = field.step()
        data = toNpArray(data)
        label = toNpArray(label)
        store = stores[agent-1]

        startTime = time.time()
#------------------------
        identityFeedback = np.diag(agentsFeedback)
        labelDelta = np.matmul(store.mWight, identityFeedback)

        agntMoveDirs = np.zeros([store.agentsCount, moveDirsCount])
        for i in range(store.agentsCount):
            agntMoveDirs[i][moves[i]] = 1

        if(store.agntMoveDirsArray is None):
            store.agntMoveDirsArray = agntMoveDirs[np.newaxis]
        else:
            store.agntMoveDirsArray = np.vstack([agntMoveDirs[np.newaxis], store.agntMoveDirsArray]) # adding moves perfomed by agents during last step

        if(len(store.agntMoveDirsArray)>vr):
            store.agntMoveDirsArray = store.agntMoveDirsArray[:-1] # removing the last row so in array we have the moves for exactly vr steps

        store.dataQ.append(data)
        store.labelQ.append(label)

        if(len(store.agntMoveDirsArray)==vr): # first vr-1 steps will be skipped till we 
            labelDirectionDelta = labelDelta[:, :, np.newaxis] * store.agntMoveDirsArray

            for i in range(vr):
                for j in range(store.agentsCount):
                    found = store.bst.search(store.dataQ[i][j])
                    if(found is None):
                        store.labelQ[i][j] += labelDirectionDelta[i][j] 
                        store.trainData.append(store.dataQ[i][j])
                        store.trainLabels.append(store.labelQ[i][j])
                        store.bst.insert(store.dataQ[i][j], len(store.trainData)-1)
                    else:
                        store.trainLabels[found.tag] += labelDirectionDelta[i][j] 
                        updatesCount += 1
#------------------------

        if(len(store.dataQ)>=vr):
            store.dataQ.pop(0)
            store.labelQ.pop(0)

        timeList.append(time.time()-startTime)
        if(field.aliveRabitsCount()<countR/4 or field.aliveFoxesCount()<countF/4):  # Restart the world if there are less then 1/4 of rabits or foxes  
            field = Field(width, height, countR, countF, vr, Mode.Reinforcement)

        stepsCount += 1
    
    #====================================================================================================
    print("Average step processing time: " + str(reduce(lambda x, y: x + y, timeList) / len(timeList)) )
    print("Updates Count: " + str(updatesCount))    
    trainDataR = toNpArray(trainDataR)
    trainLabelsR = toNpArray(trainLabelsR)
    trainDataF = toNpArray(trainDataF)
    trainLabelsF = toNpArray(trainLabelsF)

    saveNpArrayToFile(pathToDataR, trainDataR)
    saveNpArrayToFile(pathToLabelR, trainLabelsR)
    saveNpArrayToFile(pathToDataF, trainDataF)
    saveNpArrayToFile(pathToLabelF, trainLabelsF)

    return