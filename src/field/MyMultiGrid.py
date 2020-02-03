
from mesa.space import MultiGrid




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