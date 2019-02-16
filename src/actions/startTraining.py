from settings import fieldW, fieldH, FoxN, RabitN, Mode
from field.Field import Field

def startTraining(args):
    field = Field(fieldW, fieldH, RabitN, FoxN, Mode.Training)
    runStats = []
    restart = 0
    iterationsCount = 0

    while True:
        if(field.aliveRabitsCount()<RabitN/2 or field.aliveFoxesCount()<FoxN/2): 
            runStats.append({"restart": restart, "iterationsCount": iterationsCount, "rabitsLeft": field.aliveRabitsCount(), "foxesLeft": field.aliveFoxesCount()})
            field = Field(fieldW, fieldH, RabitN, FoxN, Mode.Training)            
            restart += 1
            iterationsCount = 0
        field.step()
        iterationsCount += 1