from .baseAgent import BaseAgent
from settings import AgentType
import settings

class Fox(BaseAgent):
    InitialFullness = 2.
    Hunger = 0.2
    EatARabit = 1.  # if eats a rabit its fullness will be increased by this amount
    DeadCount = 0
    def __init__(self, unique_id, model):
        BaseAgent.__init__(self, AgentType.Fox, unique_id, model, Fox.InitialFullness)

    def setDead(self):
        BaseAgent.setDead(self)
        Fox.DeadCount += 1


    def eatApplyHungerAndEvaluateFullness(self):
        (x, y) = self.pos
        rabit = self.model.grid.getFirstAgentOfTypeIfExist(x, y, AgentType.Rabit)
        if(rabit != None):
            self.fullness += rabit.wasBitten(Fox.EatARabit)
            self.feedback = 1
            rabit.feedback = -1

        self.fullness -= Fox.Hunger

        if(self.fullness <= 0):
            if(settings.dieOfHunger in (None, True)):                            
                self.setDead()                
            else: 
                self.fullness = Fox.InitialFullness
            self.feedback = -1


    def step(self):
        if(not self.isDead):
            if not self.model.grid.out_of_bounds(self.nextPos):
                self.model.grid.move_agent(self, self.nextPos)
            self.nextPos = None # self.pos is already nextPost, so nextPos not needed
            (x,y) = self.pos
            self.model.cells[x][y].foxesCount += 1


    def advance(self):
        self.eatApplyHungerAndEvaluateFullness()        