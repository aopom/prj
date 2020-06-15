from pprint import pprint
import requests
import sys

__author__ = "Sylvain Lagrue"
__copyright__ = "Copyright 2020, UTC"
__license__ = "LGPL-3.0"
__version__ = "0.5.0"
__maintainer__ = "Sylvain Lagrue"
__email__ = "sylvain.lagrue@utc.fr"
__status__ = "dev"


def perror(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


class WumpusWorldRemote:
    def __init__(self, server: str, group: str, members: str):
        self._basename = server + "/wumpus"
        self._members = members
        self._id = group
        self._token = "No Defined..."
        self.register()
        self.phase = 0
        self.dead = False

    def _request(self, cmd: str, position={"x": 0, "y": 0}):
        data = {
            "id": self._id,
            "members": self._members,
            "token": self._token,
            "position": position,
        }

        r = requests.post(f"{self._basename}/{cmd}", json=data)

        if r.status_code != requests.codes.ok:
            r.raise_for_status()

        # TODO: gestion des erreurs json
        answer = r.json()

        # print("REQUEST:", cmd)
        # pprint(data)
        # pprint(answer)

        return answer

    def register(self):
        r = self._request("register")

        self._token = r["token"]

    def get_status(self):
        data = self._request("status")

        return data["phase"], (data["position"]["x"], data["position"]["y"])

    def next_maze(self):
        assert self.phase == 0, "next_maze called but you're not in Phase 0..."

        try:
            r = self._request("next-maze")
        except requests.exceptions.ConnectionError:
            return ("[Err]", None, None)

        # FIXME: plutôt faire un statu dans le retour
        # if r["status"] == "[Err]":
        #     return None

        msg = r["msg"]
        size = r["grid_size"]
        self.phase = 1
        self.dead = False

        return "[OK]", msg, size

    def end_map(self):
        assert self.phase == 1, "end_map called but you're not in Phase 1..."

        try:
            data = self._request("end-map")
        except requests.exceptions.HTTPError:
            assert False, "end_map fatal error: the map was not totally discovered!"

        self.phase = 2

        msg = data["msg"]
        status = "[OK]"

        return status, msg

    def cautious_probe(self, i: int, j: int):
        assert self.phase == 1, "cautious_probe called but you're not in Phase 1..."

        data = self._request("cautious-probe", {"x": i, "y": j})

        status = data["status"]
        percepts = data["msg"][len("you feel ") :]
        cost = -data["action_cost"]

        return status, percepts, cost

    def probe(self, i: int, j: int):
        assert self.phase == 1, "probe called but you're not in Phase 1..."

        data = self._request("probe", {"x": i, "y": j})

        status = data["status"]

        if status == "[OK]":
            percepts = data["msg"][len("you feel ") :]
        else:
            percepts = data["msg"]

        cost = -data["action_cost"]

        return status, percepts, cost

    def know_wumpus(self, i: int, j: int):
        assert self.phase == 1, "know_wumpus called but you're not in Phase 1..."

        try:
            data = self._request("know-wumpus", {"x": i, "y": j})
        except requests.exceptions.HTTPError as err:
            status = [err]
            msg = f"Error for your inference: Wumpus is not in ({i},{j}), you lose 5000..."
            return status, msg

        msg = data["msg"]
        status = ["OK"]

        return status, msg, 0

    def know_pit(self, i: int, j: int):
        assert self.phase == 1, "know_pit called but you're not in Phase 1..."

        try:
            data = self._request("know-pit", {"x": i, "y": j})
        except requests.exceptions.HTTPError as err:
            pprint(
                f"Erreur fatale dans votre déduction du Pit ({i},{j}), le jeu est fini..."
            )
            sys.exit(-1)

        msg = data["msg"]
        status = ["OK"]

        return status, msg, 0

    def get_position(self):
        assert (
            self.phase == 2
        ), "get_position called but you're not in Phase 2 (are you dead?)..."

        data = self._request("get-position")

        return data["position"]["x"], data["position"]["y"]

    def go_to(self, i: int, j: int):
        assert (
            self.phase == 2
        ), "go_to called but you're not in Phase 2 (are you dead?)..."
        assert not self.dead, "go_to called but you're dead!"

        data = self._request("go-to", position={"x": i, "y": j})

        status = data["status"]
        msg = data["msg"]

        if status == "[Err]":
            cost = -data["action_cost"]

        elif status == "[KO]":
            self.dead = True
            self.phase = 0
            cost = -data["action_cost"]
        elif status == "[OK]":
            cost = 0
            if "action_cost" in data:
                cost -= data["action_cost"]
            if "action_reward" in data:
                cost += data["action_reward"]
        else:
            assert False, "Unexpected data sent to go-to"

        return (status, msg, cost)

    def maze_completed(self):
        assert self.phase == 2, "maze_completed called but you're not in Phase 2..."

        if not self.dead:
            assert self.get_position() == (
                0,
                0,
            ), "Fatal error: you must be in (0,0) or dead to call maze_completed"

        self.phase = 0

        data = self._request("maze-completed")

        status = "[OK]"
        msg = data["msg"]

        return status, msg, NotImplemented


# TODO: gérer le GOTOPIT comme une mort (direct phase 0)
