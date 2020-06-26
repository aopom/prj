import random, threading, multiprocessing
from lib.gopherpysat import Gophersat
from lib.wumpus import WumpusWorld
import timeit


class Mapper:
    def __init__(self, ww=0, n=10, seed=23, explore_type="optimised", verbose=0):
        # DEBUG
        self.verbose = verbose
        self.interrogation_count = 0

        # self.precedent_iteration_knowledge = []
        self.precedent_iter_kno = []

        # used by Explorer
        self.full_knowledge = [["" for i in range(n)] for j in range(n)]
        self.full_knowledge_lock = threading.Lock()

        # used to add only the new knowledge to the gophersats
        self.new_kno = []
        self.new_kno_lock = threading.Lock()

        # WUMPUS WORLD
        if ww:
            self.ww = ww
            self.WORLD_SIZE = n
        else:
            self.ww = WumpusWorld(n=n, seed=seed)
            self.WORLD_SIZE = self.ww.get_n()

        # VOC
        self.voc = [f"{letter}_{i}_{j}" for i in range(self.WORLD_SIZE) for j in range(self.WORLD_SIZE) for letter in ["P", "W", "B", "S", "G"]]

        # THREADING RELATED MATERIAL

        # self.cpus = multiprocessing.cpu_count()
        self.cpus = 1
        if self.verbose:
            print(f"cpus: {self.cpus}")

        self.gopherpysats = [Gophersat(voc=self.voc) for i in range(self.cpus)]
        self.wumpus_position = (-1, -1)
        self.wumpus_found = [False for i in range(self.cpus)]

        # SAT
        self.gopherpysats = [Gophersat(voc=self.voc) for i in range(self.cpus)]

        # GR
        self.game_rules = []

        # sets
        self.not_mapped_tiles = set((i, j) for i in range(self.WORLD_SIZE) for j in range(self.WORLD_SIZE))
        self.newly_mapped_tiles = set()

    def main(self):
        """ main steps, fill rules into the SATs and start the mapping loop. 
        """
        # explo
        self.fill_rules()
        for clause in self.game_rules:
            for gs in self.gopherpysats:
                gs.push_pretty_clause(clause)

        self.mapper_loop()
        print("\ncost : {}".format(self.ww.get_cost()))
        print("interrogation_count : {}".format(self.interrogation_count))
        self.ww.print_knowledge()

    def dumb_main(self):
        """Debug alt to self.main()"""
        for i in range(self.WORLD_SIZE):
            for j in range(self.WORLD_SIZE):
                self.generic_probe(i, j, self.ww.cautious_probe, "", 0)

    def beauty_print(self, double_array):
        """Makes 2Darrays print beatifully !"""
        print("[")
        for line in double_array:
            print(line, ",", sep="")
        print("]")

    def fill_rules(self):
        """ All static rules made by our little brains are defined here"""
        min_one_wumpus = []
        for i in range(self.WORLD_SIZE):
            for j in range(self.WORLD_SIZE):
                min_one_wumpus.append(f"W_{i}_{j}")
        self.game_rules.append(min_one_wumpus)
        for i in range(self.WORLD_SIZE):
            for j in range(self.WORLD_SIZE):
                # One thing per tile
                self.game_rules.append([f"-G_{i}_{j}", f"-W_{i}_{j}"])
                self.game_rules.append([f"-G_{i}_{j}", f"-P_{i}_{j}"])
                self.game_rules.append([f"-P_{i}_{j}", f"-W_{i}_{j}"])
                # One Wumpus per game
                for k in range(self.WORLD_SIZE):
                    for l in range(self.WORLD_SIZE):
                        if i < k or j < l:
                            self.game_rules.append([f"-W_{i}_{j}", f"-W_{k}_{l}"])
                # Pits around the Breeze
                clause = [f"-B_{i}_{j}"]
                if i > 0:
                    clause.append(f"P_{i - 1}_{j}")
                if j > 0:
                    clause.append(f"P_{i}_{j - 1}")
                if i < self.WORLD_SIZE - 1:
                    clause.append(f"P_{i + 1}_{j}")
                if j < self.WORLD_SIZE - 1:
                    clause.append(f"P_{i}_{j + 1}")
                self.game_rules.append(clause)
                # Wumpus around the Strench
                clause = [f"-S_{i}_{j}"]
                if i > 0:
                    clause.append(f"W_{i - 1}_{j}")
                if j > 0:
                    clause.append(f"W_{i}_{j - 1}")
                if i < self.WORLD_SIZE - 1:
                    clause.append(f"W_{i + 1}_{j}")
                if j < self.WORLD_SIZE - 1:
                    clause.append(f"W_{i}_{j + 1}")
                self.game_rules.append(clause)
                # un puit est entouré de environ 4 breeze sauf sur les bords
                clause = [f"-P_{i}_{j}"]
                if i > 0:
                    self.game_rules.append(clause + [f"B_{i - 1}_{j}"])
                if j > 0:
                    self.game_rules.append(clause + [f"B_{i}_{j - 1}"])
                if i < self.WORLD_SIZE - 1:
                    self.game_rules.append(clause + [f"B_{i + 1}_{j}"])
                if j < self.WORLD_SIZE - 1:
                    self.game_rules.append(clause + [f"B_{i}_{j + 1}"])
                # un wumpus est entouré de environ 4 strench sauf sur les bords
                clause = [f"-W_{i}_{j}"]
                if i > 0:
                    self.game_rules.append(clause + [f"S_{i - 1}_{j}"])
                if j > 0:
                    self.game_rules.append(clause + [f"S_{i}_{j - 1}"])
                if i < self.WORLD_SIZE - 1:
                    self.game_rules.append(clause + [f"S_{i + 1}_{j}"])
                if j < self.WORLD_SIZE - 1:
                    self.game_rules.append(clause + [f"S_{i}_{j + 1}"])
                # pas d'odeur donc pas de wumpus autour
                clause = [f"S_{i}_{j}"]
                # clause = [f"S_{i}_{j}", f"P_{i}_{j}"]
                if i > 0:
                    self.game_rules.append(clause + [f"-W_{i - 1}_{j}"])
                if j > 0:
                    self.game_rules.append(clause + [f"-W_{i}_{j - 1}"])
                if i < self.WORLD_SIZE - 1:
                    self.game_rules.append(clause + [f"-W_{i + 1}_{j}"])
                if j < self.WORLD_SIZE - 1:
                    self.game_rules.append(clause + [f"-W_{i}_{j + 1}"])
                # pas de vent donc pas de puit autour
                clause = [f"B_{i}_{j}", f"W_{i}_{j}"]
                if i > 0:
                    self.game_rules.append(clause + [f"-P_{i - 1}_{j}"])
                if j > 0:
                    self.game_rules.append(clause + [f"-P_{i}_{j - 1}"])
                if i < self.WORLD_SIZE - 1:
                    self.game_rules.append(clause + [f"-P_{i + 1}_{j}"])
                if j < self.WORLD_SIZE - 1:
                    self.game_rules.append(clause + [f"-P_{i}_{j + 1}"])
        return self.game_rules

    def interrogate(self, gopherpysat, clause):
        """Return False if clause is not compatible with gopherpysat's clauses.
        """
        self.interrogation_count += 1
        gopherpysat.push_pretty_clause(clause)
        output = gopherpysat.solve()
        gopherpysat.pop_clause()
        return output

    def guess_if_safe(self, gopherpysat, i, j, wumpus_found_index):
        """Returns -1 if danger, 0 if dont know and 1 if safe
        """
        # print(f"self.wumpus_position \t{self.wumpus_position}")
        if not self.wumpus_found[wumpus_found_index]:
            # Are we sure there is a wumpus ?
            there_is_a_wumpus = 0 == self.interrogate(gopherpysat, [f"-W_{i}_{j}"])
            if there_is_a_wumpus:
                self.wumpus_position = (i, j)
                self.wumpus_found[wumpus_found_index] = True
                return -1
            # Are we sure there is a pit ?
            there_is_a_pit = 0 == self.interrogate(gopherpysat, [f"-P_{i}_{j}"])
            if there_is_a_pit:
                return -1
            # Are we sure there is no wumpus ?
            there_is_no_wumpus = 0 == self.interrogate(gopherpysat, [f"W_{i}_{j}"])
            if not there_is_no_wumpus:
                return 0
            # Are we sure there is a pit ?
            there_is_no_pit = 0 == self.interrogate(gopherpysat, [f"P_{i}_{j}"])
            return there_is_no_pit
        elif self.wumpus_position == (i, j):
            return -1
        else:
            there_is_no_pit = 0 == self.interrogate(gopherpysat, [f"P_{i}_{j}"])
            if there_is_no_pit:
                return 1
            there_is_a_pit = 0 == self.interrogate(gopherpysat, [f"-P_{i}_{j}"])
            return -there_is_a_pit

    def neighbours(self, i, j):
        """Give it a tile, get it's neighbours"""
        neighbours_tiles = set()
        if i > 0:
            neighbours_tiles.add((i - 1, j))
        if j > 0:
            neighbours_tiles.add((i, j - 1))
        if i < self.WORLD_SIZE:
            neighbours_tiles.add((i + 1, j))
        if j < self.WORLD_SIZE:
            neighbours_tiles.add((i, j + 1))
        return neighbours_tiles

    def generic_probe(self, i, j, probe_function, probe_name, wumpus_found_index):
        """The type of probe is given by the probe function argument
           This function probes and updates all the state variables according to the answer
        """
        status, percepts, cost = probe_function(i, j)

        # print(f"{i} {j} : {probe_name}, status: {status}, percepts: {percepts}")
        print(probe_name, end="")

        self.action = True

        # Sets management
        self.newly_mapped_tiles.add((i, j))
        self.not_mapped_tiles.discard((i, j))

        with self.full_knowledge_lock:
            self.full_knowledge[i][j] = percepts

        for letter in "PWBSG":
            if letter in percepts:
                with self.new_kno_lock:
                    self.new_kno.append([f"{letter}_{i}_{j}"])
            else:
                with self.new_kno_lock:
                    self.new_kno.append([f"-{letter}_{i}_{j}"])

        if not self.wumpus_found[wumpus_found_index]:
            if "W" in percepts:
                self.wumpus_position = (i, j)
                self.wumpus_found[wumpus_found_index] = True

    def thread_guess_and_probe(self, gopherpysat, tiles, start):
        """ The function executed by the thread workers.
            Try to determine for each tile given, it it's safe, unsafe or if we lack knowledge.
            If it's safe, we probe the tile, if it's not, we cautious_probe the tile.
            Work on all (start + self.cpus * n) tuples of the tiles array.
        """
        for clause in self.precedent_iter_kno:
            gopherpysat.push_pretty_clause(clause)

        index = start
        while index < len(tiles):
            (i, j) = tiles[index]
            index += self.cpus
            safe = self.guess_if_safe(gopherpysat, i, j, start)
            if safe == 1:
                self.generic_probe(i, j, self.ww.probe, ".", start)
            elif safe == -1:
                self.generic_probe(i, j, self.ww.cautious_probe, "c", start)

    def mapper_loop(self):
        """ main loop pour explorer le plateau de jeu
        """
        # première action
        self.generic_probe(0, 0, self.ww.probe, ".", 0)
        to_map_next = set()

        # While some tiles are unknown
        while self.not_mapped_tiles:

            self.precedent_iter_kno = self.new_kno
            self.new_kno = []

            to_map_next.clear()

            # To save (alot) of time, we only re-check SAT's results
            # for tiles close to the one we learnt something about last iteration
            for (i, j) in self.newly_mapped_tiles:
                to_map_next |= self.neighbours(i, j) & self.not_mapped_tiles

            # The one we will soon SAT-check
            tile_playlist = list(to_map_next)

            self.newly_mapped_tiles.clear()

            # launch threads
            threads = []
            self.action = False
            for i in range(self.cpus):
                thread = threading.Thread(target=self.thread_guess_and_probe, args=(self.gopherpysats[i], tile_playlist, i),)
                threads.append(thread)
                thread.start()
            # wait for threads
            for thread in threads:
                thread.join()

            # if no tile was probed
            if not self.action and self.not_mapped_tiles:
                (i, j) = next(iter(self.not_mapped_tiles))
                self.generic_probe(i, j, self.ww.cautious_probe, "C", 0)

            if True in self.wumpus_found:
                self.wumpus_found = [True for i in range(self.cpus)]


if __name__ == "__main__":
    mapper = Mapper(n=10, seed=50, verbose=True)
    mapper.main()
