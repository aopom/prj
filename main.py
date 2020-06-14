import random
import threading
import multiprocessing
from lib.gopherpysat import Gophersat
from lib.wumpus import WumpusWorld


def beauty_print(double_array):
    print("[")
    for line in double_array:
        print(line, ",", sep="")
    print("]")


def fill_rules():
    game_rules = []
    almeno_uno_wumpus = []
    for i in range(WORLD_SIZE):
        for j in range(WORLD_SIZE):
            almeno_uno_wumpus.append(f"W_{i}_{j}")

    game_rules.append(almeno_uno_wumpus)

    for i in range(WORLD_SIZE):
        for j in range(WORLD_SIZE):
            # One thing per tile
            game_rules.append([f"-G_{i}_{j}", f"-W_{i}_{j}"])
            game_rules.append([f"-G_{i}_{j}", f"-P_{i}_{j}"])
            game_rules.append([f"-P_{i}_{j}", f"-W_{i}_{j}"])

            # One Wumpus per game
            # for i in range(WORLD_SIZE):
            # for j in range(WORLD_SIZE):
            for k in range(WORLD_SIZE):
                for l in range(WORLD_SIZE):
                    # if i != k or j != l:
                    # 10% plus rapide xD à l'éxecution
                    if i < k or j < l:
                        game_rules.append([f"-W_{i}_{j}", f"-W_{k}_{l}"])

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
            game_rules.append(clause)

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
            game_rules.append(clause)

            # un puit est entouré de environ 4 breeze sauf sur les bords
            # for i in range(WORLD_SIZE):
            # for j in range(WORLD_SIZE):
            clause = [f"-P_{i}_{j}"]
            if i > 0:
                game_rules.append(clause + [f"B_{i - 1}_{j}"])
            if j > 0:
                game_rules.append(clause + [f"B_{i}_{j - 1}"])
            if i < WORLD_SIZE - 1:
                game_rules.append(clause + [f"B_{i + 1}_{j}"])
            if j < WORLD_SIZE - 1:
                game_rules.append(clause + [f"B_{i}_{j + 1}"])

            # un wumpus est entouré de environ 4 strench sauf sur les bords
            # for i in range(WORLD_SIZE):
            # for j in range(WORLD_SIZE):
            clause = [f"-W_{i}_{j}"]
            if i > 0:
                game_rules.append(clause + [f"S_{i - 1}_{j}"])
            if j > 0:
                game_rules.append(clause + [f"S_{i}_{j - 1}"])
            if i < WORLD_SIZE - 1:
                game_rules.append(clause + [f"S_{i + 1}_{j}"])
            if j < WORLD_SIZE - 1:
                game_rules.append(clause + [f"S_{i}_{j + 1}"])

            # pas d'odeur donc pas de wumpus autour
            # for i in range(WORLD_SIZE):
            # for j in range(WORLD_SIZE):
            clause = [f"S_{i}_{j}"]
            # clause = [f"S_{i}_{j}", f"P_{i}_{j}"]
            if i > 0:
                game_rules.append(clause + [f"-W_{i - 1}_{j}"])
            if j > 0:
                game_rules.append(clause + [f"-W_{i}_{j - 1}"])
            if i < WORLD_SIZE - 1:
                game_rules.append(clause + [f"-W_{i + 1}_{j}"])
            if j < WORLD_SIZE - 1:
                game_rules.append(clause + [f"-W_{i}_{j + 1}"])

            # pas de vent donc pas de puit autour
            # for i in range(WORLD_SIZE):
            # for j in range(WORLD_SIZE):
            clause = [f"B_{i}_{j}", f"W_{i}_{j}"]
            if i > 0:
                game_rules.append(clause + [f"-P_{i - 1}_{j}"])
            if j > 0:
                game_rules.append(clause + [f"-P_{i}_{j - 1}"])
            if i < WORLD_SIZE - 1:
                game_rules.append(clause + [f"-P_{i + 1}_{j}"])
            if j < WORLD_SIZE - 1:
                game_rules.append(clause + [f"-P_{i}_{j + 1}"])

    return game_rules


def knowledge_to_clauses():
    clauses = []
    size = WORLD_SIZE
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


