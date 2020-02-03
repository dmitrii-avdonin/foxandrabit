from .baseAgent import BaseAgent
from settings import AgentType, vr
import settings

class Rabit(BaseAgent):
    InitialFullness = 5.
    Hunger = 0.3 # fullness decrease per step
    MaxEat = 0.6 # max how much can eat one time if it is available on current field cell
    DeadCount = 0
    MeatAmount = 3

    StarvationDeathCount = 0
    ReinforcedStates = []
    ReinforcedLabels = []

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
            feedback = (self.fullness - self.fullness5)/(Rabit.MaxEat * vr)  # can be in range [ -Hunger/MaxEat, +MaxEat ]
            self.applySequenceReinforcement(feedback)
            #self.dayCounter = 0
            self.fullness5 = self.fullness
        else:
            self.dayCounter += 1


    def applyReinforcement(self, feedback, labelIndex=-1):
        if(labelIndex >= 0):
            raise Exception("ERROR: it is expected to be negative since we are updating them from most recent one to oldes one")
        percentDecrease = [0.7, 0.8, 0.9, 1] # decreasing the feedback value depending on how far in time the step is 
        d = self.directionSequence[labelIndex]
        label = self.labelSequence[labelIndex]
        label[d] = label[d] + feedback * percentDecrease[labelIndex]

    def applySequenceReinforcement(self, feedback):
        labelIndex = -1
        for(i in range(len(self.self.labelSequence))):
            self.applyReinforcement(feedback, labelIndex)
            labelIndex += -1

    def reinforce(self):
        if (self.feedback != 0):
            if(self.isDead):
                if (self.feedback >=0):
                    raise Exception("ERROR: Feedback cannot be positive if the agent died")
                self.applySequenceReinforcement()
            if()
                

        slef.feedback = 0


    def eatGrassOnCurrentFiledCellAndEvaluateFullness(self):
        (x,y) = self.pos
        actualEat = self.model.cells[x][y].removeFood(Rabit.MaxEat)
        self.fullness += actualEat
        self.fullness -= Rabit.Hunger
        
        if(self.fullness <= 0):
            if (settings.dieOfHunger in (None, True)):
                self.setDead()
                self.model.grid.remove_agent(self)
                Rabit.StarvationDeathCount += 1           
            else:
                self.fullness = Rabit.InitialFullness
            self.feedback = -1 

    def step(self):
        if( not self.isDead ):
            if not self.model.grid.out_of_bounds(self.nextPos):
                self.model.grid.move_agent(self, self.nextPos)
            self.nextPos = None # self.pos is already nextPost, so nextPos not needed
            (x,y) = self.pos
            self.model.cells[x][y].rabitsCount += 1

    def advance(self):
        if( not self.isDead ):
            self.eatGrassOnCurrentFiledCellAndEvaluateFullness()
            self.evaluateFeedEfeciency()
        
