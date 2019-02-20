from numpy.random import randint

class FieldCell:
    MaxFood = 0.9
    inc = 0.3
    def __init__(self):
        self.rabitsCount = None
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

        self.food += max(0, FieldCell.inc - 0.1 * self.rabitsCount)

        self.food = min(FieldCell.MaxFood, self.food)