def interrogate(gopherpysat, clause):
    global interrogation_count
    interrogation_count += 1
    gopherpysat.push_pretty_clause(clause)
    output = gopherpysat.solve()
    gopherpysat.pop_clause()
    return output


def safe_tile2(gopherpysat, i, j):
    # Are we sure there is a pit ?
    there_is_a_pit = 0 == interrogate(gopherpysat, [f"-P_{i}_{j}"])
    if there_is_a_pit:
        return -1
    # Are we sure there is a wumpus ?
    there_is_a_wumpus = 0 == interrogate(gopherpysat, [f"-W_{i}_{j}"])
    if there_is_a_wumpus:
        return -1
    # Are we sure there is no wumpus ?
    there_is_no_wumpus = 0 == interrogate(gopherpysat, [f"W_{i}_{j}"])
    if not there_is_no_wumpus:
        return 0
    # Are we sure there is a pit ?
    there_is_no_pit = 0 == interrogate(gopherpysat, [f"P_{i}_{j}"])
    return there_is_no_pit


def adjacent_to_known_tile(knowledge, i, j):
    return (
        (i > 0 and knowledge[i - 1][j] != "?")
        or (j > 0 and knowledge[i][j - 1] != "?")
        or (i < WORLD_SIZE - 1 and knowledge[i + 1][j] != "?")
        or (j < WORLD_SIZE - 1 and knowledge[i][j + 1] != "?")
    )


def try_multiple_tiles(gopherpysat, tiles, start, step, knowledge):
    global action

    for clause in knowledge:
        gopherpysat.push_pretty_clause(clause)

    index = start
    while index < len(tiles):
        (i, j) = tiles[index]
        index += step

        safe = safe_tile2(gopherpysat, i, j)
        if safe == 1:
            action = True
            ww.probe(i, j)
            print(f"ninja probe {i} {j}")
        elif safe == -1:
            action = True
            ww.cautious_probe(i, j)
            print(f"sure cautious probe {i} {j}")


def explo_full_gopherpysat2(gopherpysats):
    # première action
    ww.probe(0, 0)
    unknown_tiles = [(i, j) for i in range(WORLD_SIZE) for j in range(WORLD_SIZE)]
    # While some tiles are unknown
    while len(unknown_tiles) > 0:
        # select all unknown tiles
        knowledge = ww.get_knowledge()
        unknown_tiles = [(i, j) for (i, j) in unknown_tiles if knowledge[i][j] == "?"]

        # choose only tiles worth trying
        peripheric_tiles = [(i, j) for (i, j) in unknown_tiles if adjacent_to_known_tile(knowledge, i, j)]

        # prepare knowledge to be added to each gopherpysat
        knowledge = knowledge_to_clauses()

        # launch threads
        threads = []
        global action
        action = False

        for i in range(len(gopherpysats)):
            thread = threading.Thread(target=try_multiple_tiles, args=(gopherpysats[i], peripheric_tiles, i, len(gopherpysats), knowledge))
            threads.append(thread)
            thread.start()

        # wait for threads
        for thread in threads:
            thread.join()

        # if no tile was probed
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
    ww = WumpusWorld(n=10, seed=11)
    # World width
    global WORLD_SIZE
    WORLD_SIZE = ww.get_n()

    # Generate Vocabulary
    # Pit, Wumpus, Breeze, Stench, Gold
    voc = [f"{letter}_{i}_{j}" for i in range(WORLD_SIZE) for j in range(WORLD_SIZE) for letter in ["P", "W", "B", "S", "G"]]

    # Create gophersat object
    cpus = multiprocessing.cpu_count()
    gopherpysats = [Gophersat(voc=voc) for i in range(cpus)]
    print(f"cpus: {cpus}")

    for clause in fill_rules():
        for gs in gopherpysats:
            gs.push_pretty_clause(clause)

    global interrogation_count
    interrogation_count = 0

    explo_full_gopherpysat2(gopherpysats)
    print("cost : {}".format(ww.get_cost()))
    print("interrogation_count : {}".format(interrogation_count))
    ww.print_knowledge()


if __name__ == "__main__":
    mainloop()
