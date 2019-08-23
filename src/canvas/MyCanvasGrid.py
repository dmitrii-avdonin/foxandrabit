
from settings import AgentType
from mesa.visualization.modules import CanvasGrid
from collections import defaultdict
from field.FieldCell import FieldCell

class MyCanvasGrid(CanvasGrid):
    def __init__(self, rabit_portrayal_method, fox_portrayal_method, terain_portrayal_method, grid_width, grid_height,
                 canvas_width, canvas_height):
        super().__init__(None, grid_width, grid_height, canvas_width, canvas_height)
        self.rabit_portrayal_method = rabit_portrayal_method
        self.fox_portrayal_method = fox_portrayal_method
        self.terain_portrayal_method = terain_portrayal_method


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
                        portrayal["fullness"] = round(obj.fullness, 2)
                        portrayal["unique_id"] = obj.unique_id
                        grid_state[1].append(portrayal)
                if (self.terain_portrayal_method != None):
                    grid_state[0].append(self.terain_portrayal_method(x, y, model.cells[x][y]))


        return grid_state 

def terain_portrayal(x, y, cell):
    color = "rgb(223, 221, 195)"
    if(cell.foodExists):
        #https://www.w3schools.com/colors/colors_hsl.asp
        ligthness = 40 + 55 - 55 * cell.food/FieldCell.MaxFood
        color = "hsl(128, 33%, " + str(ligthness) + "%)"
    portrayal = {"Shape": "rect",
                 "Filled": "true",
                 "x": x,
                 "y": y,
                 "Color": color,
                 "w": 0.99,
                 "h": 0.99}
    return portrayal    

def rabit_portrayal(agent):
    color = "black" if agent.isDead else "blue"
    portrayal = {"Shape": "circle",
                 "Filled": "true",
                 "Color": color,
                 "r": 0.8}
    return portrayal    

def fox_portrayal(agent):
    portrayal = {"Shape": "circle",
                 "Filled": "true",
                 "Color": "red",
                 "r": 1.1}
    return portrayal         