from settings import pathToDataR, pathToDataF, pathToLabelR, pathToLabelF
from utils.Utils import loadNpArrayFromFile, printCoordsArray
from Trainer import train
from Trainer import predict

def trainFromFile(args):
    #stepsCount = None
    if (len(args)>0):
        stepsCount = int(args[0])

    dataR = loadNpArrayFromFile(pathToDataR)
    labelR = loadNpArrayFromFile(pathToLabelR)
    if(len(labelR.shape)==3):
        labelR = labelR[:, 0, :]
    train(dataR, labelR, True, False, stepsCount)


    dataF = loadNpArrayFromFile(pathToDataF)
    labelF = loadNpArrayFromFile(pathToLabelF)
    if(len(labelF.shape)==3):
        labelF = labelF[:, 0, :]
    train(dataF, labelF, False, False, stepsCount)

    return

