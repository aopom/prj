from lib.gopherpysat import Gophersat
from lib.wumpus import WumpusWorld
from lib.variable import *

def beauty_print(double_array):
    print("[")
    for line in double_array:
        print(line, ",", sep="")
    print("]")


def explo_full_cautious():  # coute 800
    for i in range(WORLD_SIZE):
        for j in range(WORLD_SIZE):
            ww.cautious_probe(i, j)


def explo_full_simple_probe():  # coute 4160
    for i in range(WORLD_SIZE):
        for j in range(WORLD_SIZE):
            ww.probe(i, j)


def explo_full_gopherpysat():
    known_tiles = [[False for i in range(WORLD_SIZE)] for j in range(WORLD_SIZE)]
    known_tiles[0][0] = True
    for i in range(WORLD_SIZE):
        for j in range(WORLD_SIZE):
            print(i, j, safe_tile(i, j))


def fill_rules():
    # First tile rule
    game_rules = [
        [Variable(False, "W", 0, 0)],
        [Variable(False, "P", 0, 0)],
        [Variable(False, "S", 0, 0)],
        [Variable(False, "B", 0, 0)],
    ]
    # One thing per tile
    for i in range(WORLD_SIZE):
        for j in range(WORLD_SIZE):
            game_rules.append([Variable(False, "G", i, j), Variable(False, "W", i, j)])
            game_rules.append([Variable(False, "G", i, j), Variable(False, "P", i, j)])
            game_rules.append([Variable(False, "P", i, j), Variable(False, "W", i, j)])

    # One Wumpus per game
    for i in range(WORLD_SIZE):
        for j in range(WORLD_SIZE):
            for k in range(WORLD_SIZE):
                for l in range(WORLD_SIZE):
                    if i != k or j != l:
                        game_rules.append([Variable(False, "W", i, j), Variable(False, "W", k, l)])

    # Pits around the Breeze
    for i in range(WORLD_SIZE):
        for j in range(WORLD_SIZE):
            clause = [Variable(False, "B", i, j)]
            if i > 0:
                clause.append(Variable(True, "P", i - 1, j))
            if j > 0:
                clause.append(Variable(True, "P", i, j - 1))
            if i < WORLD_SIZE - 1:
                clause.append(Variable(True, "P", i + 1, j))
            if j < WORLD_SIZE - 1:
                clause.append(Variable(True, "P", i, j + 1))
            game_rules.append(clause)

    # Wumpus around the Strench
    for i in range(WORLD_SIZE):
        for j in range(WORLD_SIZE):
            clause = [Variable(False, "B", i, j)]
            if i > 0:
                clause.append(Variable(True, "W", i - 1, j))
            if j > 0:
                clause.append(Variable(True, "W", i, j - 1))
            if i < WORLD_SIZE - 1:
                clause.append(Variable(True, "W", i + 1, j))
            if j < WORLD_SIZE - 1:
                clause.append(Variable(True, "W", i, j + 1))
            game_rules.append(clause)
    return game_rules


def knowledge_to_clauses():
    clauses = []
    size = ww.get_n()
    knowledge = ww.get_knowledge()
    for i in range(size):
        for j in range(size):
            if knowledge[i][j] != "?":
                for letter in "PWBSG":
                    clauses.append(Variable((letter in knowledge[i][j]), letter, i, j))
    return clauses


def interrogate(clause):
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


def safe_tile(i, j):
    """should you probe this tile without cautious_probe ?
    """
    return 1 == test_variable(Variable(False, "W", i, j)) and 1 == test_variable(Variable(False, "P", i, j))


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
        Variable(True, letter, i, j).pretty()
        for i in range(WORLD_SIZE)
        for j in range(WORLD_SIZE)
        for letter in ["P", "W", "B", "S", "G"]
    ]

    # Create gophersat object
    global gs
    gs = Gophersat(voc=voc)

    global game_rules
    game_rules = fill_rules()
    # print("game rules:")
    # beauty_print(game_rules)

    explo_full_gopherpysat()

    print("cost : {}".format(ww.get_cost()))

    # print(test_variable(Variable(True, "W", 0, 0)))
    # print(test_variable(Variable(True, "W", 3, 3)))
    # print(test_variable(Variable(True, "W", 2, 0)))
    # print(ww)

    # # Create gophersat object
    # gs = Gophersat(voc=voc)
    # clauses = [
    #     # There are no obstacles on third first tile
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
