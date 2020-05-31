class Variable:
    def __init__(self, positive, letter, i, j):
        self.letter = letter
        self.i = i
        self.j = j
        self.positive = positive

    def __str__(self):
        if self.positive:
            output = ""
        else:
            output = "-"
        return output + "{}_{}_{}".format(self.letter, self.i, self.j)

    __repr__ = __str__
    pretty = __str__

    def __neg__(self):
        return Variable(not self.positive, self.letter, self.i, self.j)

