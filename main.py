import random
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
    # première action
    ww.probe(0, 0)
    unknown_tiles = [":troll_face:"]
    # While some tiles are unknown
    while len(unknown_tiles) > 0:
        # add new knowledge
        for clause in knowledge_to_clauses():
            gs.push_variable_clause(clause)
        # pick a tile
        knowledge = ww.get_knowledge()
        len_knowledge = len(knowledge)
        unknown_tiles = [(i, j) for i in range(len_knowledge) for j in range(len_knowledge) if knowledge[i][j] == "?"]
        safe_tiles = [(i, j) for (i, j) in unknown_tiles if safe_tile(i, j)]
        # probe
        if len(safe_tiles) > 0:
            for (i, j) in safe_tiles:
                ww.probe(i, j)
                print("ninja probe {} {}".format(i, j))
        elif len(unknown_tiles) > 0:
            (i, j) = unknown_tiles[random.randrange(len(unknown_tiles))]
            ww.cautious_probe(i, j)
            print("cautious probe {} {}".format(i, j))
        ww.print_knowledge()


def fill_rules():
    # First tile rule
    """game_rules = [
        [Variable(False, "W", 0, 0).pretty()],
        [Variable(False, "P", 0, 0).pretty()],
        [Variable(False, "S", 0, 0).pretty()],
        [Variable(False, "B", 0, 0).pretty()],
    ]"""
    game_rules = []

    almeno_uno_wumpus = []
    for i in range(WORLD_SIZE):
        for j in range(WORLD_SIZE):
            almeno_uno_wumpus.append(Variable(True, "W", i, j).pretty())

    game_rules.append(almeno_uno_wumpus)

    for i in range(WORLD_SIZE):
        for j in range(WORLD_SIZE):
            # One thing per tile
            game_rules.append([Variable(False, "G", i, j).pretty(), Variable(False, "W", i, j).pretty()])
            game_rules.append([Variable(False, "G", i, j).pretty(), Variable(False, "P", i, j).pretty()])
            game_rules.append([Variable(False, "P", i, j).pretty(), Variable(False, "W", i, j).pretty()])

            # One Wumpus per game
            # for i in range(WORLD_SIZE):
            # for j in range(WORLD_SIZE):
            for k in range(WORLD_SIZE):
                for l in range(WORLD_SIZE):
                    if i != k or j != l:
                        game_rules.append([Variable(False, "W", i, j).pretty(), Variable(False, "W", k, l).pretty()])

            # Pits around the Breeze
            # for i in range(WORLD_SIZE):
            # for j in range(WORLD_SIZE):
            clause = [Variable(False, "B", i, j).pretty()]
            if i > 0:
                clause.append(Variable(True, "P", i - 1, j).pretty())
            if j > 0:
                clause.append(Variable(True, "P", i, j - 1).pretty())
            if i < WORLD_SIZE - 1:
                clause.append(Variable(True, "P", i + 1, j).pretty())
            if j < WORLD_SIZE - 1:
                clause.append(Variable(True, "P", i, j + 1).pretty())
            game_rules.append(clause)

            # Wumpus around the Strench
            # for i in range(WORLD_SIZE):
            # for j in range(WORLD_SIZE):
            clause = [Variable(False, "S", i, j).pretty()]
            if i > 0:
                clause.append(Variable(True, "W", i - 1, j).pretty())
            if j > 0:
                clause.append(Variable(True, "W", i, j - 1).pretty())
            if i < WORLD_SIZE - 1:
                clause.append(Variable(True, "W", i + 1, j).pretty())
            if j < WORLD_SIZE - 1:
                clause.append(Variable(True, "W", i, j + 1).pretty())
            game_rules.append(clause)

            # un puit est entouré de environ 4 breeze sauf sur les bords
            # for i in range(WORLD_SIZE):
            # for j in range(WORLD_SIZE):
            clause = [Variable(False, "P", i, j).pretty()]
            if i > 0:
                game_rules.append(clause + [Variable(True, "B", i - 1, j).pretty()])
            if j > 0:
                game_rules.append(clause + [Variable(True, "B", i, j - 1).pretty()])
            if i < WORLD_SIZE - 1:
                game_rules.append(clause + [Variable(True, "B", i + 1, j).pretty()])
            if j < WORLD_SIZE - 1:
                game_rules.append(clause + [Variable(True, "B", i, j + 1).pretty()])

            # un wumpus est entouré de environ 4 strench sauf sur les bords
            # for i in range(WORLD_SIZE):
            # for j in range(WORLD_SIZE):
            clause = [Variable(False, "W", i, j).pretty()]
            if i > 0:
                game_rules.append(clause + [Variable(True, "S", i - 1, j).pretty()])
            if j > 0:
                game_rules.append(clause + [Variable(True, "S", i, j - 1).pretty()])
            if i < WORLD_SIZE - 1:
                game_rules.append(clause + [Variable(True, "S", i + 1, j).pretty()])
            if j < WORLD_SIZE - 1:
                game_rules.append(clause + [Variable(True, "S", i, j + 1).pretty()])

            # pas d'odeur ni de puit donc pas de wumpus autour ( un puit cache une odeur pestidenntielle)
            # for i in range(WORLD_SIZE):
            # for j in range(WORLD_SIZE):
            clause = [Variable(True, "S", i, j).pretty()]
            # clause = [Variable(True, "S", i, j).pretty(), Variable(True, "P", i, j).pretty()]
            if i > 0:
                game_rules.append(clause + [Variable(False, "W", i - 1, j).pretty()])
            if j > 0:
                game_rules.append(clause + [Variable(False, "W", i, j - 1).pretty()])
            if i < WORLD_SIZE - 1:
                game_rules.append(clause + [Variable(False, "W", i + 1, j).pretty()])
            if j < WORLD_SIZE - 1:
                game_rules.append(clause + [Variable(False, "W", i, j + 1).pretty()])

            # pas de vent ni de wumpus donc pas de puit autour
            # for i in range(WORLD_SIZE):
            # for j in range(WORLD_SIZE):
            clause = [Variable(True, "B", i, j).pretty(), Variable(True, "W", i, j).pretty()]
            if i > 0:
                game_rules.append(clause + [Variable(False, "P", i - 1, j).pretty()])
            if j > 0:
                game_rules.append(clause + [Variable(False, "P", i, j - 1).pretty()])
            if i < WORLD_SIZE - 1:
                game_rules.append(clause + [Variable(False, "P", i + 1, j).pretty()])
            if j < WORLD_SIZE - 1:
                game_rules.append(clause + [Variable(False, "P", i, j + 1).pretty()])

    return game_rules


