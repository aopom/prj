import random, threading, multiprocessing
from lib.gopherpysat import Gophersat
from lib.wumpus import WumpusWorld
import timeit


class Mapper:
    def __init__(self, n=10, seed=23, explore_type="optimised", verbose=0):
        # DEBUG
        self.verbose = verbose
        self.interrogation_count = 0

        # self.precedent_iteration_knowledge = []
        self.precedent_iter_kno = []

        self.new_kno = []
        self.new_kno_lock = threading.Lock()

        self.wumpus_position = (-1, -1)
        self.wumpus_found = False

        # WUMPUS WORLD
        self.ww = WumpusWorld(n=n, seed=seed)
        print(self.ww)
        if self.verbose:
            print("cost : {}".format(self.ww.get_cost()))

        self.WORLD_SIZE = self.ww.get_n()

        # VOC
        self.voc = [
            f"{letter}_{i}_{j}"
            for i in range(self.WORLD_SIZE)
            for j in range(self.WORLD_SIZE)
            for letter in ["P", "W", "B", "S", "G"]
        ]

        # THREADING RELATED MATERIAL
        self.cpus = multiprocessing.cpu_count()
        if self.verbose:
            print(f"cpus: {self.cpus}")
        self.gopherpysats = [Gophersat(voc=self.voc) for i in range(self.cpus)]

        # SAT
        self.gopherpysats = [Gophersat(voc=self.voc) for i in range(self.cpus)]

        # GR
        self.game_rules = []

        # sets
        self.mapped_tiles = set()
        self.not_mapped_tiles = set(
            (i, j) for i in range(self.WORLD_SIZE) for j in range(self.WORLD_SIZE)
        )
        self.newly_mapped_tiles = set()

        if verbose:
            print(f"game_rules {self.game_rules}")

    def main(self):
        # explo
        self.fill_rules()
        for clause in self.game_rules:
            for gs in self.gopherpysats:
                gs.push_pretty_clause(clause)

        self.mapper_loop()
        print("cost : {}".format(self.ww.get_cost()))
        print("interrogation_count : {}".format(self.interrogation_count))
        self.ww.print_knowledge()

    def beauty_print(self, double_array):
        print("[")
        for line in double_array:
            print(line, ",", sep="")
        print("]")

    def knowledge_to_clauses(self):
        clauses = []
        knowledge = self.ww.get_knowledge()
        for i in range(self.WORLD_SIZE):
            for j in range(self.WORLD_SIZE):
                if knowledge[i][j] != "?":
                    for letter in "PWBSG":
                        if letter in knowledge[i][j]:
                            clauses.append([f"{letter}_{i}_{j}"])
                        else:
                            clauses.append([f"-{letter}_{i}_{j}"])
        return clauses

    def fill_rules(self):
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

    def guess_if_safe(self, gopherpysat, i, j):
        """Returns -1 if danger, 0 if dont know and 1 if safe
        """
        # print(f"self.wumpus_position \t{self.wumpus_position}")
        if not self.wumpus_found:
            # Are we sure there is a wumpus ?
            there_is_a_wumpus = 0 == self.interrogate(gopherpysat, [f"-W_{i}_{j}"])
            if there_is_a_wumpus:
                print(
                    "############################ DéDUCTED THE WUMPUS (guess_if_safe)"
                )
                self.wumpus_position = (i, j)
                self.wumpus_found = True
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
            there_is_a_pit = 0 == self.interrogate(gopherpysat, [f"-P_{i}_{j}"])
            return there_is_no_pit - there_is_a_pit

    def neighbours(self, i, j):
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

    def adjacent_to_known_tile(self, knowledge, i, j):
        """ faut pas s' en servir """
        return (
            (i > 0 and knowledge[i - 1][j] != "?")
            or (j > 0 and knowledge[i][j - 1] != "?")
            or (i < self.WORLD_SIZE - 1 and knowledge[i + 1][j] != "?")
            or (j < self.WORLD_SIZE - 1 and knowledge[i][j + 1] != "?")
        )

    def after_probe(self, i, j):
        self.action = True

        # sets mangement
        self.mapped_tiles.add((i, j))
        self.newly_mapped_tiles.add((i, j))
        self.not_mapped_tiles.discard((i, j))

        a, b, percepts = self.ww.get_percepts()
        for letter in "PWBSG":
            if letter in percepts:
                with self.new_kno_lock:
                    self.new_kno.append([f"{letter}_{i}_{j}"])
            else:
                with self.new_kno_lock:
                    self.new_kno.append([f"-{letter}_{i}_{j}"])

        if not self.wumpus_found:
            if "W" in percepts:
                self.wumpus_position = (i, j)
                self.wumpus_found = True
                print("############################ found the wumpus (after probe)")

    def probe(self, i, j):
        self.ww.probe(i, j)
        self.after_probe(i, j)
        print(f"ninja probe {i} {j}")

    def sure_cautious_probe(self, i, j):
        self.ww.cautious_probe(i, j)
        self.after_probe(i, j)
        print(f"sure cautious probe {i} {j}")

    def cautious_probe(self, i, j):
        self.ww.cautious_probe(i, j)
        self.after_probe(i, j)
        print("cautious probe {} {}".format(i, j))

    def thread_guess_and_probe(self, gopherpysat, tiles, start):
        # print("Push...",start)
        for clause in self.precedent_iter_kno:
            gopherpysat.push_pretty_clause(clause)
        # print("\t... clauses", start)

        index = start
        while index < len(tiles):
            (i, j) = tiles[index]
            index += self.cpus
            safe = self.guess_if_safe(gopherpysat, i, j)
            if safe == 1:
                self.probe(i, j)
            elif safe == -1:
                self.sure_cautious_probe(i, j)

    def mapper_loop(self):
        """ main loop pour explorer tout 
        """
        # première action
        self.probe(0, 0)
        # on a 0,0 dans mapped_tiles
        to_map_next = set()

        # While some tiles are unknown
        while self.not_mapped_tiles:

            self.precedent_iter_kno = self.new_kno
            self.new_kno = []

            to_map_next.clear()
            for (i, j) in self.newly_mapped_tiles:
                to_map_next |= self.neighbours(i, j) & self.not_mapped_tiles

            tile_playlist = list(to_map_next)

            self.newly_mapped_tiles.clear()

            # launch threads
            threads = []
            self.action = False
            for i in range(self.cpus):
                thread = threading.Thread(
                    target=self.thread_guess_and_probe,
                    args=(self.gopherpysats[i], tile_playlist, i),
                )
                threads.append(thread)
                thread.start()
            # wait for threads
            for thread in threads:
                thread.join()
            # if no tile was probed
            if not self.action and self.not_mapped_tiles:
                (i, j) = next(iter(self.not_mapped_tiles))
                self.cautious_probe(i, j)


if __name__ == "__main__":
    e = Mapper(n=20, seed=50, verbose=True)
    e.main()
