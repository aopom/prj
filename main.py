from lib.gopherpysat import Gophersat
from lib.wumpus import WumpusWorld


def print_array_multiline(arraaaay):
    print()
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
                    if letter in knowledge[i][j]:
                        clauses.append("{}_{}_{}".format(letter, i, j))
                    else:
                        clauses.append("-{}_{}_{}".format(letter, i, j))

    return clauses


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
        f"{letter}{i}_{j}"
        for i in range(WORLD_SIZE)
        for j in range(WORLD_SIZE)
        for letter in ["P", "W", "B", "S", "G"]
    ]
    print(knowledge_to_clauses())

    for i in range(WORLD_SIZE):
        for j in range(WORLD_SIZE):
            ww.cautious_probe(i, j)

    ww.print_knowledge()

    print(knowledge_to_clauses())
    print("cost : {}".format(ww.get_cost()))

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
