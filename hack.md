# CNFs projet wumpus IA02

## TODO

- [x] creer wumpus world
- [x] transformer du ww.knowledge en clauses
- [x] formalisation des clauses
- [x] Permettre de poser une question au gopherpysat
- [ ] Formaliser nos idées VU QUE XOR CA MARCHE PAS ! 
- [ ] CNFiser nos idées 
- [ ] Nourrir le gopherpysat en clauses :fork_and_knife: 
- [ ] tester nos fonctions
- [ ] mettre dans les regles qu' on sent pass les brises quand y' a un wumpus et *vis-versa*
- [ ] 
- [ ] 
- [ ] 


## Logique choix type de probe
Si gopherpysat dit : danger -> cautious probe
Sinon, probe

## Logique choix ordre de probe des cases

## Pas CNFs

### une odeur est entouree d'un unique wumpus
Si_j <=> Wi+1_j xor Wi-1_j xor Wi_j+1 xor Wi+1_j-1 
Si_j <=> Wi+1_j xor Wi-1_j xor Wi_j+1 xor Wi+1_j-1 


## Normalisation

https://www.hds.utc.fr/~lagruesy/ens/ia02/01-logique-propositionnelle/cm/#42

## CNFs

***Connaissances de départ***
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
```python
one_per_case = []
```

### Il y a exactement un wumpus sur la grille

(un wumpus sur une case implique pas de wumpus sur les autres) pour chaque case
```python
unique_wumpus = []
for i in range(WORLD_SIZE):
    for j in range(WORLD_SIZE):
        for k in range(WORLD_SIZE):
            for l in range(WORLD_SIZE):
                if i != k or j != l:
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
        clause = [ Variable(False, "B", i, j) ]
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

### pas d'odeur ni de puit donc pas de wumpus autour
- !Si_j and ! P_ij => !Wi+1_j and !Wi-1_j and !Wi_j+1 and !Wi_j-1
    - (Si_j ∨ Pi_j ∨ ¬Wi+1_j) ∧ (Si_j ∨ Pi_j ∨ ¬Wi-1_j) ∧ (Si_j ∨ Pi_j ∨ ¬Wi_j+1) ∧ (Si_j ∨ Pi_j ∨ ¬Wi_j-1)
```python
for i in range(WORLD_SIZE):
    for j in range(WORLD_SIZE):
        clause = [ Variable(True, "S", i, j), Variable(True, "P", i, j) ]
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


## Méthode

pour faire des conclusions, tu ajoutes `¬ ${la chose à tester}`et si gophersat te dit "UNSATISFIABLE" c'est que `${la chose à tester}` est vraie

[Un truc intéressant sur les XOR](https://www.msoos.org/xor-clauses/)


## En attente d'intérêt

Bi_j <=> Pi+1_j or Pi-1_j or Pi_j+1 or Pi_j-1
$\Leftrightarrow$ 

- Pi_j => Bi+1_j and Bi-1_j and Bi_j+1 and Pi_j-1

- Bi_j <= Pi+1_j or Pi-1_j or Pi_j+1 or Pi_j-1
    - Bi_j or -Pi-1_j
    - Bi_j or -Pi+1_j
    - Bi_j or -Pi_j+1
    - Bi_j or -Pi_j-1
### pas de vent ni de wumpus donc pas de puit autour
- !Bi_j and !W_ij => !Pi+1_j and !Pi-1_j and !Pi_j+1 and !Pi_j-1
    - (Bi_j ∨ Wi_j ∨ ¬Pi+1_j) ∧ (Bi_j ∨ Wi_j ∨ ¬Pi-1_j) ∧ (Bi_j ∨ Wi_j ∨ ¬Pi_j+1) ∧ (Bi_j ∨ Wi_j ∨ ¬Pi_j-1)
```python
for i in range(WORLD_SIZE):
    for j in range(WORLD_SIZE):
        clause = [ Variable(True, "B", i, j), Variable(True, "W", i, j) ]
        if i > 0:
            game_rules.append(clause + [Variable(False, "P", i-1, j)])
        if j > 0:
            game_rules.append(clause + [Variable(False, "P", i, j-1)])
        if i < WORLD_SIZE - 1:
            game_rules.append(clause + [Variable(False, "P", i+1, j)])
        if j < WORLD_SIZE - 1:
            game_rules.append(clause + [Variable(False, "P", i, j+1)])
```

