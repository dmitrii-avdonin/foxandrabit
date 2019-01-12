from canvas.MyCanvasGrid import MyCanvasGrid, rabit_portrayal, fox_portrayal
from settings import fieldW, fieldH, FoxN, RabitN, vr, Mode
from mesa.visualization.ModularVisualization import ModularServer
from field.Field import Field


def visualize():
    grid = MyCanvasGrid(rabit_portrayal, fox_portrayal, fieldW, fieldW, 1500, 1000)
    server = ModularServer(Field,
                        [grid],
                        "Rabit VS Fox Model",
                        {"width": fieldW , "height": fieldW, "num_rabits": RabitN, "num_foxes": FoxN, "viewRadius": vr, "mode": Mode.Visualization})
    server.port = 8521 # The default
    server.launch()