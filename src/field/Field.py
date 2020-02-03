from mesa import Model
from .FieldCell import FieldCell
from .MyMultiGrid import MyMultiGrid
from mesa.time import SimultaneousActivation

from agents.Rabit import Rabit
from agents.Fox import Fox
from settings import vr, mr, AgentType, RandomizationEnabled
from Trainer import predict
from utils.Utils import toNpArray
import numpy as np

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
        self.scheduleRabit = SimultaneousActivation(self)
        self.scheduleFox = SimultaneousActivation(self)
        self.stepCounter = 0

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


    def getStates(self, agentType):
        agentList = self.getAliveAgetns(agentType)
        states = []
        for a in agentList:
            states.append(a.getState(self.cells))
        return states 

    def setNextPos(self, agentType, shifts):
        agentsList = self.getAliveAgetns(agentType)
        for i in range(len(agentsList)):
            if(not agentsList[i].isDead):
                agentsList[i].setNextPos(shifts[i])
    
    def clearAgentsInFiledCells(self, agentType):
        attribute = None
        if(agentType == AgentType.Rabit):
            attribute = "rabitsCount"
        else:
            attribute = "foxesCount"

        for j in range(self.width):
            for i in range(self.height):
                setattr( self.cells[j][i], attribute, 0 )


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

    
    def makeChoice(self, prob):
        choice = 0
        rand = self.random.random()
        for i in range(len(prob)):
            choice += prob[i]
            if(rand<=choice):
                return i

        raise Exception("ERROR: This should not happen")        

    def applyMovesProbabylityRandomization(self, predictedMoves):
        moves = []
        if RandomizationEnabled:
            for m in predictedMoves:
                minm = np.min(m) 
                m1 = m - minm + 1
                mProb = m1 / sum(m1)
                moves.append(self.makeChoice(mProb))
        else:
            for m in predictedMoves:
                moves.append(np.argmax(m))

        return moves 

    def getAgents(self, agentType):
        if agentType == AgentType.Rabit:
            return self.rabits
        elif agentType == AgentType.Fox:
            return self.foxes
        else:
            raise Exception("ERROR: Unknown agent type")

    def getAliveAgetns(self, agentType):
        allAgents = self.getAgents(agentType)
        alive = [a for a in allAgents if not a.isDead]
        return alive

    def setAgetntLabels(self, agentType, labels, moves):
        agents = self.getAliveAgetns(agentType)
        for i in range(len(agents)):
            agents[i].labelSequence.append(labels[i])
            agents[i].directionSequence.append(moves[i])


    def step(self):

        if(self.aliveRabitsCount()==0 or self.aliveFoxesCount()==0):
            self.running = False
            return        

        if self.rabitsMove:
            self.clearAgentsInFiledCells(AgentType.Rabit) # scheduleRabit.step() will initialize the next filedCells with Rabits 
            data = self.getStates(AgentType.Rabit)
            movesP = predict(toNpArray(data), True, False)
            moves = self.applyMovesProbabylityRandomization(movesP)
            self.setAgetntLabels(AgentType.Rabit, movesP, moves)
            self.setNextPos(AgentType.Rabit, moves)
            self.scheduleRabit.step()        
        else:
            self.clearAgentsInFiledCells(AgentType.Fox) # scheduleRabit.step() will initialize the next filedCells with Foxes 
            data = self.getStates(AgentType.Fox)
            movesP = predict(toNpArray(data), False, False)
            moves = self.applyMovesProbabylityRandomization(movesP)
            self.setAgetntLabels(AgentType.Fox, movesP, moves)
            self.setNextPos(AgentType.Fox, moves)        
            self.scheduleFox.step()

            self.increaseFoodInFiledCells() # grass is growing in cells

        self.rabitsMove = not self.rabitsMove
        self.stepCounter += 1        
