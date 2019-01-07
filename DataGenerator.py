from numpy.random import randint
from collections import defaultdict
import numpy as np
from Trainer import train
from Trainer import predict
from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import SingleGrid
from mesa.visualization.modules import CanvasGrid
from mesa.visualization.ModularVisualization import ModularServer

fieldW = 150
fieldH = 100

RabitN = 600
FoxN = 200

FoxAgentType = 1
RabitAgentType = 2


vr = 2 # viewRadius: number of cell visible for estimating current situation 



class MyAgent(Agent):
    global field
    def __init__(self, agType, unique_id, model, initialFullness):
        super().__init__(unique_id, model)
        self.agentType = agType
        self.fullness = initialFullness
        self.nextPos = (0, 0)
        self.pos = (0, 0)
        self.isDead = False
        self.tempFullness = 0
        self.feedback = 0


    def setDead(self, dryRun = False):
        self.feedback += Actions.death
        if not dryRun:
            self.isDead = True
            self.model.grid.remove_agent(self)


    def setNextPos(self, direction):
        (x, y) = self.pos
        (dx, dy) = self.directionToShift(direction)
        self.nextPos = (x+dx, y+dy)


    def posToDirection(self, aPos):
        ax, ay = aPos
        x, y = self.pos
        shift = (ax-x, ay-y)

        switcher = {            
            (-1, -1): 1, #    ↙
            ( 0, -1): 2, #    ↓
            ( 1, -1): 3, #    ↘
            (-1,  0): 4, #    ⟵
            ( 0,  0): 5, #    0
            ( 1,  0): 6, #    ⟶
            (-1,  1): 7, #    ↖
            ( 0,  1): 8, #    ↑
            ( 1,  1): 9, #    ↗
        }

        direction = switcher.get(shift)-1
        if direction == None: 
            raise ValueError('Cannot convet to direction follwing shift ' + str(shift))
        
        return direction

    def directionToShift(self, direction): # 

        if direction<0 or direction>8:
            raise ValueError('direction can be a value in range [0, 8]. Current value: ' + direction)

        switcher = {            
            1: (-1, -1), #    ↙
            2: ( 0, -1), #    ↓
            3: ( 1, -1), #    ↘
            4: (-1,  0), #    ⟵
            5: ( 0,  0), #    0
            6: ( 1,  0), #    ⟶
            7: (-1,  1), #    ↖
            8: ( 0,  1), #    ↑
            9: ( 1,  1), #    ↗
        }
        return switcher.get(direction+1)


class Actions:
    #general:
    goAutOfBounds = -1          #attempt to move outside of the field 
    goToBusyBySameKind = -1     #attempt to move on a cell ocupied by other Agent of same kind
    death = -3                  #agent has died during this run
    eatFood = +1                #agent eat some food during this round 
    hungerIncreased = -1        #agent hunger increased during this round

    #Rabit speciffic ActionsScore:
    goToCellWithFox = -2

class Fox(MyAgent):
    InitialFullness = 2.
    Hunger = 0.2
    EatARabit = 1.  # if eats a rabit its fullness will be increased by this amount
    def __init__(self, unique_id, model):
        MyAgent.__init__(self, FoxAgentType, unique_id, model, Fox.InitialFullness)


    def calcFeedback(self, posToGo, dryRun = True):
        self.feedback = 0.
        self.tempFullness = self.fullness

        if self.model.grid.out_of_bounds(self.nextPos):
            self.feedback += Actions.goAutOfBounds
            self.applyHungerAndEvaluateFullness(dryRun)
            return 

        if(self.nextPos == self.pos):
            self.applyHungerAndEvaluateFullness(dryRun)
            return             

        if not self.model.grid.is_cell_empty(self.nextPos) :
            (x, y) = self.nextPos
            agentOnNextPos = self.model.grid.grid[x][y]
            if(agentOnNextPos.agentType == self.agentType):
                self.feedback += Actions.goToBusyBySameKind
                self.applyHungerAndEvaluateFullness(dryRun)
                return
            else:
                self.feedback += Actions.eatFood
                self.tempFullness += Fox.EatARabit
                agentOnNextPos.setDead(dryRun)
        else:
            self.applyHungerAndEvaluateFullness(dryRun)

        if(not self.isDead and not dryRun):
            self.model.grid.move_agent(self, self.nextPos)

        return


    def applyHungerAndEvaluateFullness(self, dryRun = True):
        self.feedback += Actions.hungerIncreased
        self.tempFullness -= Fox.Hunger
        if(self.tempFullness <= 0):
            self.setDead(dryRun)    


    def step(self):
        self.calcFeedback(self.nextPos, False)
        self.fullness = self.tempFullness
        return



