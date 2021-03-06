#!/usr/bin/env python3

import heapq, queue
from mapper import Mapper
from typing import Dict, Tuple, Sequence, Set
from PIL import Image
from PIL import ImageDraw
import random as rnd
import numpy as np
import matplotlib.pyplot as plt

__author__ = "Joris Placette, Paco Pompeani"
__copyright__ = "Copyright 2020, UTC"
__license__ = "LGPL-3.0"
__version__ = "0.1.0"
__maintainer__ = "Joris Placette, Paco Pompeani"
__status__ = "dev"

Point = Tuple[int, int]
Segment = Tuple[Point, Point]


class SquareGrid:
    """Used by the A* algorithm"""
    def __init__(self, width, height, walls=[]):
        self.width = width
        self.height = height
        self.walls = walls

    def in_bounds(self, id):
        (x, y) = id
        return 0 <= x < self.width and 0 <= y < self.height

    def passable(self, id):
        return id not in self.walls

    def neighbors(self, id):
        (x, y) = id
        results = [(x + 1, y), (x, y - 1), (x - 1, y), (x, y + 1)]
        if (x + y) % 2 == 0:
            results.reverse()  # aesthetics
        results = filter(self.in_bounds, results)
        results = filter(self.passable, results)
        return results


class PriorityQueue:
    """Used by the A* algorithm"""

    def __init__(self):
        self.elements = []

    def empty(self):
        return len(self.elements) == 0

    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))

    def get(self):
        return heapq.heappop(self.elements)[1]


