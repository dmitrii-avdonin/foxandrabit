from mesa import Model
from .FieldCell import FieldCell
import sys
sys.path.append('..')
from agents.Rabit import Rabit
from agents.Fox import Fox
import numpy as np
from settings import Mode, AgentType, vr, mr, lblShape, randomMoveP, moveDirections
import settings
from utils.Utils import toNpArray, printCoordsArray, dice
from Trainer import train
from Trainer import predict
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from utils.VisualizeAgentEnvironment import visualizeAgentEnvironment
from numpy.random import randint
import numpy as np

class MyMultiGrid(MultiGrid):
    def __init__(self, width, height, torus):
        MultiGrid.__init__(self, width, height, torus)

    def getFirstAgentOfTypeIfExist(self, x, y, agentType):
        cellAgentsSet = self.grid[x][y]
        agentsOfType = [a for a in cellAgentsSet if a.agentType == agentType]
        if(len(agentsOfType)==0):
            return None
        return agentsOfType[0]

    def getAgentsCountOnCell(self, x, y, agentType):
        cellAgentsSet = self.grid[x][y]
        counter = 0
        for agent in cellAgentsSet:
            if agent.agentType == agentType:
                counter+=1
        return counter


    def position_agent(self, agent, x="random", y="random"):
        if x == "random" or y == "random":
            if len(self.empties) == 0:
                raise Exception("ERROR: Grid full")
            coords = agent.random.choice(self.empties)
        else:
            coords = (x, y)
        agent.pos = coords
        self._place_agent(coords, agent)        

