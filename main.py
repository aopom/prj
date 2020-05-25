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
# There are no obstacles on third first cases
gs.push_pretty_clause(["¬P0,0"])
gs.push_pretty_clause(["¬P1,0"])
gs.push_pretty_clause(["¬P0,1"])
gs.push_pretty_clause(["¬W0,0"])
gs.push_pretty_clause(["¬W1,0"])
gs.push_pretty_clause(["¬W0,1"])

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
