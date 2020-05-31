from lib.gopherpysat import Gophersat
from lib.wumpus import WumpusWorld
from lib.variable import *

from lib.functions import *


def test_gamerules():
# Create world
    #global ww
    ww = WumpusWorld()
    print(ww)
    print("cost : {}".format(ww.get_cost()))

    # World width
    #global WORLD_SIZE
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
   #global gs
    gs = Gophersat(voc=voc)

    #global game_rules
    game_rules = fill_rules()
    for clause in game_rules:
        gs.push_pretty_clause(clause)
    
    assert gs.solve() == True;

    # on ne sait pas ou le wumpus est ni les pits
    for i in range(WORLD_SIZE):
        for j in range(WORLD_SIZE):
            if (i, j) != (0, 0) and (i, j) != (0, 1) and (i,j) != (1, 0):
                for letter in "WPBS":
                    # on ne sait rien  sur ces cases là!
                    assert test_variable(Variable(True, letter, i, j)) == 0
                    assert test_variable(Variable(False, letter, i, j)) == 0
            elif (i, j) == (0,0) :
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
    
    # pas de mechant en 0, 1 
    # print("""test_variable(Variable(True, "W", 0, 1)): """, test_variable(Variable(True, "W", 0, 1)))
    # assert test_variable(Variable(True, "W", 0, 1)) == -1
    # assert test_variable(Variable(False, "W", 0, 1)) == 1
    # assert test_variable(Variable(True, "P", 0, 1)) == -1
    # assert test_variable(Variable(False, "P", 0, 1)) == 1

    # pas de mechant en 1, 0
    # assert test_variable(Variable(True, "W", 1, 0)) == -1
    # assert test_variable(Variable(False, "W", 1, 0)) == 1
    # assert test_variable(Variable(True, "P", 1, 0)) == -1
    # assert test_variable(Variable(False, "P", 1, 0)) == 1

    # print("game rules:")
    # beauty_print(game_rules)

    # runtime tests
    ww.print_knowledge()
    ww.cautious_probe(2, 0) # trouve un wumpus
    for clause in knowledge_to_clauses():
        gs.push_variable_clause(clause)
        
    ww.print_knowledge()
    for i in range(WORLD_SIZE):
        for j in range(WORLD_SIZE):
            if (i, j) != (2, 0):
                assert test_variable(Variable(True, "W", i, j)) == -1
                assert test_variable(Variable(False, "W", i, j)) == 1
            elif (i, j) == (0,0) :
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




    print("cost : {}".format(ww.get_cost()))

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
    #mainloop()
    test_gamerules()