def knowledge_to_clauses():
    clauses = []
    size = ww.get_n()
    knowledge = ww.get_knowledge()
    for i in range(size):
        for j in range(size):
            if knowledge[i][j] != "?":
                for letter in "PWBSG":
                    clauses.append([Variable((letter in knowledge[i][j]), letter, i, j)])
    return clauses


def interrogate(clause):
    global interrogation_count
    interrogation_count += 1
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


def safe_tile2(i, j):
    # Are we sure there is a wumpus ?
    no_wumpus = Variable(False, "W", i, j)
    there_is_a_wumpus = 0 == interrogate([no_wumpus.pretty()])
    if there_is_a_wumpus:
        return -1

    # Are we sure there is a pit ?
    no_pit = Variable(False, "P", i, j)
    there_is_a_pit = 0 == interrogate([no_pit.pretty()])
    if there_is_a_pit:
        return -1

    # Are we sure there is no wumpus ?
    there_is_no_wumpus = 0 == interrogate([(-no_wumpus).pretty()])
    if not there_is_no_wumpus:
        return 0

    # Are we sure there is a pit ?
    there_is_no_pit = 0 == interrogate([(-no_pit).pretty()])
    return there_is_no_pit


def explo_full_gopherpysat2():
    # première action
    ww.probe(0, 0)
    unknown_tiles = [":troll_face:"]
    # While some tiles are unknown
    while len(unknown_tiles) > 0:
        # add new knowledge
        for clause in knowledge_to_clauses():
            gs.push_variable_clause(clause)
        # pick a tile
        knowledge = ww.get_knowledge()
        len_knowledge = len(knowledge)
        unknown_tiles = [(i, j) for i in range(len_knowledge) for j in range(len_knowledge) if knowledge[i][j] == "?"]
        safe_tiles = []
        unsafe_tiles = []
        for (i, j) in unknown_tiles:
            safe = safe_tile2(i, j)
            if safe == 1:
                safe_tiles.append((i, j))
            elif safe == -1:
                unsafe_tiles.append((i, j))

        # probe
        knew = False
        if len(safe_tiles) > 0:
            knew = True
            for (i, j) in safe_tiles:
                ww.probe(i, j)
                print("ninja probe {} {}".format(i, j))
        if len(unsafe_tiles) > 0:
            knew = True
            for (i, j) in unsafe_tiles:
                ww.cautious_probe(i, j)
                print("sure cautious probe {} {}".format(i, j))

        elif not knew and len(unknown_tiles) > 0:
            (i, j) = unknown_tiles[random.randrange(len(unknown_tiles))]
            ww.cautious_probe(i, j)
            print("cautious probe {} {}".format(i, j))
        # ww.print_knowledge()


