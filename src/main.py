import sys
from actions.generateTrainingData import generateTrainingDataSet
from actions.initModels import initModels
from actions.startTraining import startTraining
from actions.visualize import visualize
from actions.trainFromFile import trainFromFile






Actions = {
    "initModels" : initModels,
    "trainModels" : startTraining,
    "trainFromFile" : trainFromFile,
    "visualize" : visualize,
    "generateData": generateTrainingDataSet,
    "initializeModels" : initModels
}
    

if __name__ == "__main__":
    actionName = sys.argv[1]
    action = Actions.get(actionName)
    if(action == None):
        print("Unknown action: " + actionName)
    else:
        action(sys.argv[2:100])
