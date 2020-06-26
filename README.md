# Projet wumpus IA02

Projet du Wumpus, Paco Pompeani et Joris Placette, 2020

[Dépot Git](https://gitlab.utc.fr/ppompean/prj-ai27)

## execution 

### Phase 1 seulement

`python3 mapper.py`

### Phase 2 seulement

`python3 explorer.py`

### Client complet

Renseigner au préalable l'ID et l'adresse du serveur.

`python3 client.py`

## Fonctionnement

### Phase 1

Le code de la phase 1 devait tirer profit du threading dans python (on sait, ce n'est pas un **Vrai** threading). Seulement, au moment d'adapter notre code à l'interface client serveur, des erreurs en lien avec le threading sont survenues. De fait, nous avons laissé le code en lien avec le threading mais en forcant la valeur à un seul cpu/thread.

L'essentiel du travail est réalisé dans la `Mapper.mapper_loop()`, appelée par `Mapper.main()` appelée par `Mapper.__init__()`.

### 




## Phase 1

### mainloop explore intelligent
- Probe en 0,0
- tant que tout n'a pas ete exploré
    - Prioriser les case à explorer en premier par ce qu'elles sont safe
    - si cases_safe non vide
        - `probe()` une case safe
    - sinon
        - cautious_probe() une case au pif (idéalement loin de truc deja exploré)

```python

unknown_tiles = [(i, j) for i in range(len(knowledge)) for j in range(len(knowledge)) if knowledge[i][j]=="?"]

safe_tiles = [(i, j) for (i, j) in unknown_tiles if safe_tile(i, j)]

unsafe_tiles = [(i, j) for (i, j) in unknown_tiles if not (i, j) in safe_tiles]

```

## Logique choix type de probe
Si gopherpysat dit : danger -> cautious probe
Si gopherpysat dit : pas danger -> probe

## Pas CNFs

### une odeur est entouree d'un unique wumpus
Si_j <=> Wi+1_j xor Wi-1_j xor Wi_j+1 xor Wi+1_j-1 
Si_j <=> Wi+1_j xor Wi-1_j xor Wi_j+1 xor Wi+1_j-1 


## Normalisation

https://www.hds.utc.fr/~lagruesy/ens/ia02/01-logique-propositionnelle/cm/#42

## CNFs

***Connaissances de départ*** acquises par le premier probe en (0 0)
-W0_0
-P0_0
-S0_0 
-B0_0

```python
# Origin is emply
origin_empty = [[Variable(False, "W", 0, 0)], [Variable(False, "P", 0, 0)], [Variable(False, "S", 0, 0)], [Variable(False, "B", 0, 0)] ]
```

### une case n'est occupée au plus que par un Wumpus ou un gold ou un pit.
wumpus => not gold and not pit
gold => not wumpus and not pit
pit => not wumpus and not gold

(¬g ∨ ¬w) ∧ (¬p ∨ ¬w)
(¬g ∨ ¬p) ∧ (¬p ∨ ¬w)
(¬g ∨ ¬p) ∧ (¬g ∨ ¬w)

simplification :
(¬g ∨ ¬w) ∧ (¬p ∨ ¬w) ∧ (¬g ∨ ¬p)

### Il y a exactement un wumpus sur la grille

(un wumpus sur une case implique pas de wumpus sur les autres) pour chaque case
```python
unique_wumpus = []
for i in range(WORLD_SIZE):
    for j in range(WORLD_SIZE):
        for k in range(WORLD_SIZE):
            for l in range(WORLD_SIZE):
                # if i != k or j != l:
                if i < k or j < l:
                    unique_wumpus.append([Variable(False, "W", i, j), Variable(False, "W", k, l)])
```

### une brise est entourée d'au moins un puit
- Bi_j => Pi+1_j or Pi-1_j or Pi_j+1 or Pi_j-1
    - -Bi_j or Pi+1_j or Pi-1_j or Pi_j+1 or Pi_j-1
```python
for i in range(WORLD_SIZE):
    for j in range(WORLD_SIZE):
        clause = [ Variable(False, "B", i, j) ]
        if i > 0:
            clause.append(Variable(True, "P", i-1, j))
        if j > 0:
            clause.append(Variable(True, "P", i, j-1))
        if i < WORLD_SIZE - 1:
            clause.append(Variable(True, "P", i+1, j))
        if j < WORLD_SIZE - 1:
            clause.append(Variable(True, "P", i, j+1))
        pit_near_breeze.append(clause)
```

### une odeur est entourée d'un unique wumpus
- Si_j => Wi+1_j or Wi-1_j or Wi_j+1 or Wi_j-1
    - -Si_j or Wi+1_j or Wi-1_j or Wi_j+1 or Wi_j-1
```python
for i in range(WORLD_SIZE):
    for j in range(WORLD_SIZE):
        clause = [ Variable(False, "S", i, j) ]
        if i > 0:
            clause.append(Variable(True, "W", i-1, j))
        if j > 0:
            clause.append(Variable(True, "W", i, j-1))
        if i < WORLD_SIZE - 1:
            clause.append(Variable(True, "W", i+1, j))
        if j < WORLD_SIZE - 1:
            clause.append(Variable(True, "W", i, j+1))
        pit_near_breeze.append(clause)
```

### pas d'odeur donc pas de wumpus autour
- !Si_j => !Wi+1_j and !Wi-1_j and !Wi_j+1 and !Wi_j-1
    - (Si_j ∨ ¬Wi+1_j) ∧ (Si_j ∨ ¬Wi-1_j) ∧ (Si_j ∨ ¬Wi_j+1) ∧ (Si_j ∨ ¬Wi_j-1)
```python
for i in range(WORLD_SIZE):
    for j in range(WORLD_SIZE):
        clause = [ Variable(True, "S", i, j) ]
        if i > 0:
            game_rules.append(clause + [Variable(False, "W", i-1, j)])
        if j > 0:
            game_rules.append(clause + [Variable(False, "W", i, j-1)])
        if i < WORLD_SIZE - 1:
            game_rules.append(clause + [Variable(False, "W", i+1, j)])
        if j < WORLD_SIZE - 1:
            game_rules.append(clause + [Variable(False, "W", i, j+1)])
```

### un puit est entouré de environ 4 breeze sauf sur les bords
P => B and C and D and E

(B OR (NOT P)) AND (C OR (NOT P)) AND (D OR (NOT P)) AND (E OR (NOT P))

```python
for i in range(WORLD_SIZE):
    for j in range(WORLD_SIZE):
        clause = [ Variable(False, "P", i, j)]
        if i > 0:
            game_rules.append(clause + [Variable(True, "B", i-1, j)])
        if j > 0:
            game_rules.append(clause + [Variable(True, "B", i, j-1)])
        if i < WORLD_SIZE - 1:
            game_rules.append(clause + [Variable(True, "B", i+1, j)])
        if j < WORLD_SIZE - 1:
            game_rules.append(clause + [Variable(True, "B", i, j+1)])

```

### un wumpus est entouré de environ 4 strench sauf sur les bords
W => S and T and U and V

(S OR (NOT W)) AND (T OR (NOT W)) AND (U OR (NOT W)) AND (V OR (NOT W))

```python
for i in range(WORLD_SIZE):
    for j in range(WORLD_SIZE):
        clause = [ Variable(False, "W", i, j)]
        if i > 0:
            game_rules.append(clause + [Variable(True, "S", i-1, j)])
        if j > 0:
            game_rules.append(clause + [Variable(True, "S", i, j-1)])
        if i < WORLD_SIZE - 1:
            game_rules.append(clause + [Variable(True, "S", i+1, j)])
        if j < WORLD_SIZE - 1:
            game_rules.append(clause + [Variable(True, "S", i, j+1)])
```


## Méthode

pour faire des conclusions, tu ajoutes `¬ ${la chose à tester}`et si gophersat te dit "UNSATISFIABLE" c'est que `${la chose à tester}` est vraie

[Un truc intéressant sur les XOR](https://www.msoos.org/xor-clauses/)

