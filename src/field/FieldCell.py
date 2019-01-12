from numpy.random import randint

class FieldCell:
    MaxFood = 0.9
    def __init__(self):
        self.Rabit = None
        self.foodExists = False
        self.food = 0.
        if randint(10) < 2:
            self.food = 0.9
            self.foodExists = True

    def removeFood(self, requiredAmount):
        actualAmount = min(self.food, requiredAmount)
        self.food -= actualAmount
        return actualAmount

    def incFood(self):
        if not self.foodExists:
            return

        if(self.Rabit == None):
            self.food += 0.3
        else:
            self.food += 0.

        self.food = self.food if self.food<FieldCell.MaxFood else FieldCell.MaxFood