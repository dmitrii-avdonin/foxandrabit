from canvas.MyCanvasGrid import MyCanvasGrid, rabit_portrayal, fox_portrayal, terain_portrayal
from settings import fieldW, fieldH, FoxN, RabitN, vr, Mode
from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import ChartModule
from field.Field import Field


def visualize():
    ppdw = 8 #pixels per dimension
    ppdh = 11 #pixels per dimension
    grid = MyCanvasGrid(rabit_portrayal, fox_portrayal, terain_portrayal, fieldW, fieldW, fieldW * ppdw, fieldH * ppdh)

    FoxesNr = {"Label": "FoxesNr", "Color": "red"}
    RabitsNr = {"Label": "RabitsNr", "Color": "blue"}
    chart_count = ChartModule([FoxesNr, RabitsNr], data_collector_name='datacollector')

    server = ModularServer(Field,
                        [grid, chart_count],
                        "Rabit VS Fox Model",
                        {"width": fieldW , "height": fieldW, "num_rabits": RabitN, "num_foxes": FoxN, "viewRadius": vr, "mode": Mode.Visualization})
    server.port = 8521 # The default
    server.launch()