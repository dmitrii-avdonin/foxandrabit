from mesa import Agent
from settings import vr, AgentType
from utils.Utils import get_neighborhood

class BaseAgent(Agent):
    wallConst = -9

    def __init__(self, agType, unique_id, model, initialFullness):
        super().__init__(unique_id, model)
        self.agentType = agType
        self.fullness = initialFullness
        self.nextPos = None
        self.pos = (0, 0)        
        self.isDead = False

        self.stateSequence = []
        self.labelSequence = []
        self.directionSequence = []  #the index from labelSequence chosen as actual move direction


    def setDead(self):
        self.isDead = True
        self.model.grid.remove_agent(self)
        self.model.getScheduler(self.agentType).remove(self)


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

    def getState(self, cells):
        if(not self.isDead):
            nbh = get_neighborhood(self.pos, vr)
            agentState = [[ [] for j in range(vr*2 +1)] for i in range(vr*2 + 1 + 1)]
            for i in range(vr*2+1):
                for j in range(vr*2+1):
                    (x,y) = nbh[i][j]
                    if self.model.grid.out_of_bounds((x, y)):  #this cell can't be reached 
                        agentState[i][j] = [BaseAgent.wallConst, BaseAgent.wallConst, BaseAgent.wallConst]
                    else:
                        food = cells[x][y].food
                        food = round(food, 1) #rounding to one decimal place
                        rabitsCount = self.model.grid.getAgentsCountOnCell(x, y, AgentType.Rabit)
                        foxesCount = self.model.grid.getAgentsCountOnCell(x, y, AgentType.Fox)
                        agentState[i][j] = [food, rabitsCount, foxesCount]
        else:
            raise Exception("ERROR: Atemt to get the state of dead agent")
            
        for j in range(vr*2+1):
            agentState[vr*2 + 1][j] = [0, 0, 0]
        if(not self.isDead):
            agentState[vr*2 + 1][0] = [self.fullness, 0, 0]

        #printCoordsArray(agentState)
        self.stateSequence.append(agentState)
        return agentState


