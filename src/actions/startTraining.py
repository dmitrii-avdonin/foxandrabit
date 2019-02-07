from settings import fieldW, fieldH, FoxN, RabitN, vr, Mode
from field.Field import Field

def startTraining(args):
    field = Field(fieldW, fieldH, RabitN, FoxN, vr, Mode.Training)
    runStats = []
    restart = 0
    iterationsCount = 0

    while True:
        if(len(field.rabits)<RabitN/2 or len(field.foxes)<FoxN/2): 
            runStats.append({"restart": restart, "iterationsCount": iterationsCount, "rabitsLeft": len(field.rabits), "foxesLeft": len(field.foxes)})
            field = Field(fieldW, fieldH, RabitN, FoxN, vr, Mode.Training)            
            restart += 1
            iterationsCount = 0
        field.step()
        iterationsCount += 1