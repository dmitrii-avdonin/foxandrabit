import sys
from actions.initModels import initModels
from actions.visualize import visualize



Actions = {
    "initModels" : initModels,
    "visualize" : visualize
}
    

if __name__ == "__main__":
    actionName = sys.argv[1]
    action = Actions.get(actionName)
    if(action == None):
        print("Unknown action: " + actionName)
    else:
        action(sys.argv[2:100])
