from .baseAgent import BaseAgent
from settings import AgentType

class Fox(BaseAgent):
    InitialFullness = 2.
    Hunger = 0.2
    EatARabit = 1.  # if eats a rabit its fullness will be increased by this amount
    def __init__(self, unique_id, model):
        BaseAgent.__init__(self, AgentType.Fox, unique_id, model, Fox.InitialFullness)


    def makeStep(self, posToGo):
        self.fullness = self.fullness

        if self.model.grid.out_of_bounds(self.nextPos):
            self.applyHungerAndEvaluateFullness()
            return 

        if(self.nextPos == self.pos):
            self.applyHungerAndEvaluateFullness()
            return             

        if not self.model.grid.is_cell_empty(self.nextPos) :
            (x, y) = self.nextPos
            agentOnNextPos = self.model.grid.grid[x][y]
            if(agentOnNextPos.agentType == self.agentType):
                self.applyHungerAndEvaluateFullness()
                return
            else:
                self.fullness += Fox.EatARabit
                agentOnNextPos.setDead()
        else:
            self.applyHungerAndEvaluateFullness()

        if(not self.isDead):
            self.model.grid.move_agent(self, self.nextPos)

        return


    def applyHungerAndEvaluateFullness(self):
        self.fullness -= Fox.Hunger
        if(self.fullness <= 0):
            self.setDead()    


    def step(self):
        self.makeStep(self.nextPos)
        return