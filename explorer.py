#!/usr/bin/env python3

import heapq, queue
from mapper import Mapper


class SquareGrid:
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
    def __init__(self):
        self.elements = []

    def empty(self):
        return len(self.elements) == 0

    def put(self, item, priority):
        heapq.heappush(self.elements, (priority, item))

    def get(self):
        return heapq.heappop(self.elements)[1]


class Explorer:
    def __init__(self, n=10, seed=42, verbose=False):
        self.WORLD_SIZE = n
        self.seed = seed
        self.my_mapper = Mapper(n=self.WORLD_SIZE, seed=self.seed, verbose=True)
        self.reachable_golds = []
        self.walls = []
        # self.grid

    def closest_heuristic(self, origin, destinations):
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

    # def closest_spiral(self, origin):
    #     for i in range(self.WORLD_SIZE):
    #         if

    def manhattan(self, a, b):
        (x1, y1) = a
        (x2, y2) = b
        return abs(x1 - x2) + abs(y1 - y2)

    def test_astar(self):
        self.my_mapper.main()

        self.reachable_tiles_and_golds()
        self.grid = SquareGrid(self.WORLD_SIZE, self.WORLD_SIZE, self.walls)

        start = (0, 0)
        end = (self.WORLD_SIZE - 1, self.WORLD_SIZE - 1)

        path = self.a_star_search(start, end)
        print(path)

    def run(self):
        self.my_mapper.main()

        self.reachable_tiles_and_golds()
        self.grid = SquareGrid(self.WORLD_SIZE, self.WORLD_SIZE, self.walls)

        self.salesman_sort()

        for i in range(len(self.reachable_golds) - 1):
            start = self.reachable_golds[i]
            goal = self.reachable_golds[i + 1]
            path = self.a_star_search(start, goal)
            print(path)
            for (i, j) in path:
                if self.my_mapper.ww.get_position() != (i, j):
                    self.my_mapper.ww.go_to(i, j)

    def salesman_sort(self):
        # first loop
        start = (0, 0)
        sorted_golds = [start]
        print("golds:", self.reachable_golds)
        while self.reachable_golds:
            start = self.closest_heuristic(start, self.reachable_golds)
            sorted_golds.append(start)
            print("start", start)
            self.reachable_golds.remove(start)
        sorted_golds.append((0, 0))
        self.reachable_golds = sorted_golds
        print(self.reachable_golds)
        # decrossin'

    def crossed(self, tuple1, tuple2):
        pass

    def a_star_search(self, start, goal):
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

    def reachable_tiles_and_golds(self):
        knowledge = self.my_mapper.ww.get_knowledge()
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

        self.my_mapper.beauty_print(reachable_tiles)
        self.walls = tuple((i, j) for i in range(self.WORLD_SIZE) for j in range(self.WORLD_SIZE) if not reachable_tiles[i][j])


if __name__ == "__main__":
    # n = 300
    # maze = [[False for i in range(n)]for j in range(n)]
    # gr = SquareGrid(n,n)
    # start = (0,0)
    # end = (n-1, n-1)

    # path = a_star_search(gr, start , end)
    # print(path)

    e = Explorer(n=10, seed=42 * 1001)
    e.run()
