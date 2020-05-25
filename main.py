from lib.gopherpysat import Gophersat
from lib.wumpus import WumpusWorld

# Create world
ww = WumpusWorld()
# World width
N = ww.get_n()
# Generate Vocabulary
# Pit, Wumpus, Breeze, Stench, Gold
voc = [
    f"{letter}{i}_{j}"
    for i in range(N)
    for j in range(N)
    for letter in ["P", "W", "B", "S", "G"]
]
# Create gophersat object
gs = Gophersat(voc=voc)
clauses = [
    # There are no obstacles on third first cases
    ["¬P0_0"],
    ["¬P1_0"],
    ["¬P0_1"],
    ["¬W0_0"],
    ["¬W1_0"],
    ["¬W0_1"],
]
# Neither a pit, the wumpus nor gold can be in se same case
"""
voici ce que je veux faire, faut en faire une cnf :
(!P et !W et !G) ou (P et !W et !G) ou (!P et W et !G) ou (!P et !W et G)
for i in range(N):
    for j in range(N):
        clauses.extend([[f"¬P{i}_{j}",]])
"""


# Finally add clauses
for i in range(len(clauses)):
    gs.push_pretty_clause(clauses[i])

# Solve...
print(gs.dimacs())
print(gs.solve())
print(gs.get_pretty_model())
print(gs.get_model())

# Exemples
print(ww.get_knowledge())
print(ww.get_percepts())
print(ww.probe(0, 1))
print(ww)