def mainloop():
    # Create world
    global ww
    # We provide a world length and a seed
    ww = WumpusWorld(n=8, seed=21)
    print(ww)
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
    for clause in game_rules:
        gs.push_pretty_clause(clause)

    global interrogation_count
    interrogation_count = 0

    explo_full_gopherpysat()
    print("cost : {}".format(ww.get_cost()))
    print("interrogation_count : {}".format(interrogation_count))
    ww.print_knowledge()


# # Finally add clauses
# for i in range(len(clauses)):
#     gs.push_pretty_clause(clauses[i])

# # Solve...
# print(gs.dimacs())
# print(gs.solve())
# print(gs.get_pretty_model())
# print(gs.get_model())


def test_gamerules():
    # Create world
    global ww
    ww = WumpusWorld()
    print(ww)
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
    for clause in game_rules:
        gs.push_pretty_clause(clause)

    assert gs.solve() == True

    ww.probe(0, 0)  # première action
    for clause in knowledge_to_clauses():
        gs.push_variable_clause(clause)
    ww.print_knowledge()

    print("beauty_print(game_rules)")
    beauty_print(game_rules)
    print("beauty_print(knowledge_to_clauses())")
    beauty_print(knowledge_to_clauses())

    # on ne sait pas ou le wumpus est ni les pits
    for i in range(WORLD_SIZE):
        for j in range(WORLD_SIZE):
            if (i, j) != (0, 0) and (i, j) != (0, 1) and (i, j) != (1, 0):
                for letter in "WPBS":
                    # on ne sait rien  sur ces cases là!
                    assert test_variable(Variable(True, letter, i, j)) == 0
                    assert test_variable(Variable(False, letter, i, j)) == 0
            elif (i, j) == (0, 0):
                for letter in "WPBS":
                    # Y' a R
                    assert test_variable(Variable(True, letter, i, j)) == -1
                    assert test_variable(Variable(False, letter, i, j)) == 1
            elif (i, j) == (0, 1) or (i, j) == (1, 0):
                # on ne sait pas s' il y a une brise ou odeur pestidentielle
                print("""test_variable(Variable(True, "B", i, j)) == 0   """, test_variable(Variable(True, "B", i, j)))
                assert test_variable(Variable(True, "B", i, j)) == 0
                assert test_variable(Variable(False, "B", i, j)) == 0
                assert test_variable(Variable(True, "S", i, j)) == 0
                assert test_variable(Variable(False, "S", i, j)) == 0
                # il n'y a pas de danger
                assert test_variable(Variable(True, "W", i, j)) == -1
                assert test_variable(Variable(False, "W", i, j)) == 1
                assert test_variable(Variable(True, "P", i, j)) == -1
                assert test_variable(Variable(False, "P", i, j)) == 1

    # print("game rules:")
    # beauty_print(game_rules)

    # runtime tests
    ww.print_knowledge()
    ww.cautious_probe(2, 0)  # trouve un wumpus
    for clause in knowledge_to_clauses():
        gs.push_variable_clause(clause)

    ww.print_knowledge()
    for i in range(WORLD_SIZE):
        for j in range(WORLD_SIZE):
            if (i, j) != (2, 0):
                assert test_variable(Variable(True, "W", i, j)) == -1
                assert test_variable(Variable(False, "W", i, j)) == 1
            elif (i, j) == (0, 0):
                for letter in "WPBS":
                    # Y' a R
                    assert test_variable(Variable(True, letter, i, j)) == -1
                    assert test_variable(Variable(False, letter, i, j)) == 1
            elif (i, j) == (0, 1) or (i, j) == (1, 0):
                # on ne sait pas s' il y a une brise ou odeur pestidentielle
                assert test_variable(Variable(True, "B", i, j)) == 0
                assert test_variable(Variable(False, "B", i, j)) == 0
                assert test_variable(Variable(True, "S", i, j)) == 0
                assert test_variable(Variable(False, "S", i, j)) == 0

    # for (i, j) in ((1, 0), (3, 0), (2, 1)):
    # assert interrogate([Variable(True, "P", i, j), Variable(True, "P", i, j)])

    print("cost : {}".format(ww.get_cost()))


if __name__ == "__main__":
    mainloop()
    # test_gamerules()
