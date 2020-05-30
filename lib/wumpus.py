from typing import Dict, Tuple, List, Union
import random

__author__ = "Sylvain Lagrue"
__copyright__ = "Copyright 2019, UTC"
__license__ = "LGPL-3.0"
__version__ = "0.10.0"
__maintainer__ = "Sylvain Lagrue"
__email__ = "sylvain.lagrue@utc.fr"
__status__ = "dev"


REWARD = {"gold": 1000, "killed_wumpus": 500, "initial": 100}
COST = {
    "initial": 0,
    "step": 1,
    "arrow": 100,
    "percept": 1,
    "probe": 10,
    "failed_probe": 1000,
    "cautious_probe": 50,
    "death": 5000,
}
RATES = {"pit_rate": 0.25, "gold_rate": 0.025}

world1 = [
    ["", "", "P", ""],
    ["", "", "", ""],
    ["W", "G", "P", ""],
    ["", "", "", "P"],
]

world2 = [
    ["", "", "", ""],
    ["P", "", "P", "W"],
    ["", "G", "P", ""],
    ["", "", "", "P"],
]


def compute_breeze(world: List[List[str]], n: int) -> List[List[str]]:
    for i in range(n):
        for j in range(n):
            if "P" in world[i][j]:
                if i + 1 < n and "B" not in world[i + 1][j]:
                    world[i + 1][j] += "B"
                if j + 1 < n and "B" not in world[i][j + 1]:
                    world[i][j + 1] += "B"
                if i - 1 >= 0 and "B" not in world[i - 1][j]:
                    world[i - 1][j] += "B"
                if j - 1 >= 0 and "B" not in world[i][j - 1]:
                    world[i][j - 1] += "B"

    return world


def compute_stench(world: List[List[str]], n: int) -> List[List[str]]:
    for i in range(n):
        for j in range(n):
            if "W" in world[i][j]:
                if i + 1 < n:
                    world[i + 1][j] += "S"
                if j + 1 < n:
                    world[i][j + 1] += "S"
                if i - 1 >= 0:
                    world[i - 1][j] += "S"
                if j - 1 >= 0:
                    world[i][j - 1] += "S"
    return world


def compute_empty(world: List[List[str]], n: int) -> List[List[str]]:
    for i in range(n):
        for j in range(n):
            if world[i][j] == "":
                world[i][j] = "."
    return world


def random_world(n: int, pit_rate: float = 0.25, gold_rate: float = 0.025):
    # empty world generation
    world = [[""] * n for i in range(n)]

    # Wumpus location generation
    posw = (random.randrange(n), random.randrange(n))
    while posw == (0, 0):
        posw = (random.randrange(n), random.randrange(n))
    x, y = posw
    world[x][y] = "W"

    # put at least one gold
    posg = (random.randrange(n), random.randrange(n))
    while posg == posw:
        posg = (random.randrange(n), random.randrange(n))
    x, y = posg
    world[x][y] = "G"

    # pits and gold location generation
    for i in range(n):
        for j in range(n):
            if (i, j) != (0, 0) and "W" not in world[i][j]:
                r = random.random()
                if r < RATES["pit_rate"] and "G" not in world[i][j]:

                    world[i][j] += "P"

                r = random.random()
                if r < RATES["gold_rate"] and "P" not in world[i][j]:
                    world[i][j] += "G"

    # generation of percepts
    world = compute_stench(world, n)
    world = compute_breeze(world, n)
    world = compute_empty(world, n)

    return world

