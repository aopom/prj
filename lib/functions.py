global ww
global WORLD_SIZE
global gs
global game_rules

from variable import Variable

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
        [Variable(False, "W", 0, 0).pretty()],
        [Variable(False, "P", 0, 0).pretty()],
        [Variable(False, "S", 0, 0).pretty()],
        [Variable(False, "B", 0, 0).pretty()],
    ]
    # One thing per tile
    for i in range(WORLD_SIZE):
        for j in range(WORLD_SIZE):
            game_rules.append([Variable(False, "G", i, j).pretty(), Variable(False, "W", i, j).pretty()])
            game_rules.append([Variable(False, "G", i, j).pretty(), Variable(False, "P", i, j).pretty()])
            game_rules.append([Variable(False, "P", i, j).pretty(), Variable(False, "W", i, j).pretty()])

    # One Wumpus per game
    for i in range(WORLD_SIZE):
        for j in range(WORLD_SIZE):
            for k in range(WORLD_SIZE):
                for l in range(WORLD_SIZE):
                    if i != k or j != l:
                        game_rules.append([Variable(False, "W", i, j).pretty(), Variable(False, "W", k, l).pretty()])

    # Pits around the Breeze
    for i in range(WORLD_SIZE):
        for j in range(WORLD_SIZE):
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
    for i in range(WORLD_SIZE):
        for j in range(WORLD_SIZE):
            clause = [Variable(False, "B", i, j).pretty()]
            if i > 0:
                clause.append(Variable(True, "W", i - 1, j).pretty())
            if j > 0:
                clause.append(Variable(True, "W", i, j - 1).pretty())
            if i < WORLD_SIZE - 1:
                clause.append(Variable(True, "W", i + 1, j).pretty())
            if j < WORLD_SIZE - 1:
                clause.append(Variable(True, "W", i, j + 1).pretty())
            game_rules.append(clause)

    # pas d'odeur ni de puit donc pas de wumpus autour ( un puit cache une odeur pestidenntielle)
    for i in range(WORLD_SIZE):
        for j in range(WORLD_SIZE):
            clause = [ Variable(False, "S", i, j).pretty(), Variable(False, "P", i, j).pretty() ]
            if i > 0:
                game_rules.append(clause + [Variable(False, "W", i-1, j).pretty()])
            if j > 0:
                game_rules.append(clause + [Variable(False, "W", i, j-1).pretty()])
            if i < WORLD_SIZE - 1:
                game_rules.append(clause + [Variable(False, "W", i+1, j).pretty()])
            if j < WORLD_SIZE - 1:
                game_rules.append(clause + [Variable(False, "W", i, j+1).pretty()])

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
    assert  a or b
    return a - b


def safe_tile(i, j):
    """should you probe this tile without cautious_probe ?
    """
    return 1 == test_variable(Variable(False, "W", i, j)) and 1 == test_variable(Variable(False, "P", i, j))

