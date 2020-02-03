from utils.Utils import toNpArray, saveNpArrayToFile, printCoordsArray, loadNpArrayFromFile
from settings import AgentType, Mode, vr, moveDirections
from settings import pathToDataR, pathToDataF, pathToLabelR, pathToLabelF
from field.Field import Field
from Trainer import train
import settings
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
    argsCount = len(args)

    targetStepsCount = 500
    if(argsCount>0):
        targetStepsCount = int(args[0])
    
    width = 250
    height = 250
    if(argsCount>=3):
        width = int(args[1])
        height = int(args[2])

    countR = int(round(height * width / 25 * 3)) # avg 3 Rabits per each 5x5 cells square
    countF = int(round(height * width / 25 * 1)) # avg 1 Fox per each 5x5 cells square 
    if(argsCount>=5):
        countR = int(args[3])
        countF = int(args[4])
    
    return (targetStepsCount, width, height, countR, countF)


def addItemsToLib(data, lib, offset, threadIdx):
    i = threadIdx
    while i< len(data):
        lib[hash(data[i][:9, :, :].data.tobytes())] = i
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
    seed = None
    settings.setDieOfHunger(False)

    if(not "PYTHONHASHSEED" in os.environ):
        raise EnvironmentError("'PYTHONHASHSEED' should be defined and set to zero in order to disable hash randomization")
    if(int(os.environ["PYTHONHASHSEED"]) != 0):
        raise EnvironmentError("'PYTHONHASHSEED' should beset to zero in order to disable hash randomization")

    test = np.array([[[1], [2]], [[3], [4]]])
    if(hash(str(test))!=7198400437482662842):
        raise EnvironmentError("Something is wrong hash randomization is enabled")

    targetStepsCount, width, height, countR, countF = parseArgs(args)

    trainDataR = []
    trainLabelsR = []
    trainDataF = []
    trainLabelsF = []

    dataRlib = {}
    dataFlib = {}

    field = Field(width, height, countR, countF, Mode.Reinforcement, seed = seed)

    decrees = 1.1   # the rate increment is decreasing if we go one step back
    increment = 0.09 # the amout by wich we encrease the label

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
        agent, data, labelCalc, agentsFeedback, moves, movesPredicted = field.step()
        data = toNpArray(data)
        label = toNpArray(movesPredicted)
        store = stores[agent-1]

        startTime = time.time()
#------------------------
        identityFeedback = np.diag(agentsFeedback)
        labelDelta = np.matmul(store.mWight, identityFeedback)

        agntMoveDirs = np.zeros([store.agentsCount, moveDirsCount])
        for i in range(store.agentsCount):
            if(moves[i]>=0): # can be -1 in case when a rabit died on previous step eaten by a fox, so current move sould not be penalized - ignoring
                agntMoveDirs[i][moves[i]] = 1

        if(store.agntMoveDirsArray is None):
            store.agntMoveDirsArray = agntMoveDirs[np.newaxis]
        else:
            store.agntMoveDirsArray = np.vstack([agntMoveDirs[np.newaxis], store.agntMoveDirsArray]) # adding moves perfomed by agents during last step

        if(len(store.agntMoveDirsArray)>vr):
            store.agntMoveDirsArray = store.agntMoveDirsArray[:-1] # removing the last row so in array we have the moves for exactly vr steps

        store.dataQ.insert(0, data)
        store.labelQ.insert(0, label)

        if(len(store.agntMoveDirsArray)==vr): # first vr-1 steps will be skipped till we 
            labelDirectionDelta = labelDelta[:, :, np.newaxis] * store.agntMoveDirsArray

            for i in range(vr):
                for j in range(store.agentsCount):
                    if(not labelDirectionDelta[i][j].any()):  # ignoring if direction delta is zero, can happen for dead agents
                        continue
                    stateHash = hash(store.dataQ[i][j][:9, :, :].data.tobytes())
                    if(not (stateHash in store.dataLib)):
                        store.labelQ[i][j] += labelDirectionDelta[i][j] 
                        store.trainData.append(store.dataQ[i][j])
                        newLabelWithMetadata = np.insert(store.labelQ[i][j][np.newaxis], [1, 1, 1], np.zeros(moveDirections), axis=0)
                        store.trainLabels.append(newLabelWithMetadata)
                        store.dataLib[stateHash] = len(store.trainData)-1
                    else:
                        updDir = np.nonzero(labelDirectionDelta[i][j])[0][0] # getting index of updated direction
                        lbl = store.trainLabels[store.dataLib[stateHash]][0]
                        argSort = np.flip(np.argsort(lbl)) # getting initial indeces of labels sorted descendig
                        if(labelDirectionDelta[i][j][updDir]>=0): # increasing label
                            if(argSort[0]==updDir and (lbl[argSort[0]]-lbl[argSort[1]])>0.2 ): # if increasing the best label and difference between best label and second best label is more than 0.2
                                continue # skipping to not allow best label to grow continuously
                        else: # decreasing label
                            if(argSort[moveDirections-1]==updDir and (lbl[argSort[moveDirections-2]]-lbl[argSort[moveDirections-1]])>0.2 ): # if decreasing the worst label and difference between worst label and second wors label is more than 0.2
                                continue # skipping to not allow worst label to continuously decrease

                        store.trainLabels[store.dataLib[stateHash]][0] += labelDirectionDelta[i][j] # updating actual label
                        store.trainLabels[store.dataLib[stateHash]][1] += labelDirectionDelta[i][j] # reinforcement delta - for statistical analisys
                        store.trainLabels[store.dataLib[stateHash]][2] += store.agntMoveDirsArray[i][j] # count reinforcements for each direction - for analisys
                        updatesCount += 1
#------------------------

        if(len(store.dataQ)>=vr):
            del store.dataQ[-1] # removing oldest state
            del store.labelQ[-1] # and coresponding label

        timeList.append(time.time()-startTime)
        if(field.aliveRabitsCount()<countR/5 or field.aliveFoxesCount()<countF/5):  # Restart the world if there are less then 1/4 of rabits or foxes  
            field = Field(width, height, countR, countF, Mode.Reinforcement, seed = seed)
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

    if(True): # removing the data that wasn't updated during reinforcement
        for i in reversed(range(len(trainLabelsR))):
            if(trainLabelsR[i][2].sum()==0):
                del trainDataR[i]
                del trainLabelsR[i]

        for i in reversed(range(len(trainLabelsF))):
            if(trainLabelsF[i][2].sum()==0):
                del trainDataF[i]
                del trainLabelsF[i]

    trainDataR = toNpArray(trainDataR)
    trainLabelsR = toNpArray(trainLabelsR)
    trainDataF = toNpArray(trainDataF)
    trainLabelsF = toNpArray(trainLabelsF)

    saveNpArrayToFile(pathToDataR, trainDataR)
    saveNpArrayToFile(pathToLabelR, trainLabelsR)
    saveNpArrayToFile(pathToDataF, trainDataF)
    saveNpArrayToFile(pathToLabelF, trainLabelsF)

    trainLabelsR = trainLabelsR[:, 0, :]
    trainLabelsF = trainLabelsF[:, 0, :]

    train(trainDataR, trainLabelsR, True, False, 75000)
    train(trainDataF, trainLabelsF, False, False, 75000)

    return