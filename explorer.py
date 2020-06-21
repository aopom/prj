#!/usr/bin/env python3

import heapq
from mapper import Mapper
import mapper

class SquareGrid:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.walls = []
    
    def in_bounds(self, id):
        (x, y) = id
        return 0 <= x < self.width and 0 <= y < self.height
         
    def passable(self, id):
        return id not in self.walls
    
    def neighbors(self, id):
        (x, y) = id
        results = [(x+1, y), (x, y-1), (x-1, y), (x, y+1)]
        if (x + y) % 2 == 0: results.reverse() # aesthetics
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

class Explorer():
    def __init__(self, n=10, seed = 42 ,verbose = False):
        self.WORLD_SIZE = n
        self.grid = SquareGrid(self.WORLD_SIZE, self.WORLD_SIZE)


    def heuristic(self, a, b):
        (x1, y1) = a
        (x2, y2) = b
        return abs(x1 - x2) + abs(y1 - y2)

    def run(self):
        # my_mapper = Mapper(n=7, seed=5, verbose=True)
        # my_mapper.main()

        
        start = (0,0)
        end = (self.WORLD_SIZE-1, self.WORLD_SIZE-1)

        path = self.a_star_search(start , end)
        print(path)
        
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
                    priority = new_cost + self.heuristic(goal, next)
                    frontier.put(next, priority)
                    came_from[next] = current
        
        # return came_from, cost_so_far
        path = []
        path.append(goal)
        while (came_from[path[-1]] != None):
            path.append(came_from[path[-1]])

        return path[::-1]




if __name__ == "__main__":
    # n = 300
    # maze = [[False for i in range(n)]for j in range(n)]
    # gr = SquareGrid(n,n)
    # start = (0,0)
    # end = (n-1, n-1)

    # path = a_star_search(gr, start , end)
    # print(path)

    e = Explorer()
    e.run()