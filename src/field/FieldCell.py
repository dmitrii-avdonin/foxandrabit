class FieldCell:
    MaxFood = 0.9
    inc = 0.3
    def __init__(self, randint):
        self.rabitsCount = None
        self.foxesCount = None
        self.foodExists = False
        self.food = 0.
        if randint(1, 10) <= 2:
            self.food = FieldCell.MaxFood
            self.foodExists = True

    def removeFood(self, requiredAmount):
        actualAmount = min(self.food/self.rabitsCount, requiredAmount) # each rabit on current cell will eat equal amount of food
        self.food -= actualAmount
        return actualAmount

    def incFood(self):
        if not self.foodExists:
            return

        self.food += max(0, FieldCell.inc - 0.1 * self.rabitsCount)

        self.food = min(FieldCell.MaxFood, self.food)