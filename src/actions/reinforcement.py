from utils.Utils import toNpArray, saveNpArrayToFile, printCoordsArray, loadNpArrayFromFile
from settings import AgentType, Mode, vr, moveDirections
from settings import pathToDataR, pathToDataF, pathToLabelR, pathToLabelF
from field.Field import Field
import time
import numpy as np
from functools import reduce
import os
import threading


class VarStore:
    def __init__(self, trainData, trainLabels, mWight, count, dataLib):
        self.dataQ = []
        self.labelQ = []
        self.agntMoveDirsArray = None
        self.trainData = trainData
        self.trainLabels = trainLabels
        self.mWight = mWight
        self.agentsCount = count
        self.dataLib = dataLib

def parseArgs(args):    
    targetStepsCount = 100
    width = 150
    height = 150
    countR = int(round(height * width / 25 * 3)) # avg 3 Rabits per each 5x5 cells square
    countF = int(round(height * width / 25 * 1)) # avg 1 Fox per each 5x5 cells square 

    argsCount = len(args)
    if(argsCount>0):
        targetStepsCount = int(args[0])

    if(argsCount>=3):
        width = int(args[1])
        height = int(args[2])

    if(argsCount>=5):
        countR = int(args[3])
        countF = int(args[4])
    
    return (targetStepsCount, width, height, countR, countF)


def addItemsToLib(data, lib, offset, threadIdx):
    i = threadIdx
    while i< len(data):
        lib[hash(data[i].data.tobytes())] = i
        i += offset
        #if threadIdx==0 and i%100==0:
        #    print(str(len(lib)))
def generateLib(data, lib):
    threads = []
    offset = 5
    for idx in range(offset):
        thread = threading.Thread(target=addItemsToLib, args=(data, lib, offset, idx,))
        threads.append(thread)
        thread.start()
    
    for idx in range(offset):
        threads[idx].join()


def reinforcement(args):
    if(not "PYTHONHASHSEED" in os.environ):
        raise EnvironmentError("'PYTHONHASHSEED' should be defined and set to zero in order to disable hash randomization")
    if(int(os.environ["PYTHONHASHSEED"]) != 0):
        raise EnvironmentError("'PYTHONHASHSEED' should beset to zero in order to disable hash randomization")

    test = np.array([[[1], [2]], [[3], [4]]])
    if(hash(str(test))!=7198400437482662842):
        raise EnvironmentError("Something is wrong hash randomization is enabled")

    targetStepsCount, width, height, countR, countF = parseArgs(args)

    # loading existing training data from files
    _dataR = loadNpArrayFromFile(pathToDataR)
    _labelR = loadNpArrayFromFile(pathToLabelR)
    _dataF = loadNpArrayFromFile(pathToDataF)
    _labelF = loadNpArrayFromFile(pathToLabelF)

    # adding aditional dimenion for metadata if it doesn't exit yet
    emptyDim = np.zeros(moveDirections)
    if(len(_labelR.shape)==2):
        _labelR = np.insert(_labelR[:,np.newaxis], [1, 1, 1], emptyDim, axis=1)
    if(len(_labelF.shape)==2):
        _labelF = np.insert(_labelF[:,np.newaxis], [1, 1, 1], emptyDim, axis=1)

    # converting to lists
    trainDataR = [a for a in _dataR]
    trainLabelsR = [a for a in _labelR]
    trainDataF = [a for a in _dataF]
    trainLabelsF = [a for a in _labelF]

    dataRlib = {}
    generateLib(_dataR, dataRlib)

    dataFlib = {}
    generateLib(_dataF, dataFlib)

    field = Field(width, height, countR, countF, Mode.Reinforcement)

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
        VarStore(trainDataF, trainLabelsF, mWightF, countF, dataFlib),
        VarStore(trainDataR, trainLabelsR, mWightR, countR, dataRlib),
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
                    if(not labelDirectionDelta[i][j].any()):  # ignoring if direction delta is zero, can happen for dead agents
                        continue
                    stateHash = hash(store.dataQ[i][j].data.tobytes())
                    if(not (stateHash in store.dataLib)):
                        store.labelQ[i][j] += labelDirectionDelta[i][j] 
                        store.trainData.append(store.dataQ[i][j])
                        newLabelWithMetadata = np.insert(store.labelQ[i][j][np.newaxis], [1, 1, 1], emptyDim, axis=0)
                        store.trainLabels.append(newLabelWithMetadata)
                        store.dataLib[stateHash] = len(store.trainData)-1
                    else:
                        store.trainLabels[store.dataLib[stateHash]][0] += labelDirectionDelta[i][j] # updating actual label
                        store.trainLabels[store.dataLib[stateHash]][1] += labelDirectionDelta[i][j] # reinforcement delta - for statistical analisys
                        store.trainLabels[store.dataLib[stateHash]][2] += store.agntMoveDirsArray[i][j] # count reinforcements for each direction - for analisys
                        updatesCount += 1
#------------------------

        if(len(store.dataQ)>=vr):
            store.dataQ.pop(0)
            store.labelQ.pop(0)

        timeList.append(time.time()-startTime)
        if(field.aliveRabitsCount()<countR/4 or field.aliveFoxesCount()<countF/4):  # Restart the world if there are less then 1/4 of rabits or foxes  
            field = Field(width, height, countR, countF, Mode.Reinforcement)
            for k in range(2):
                stores[k].agntMoveDirsArray = None
                stores[k].dataQ = []
                stores[k].labelQ = []

        stepsCount += 1
        print("-----------------------------------------")
        print("targetStepsCount = " + str(targetStepsCount))
        print("stepsCount       = " + str(stepsCount))
        print("Remaining        = " + str(targetStepsCount-stepsCount))
        print("-----------------------------------------")
    
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