from lib.wumpus_client import WumpusWorldRemote

from requests.exceptions import HTTPError

# SWAG
from mapper import Mapper
from explorer import Explorer


__author__ = "Joris Placette & Paco Pompeani"
__copyright__ = "Copyright 2020, UTC"
__license__ = "LGPL-3.0"
__version__ = "0.1.0"
__maintainer__ = "Joris Placette & Paco Pompeani"
__status__ = "dev"


def client():
    # Connexion au serveur
    server = "http://82.65.60.26:8080"
    groupe_id = "Binôme de projet 40"  # votre vrai numéro de groupe
    names = "Joris & Paco"  # vos prénoms et noms

    try:
        wwr = WumpusWorldRemote(server, groupe_id, names)
    except HTTPError as e:
        print(e)
        print("Try to close the server (Ctrl-C in terminal) and restart it")
        return

    # Récupération du premier labyrinthe
    status, msg, size = wwr.next_maze()
    maze = 1
    while status == "[OK]":
        print(f"MAZE n°{maze}")
        print(msg)
        print("taille: ", size)

        ###################
        ##### PHASE 1 #####
        ###################

        mapper = Mapper(n=size, ww=wwr, verbose=True)

        # mapper.dumb_main()
        mapper.main()

        status, msg = wwr.end_map()
        print(status, msg)

        ###################
        ##### PHASE 2 #####
        ###################

        explorer = Explorer(mapper, verbose=True)

        explorer.run()

        res = wwr.maze_completed()

        print(res)

        # Récupération du labyrinthe suivant
        maze += 1
        status, msg, size = wwr.next_maze()
        print(status, msg, size)


if __name__ == "__main__":
    client()
