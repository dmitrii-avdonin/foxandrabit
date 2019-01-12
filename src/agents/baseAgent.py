from mesa import Agent

class BaseAgent(Agent):

    def __init__(self, agType, unique_id, model, initialFullness):
        super().__init__(unique_id, model)
        self.agentType = agType
        self.fullness = initialFullness
        self.nextPos = (0, 0)
        self.pos = (0, 0)
        self.isDead = False


    def setDead(self):
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