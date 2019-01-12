import sys
from actions.generateTrainingData import generateTrainingDataSet
from actions.initModels import initModels
from actions.startTraining import startTraining
from actions.visualize import visualize






Actions = {
    "initModels" : initModels,
    "trainModels" : startTraining,
    "visualize" : visualize,
    "generateData": generateTrainingDataSet 
}
    

if __name__ == "__main__":
    actionName = sys.argv[1]
    action = Actions.get(actionName)
    if(action == None):
        print("Unknown action: " + actionName)
    else:
        action()
