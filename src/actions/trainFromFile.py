from settings import pathToDataR, pathToDataF, pathToLabelR, pathToLabelF
from utils.Utils import loadNpArrayFromFile
from Trainer import train

def trainFromFile():
    dataR = loadNpArrayFromFile(pathToDataR)
    labelR = loadNpArrayFromFile(pathToLabelR)

    train(dataR, labelR, True, False)

    return