class Explorer:
    """Our main class"""

    def __init__(self, mapper=0, n=10, seed=42, verbose=False):
        if mapper:
            # If the mapper is provided, it has already done its main()
            self.my_mapper = mapper
            self.WORLD_SIZE = mapper.WORLD_SIZE
        else:
            # If the mapper is not provided, assume it's to because we only want to test the second phase
            self.my_mapper = Mapper(n=n, seed=seed, verbose=verbose)
            self.my_mapper.dumb_main()
            self.WORLD_SIZE = n

        # used to prepare the path finding
        self.reachable_golds = []

        # used to construct a SquareGrid and to make a graphical display
        # consist of a list of tuples
        self.walls = []

        # used to construct a graphical display
        print("Please check the generated image (may be in a new window).")
        self.im = Image.new("RGBA", (self.WORLD_SIZE, self.WORLD_SIZE), (255, 255, 255, 255))
        self.draw = ImageDraw.Draw(self.im)

    def closest_heuristic_astar(self, origin, destinations):
        """heuristic to choose the next gold to reach
        using A*
        """
        if destinations:
            distance = self.WORLD_SIZE * self.WORLD_SIZE + 1
            closest = None
            for destination in destinations:
                new_distance = self.a_star_distance(origin, destination)
                if new_distance < distance:
                    distance = new_distance
                    closest = destination
            return closest
        else:
            return None

    def closest_heuristic_manhattan(self, origin, destinations):
        """Unused
        heuristic to choose the next gold to reach
        using Manhattan distance
        """
        if destinations:
            distance = self.WORLD_SIZE * self.WORLD_SIZE + 1
            closest = None
            for destination in destinations:
                new_distance = self.manhattan(origin, destination)
                if new_distance < distance:
                    distance = new_distance
                    closest = destination
            return closest
        else:
            return None

    def manhattan(self, a, b):
        """Unused"""
        (x1, y1) = a
        (x2, y2) = b
        return abs(x1 - x2) + abs(y1 - y2)

    def test_astar(self):
        """Unused"""
        self.my_mapper.main()
        self.reachable_tiles_and_golds()
        self.grid = SquareGrid(self.WORLD_SIZE, self.WORLD_SIZE, self.walls)

        start = (0, 0)
        end = (self.WORLD_SIZE - 1, self.WORLD_SIZE - 1)
        path = self.a_star_search(start, end)
        print(path)

    def run(self):
        """Main run for the wumpus client's phase 2"""

        self.reachable_tiles_and_golds()
        self.grid = SquareGrid(self.WORLD_SIZE, self.WORLD_SIZE, self.walls)

        self.salesman_sort()

        total_steps = 0

        # self.draw_summary()
        nb_reachable_golds = len(self.reachable_golds)
        for i in range(nb_reachable_golds - 1):
            start = self.reachable_golds[i]
            goal = self.reachable_golds[i + 1]
            path = self.a_star_search(start, goal)
            # print(path)

            color = (int(i / nb_reachable_golds * 100), int(200), int(rnd.random() * 256), 255)
            for (i, j) in path:
                self.draw.point((i, j), fill=color)
                if self.my_mapper.ww.get_position() != (i, j):
                    self.my_mapper.ww.go_to(i, j)
                    total_steps += 1

        print("reachable golds : ", len(self.reachable_golds))
        print("total steps : ", total_steps)

    def run_phase2_only(self):
        """Main run to run the standalone phase 2"""
        self.reachable_tiles_and_golds()
        self.grid = SquareGrid(self.WORLD_SIZE, self.WORLD_SIZE, self.walls)

        self.salesman_sort()

        total_steps = 0

        nb_reachable_golds = len(self.reachable_golds)
        for i in range(nb_reachable_golds - 1):
            start = self.reachable_golds[i]
            goal = self.reachable_golds[i + 1]
            path = self.a_star_search(start, goal)
            print(path)

            color = (int(i / nb_reachable_golds * 100), int(200), int(rnd.random() * 256), 255)
            for (i, j) in path:
                self.draw.point((i, j), fill=color)
                if self.my_mapper.ww.get_position() != (i, j):
                    self.my_mapper.ww.go_to(i, j)
                    total_steps += 1

            # STEP BY STEP DRAWING
            # self.draw_summary()
            # input("Press Enter to continue...")

        self.draw_summary()
        print("reachable golds : ", len(self.reachable_golds))
        print("total steps : ", total_steps)

    def draw_summary(self):
        """graphical display"""
        for wall in self.walls:
            # print("wall", wall)
            self.draw.point(wall, fill=(50, 50, 50, 200))

        for reachable_gold in self.reachable_golds:
            self.draw.point(reachable_gold, fill=(255, 80, 0, 255))

        plt.imshow(np.asarray(self.im), origin="lower")
        plt.show()

    def salesman_sort(self):
        """Sort the golds
        Starting with (0,0)
        We choose the next gold by computing the closest to the current one
        """
        start = (0, 0)
        sorted_golds = [start]
        # print("golds:", self.reachable_golds)
        while self.reachable_golds:
            start = self.closest_heuristic_astar(start, self.reachable_golds)
            sorted_golds.append(start)
            # print("start", start)
            self.reachable_golds.remove(start)
        sorted_golds.append((0, 0))

        # Now we "uncross" all the segments formed
        cross_found = True
        while cross_found:
            cross_found = False
            for i in range(len(sorted_golds) - 2):
                for j in range(i + 2, len(sorted_golds) - 1):
                    a = sorted_golds[i]
                    b = sorted_golds[i + 1]
                    c = sorted_golds[j]
                    d = sorted_golds[j + 1]
                    if self.crossed((a, b), (c, d)):
                        # print("decrossing ", (a, b), (c, d))
                        cross_found = True
                        sorted_golds[i + 1] = c
                        sorted_golds[j] = b

        self.reachable_golds = sorted_golds

    def which_side(self, segment: Segment, point: Point):
        """ Return -1 si en dessous / gouche
            Return 0 si point sur la droite (a,b)
            Return 1 sinon (dessus/froite)
            Used by self.crossed
        """
        ((ax, ay), (bx, by)) = segment
        (cx, cy) = point

        if ax == bx:  # vertical
            if ax < cx:
                return -1
            elif ax > cx:
                return 1
            elif ax == cx:
                return 0
        else:  # not vertical
            for i in [ax, ay, bx, by, cx, cy]:
                i = float(i)

            # Droite portant le segment
            coef_dir = (by - ay) / (bx - ax)
            b_shift = ay - coef_dir * ax

            # print("coef_dir", coef_dir)
            # print("b_shift", b_shift)

            # point (mx, my) sur la droite de coord x meme que point
            mx = cx
            my = coef_dir * mx + b_shift

            if my < cy:
                return -1
            elif my > cy:
                return 1
            elif my == cy:
                return 0

        # Si ab non vertical:
        #   faut trouver un point (mi, mj) app a droite (ab) tel que mj=pointj
        #   Si mi < a pointi return -1
        #   Si mi > a pointi return 1
        #   Si mi == a pointi return 0
        # Si ab vertical:
        #   faut trouver un point (mi, mj) app a droite (ab) tel que mi=pointi
        #   Si mj < a pointj return -1
        #   Si mj > a pointj return 1
        #   Si mj == a pointj return 0

    def crossed(self, ab: Segment, cd: Segment) -> bool:
        (a, b) = ab
        (c, d) = cd

        if self.which_side(ab, c) != 0 and self.which_side(ab, c) == -self.which_side(ab, d):
            if self.which_side(cd, a) != 0 and self.which_side(cd, a) == -self.which_side(cd, b):
                return True
        return False

    def a_star_search(self, start, goal):
        """Used to go from one gold to another"""
        frontier = PriorityQueue()
        frontier.put(start, 0)
        came_from = {}
        cost_so_far = {}
        came_from[start] = None
        cost_so_far[start] = 0

        while not frontier.empty():
            current = frontier.get()

            if current == goal:
                break

            for next in self.grid.neighbors(current):
                new_cost = cost_so_far[current] + 1
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + self.manhattan(goal, next)
                    frontier.put(next, priority)
                    came_from[next] = current

        # return came_from, cost_so_far
        path = []
        path.append(goal)
        while came_from[path[-1]] != None:
            path.append(came_from[path[-1]])

        return path[::-1]

    def a_star_distance(self, a, b):
        """Used as heuristic"""
        return len(self.a_star_search(a, b))

    def reachable_tiles_and_golds(self):
        """
        First processing made by the Explorer
        Uses the BFS algorithm
        Compute an boolean 2D array of all reachable tiles
        List in the same pass all the reachable golds
        """
        knowledge = self.my_mapper.full_knowledge
        q = queue.Queue()
        q.put((0, 0))
        already_seen = [[False for i in range(self.WORLD_SIZE)] for j in range(self.WORLD_SIZE)]
        reachable_tiles = [[False for i in range(self.WORLD_SIZE)] for j in range(self.WORLD_SIZE)]
        self.reachable_golds = []
        while not q.empty():
            (current_i, current_j) = q.get()
            reachable_tiles[current_i][current_j] = True
            for (di, dj) in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                i = current_i + di
                j = current_j + dj
                if (
                    i >= 0
                    and i < self.WORLD_SIZE
                    and j >= 0
                    and j < self.WORLD_SIZE
                    and already_seen[i][j] == False
                    and not "W" in knowledge[i][j]
                    and not "P" in knowledge[i][j]
                ):
                    q.put((i, j))
                    already_seen[i][j] = True
                    if "G" in knowledge[i][j]:
                        self.reachable_golds.append((i, j))

        # self.my_mapper.beauty_print(reachable_tiles)
        self.walls = tuple((i, j) for i in range(self.WORLD_SIZE) for j in range(self.WORLD_SIZE) if not reachable_tiles[i][j])


if __name__ == "__main__":
    e = Explorer(n=30, seed=42 * 1001)
    e.run_phase2_only()
