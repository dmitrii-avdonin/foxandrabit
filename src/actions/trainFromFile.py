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
    train(dataR, labelR, True, False, stepsCount)


    dataF = loadNpArrayFromFile(pathToDataF)
    labelF = loadNpArrayFromFile(pathToLabelF)
    train(dataF, labelF, False, False, stepsCount)

    return

