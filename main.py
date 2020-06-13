import random
from lib.gopherpysat import Gophersat
from lib.wumpus import WumpusWorld


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
            gs.push_pretty_clause(clause)
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
        # ww.print_knowledge()


def fill_rules():
    # First tile rule
    """game_rules = [
        [f"-W_0_0"],
        [f"-P_0_0"],
        [f"-S_0_0"],
        [f"-B_0_0"],
    ]"""
    almeno_uno_wumpus = []
    for i in range(WORLD_SIZE):
        for j in range(WORLD_SIZE):
            almeno_uno_wumpus.append(f"W_{i}_{j}")

    gs.push_pretty_clause(almeno_uno_wumpus)

    for i in range(WORLD_SIZE):
        for j in range(WORLD_SIZE):
            # One thing per tile
            gs.push_pretty_clause([f"-G_{i}_{j}", f"-W_{i}_{j}"])
            gs.push_pretty_clause([f"-G_{i}_{j}", f"-P_{i}_{j}"])
            gs.push_pretty_clause([f"-P_{i}_{j}", f"-W_{i}_{j}"])

            # One Wumpus per game
            # for i in range(WORLD_SIZE):
            # for j in range(WORLD_SIZE):
            for k in range(WORLD_SIZE):
                for l in range(WORLD_SIZE):
                    # if i != k or j != l:
                    # 10% plus rapide xD à l'éxecution
                    if i < k or j < l:
                        gs.push_pretty_clause([f"-W_{i}_{j}", f"-W_{k}_{l}"])

            # Pits around the Breeze
            # for i in range(WORLD_SIZE):
            # for j in range(WORLD_SIZE):
            clause = [f"-B_{i}_{j}"]
            if i > 0:
                clause.append(f"P_{i - 1}_{j}")
            if j > 0:
                clause.append(f"P_{i}_{j - 1}")
            if i < WORLD_SIZE - 1:
                clause.append(f"P_{i + 1}_{j}")
            if j < WORLD_SIZE - 1:
                clause.append(f"P_{i}_{j + 1}")
            gs.push_pretty_clause(clause)

            # Wumpus around the Strench
            # for i in range(WORLD_SIZE):
            # for j in range(WORLD_SIZE):
            clause = [f"-S_{i}_{j}"]
            if i > 0:
                clause.append(f"W_{i - 1}_{j}")
            if j > 0:
                clause.append(f"W_{i}_{j - 1}")
            if i < WORLD_SIZE - 1:
                clause.append(f"W_{i + 1}_{j}")
            if j < WORLD_SIZE - 1:
                clause.append(f"W_{i}_{j + 1}")
            gs.push_pretty_clause(clause)

            # un puit est entouré de environ 4 breeze sauf sur les bords
            # for i in range(WORLD_SIZE):
            # for j in range(WORLD_SIZE):
            clause = [f"-P_{i}_{j}"]
            if i > 0:
                gs.push_pretty_clause(clause + [f"B_{i - 1}_{j}"])
            if j > 0:
                gs.push_pretty_clause(clause + [f"B_{i}_{j - 1}"])
            if i < WORLD_SIZE - 1:
                gs.push_pretty_clause(clause + [f"B_{i + 1}_{j}"])
            if j < WORLD_SIZE - 1:
                gs.push_pretty_clause(clause + [f"B_{i}_{j + 1}"])

            # un wumpus est entouré de environ 4 strench sauf sur les bords
            # for i in range(WORLD_SIZE):
            # for j in range(WORLD_SIZE):
            clause = [f"-W_{i}_{j}"]
            if i > 0:
                gs.push_pretty_clause(clause + [f"S_{i - 1}_{j}"])
            if j > 0:
                gs.push_pretty_clause(clause + [f"S_{i}_{j - 1}"])
            if i < WORLD_SIZE - 1:
                gs.push_pretty_clause(clause + [f"S_{i + 1}_{j}"])
            if j < WORLD_SIZE - 1:
                gs.push_pretty_clause(clause + [f"S_{i}_{j + 1}"])

            # pas d'odeur donc pas de wumpus autour
            # for i in range(WORLD_SIZE):
            # for j in range(WORLD_SIZE):
            clause = [f"S_{i}_{j}"]
            # clause = [f"S_{i}_{j}", f"P_{i}_{j}"]
            if i > 0:
                gs.push_pretty_clause(clause + [f"-W_{i - 1}_{j}"])
            if j > 0:
                gs.push_pretty_clause(clause + [f"-W_{i}_{j - 1}"])
            if i < WORLD_SIZE - 1:
                gs.push_pretty_clause(clause + [f"-W_{i + 1}_{j}"])
            if j < WORLD_SIZE - 1:
                gs.push_pretty_clause(clause + [f"-W_{i}_{j + 1}"])

            # pas de vent donc pas de puit autour
            # for i in range(WORLD_SIZE):
            # for j in range(WORLD_SIZE):
            clause = [f"B_{i}_{j}", f"W_{i}_{j}"]
            if i > 0:
                gs.push_pretty_clause(clause + [f"-P_{i - 1}_{j}"])
            if j > 0:
                gs.push_pretty_clause(clause + [f"-P_{i}_{j - 1}"])
            if i < WORLD_SIZE - 1:
                gs.push_pretty_clause(clause + [f"-P_{i + 1}_{j}"])
            if j < WORLD_SIZE - 1:
                gs.push_pretty_clause(clause + [f"-P_{i}_{j + 1}"])

    # return game_rules


