from .baseAgent import BaseAgent
from settings import AgentType, vr
import settings

class Rabit(BaseAgent):
    InitialFullness = 5.
    Hunger = 0.3 # fullness decrease per step
    MaxEat = 0.6 # max how much can eat one time if it is available on current field cell
    DeadCount = 0
    MeatAmount = 3
    def __init__(self, unique_id, model):
        BaseAgent.__init__(self, AgentType.Rabit, unique_id, model, Rabit.InitialFullness)
        self.dayCounter = 1
        self.fullness5 = self.fullness
        self.meatAmount = Rabit.MeatAmount

    def setDead(self):
        self.isDead = True
        self.model.getScheduler(self.agentType).remove(self)
        Rabit.DeadCount += 1

    def wasBitten(self, biteSize):
        result = min(biteSize, self.meatAmount)
        self.meatAmount -= biteSize
        if(self.meatAmount <= 0):
            self.model.grid.remove_agent(self)
        if(not self.isDead):
            self.setDead()
        return result


    def evaluateFeedEfeciency(self):
        if(self.dayCounter==vr):            
            self.feedback = (self.fullness - self.fullness5)/(Rabit.MaxEat * vr)
            self.dayCounter = 0
            self.fullness5 = self.fullness
        else:
            self.dayCounter += 1


    def eatGrassOnCurrentFiledCellAndEvaluateFullness(self):
        (x,y) = self.pos
        actualEat = self.model.cells[x][y].removeFood(Rabit.MaxEat)
        self.fullness += actualEat
        self.fullness -= Rabit.Hunger
        
        if(self.fullness <= 0):
            if (settings.dieOfHunger in (None, True)):
                self.setDead()
                self.model.grid.remove_agent(self)                
            else:
                self.fullness = Rabit.InitialFullness
            #self.feedback = -1 # temporary commenting since NN does not know about Agent Fullness

    # posToGo - next position to go
    def makeStep(self, posToGo):
        self.fullness = self.fullness

        if self.model.grid.out_of_bounds(posToGo):
            self.eatGrassOnCurrentFiledCellAndEvaluateFullness()
            return

        if(posToGo == self.pos):
            self.eatGrassOnCurrentFiledCellAndEvaluateFullness()
            return
        
        (x, y) = posToGo
        if not self.model.grid.is_cell_empty(posToGo):
            fox = self.model.grid.getFirstAgentOfTypeIfExist(x, y, AgentType.Fox)
            if(fox != None):
                self.setDead()
                self.model.grid.remove_agent(self)
                self.feedback = -1
                # we do not increase here the fox fullness because this increase is not determinde by fox decision
                return
        
        if(self.isDead):
            return
        self.model.grid.move_agent(self, posToGo)
        self.model.cells[x][y].rabitsCount += 1
        self.eatGrassOnCurrentFiledCellAndEvaluateFullness()
        
        if(not self.isDead):
            self.evaluateFeedEfeciency()

        return

    def step(self):
        self.makeStep(self.nextPos)
        return