from field.Field import Field
from numpy.random import randint
import numpy as np
from settings import fieldW, fieldH, FoxN, RabitN, vr, Mode
from Trainer import train
from utils.Utils import toNpArray


def generateDummyLabels(populationSize):
    labels=[]
    for j in range(populationSize): 
        label=[.0, .0, .0, .0, .0, .0, .0, .0, .0]
        direction = randint(9)
        label[direction] = .3
        labels.append(label)

    npLabels = np.array(labels, dtype=np.float32)
    return npLabels

def initModels(args):
    field = Field(fieldW, fieldH, RabitN, FoxN, vr, Mode.Initialization)

    dataR = toNpArray(field.getStatesR())
    labelR = generateDummyLabels(RabitN)

    dataF = toNpArray(field.getStatesF())
    labelF = generateDummyLabels(FoxN)

    train(dataR, labelR, True, True)
    train(dataF, labelF, False, True)
    return None