class Rabit(MyAgent):
    InitialFullness = 5.
    Hunger = 0.5 # fullness decrease per step
    MaxEat = 0.6 # max how much can eat one time if it is available on current field cell
    def __init__(self, unique_id, model):
        MyAgent.__init__(self, RabitAgentType, unique_id, model, Rabit.InitialFullness)

    def eatGrassOnCurrentFiledCellAndEvaluateFullness(self, dryRun):
        (x,y) = self.pos
        actualEat = self.model.cells[x][y].removeFood(Rabit.MaxEat, dryRun)
        self.feedback += Actions.eatFood * actualEat/Rabit.MaxEat
        self.feedback += Actions.hungerIncreased * max((Rabit.Hunger - actualEat), 0)/Rabit.Hunger
        self.tempFullness += actualEat
        self.tempFullness -= Rabit.Hunger
        if(self.tempFullness <= 0):
            self.setDead(dryRun)

    # posToGo - next position to go
    def calcFeedback(self, posToGo, dryRun = True):
        self.feedback = 0.
        self.tempFullness = self.fullness

        if self.model.grid.out_of_bounds(posToGo):
            self.feedback += Actions.goAutOfBounds
            self.eatGrassOnCurrentFiledCellAndEvaluateFullness(dryRun)
            return

        if(posToGo == self.pos):
            self.eatGrassOnCurrentFiledCellAndEvaluateFullness(dryRun)
            return
        
        (x, y) = posToGo
        if not self.model.grid.is_cell_empty(posToGo):            
            agentOnNextPos = self.model.grid.grid[x][y]
            if(agentOnNextPos.agentType == self.agentType):
                self.feedback += Actions.goToBusyBySameKind
                self.eatGrassOnCurrentFiledCellAndEvaluateFullness(dryRun)
            else:
                self.feedback += Actions.goToCellWithFox                
                self.setDead(dryRun)
                # we do not increase here the fox fullness because this increase is not determinde by fox decision
            return
        
        if not dryRun:
            self.model.grid.move_agent(self, posToGo)
            self.model.cells[x][y].Rabit = self

        self.eatGrassOnCurrentFiledCellAndEvaluateFullness(dryRun)

        return

    def step(self):
        self.calcFeedback(self.nextPos, False)
        self.fullness = self.tempFullness
        return


    