class WumpusWorld:
    def __init__(self, n: int = 4, rand: bool = False):
        random.seed(12)
        self.__N = n
        self.__knowledge = [[False] * self.__N for i in range(self.__N)]

        if rand:
            self.__world = random_world(self.__N)
        else:
            self.__world = world1
            self.__world = compute_stench(self.__world, self.__N)
            self.__world = compute_breeze(self.__world, self.__N)
            self.__world = compute_empty(self.__world, self.__N)

        self.__position = (0, 0)
        self.__dead = False
        self.__gold_found = False

        self.__cost = COST["initial"]
        self.__reward = REWARD["initial"]

    def get_n(self):
        return self.__N

    def get_knowledge(self):
        res = [["?"] * self.__N for i in range(self.__N)]

        for i in range(self.__N):
            for j in range(self.__N):
                if self.__knowledge[i][j]:
                    res[i][j] = self.__world[i][j]

        return res

    def print_knowledge(self):
        print("Knowledge:")
        for line in self.get_knowledge():
            print(line)


    def get_position(self) -> Tuple[int, int]:
        return self.__position

    def get_percepts(self) -> Tuple[str, str, str]:
        i = self.__position[0]
        j = self.__position[1]
        self.__knowledge[i][j] = True

        return (f"[OK]", f'you feel "{self.__world[i][j]}"', self.__world[i][j])

    def get_reward(self) -> int:
        return self.__reward

    def get_cost(self) -> int:
        return self.__cost

    def probe(self, i, j) -> Tuple[str, str, int]:
        self.__cost += COST["probe"]

        if i < 0 or j < 0 or i >= self.__N or j >= self.__N:
            return (
                "[err]",
                " impossible move, you lose {COST['probe']} coins",
                -COST["probe"],
            )

        self.__position = (i, j)
        content = self.__world[i][j]

        if "W" in content or "P" in content:
            self.__cost += COST["failed_probe"]
            return (
                "[KO]",
                f"The wizard catches a glimpse of the unthinkable and turns mad: you lose {COST['failed_probe']} coins",
                -COST["failed_probe"],
            )

        a, b, c = self.get_percepts()

        return (a, c, -COST["probe"])

    def cautious_probe(self, i, j) -> Tuple[str, str, int]:
        self.__cost += COST["cautious_probe"]

        if i < 0 or j < 0 or i >= self.__N or j >= self.__N:

            return (
                "[err]",
                " impossible move, you lose {COST['cautious_probe']} coins",
                -COST["cautious_probe"],
            )

        self.__position = (i, j)
        content = self.__world[i][j]

        a, b, c = self.get_percepts()

        return (a, c, -COST["cautious_probe"])

    def go_to(self, i, j) -> Tuple[str, str, Union[int, Tuple[int, int]]]:
        if i == 0 and j == 0 and self.__gold_found:
            return "[OK]", f"you find {REWARD['gold']} coins", REWARD["gold"]

        if (
            abs(i - self.__position[0]) + abs(j - self.__position[1]) != 1
            or i < 0
            or j < 0
            or i >= self.__N
            or j >= self.__N
        ):
            return ("[err]", "impossible move...", -COST["step"])

        self.__position = (i, j)
        content = self.__world[i][j]
        if "W" in content:
            self.__dead = True
            self.__cost += COST["death"]
            return (
                "[KO]",
                f"You've been killed by the terrible Wumpus. You're dead. You lose {COST['death']} coins",
                -COST["death"],
            )
        if "P" in content:
            self.__dead = True
            self.__cost += COST["death"]
            return (
                "[KO]",
                f"You've fallen in a pit... You're dead. And you lose {COST['death']} coins",
                -COST["death"],
            )
        if "G" in content:
            self.__gold_found = True
            self.__reward += REWARD["gold"]
            return (
                "[OK]",
                f"You've found the gold and you win {REWARD['gold']} coins",
                REWARD["gold"],
            )

        return ("[OK]", f"You are now in {self.__position}", self.__position)

    def __str__(self) -> str:
        s = ""
        for i in range(self.__N):
            s += f"{i}:"
            for j in range(self.__N):
                s += f" {self.__world[i][j]} "
            s += "\n"

        return s


def test():
    ww = WumpusWorld()

    print(ww.get_percepts())
    print(ww.go_to(0, 1))
    print(ww.get_percepts())
    print(ww.get_position())

    print(ww.probe(0, 1))
    print(ww.probe(0, 2))
    print(ww.cautious_probe(0, 2))
    print(ww.go_to(0, 2))

    print(ww)

    for _ in range(10):
        print(random_world(4))


if __name__ == "__main__":
    test()
