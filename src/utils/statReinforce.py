from Utils import printCoordsArray, loadNpArrayFromFile
from matplotlib.ticker import NullFormatter  # useful for `logit` scale
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm
import sys

from time import time

sys.path.append('.\src')
from settings import pathToDataR, pathToDataF, pathToLabelR, pathToLabelF, moveDirections

global data, label, delta, count, figName

def analyzeRabitsData():
    plt.figure(figName)

    labelDistributionMin(plt)
    labelDistributionMax(plt)

    updatesCount(plt)

    updateSize(plt)

    plt.gca().yaxis.set_minor_formatter(NullFormatter())
    plt.subplots_adjust(top=0.92, bottom=0.08, left=0.10, right=0.95, hspace=0.25,
                    wspace=0.35)
    plt.show()




def labelDistributionMin(plt):
    lbl = [min(a) for a in label]
    m = min(lbl)
    M = max(lbl)
    stepNr = 10
    counts = [0 for i in range(stepNr)]
    step = (M-m)/stepNr
    for i in range(stepNr):
        for v in lbl:
            if(m<=v and v<(m+step)):
                counts[i] += 1
        m += step

    m = min(lbl)
    labels =  [round(m + step*i, 1) for i in range(stepNr)]

    plt.subplot(223)
    plt.bar(range(stepNr), counts, tick_label=labels)
    plt.yscale('log')
    plt.title('Label min value distribution')
    plt.xlabel('Value')
    plt.ylabel('Number of Labels')
    plt.grid(True)

    for i, v in enumerate(counts):
        plt.text(i , 3, str(v), color='black', verticalalignment='bottom', rotation=90)


def labelDistributionMax(plt):
    lbl = [max(a) for a in label]
    m = min(lbl)
    M = max(lbl)
    stepNr = 10
    counts = [0 for i in range(stepNr)]
    step = (M-m)/stepNr
    for i in range(stepNr):
        for v in lbl:
            if(m<=v and v<(m+step)):
                counts[i] += 1
        m += step

    m = min(lbl)
    labels =  [round(m + step*i, 1) for i in range(stepNr)]

    plt.subplot(224)
    plt.bar(range(stepNr), counts, tick_label=labels)
    plt.yscale('log')
    plt.title('Label max value distribution')
    plt.xlabel('Value')
    plt.ylabel('Number of Labels')
    plt.grid(True)

    for i, v in enumerate(counts):
        plt.text(i , 5, str(v), color='black', verticalalignment='bottom', rotation=90)


def updatesCount(plt):
    # Reinforcement eficiency investigation
    #unique, counts = np.unique(np.array([a.sum() for a in count]), return_counts=True)
    unique, counts = np.unique(np.array([a.max() for a in count]), return_counts=True)

    plt.subplot(221)
    plt.bar(range(len(unique)), counts, tick_label=unique.astype(int))
    plt.yscale('log')
    plt.title('Update Count')
    plt.xlabel('Number of times label was updated')
    plt.ylabel('Number of Labels')
    plt.grid(True)

    for i, v in enumerate(counts):
        plt.text(i , 2 , str(v), color='black', verticalalignment='bottom', rotation=90)


def updateSize(plt):
    #avgAbsDelta =  np.array([ np.sum(np.abs(a))/len(a) for a in delta if np.any(a)])
    avgAbsDelta =  np.array([ np.max(np.abs(a)) for a in delta if np.any(a)])
    bins =  [i * 0.05 for i in range(100)]
    digitized = np.digitize(avgAbsDelta, bins)
    unique, counts = np.unique(digitized, return_counts=True)
    labels =  ["<" + str(round(bins[u-1], 2)) for u in unique]

    plt.subplot(222)
    plt.bar(range(len(unique)), counts, tick_label=labels)
    plt.yscale('log')
    plt.title('Update Amount')
    plt.xlabel('Label average absolute update amount ')
    plt.ylabel('Number of Labels')
    plt.grid(True)

    for i, v in enumerate(counts):
        plt.text(i , 3, str(v), color='black', verticalalignment='bottom', rotation=90)



if __name__ == "__main__":
    global data, label, delta, count, figName

    target = sys.argv[1]
    if(target=="R"):
        pathToData = pathToDataR
        pathToLabel = pathToLabelR
        figName = "Rabits"
    elif(target=="F"):
        pathToData = pathToDataF
        pathToLabel = pathToLabelF
        figName = "Foxes"
    else:
        raise Exception("Unknown target, expected 'F' or 'R'") 

    figName += " labels reinforcement stats"

    data = loadNpArrayFromFile(pathToData)
    label = loadNpArrayFromFile(pathToLabel)
    # adding aditional dimenion for metadata if it doesn't exit yet
    emptyDim = np.zeros(moveDirections)
    if(len(label.shape)==2):
        label = np.insert(label[:,np.newaxis], [1, 1, 1], emptyDim, axis=1)    


    delta = label[:, 1, :]
    count = label[:, 2, :]
    label = label[:, 0, :]


    analyzeRabitsData()