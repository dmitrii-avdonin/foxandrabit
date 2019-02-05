from .baseAgent import BaseAgent
from settings import AgentType

class Rabit(BaseAgent):
    InitialFullness = 5.
    Hunger = 0.5 # fullness decrease per step
    MaxEat = 0.6 # max how much can eat one time if it is available on current field cell
    def __init__(self, unique_id, model):
        BaseAgent.__init__(self, AgentType.Rabit, unique_id, model, Rabit.InitialFullness)

    def eatGrassOnCurrentFiledCellAndEvaluateFullness(self):
        (x,y) = self.pos
        actualEat = self.model.cells[x][y].removeFood(Rabit.MaxEat)
        self.fullness += actualEat
        self.fullness -= Rabit.Hunger
        if(self.fullness <= 0):
            self.setDead()

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
                # we do not increase here the fox fullness because this increase is not determinde by fox decision
                return
        
        self.eatGrassOnCurrentFiledCellAndEvaluateFullness()
        if(self.isDead):
            return
        self.model.grid.move_agent(self, posToGo)
        self.model.cells[x][y].rabitsCount += 1
        self.eatGrassOnCurrentFiledCellAndEvaluateFullness()

        return

    def step(self):
        self.makeStep(self.nextPos)
        return