def knowledge_to_clauses():
    clauses = []
    size = ww.get_n()
    knowledge = ww.get_knowledge()
    for i in range(size):
        for j in range(size):
            if knowledge[i][j] != "?":
                for letter in "PWBSG":
                    if letter in knowledge[i][j]:
                        clauses.append([f"{letter}_{i}_{j}"])
                    else:
                        clauses.append([f"-{letter}_{i}_{j}"])
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

    a = interrogate([variable])
    if variable[0] == "-":
        b = interrogate([variable[1:]])
    else:
        b = interrogate([f"-{variable}"])

    return a - b


def safe_tile(i, j):
    """should you probe this tile without cautious_probe ?
    """
    return 1 == test_variable(f"-W_{i}_{j}") and 1 == test_variable(f"-P_{i}_{j}")


def safe_tile2(i, j):
    # Are we sure there is a pit ?
    there_is_a_pit = 0 == interrogate([f"-P_{i}_{j}"])
    if there_is_a_pit:
        return -1

    # Are we sure there is a wumpus ?
    there_is_a_wumpus = 0 == interrogate([f"-W_{i}_{j}"])
    if there_is_a_wumpus:
        return -1

    # Are we sure there is no wumpus ?
    there_is_no_wumpus = 0 == interrogate([f"W_{i}_{j}"])
    if not there_is_no_wumpus:
        return 0

    # Are we sure there is a pit ?
    there_is_no_pit = 0 == interrogate([f"P_{i}_{j}"])
    return there_is_no_pit


def explo_full_gopherpysat2():
    # première action
    ww.probe(0, 0)
    unknown_tiles = [(i, j) for i in range(WORLD_SIZE) for j in range(WORLD_SIZE)]
    # While some tiles are unknown
    while len(unknown_tiles) > 0:
        # add new knowledge
        for clause in knowledge_to_clauses():
            gs.push_pretty_clause(clause)
        # pick a tile
        knowledge = ww.get_knowledge()
        len_knowledge = len(knowledge)
        unknown_tiles = [(i, j) for (i, j) in unknown_tiles if knowledge[i][j] == "?"]

        action = False
        for (i, j) in unknown_tiles:
            safe = safe_tile2(i, j)
            if safe == 1:
                action = True
                ww.probe(i, j)
                print("ninja probe {} {}".format(i, j))
            elif safe == -1:
                action = True
                ww.cautious_probe(i, j)
                print("sure cautious probe {} {}".format(i, j))

        # probe
        # ninja = False
        # if len(safe_tiles) > 0:
        # ninja = True
        # for (i, j) in safe_tiles:
        # ww.probe(i, j)
        # print("ninja probe {} {}".format(i, j))
        #
        # if len(unsafe_tiles) > 0:
        # for (i, j) in unsafe_tiles:
        # ww.cautious_probe(i, j)
        # print("sure cautious probe {} {}".format(i, j))
        #
        # elif not ninja and len(unknown_tiles) > 0:
        if not action and len(unknown_tiles) > 0:
            (i, j) = unknown_tiles[random.randrange(len(unknown_tiles))]
            ww.cautious_probe(i, j)
            print("cautious probe {} {}".format(i, j))
        # ww.print_knowledge()
        print()