class Field(Model):
    def __init__(self, width, height, num_rabits, num_foxes, mode, seed=None):
        self.mode = mode
        self.running = True
        self.rabitsMove = True

        self.width = width
        self.height = height
        self.num_rabits = num_rabits
        self.num_foxes = num_foxes

        self.cells = [[FieldCell(self.random.randint) for i in range(self.height)] for j in range(self.width)]

        self.grid = MyMultiGrid(width, height, False)
        self.scheduleRabit = RandomActivation(self)
        self.scheduleFox = RandomActivation(self)
        self.stepCounter = 0

        Rabit.DeadCount = 0
        Fox.DeadCount = 0
        self.datacollector = DataCollector(
        model_reporters={"RabitsNr": lambda model : model.aliveRabitsCount(), "FoxesNr": lambda model : model.aliveFoxesCount()},  # A function to call
        agent_reporters={})  # An agent attribute

        self.rabits = []
        for i in range(self.num_rabits):
            a = Rabit(i, self)
            a.random.choices
            self.grid.position_agent(a, x="random", y="random")
            self.scheduleRabit.add(a)
            self.rabits.append(a)
            
        self.foxes = []
        for i in range(self.num_foxes):
            a = Fox(i, self)
            self.grid.position_agent(a, x="random", y="random")
            self.scheduleFox.add(a)
            self.foxes.append(a)

    def aliveRabitsCount(self):
        return self.num_rabits - Rabit.DeadCount

    def aliveFoxesCount(self):
        return self.num_foxes - Fox.DeadCount

    def getStatesR(self):
        return self.getStates(self.rabits)


    def getStatesF(self):
        return self.getStates(self.foxes)


    def getStates(self, agentList):
        states = []
        for a in agentList:
            if(not a.isBuried()):
                nbh = self.get_neighborhood(a.pos)
                agentState = [[ [] for j in range(vr*2 +1)] for i in range(vr*2 + 1 + 1)]
                for i in range(vr*2+1):
                    for j in range(vr*2+1):
                        (x,y) = nbh[i][j]
                        if self.grid.out_of_bounds((x, y)):  #this cell can't be reached 
                            agentState[i][j] = [-1, -1, a.fullness]
                        else:
                            food = self.cells[x][y].food
                            food = round(food, 1) #rounding to one decimal place
                            rabitsCount = self.grid.getAgentsCountOnCell(x, y, AgentType.Rabit)
                            foxesCount = self.grid.getAgentsCountOnCell(x, y, AgentType.Fox)
                            agentState[i][j] = [food, rabitsCount, foxesCount]
            else:
                agentState = [[ [0, 0, 0] for j in range(vr*2 +1)] for i in range(vr*2 + 1 + 1)] 
            for j in range(vr*2+1):
                agentState[vr*2 + 1][j] = [0, 0, 0]
            if(not a.isBuried()):
                agentState[vr*2 + 1][0] = [a.fullness, 0, 0]

            #printCoordsArray(agentState)
            states.append(agentState)
        return states

    def get_neighborhood(self, pos, vr=-1):
        x, y = pos
        if vr==-1:
            vr=settings.vr

        coords = [[(0, 0) for j in range(vr*2 +1)] for i in range(vr*2 +1)]
        for dy in range(-vr, vr + 1):
            for dx in range(-vr, vr + 1):
                coords[vr+dx][vr+dy]= (x+dx, y+dy)

        return coords


    def setNextPos(self, agentsList, shifts):
        for i in range(len(agentsList)):
            if(not agentsList[i].isDead):
                agentsList[i].setNextPos(shifts[i])

    def clearAgentsInFiledCells(self):
        for j in range(self.width):
            for i in range(self.height):
                self.cells[j][i].rabitsCount = 0

    def increaseFoodInFiledCells(self):
        for j in range(self.width):
            for i in range(self.height):
                self.cells[j][i].incFood() 

    def getScheduler(self, agentType):
        if(agentType == AgentType.Rabit):
            return self.scheduleRabit
        if(agentType == AgentType.Fox):
            return self.scheduleFox
        raise Exception("Unknown agent type")
        


    def describeSituation(self, data, direction):
        label = self.getLablesR(data, True)
        #visualizeAgentEnvironment(data[0])
        for i in range(len(label)):            
            x= direction[i] % (lblShape)
            y= direction[i] // (lblShape)
            if(label[i][x][y]<0):
                printCoordsArray(data[i], 1, True) # printing agents location
                printCoordsArray(data[i], 0, False) # printing food location
                printCoordsArray(label[i]) # printing 2D labels for each directions
                print("predicted direction: " + str(direction[i] + 1))
                print("===================================================")        


    def getShift(self, curentPos, radius):
        return range(curentPos-radius, curentPos+radius+1)

    def getLablesR(self, states, returnMatix=False):
        feedback = []
        stl = (vr-mr) # state array coords to label array coords
        
        for i in range(len(states)): # calculating feedback for each state
            label = [[0 for i in range(lblShape)] for j in range(lblShape)]  # the label is a 3x3 square containing the for each direction
            state = states[i]
            #printCoordsArray(state, 0) #printing food amount on cells
            #printCoordsArray(state, 1, True) # printing agents location

            if(not self.rabits[i].isBuried()):
                # calculating the feedback for each direction where the agend can go
                for dx in self.getShift(vr, mr): # shift by x for current agent - the agent is in the center of the crState Array = crState[vr][vr]
                    for dy in self.getShift(vr, mr): # samve for y coordinate  
                        lbl = 0.0          
                        for cx in self.getShift(dx, 1): # it is expected that vr is at leas mr+1 otherwise we can get out of range
                            for cy in self.getShift(dy, 1): # it is expected that vr is at leas mr+1 otherwise we can get out of range
                                cell = state[cx][cy]
                                if(cx==dx and cy==dy): #this is the direction cel
                                    if(cell[2] > 0 ): # number of AgentType.Fox on this cell
                                        lbl += -4

                                    if((cx!=vr or cy!=vr)): # condition to avoid that the agent (whose state we analize) adds a minus to his current location
                                        lbl += -0.4 * cell[1]

                                    if(cell[1]==-1):  # a wall, cannot go there
                                        lbl += -2
                                    else:
                                        lbl += cell[0]
                                else:
                                    if(cell[2]>0):
                                        lbl -= 2
                                    if(cell[1]==-1):  # a wall, cannot go there
                                        lbl += -1
                                    else:
                                        lbl += cell[0] * 0.1
                                
                        label[dx-stl][dy-stl] = lbl

            #printCoordsArray(label) # printing 2D labels for each directions
            if returnMatix:
               feedback.append(label)
            else:             
                flatLabel = self.flatFeedback(label)
                #printCoordsArray(flatLabel) # printing 1D labels for each directions
                feedback.append(flatLabel)

        return feedback



    def getLablesF(self, states):
        feedback = []
        stl = (vr-mr) # state array coords to label array coords
        
        for i in range(len(states)): # calculating feedback for each state
            label = [[0 for i in range(lblShape)] for j in range(lblShape)] # the label is a 3x3 square containing the for each direction
            state = states[i]
            #printCoordsArray(state, 0) #printing food amount on cells
            #printCoordsArray(state, 1, True) # printing agents location

            if(not self.rabits[i].isBuried()):
                # calculating the feedback for each direction where the agend can go
                for dx in self.getShift(vr, mr): # shift by x for current agent - the agent is in the center of the crState Array = crState[vr][vr]
                    for dy in self.getShift(vr, mr): # samve for y coordinate  
                        lbl = 0.0          
                        for cx in self.getShift(dx, 1): # it is expected that vr is at leas mr+1 otherwise we can get out of range
                            for cy in self.getShift(dy, 1): # it is expected that vr is at leas mr+1 otherwise we can get out of range
                                cell = state[cx][cy]
                                if(cx==dx and cy==dy): #this is the direction cel
                                    
                                    lbl += 2 * cell[1] # bonus multiplied by number of rabits on that cell

                                    if((cx!=vr or cy!=vr)): # condition to avoid that the agent (whose state we analize) adds a minus to his current location
                                        lbl += -0.2 * cell[2]
                                    if(cell[1]==-1):  # a wall, cannot go there
                                        lbl += -1
                                else:
                                    lbl += 1 * cell[1]
                                    if(cell[1]==-1):  # a wall, cannot go there
                                        lbl += -0.5                                    
                                
                        label[dx-stl][dy-stl] = lbl

            #printCoordsArray(label) # printing 2D labels for each directions
            flatLabel = self.flatFeedback(label)
            #printCoordsArray(flatLabel) # printing 1D labels for each directions
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

    def getAgentsReinforcementFeedback(self, agentsList):
        result = []
        for a in agentsList:
            result.append(a.feedback)
            a.feedback = 0
        return result

    def applyMovesRandomization(self, predictedMoves):
        moves = []
        for m in predictedMoves:
            if dice(randomMoveP):
                moves.append(randint(moveDirections))
            else:
                moves.append(np.argmax(m))
        return moves

    def step(self):
        print("RCount " + str(self.aliveRabitsCount()) )
        print("FCount " + str(self.aliveFoxesCount()) )

        if(self.aliveRabitsCount()==0 or self.aliveFoxesCount()==0):
            self.running = False
            return
        
        labels = None
        data = None
        agentsFeedback = None
        agentType = -1

        if self.rabitsMove:
            agentType = AgentType.Rabit
            self.clearAgentsInFiledCells() # scheduleRabit.step() will initialize the next filedCells with Rabits 
            
            data = self.getStatesR()
            if self.mode==Mode.Reinforcement:
                movesP = predict(toNpArray(data), True, False)
                moves = self.applyMovesRandomization(movesP)
            else:
                moves = predict(toNpArray(data), True)

            # cleaning the moves for rabits that were eaten by Foxes during previous step
            if self.mode==Mode.Reinforcement:
                for i in range(self.num_rabits) :
                    if self.rabits[i].isDead:
                        moves[i]=-1 # this move should be ignored during reinforcement because rabit died on previous step

            if self.mode==Mode.Training or self.mode==Mode.DataGeneration or self.mode==Mode.Reinforcement:  # get labels for rabits
                labels = self.getLablesR(data)
            
            #if self.mode==Mode.Visualization:
            #    self.describeSituation(data, moves)

            self.setNextPos(self.rabits, moves)        
            self.scheduleRabit.step()

            if self.mode==Mode.Training:
                train(toNpArray(data), toNpArray(labels), True, False)        #train rabits

            #if self.mode==Mode.Reinforcement:
            agentsFeedback = self.getAgentsReinforcementFeedback(self.rabits)

            self.datacollector.collect(self)
        else:
            agentType = AgentType.Fox
            data = self.getStatesF()
            if self.mode==Mode.Reinforcement:
                movesP = predict(toNpArray(data), False, False)
                moves = self.applyMovesRandomization(movesP)
            else:
                moves = predict(toNpArray(data), False)

            #if self.mode==Mode.Training or self.mode==Mode.DataGeneration or self.mode==Mode.Reinforcement: # get labels for foxes
            labels = self.getLablesF(data)
            
            self.setNextPos(self.foxes, moves)        
            self.scheduleFox.step()

            self.increaseFoodInFiledCells() # grass is growing in cells

            if self.mode==Mode.Training:
                train(toNpArray(data), toNpArray(labels), False, False)       #train foxes

            #if self.mode==Mode.Reinforcement:
            agentsFeedback = self.getAgentsReinforcementFeedback(self.foxes)

            self.datacollector.collect(self)

        self.rabitsMove = not self.rabitsMove
        self.stepCounter += 1
        print("Field Step = " + str(self.stepCounter))
        return (agentType, data, labels, agentsFeedback, moves)