class Field(Model):
    def __init__(self, width, height, num_rabits, num_foxes, viewRadius, trainingMode=True):
        self.trainingMode = trainingMode
        self.running = True
        self.rabitsMove = True

        self.width = width
        self.height = height
        self.num_rabits = num_rabits
        self.num_foxes = num_foxes
        self.viewRadius = viewRadius

        self.cells = [[FieldCell() for i in range(self.height)] for j in range(self.width)]

        self.grid = SingleGrid(width, height, False)
        self.scheduleRabit = RandomActivation(self)
        self.scheduleFox = RandomActivation(self)


        self.rabits = []
        for i in range(self.num_rabits):
            a = Rabit(i, self)
            self.grid.position_agent(a, x="random", y="random")
            self.scheduleRabit.add(a)
            self.rabits.append(a)
            
        self.foxes = []
        for i in range(self.num_foxes):
            a = Fox(i, self)
            self.grid.position_agent(a, x="random", y="random")
            self.scheduleFox.add(a)
            self.foxes.append(a)


    def getStatesR(self):
        return self.getStates(self.rabits)


    def getStatesF(self):
        return self.getStates(self.foxes)


    def getStates(self, agentList):
        states = []
        for a in agentList:
            nbh = self.get_neighborhood(a.pos)
            vr = self.viewRadius

            agentState = [[ [] for j in range(vr*2 +1)] for i in range(vr*2 +1)]
            for i in range(vr*2+1):
                for j in range(vr*2+1):
                    (x,y) = nbh[i][j]
                    if self.grid.out_of_bounds((x, y)):  #this cell can't be reached 
                        agentState[i][j] = [-1, -1, a.fullness]
                    else:
                        food = self.cells[x][y].food
                        agent = self.grid[x][y]
                        agentType = 0 if agent==None else agent.agentType
                        agentState[i][j] = [food, agentType, a.fullness]
            states.append(agentState)

        return np.array(states, dtype=np.float32)

    # { {1,2}, {2, 3}, {3, 4}}
    # width - number of columns = 3
    # height - number of rows   = 2
    def printCoordsArray(self, arr, elemIdx=None, printAsInt=False):
            width = len(arr)
            height = len(arr[0])

            for i in reversed(range(height)):
                line = ""
                for j in range(width):
                    val = 0
                    if(elemIdx != None):
                        val = arr[j][i][elemIdx]
                    else:
                        val = arr[j][i]

                    if(not printAsInt and (isinstance(val, float) or isinstance(val, np.float32))):
                        line += "{0:6.2f} ".format(val) 
                    else:
                        line += "{0:6.0f} ".format(val)
                print(line)
            print()      


    # vr - viewRadius
    def get_neighborhood(self, pos, vr=-1):
        x, y = pos
        if vr==-1:
            vr=self.viewRadius

        coords = [[(0, 0) for j in range(vr*2 +1)] for i in range(vr*2 +1)]
        for dy in range(-vr, vr + 1):
            for dx in range(-vr, vr + 1):
                coords[vr+dx][vr+dy]= (x+dx, y+dy)

        return coords

    def get_Lables(self, agentList):
        allLabels = []
        stepSize = 1  #how far can the agent move on both x and y coords
        for a in agentList:
            r1 = self.get_neighborhood(a.pos, stepSize) # coords of all cells where the agent can move
            
            size = len(r1) * len(r1[0]) # the number of positions where the agent can move including staying where it is
            agentLables = [0] * size
            
            for i in range(stepSize*2 +1):
                for j in range(stepSize*2 +1):
                    direction = a.posToDirection(r1[i][j]) # the direction coresponding to given position
                    a.calcFeedback(r1[i][j])
                    agentLables[direction] = a.feedback
            
            allLabels.append(agentLables)
        
        return np.array(allLabels, dtype=np.float32) 



    def setNextPos(self, agentsList, shifts):
        for i in range(len(agentsList)):
            agentsList[i].setNextPos(shifts[i])

    def clearAgentsInFiledCells(self):
        for j in range(self.width):
            for i in range(self.height):
                self.cells[j][i].Rabit = None 

    def increaseFoodInFiledCells(self):
        for j in range(self.width):
            for i in range(self.height):
                self.cells[j][i].incFood() 

    def removeDead(self, agentList, scheduler):
        dead = [x for x in agentList if x.isDead]
        for a in dead:
            scheduler.remove(a)
            agentList.remove(a)

    def removeDeadRabits(self):
        self.removeDead(self.rabits, self.scheduleRabit)

    def removeDeadFoxes(self):
        self.removeDead(self.foxes, self.scheduleFox)


    def getShift(self, curentPos, radius):
        return range(curentPos-radius, curentPos+radius+1)

    def getLables(self, states):
        feedback = []
        vr = self.viewRadius
        mr = 1  # move radius - how far the agent can step from curent position
        
        for i in range(len(states)): # calculating feedback for each state
            label = [[0 for i in range(vr+1)] for j in range(vr+1)]
            state = states[i]
            self.printCoordsArray(state, 0)
            self.printCoordsArray(state, 1, True)

            # calculating the feedback for each direction where the agend can go
            for dx in self.getShift(vr, mr): # shift by x for current agent - the agent is in the center of the crState Array = crState[vr][vr]
                for dy in self.getShift(vr, mr): # samve for y coordinate  
                    lbl = 0.0          
                    for cx in self.getShift(dx, 1): # it is expected that vr is at leas mr+1 otherwise we can get out of range
                        for cy in self.getShift(dy, 1): # it is expected that vr is at leas mr+1 otherwise we can get out of range
                            cell = state[cx][cy]
                            if(cx==dx and cy==dy): #this is the direction cel
                                if(cell[1]==FoxAgentType):
                                    lbl += -4

                                if((cx!=vr or cy!=vr) and cell[1]==RabitAgentType): # first condition to avoid that the agent (whose state we analize) adds a minus to his current location
                                    lbl += -1
                                lbl += cell[0]
                            else:
                                if(cell[1]==FoxAgentType):
                                    lbl -= 2
                                lbl += cell[0] * 0.1
                            
                    label[dx-1][dy-1] = lbl
            self.printCoordsArray(label)
            feedback.append(label)

        return feedback

    def step(self):
        print("RCount " + str(len(self.rabits)) )
        print("FCount " + str(len(self.foxes)) )

        if(len(self.rabits)==0 or len(self.foxes)==0):
            self.running = False
            return

        if self.rabitsMove:
            self.clearAgentsInFiledCells() # scheduleRabit.step() will initialize the next filedCells with Rabits 
            
            dataR = self.getStatesR()
            rabitMoves = predict(dataR, True)

            if self.trainingMode:  # get labels for rabits
                labelR = self.get_Lables(self.rabits)
                
            labelR1 = self.getLables(dataR)
            self.setNextPos(self.rabits, rabitMoves)        
            self.scheduleRabit.step()
            self.removeDeadRabits() # removing rabits that have died of starvation or commited suicide

            if self.trainingMode:
                train(dataR, labelR, True, False)        #train rabits
        else:
            dataF = self.getStatesF()
            foxMoves = predict(dataF, False)

            if self.trainingMode: # get labels for foxes
                labelF = self.get_Lables(self.foxes)

            self.setNextPos(self.foxes, foxMoves)        
            self.scheduleFox.step()

            self.removeDeadRabits()
            self.removeDeadFoxes()

            self.increaseFoodInFiledCells() # grass is growing in cells

            if self.trainingMode:
                train(dataF, labelF, False, False)       #train foxes

        self.rabitsMove = not self.rabitsMove
        return      
 

