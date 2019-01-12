
from settings import AgentType
from mesa.visualization.modules import CanvasGrid
from collections import defaultdict

class MyCanvasGrid(CanvasGrid):
    def __init__(self, rabit_portrayal_method, fox_portrayal_method, grid_width, grid_height,
                 canvas_width, canvas_height):
        super().__init__(None, grid_width, grid_height, canvas_width, canvas_height)
        self.rabit_portrayal_method = rabit_portrayal_method
        self.fox_portrayal_method = fox_portrayal_method


    def render(self, model):
        grid_state = defaultdict(list)
        for x in range(model.grid.width):
            for y in range(model.grid.height):
                cell_objects = model.grid.get_cell_list_contents([(x, y)])
                for obj in cell_objects:
                    if obj.agentType == AgentType.Rabit:
                        portrayal = self.rabit_portrayal_method(obj)
                    else: 
                        portrayal = self.fox_portrayal_method(obj)

                    if portrayal:
                        portrayal["x"] = x
                        portrayal["y"] = y
                        portrayal["fullness"] = obj.fullness
                        portrayal["unique_id"] = obj.unique_id
                        grid_state[portrayal["Layer"]].append(portrayal)

        return grid_state 


def rabit_portrayal(agent):
    portrayal = {"Shape": "circle",
                 "Filled": "true",
                 "Layer": 0,
                 "Color": "blue",
                 "r": 0.5}
    return portrayal    

def fox_portrayal(agent):
    portrayal = {"Shape": "circle",
                 "Filled": "true",
                 "Layer": 0,
                 "Color": "red",
                 "r": 0.9}
    return portrayal         