def mainloop():
    # Create world
    global ww
    # We provide a world length and a seed
    ww = WumpusWorld(n=8, seed=14)
    # print(ww)
    # print("cost : {}".format(ww.get_cost()))

    # World width
    global WORLD_SIZE
    WORLD_SIZE = ww.get_n()

    # Generate Vocabulary
    # Pit, Wumpus, Breeze, Stench, Gold
    voc = [f"{letter}_{i}_{j}" for i in range(WORLD_SIZE) for j in range(WORLD_SIZE) for letter in ["P", "W", "B", "S", "G"]]

    # Create gophersat object
    global gs
    gs = Gophersat(voc=voc)

    # global game_rules
    # game_rules = fill_rules()
    # for clause in game_rules:
    #     gs.push_pretty_clause(clause)
    fill_rules()

    global interrogation_count
    interrogation_count = 0

    explo_full_gopherpysat2()
    print("cost : {}".format(ww.get_cost()))
    print("interrogation_count : {}".format(interrogation_count))
    ww.print_knowledge()


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
    voc = [f"{letter}_{i}_{j}" for i in range(WORLD_SIZE) for j in range(WORLD_SIZE) for letter in ["P", "W", "B", "S", "G"]]

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
        gs.push_pretty_clause(clause)
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
                print("""test_variable(f"B_{i}_{j}" == 0  """, test_variable(f"B_{i}_{j}"))
                assert test_variable(f"B_{i}_{j}") == 0
                assert test_variable(f"-B_{i}_{j}") == 0
                assert test_variable(f"S_{i}_{j}") == 0
                assert test_variable(f"-S_{i}_{j}") == 0
                # il n'y a pas de danger
                assert test_variable(f"W_{i}_{j}") == -1
                assert test_variable(f"-W_{i}_{j}") == 1
                assert test_variable(f"P_{i}_{j}") == -1
                assert test_variable(f"-P_{i}_{j}") == 1

    # print("game rules:")
    # beauty_print(game_rules)

    # runtime tests
    ww.print_knowledge()
    ww.cautious_probe(2, 0)  # trouve un wumpus
    for clause in knowledge_to_clauses():
        gs.push_pretty_clause(clause)

    ww.print_knowledge()
    for i in range(WORLD_SIZE):
        for j in range(WORLD_SIZE):
            if (i, j) != (2, 0):
                assert test_variable(f"W_{i}_{j}") == -1
                assert test_variable(f"-W_{i}_{j}") == 1
            elif (i, j) == (0, 0):
                for letter in "WPBS":
                    # Y' a R
                    assert test_variable(Variable(True, letter, i, j)) == -1
                    assert test_variable(Variable(False, letter, i, j)) == 1
            elif (i, j) == (0, 1) or (i, j) == (1, 0):
                # on ne sait pas s' il y a une brise ou odeur pestidentielle
                assert test_variable(f"B_{i}_{j}") == 0
                assert test_variable(f"-B_{i}_{j}") == 0
                assert test_variable(f"S_{i}_{j}") == 0
                assert test_variable(f"-S_{i}_{j}") == 0

    # for (i, j) in ((1, 0), (3, 0), (2, 1)):
    # assert interrogate([f"P_{i}_{j}", f"P_{i}_{j}"]}

    print("cost : {}".format(ww.get_cost()))


if __name__ == "__main__":
    mainloop()
    # test_gamerules()