class FieldCell:
    MaxFood = 0.9
    def __init__(self):
        self.Rabit = None
        self.foodExists = False
        self.food = 0.
        if randint(10) < 2:
            self.food = 0.9
            self.foodExists = True

    def removeFood(self, requiredAmount, dryRun):
        actualAmount = min(self.food, requiredAmount)
        if not dryRun:
            self.food -= actualAmount
        return actualAmount

    def incFood(self):
        if not self.foodExists:
            return

        if(self.Rabit == None):
            self.food += 0.3
        else:
            self.food += 0.

        self.food = self.food if self.food<FieldCell.MaxFood else FieldCell.MaxFood


def generateDummyLabels(populationSize):
    labels=[]
    for j in range(populationSize): 
        label=[.0, .0, .0, .0, .0, .0, .0, .0, .0]
        direction = randint(9)
        label[direction] = .3
        labels.append(label)

    npLabels = np.array(labels, dtype=np.float32)
    return npLabels

def initModels():
    field = Field(fieldW, fieldH, RabitN, FoxN, vr)

    dataR = field.getStatesR()
    labelR = generateDummyLabels(RabitN)

    dataF = field.getStatesF()
    labelF = generateDummyLabels(FoxN)

    train(dataR, labelR, True, True)
    train(dataF, labelF, False, True)
    return None


class MyCanvasGrid(CanvasGrid):
    def __init__(self, rabit_portrayal_method, fox_portrayal_method, grid_width, grid_height,
                 canvas_width, canvas_height):
        super().__init__(None, grid_width, grid_height, canvas_width, canvas_height)
        self.rabit_portrayal_method = rabit_portrayal_method
        self.fox_portrayal_method = fox_portrayal_method


    def render(self, model):
        grid_state = defaultdict(list)
        for x in range(model.grid.width):
            for y in range(model.grid.height):
                cell_objects = model.grid.get_cell_list_contents([(x, y)])
                for obj in cell_objects:
                    if obj.agentType == RabitAgentType:
                        portrayal = self.rabit_portrayal_method(obj)
                    else: 
                        portrayal = self.fox_portrayal_method(obj)

                    if portrayal:
                        portrayal["x"] = x
                        portrayal["y"] = y
                        portrayal["fullness"] = obj.fullness
                        portrayal["unique_id"] = obj.unique_id
                        grid_state[portrayal["Layer"]].append(portrayal)

        return grid_state        

def visualize():
    grid = MyCanvasGrid(rabit_portrayal, fox_portrayal, fieldW, fieldW, 1500, 1000)
    server = ModularServer(Field,
                        [grid],
                        "Rabit VS Fox Model",
                        {"width": fieldW , "height": fieldW, "num_rabits": RabitN, "num_foxes": FoxN, "viewRadius": vr, "trainingMode": False})
    server.port = 8521 # The default
    server.launch()

def rabit_portrayal(agent):
    portrayal = {"Shape": "circle",
                 "Filled": "true",
                 "Layer": 0,
                 "Color": "blue",
                 "r": 0.5}
    return portrayal    

def fox_portrayal(agent):
    portrayal = {"Shape": "circle",
                 "Filled": "true",
                 "Layer": 0,
                 "Color": "red",
                 "r": 0.9}
    return portrayal    


def startTraining():
    #field = Field(fieldW*3, fieldH*4, RabitN*5, FoxN*10, vr)
    field = Field(fieldW, fieldH, RabitN, FoxN, vr)
    runStats = []
    restart = 0
    iterationsCount = 0

    while True:
        if(len(field.rabits)<RabitN/2 or len(field.foxes)<FoxN/2): 
            runStats.append({"restart": restart, "iterationsCount": iterationsCount, "rabitsLeft": len(field.rabits), "foxesLeft": len(field.foxes)})
            field = Field(fieldW, fieldH, RabitN, FoxN, vr)            
            restart += 1
            iterationsCount = 0
        field.step()
        iterationsCount += 1


if __name__ == "__main__":
    #initModels()
    startTraining()
    #visualize()
