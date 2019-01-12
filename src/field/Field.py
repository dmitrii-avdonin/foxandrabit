from mesa import Model
from .FieldCell import FieldCell
import sys
sys.path.append('..')
from agents.Rabit import Rabit
from agents.Fox import Fox
import numpy as np
from settings import Mode, AgentType
from Trainer import train
from Trainer import predict
from mesa.time import RandomActivation
from mesa.space import SingleGrid

class Field(Model):
    def __init__(self, width, height, num_rabits, num_foxes, viewRadius, mode):
        self.mode = mode
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

        return states

    # { {1,2}, {2, 3}, {3, 4}}
    # width - number of columns = 3
    # height - number of rows   = 2
    def printCoordsArray(self, arr, elemIdx=None, printAsInt=False):
            width = len(arr)
            hasColumns = isinstance(arr[0], (list,)) or isinstance(arr[0], (np.ndarray,))
            height = len(arr[0]) if hasColumns else 1

            for i in reversed(range(height)):
                line = ""
                for j in range(width):
                    val = 0
                    if(elemIdx != None):
                        val = arr[j][i][elemIdx] if hasColumns else arr[j][elemIdx]
                    else:
                        val = arr[j][i] if hasColumns else arr[j]

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

    def describeSituation(self, data, direction):
        label = self.getLablesR(data, True)
        for i in range(len(label)):
            x= direction[i] % 3
            y= direction[i] // 3 
            if(label[i][x][y]<0):
                self.printCoordsArray(data[i], 1, True) # printing agents location
                self.printCoordsArray(label[i]) # printing 2D labels for each directions
                print("predicted direction: " + str(direction[i] + 1))
                print("===================================================")        


    def getShift(self, curentPos, radius):
        return range(curentPos-radius, curentPos+radius+1)

    def getLablesR(self, states, returnMatix=False):
        feedback = []
        vr = self.viewRadius
        mr = 1  # move radius - how far the agent can step from curent position
        
        for i in range(len(states)): # calculating feedback for each state
            label = [[0 for i in range(vr+1)] for j in range(vr+1)]
            state = states[i]
            #self.printCoordsArray(state, 0) #printing food amount on cells
            #self.printCoordsArray(state, 1, True) # printing agents location

            # calculating the feedback for each direction where the agend can go
            for dx in self.getShift(vr, mr): # shift by x for current agent - the agent is in the center of the crState Array = crState[vr][vr]
                for dy in self.getShift(vr, mr): # samve for y coordinate  
                    lbl = 0.0          
                    for cx in self.getShift(dx, 1): # it is expected that vr is at leas mr+1 otherwise we can get out of range
                        for cy in self.getShift(dy, 1): # it is expected that vr is at leas mr+1 otherwise we can get out of range
                            cell = state[cx][cy]
                            if(cx==dx and cy==dy): #this is the direction cel
                                if(cell[1]==AgentType.Fox):
                                    lbl += -4

                                if((cx!=vr or cy!=vr) and cell[1]==AgentType.Rabit): # first condition to avoid that the agent (whose state we analize) adds a minus to his current location
                                    lbl += -1

                                if(cell[1]==-1):  # a wall, cannot go there
                                    lbl += -2
                                else:
                                    lbl += cell[0]
                            else:
                                if(cell[1]==AgentType.Fox):
                                    lbl -= 2
                                if(cell[1]==-1):  # a wall, cannot go there
                                    lbl += -1
                                else:
                                    lbl += cell[0] * 0.1

                            
                    label[dx-1][dy-1] = lbl
            #self.printCoordsArray(label) # printing 2D labels for each directions
            if returnMatix:
               feedback.append(label)
            else:             
                flatLabel = self.flatFeedback(label)
                #self.printCoordsArray(flatLabel) # printing 1D labels for each directions
                feedback.append(flatLabel)

        return feedback



    def getLablesF(self, states):
        feedback = []
        vr = self.viewRadius
        mr = 1  # move radius - how far the agent can step from curent position
        
        for i in range(len(states)): # calculating feedback for each state
            label = [[0 for i in range(vr+1)] for j in range(vr+1)]
            state = states[i]
            #self.printCoordsArray(state, 0) #printing food amount on cells
            #self.printCoordsArray(state, 1, True) # printing agents location

            # calculating the feedback for each direction where the agend can go
            for dx in self.getShift(vr, mr): # shift by x for current agent - the agent is in the center of the crState Array = crState[vr][vr]
                for dy in self.getShift(vr, mr): # samve for y coordinate  
                    lbl = 0.0          
                    for cx in self.getShift(dx, 1): # it is expected that vr is at leas mr+1 otherwise we can get out of range
                        for cy in self.getShift(dy, 1): # it is expected that vr is at leas mr+1 otherwise we can get out of range
                            cell = state[cx][cy]
                            if(cx==dx and cy==dy): #this is the direction cel
                                if(cell[1]==AgentType.Rabit):
                                    lbl += 2

                                if((cx!=vr or cy!=vr) and cell[1]==AgentType.Fox): # first condition to avoid that the agent (whose state we analize) adds a minus to his current location
                                    lbl += -1
                                if(cell[1]==-1):  # a wall, cannot go there
                                    lbl += -1
                            else:
                                if(cell[1]==AgentType.Rabit):
                                    lbl += 1
                                if(cell[1]==-1):  # a wall, cannot go there
                                    lbl += -0.5                                    

                            
                    label[dx-1][dy-1] = lbl
            #self.printCoordsArray(label) # printing 2D labels for each directions
            flatLabel = self.flatFeedback(label)
            #self.printCoordsArray(flatLabel) # printing 1D labels for each directions
            feedback.append(flatLabel)

        return feedback

    # converts a 3x3 feedback into a 1x9 form
    # 3x3 (list of columns) feedback represents the directions like on keybord numpad 
    # 1x9 will flatten the feedback like rearangig the numpad keys in a line in acending order 
    def flatFeedback(self, fb):
        fbWidth = 3       
        fbHeight = 3
        result = [0.] * 9
        for y in range(fbHeight):
            for x in range(fbWidth):
                result[fbWidth*y + x] = fb[x][y]
        return result


    def toNpArray(self, lst):
        return np.array(lst, dtype=np.float32)


    def step(self):
        print("RCount " + str(len(self.rabits)) )
        print("FCount " + str(len(self.foxes)) )

        if(len(self.rabits)==0 or len(self.foxes)==0):
            self.running = False
            return
        
        labels = None
        data = None
        agentType = -1

        if self.rabitsMove:
            agentType = AgentType.Rabit
            self.clearAgentsInFiledCells() # scheduleRabit.step() will initialize the next filedCells with Rabits 
            
            data = self.getStatesR()
            rabitMoves = predict(self.toNpArray(data), True)

            if self.mode==Mode.Training or self.mode==Mode.DataGeneration:  # get labels for rabits
                labels = self.getLablesR(data)
                #labelR = self.get_Lables(self.rabits)
            
            if self.mode==Mode.Visualization:
                self.describeSituation(data, rabitMoves)

            self.setNextPos(self.rabits, rabitMoves)        
            self.scheduleRabit.step()
            self.removeDeadRabits() # removing rabits that have died of starvation or commited suicide

            if self.mode==Mode.Training:
                train(self.toNpArray(data), self.toNpArray(labels), True, False)        #train rabits
        else:
            agentType = AgentType.Fox
            data = self.getStatesF()
            foxMoves = predict(self.toNpArray(data), False)

            if self.mode==Mode.Training or self.mode==Mode.DataGeneration: # get labels for foxes
                labels = self.getLablesF(data)
                #labelF = self.get_Lables(self.foxes)
            
            self.setNextPos(self.foxes, foxMoves)        
            self.scheduleFox.step()

            self.removeDeadRabits()
            self.removeDeadFoxes()

            self.increaseFoodInFiledCells() # grass is growing in cells

            if self.mode==Mode.Training:
                train(self.toNpArray(data), self.toNpArray(labels), False, False)       #train foxes

        self.rabitsMove = not self.rabitsMove
        return (agentType, data, labels) 