from settings import pathToDataR, pathToDataF, pathToLabelR, pathToLabelF
from utils.Utils import loadNpArrayFromFile, printCoordsArray
from Trainer import train
from Trainer import predict

def trainFromFile():
    dataR = loadNpArrayFromFile(pathToDataR)
    labelR = loadNpArrayFromFile(pathToLabelR)

    #_90p = len(dataR)//100 * 90

    #trainingD, testD = dataR[:_90p,:], dataR[_90p:,:]
    #trainingL, testL = labelR[:_90p,:], _90p[pLabelR80:,:]

    train(dataR, labelR, True, False)


    dataF = loadNpArrayFromFile(pathToDataF)
    labelF = loadNpArrayFromFile(pathToLabelF)
    train(dataF, labelF, False, False)

    return

