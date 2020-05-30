from lib.gopherpysat import Gophersat
from lib.wumpus import WumpusWorld

from pprint import pprint

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
            
def print_array_multiline(arraaaay):
    for line in arraaaay:
        print(line)

def explo_full_cautious(ww):  # coute 800
    for i in range(WORLD_SIZE):
        for j in range(WORLD_SIZE):
            ww.cautious_probe(i, j)


def explo_full_simple_probe(ww):  # coute 4160
    for i in range(WORLD_SIZE):
        for j in range(WORLD_SIZE):
            ww.probe(i, j)


def knowledge_to_clauses():
    clauses = [] 
    size = ww.get_n()
    knowledge = ww.get_knowledge()
    for i in range(size):
        for j in range(size):
            if knowledge[i][j] != "?":
                for letter in "PWBSG":
                    clauses.append(Variable( (letter in knowledge[i][j]) , letter, i, j))

    return clauses

def interrogate(clause):
    """retourne un booleen
    """
    gs.push_pretty_clause(clause)
    output = gs.solve()
    gs.pop_clause()
    return output

def test_variable(variable):
    # si c' est bon a = 1 et b = 0
    # si on sait pas a-b = 0
    # si c' est pas bon a-b = -1
    a = interrogate([variable.pretty()])
    b = interrogate([(-variable).pretty()])
    
    return a - b

def mainloop():
    # Create world
    global ww
    ww = WumpusWorld()
    print("cost : {}".format(ww.get_cost()))

    # World width
    global WORLD_SIZE
    WORLD_SIZE = ww.get_n()

    # Generate Vocabulary
    # Pit, Wumpus, Breeze, Stench, Gold
    voc = [
        f"{letter}_{i}_{j}"
        for i in range(WORLD_SIZE)
        for j in range(WORLD_SIZE)
        for letter in ["P", "W", "B", "S", "G"]
    ]

    # Create gophersat object
    global gs
    gs = Gophersat(voc=voc)

    print(knowledge_to_clauses())

    for i in range(WORLD_SIZE):
        for j in range(WORLD_SIZE):
            # if i != 3 and j != 3:
            ww.cautious_probe(i, j)

    ww.print_knowledge()

    print(knowledge_to_clauses())
    print("cost : {}".format(ww.get_cost()))

    clauses = knowledge_to_clauses()
    for clause in clauses :
        # print(clause.pretty())
        gs.push_pretty_clause([clause.pretty()])

    print(test_variable(Variable(True, "W", 0, 0)))
    print(test_variable(Variable(True, "W", 3, 3)))
    print(test_variable(Variable(True, "W", 2, 0)))
    # print(ww)

    # # Create gophersat object
    # gs = Gophersat(voc=voc)
    # clauses = [
    #     # There are no obstacles on third first cases
    #     ["-P0_0"],
    #     ["-P1_0"],
    #     ["-P0_1"],
    #     ["-W0_0"],
    #     ["-W1_0"],
    #     ["-W0_1"],
    # ]


# # Finally add clauses
# for i in range(len(clauses)):
#     gs.push_pretty_clause(clauses[i])

# # Solve...
# print(gs.dimacs())
# print(gs.solve())
# print(gs.get_pretty_model())
# print(gs.get_model())


if __name__ == "__main__":
    mainloop()
