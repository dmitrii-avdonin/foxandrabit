from canvas.MyCanvasGrid import MyCanvasGrid, rabit_portrayal, fox_portrayal, terain_portrayal
from settings import fieldW, fieldH, FoxN, RabitN, vr, Mode
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule
from field.Field import Field
import settings


def visualize(args):
    settings.setDieOfHunger(False)
    ppd = 8 #pixels per dimension
    width = 150
    height = 140
    countR = int(round(height * width / 25 * 3)) # avg 3 Rabits per each 5x5 cells square
    countF = int(round(height * width / 25 * 1)) # avg 1 Fox per each 5x5 cells square    
    grid = MyCanvasGrid(rabit_portrayal, fox_portrayal, terain_portrayal, width, height, width * ppd, height * ppd)

    FoxesNr = {"Label": "FoxesNr", "Color": "red"}
    RabitsNr = {"Label": "RabitsNr", "Color": "blue"}
    chart_count = ChartModule([FoxesNr, RabitsNr], data_collector_name='datacollector')

    server = ModularServer(Field,
                        [grid, chart_count],
                        "Rabit VS Fox Model",
                        {"width": width , "height": height, "num_rabits": countR, "num_foxes": countF, "mode": Mode.Visualization, "seed": 999})
    server.port = 8521 # The default
    server.launch()