import numpy as np
import time as t
import random


def load_file(file):
    instance = []
    x = 0  # Initialisation du nombre de sommets
    with open(file, 'r') as f:
        for line in f:  # Parcourt le fichier ligne par ligne
            line = line.strip()  # Supprime les espaces en début et fin de ligne
            if line.startswith('p'):  # Vérifie que la ligne commence par 'p'
                parts = line.split()
                try:
                    x = int(parts[2])  # Lecture du nombre de sommets (souvent à la 3e position)
                except (IndexError, ValueError):
                    print("Erreur de format pour le nombre de sommets.")
                    return None
            elif line and not line.startswith('c'): 
                instance.append(line.strip())

    matrix = np.zeros((x, x), dtype=int)
    for line in instance:
        parts = line.split()
        try:
            elem = int(parts[1]) - 1 
            elem2 = int(parts[2]) - 1
            matrix[elem][elem2] = 1
            matrix[elem2][elem] = 1
        except (IndexError, ValueError):
            print("Erreur de format pour une arête.")
            return None
    return matrix



def solution_simple_vector(sol, indice, color):
    sol[indice] = color
    return sol

def solution_vectors(sol, color):
    sol2=[]
    tmp=[]
    for i in range(1,color+1): # On parcourt les couleurs
        for j in range(len(sol)): # On parcourt les sommets
            if sol[j]==i:  # Si le sommet est de la couleur i, on l'ajoute à la liste (vecteur)
                tmp.append(j+1)
        sol2.append(tmp) # On ajoute la liste des sommets de la couleur i à la liste de solution (vecteur de vecteurs)
        tmp=[]
    return sol2

def objectif(solution):
    score = 0 
    indice = 1 
    for element in solution: # On parcourt les couleurs
        score += len(element) * indice # On ajoute le nombre de sommets de la couleur i * i
        indice += 1 
    return score

def algo_glouton_aleatoire(matrix):
    n = len(matrix)
    sol = [0] * n  # Vecteur solution initialisé à 0
    for _ in range(n):
        sommet = random.choice([i for i in range(n) if sol[i] == 0])  # Sommet non colorié
        color = 1
        while any(matrix[sommet][j] == 1 and sol[j] == color for j in range(n)):  # Vérifie conflit de couleur
            color += 1
        sol[sommet] = color  # Assigne la première couleur disponible
    return sol



def algo_glouton_1(matrix, candidats, sol):
    for i in range(len(matrix)):
        a_colorier = find_new_sommet(matrix, candidats, sol)
        color = find_color(matrix, sol, a_colorier)
        sol = solution_simple_vector(sol, a_colorier, color)
        candidats[a_colorier] = False
    return sol

def find_new_sommet(matrix, candidats, sol):
    dsat_max = 0
    result = []  
    max_alpha = 0  # Nombre de sommets non coloriés parmi les voisins
    for i in range(len(candidats)):
        if candidats[i]:  # Si le sommet n'est pas colorié
            unique_colors = []  
            alpha_size = 0 
            for voisin in range(len(matrix)):  # On parcourt les voisins
                if matrix[i][voisin] == 1 and sol[voisin] != 0:  # Si le voisin est colorié
                    if sol[voisin] not in unique_colors:  # Si la couleur n'est pas déjà dans la liste
                        unique_colors.append(sol[voisin])   
                if matrix[i][voisin] == 1 and sol[voisin] == 0:  # Si le voisin n'est pas colorié
                    alpha_size += 1 
            if len(unique_colors) > dsat_max:  # Si le nombre de couleurs du voisin est supérieur au max
                dsat_max = len(unique_colors) 
                max_alpha = alpha_size 
                result = [i]
            elif len(unique_colors) == dsat_max and alpha_size > max_alpha:  # Si le nombre de couleurs du voisin est égal au max
                max_alpha = alpha_size 
                result = [i] 
            elif len(unique_colors) == dsat_max and alpha_size == max_alpha:  # Si le nombre de couleurs du voisin est égal au max
                result.append(i) 
    if result: # si après tout ça notre liste n'est pas vide => égalité de dsat_max et max_alpha
        return np.random.choice(result)  
    return -1 # Si la liste est vide => tous les sommets sont coloriés

def find_color(matrix, sol, a_colorier):
    color = 1
    while True:
        conflit = False
        for i in range(len(matrix)):
            if matrix[a_colorier][i] == 1 and sol[i] == color:
                conflit = True
                break
        if not conflit:
            return color
        color += 1

def algo_glouton_2(matrix, status_node, color, sol, step):
    # Vérification si tous les sommets sont coloriés
    if all(node == 2 for node in status_node):
        return sol, color  # Sortie avec la solution finale
    
    # Remise à zéro des sommets colorables/non-colorables
    for i in range(len(status_node)):
        if status_node[i] == 1:
            status_node[i] = 0  # Marque le sommet comme non-coloré à nouveau
    
    done = False
    over = False
    
    while not done:
        # Initialisation de Co_NCo pour stocker le nombre de voisins coloriables et non-coloriables
        Co_NCo = [[0, 0] for _ in range(len(matrix))]
        
        # Mise à jour des statuts des sommets voisins en fonction des couleurs
        for i in range(len(matrix)):
            for j in range(len(matrix)):
                if matrix[i, j] == 1:
                    for k in range(len(matrix)):
                        if matrix[j, k] == 1 and status_node[k] == 2 and sol[k] == color and status_node[j] != 2:
                            status_node[j] = 1  # Marque j comme non-coloriable
        
        # Mise à jour du nombre de voisins coloriables et non-coloriables
        for j in range(len(matrix)):
            for k in range(len(matrix)):
                if matrix[j, k] == 1:
                    if status_node[k] == 0:
                        Co_NCo[j][0] += 1  # Nombre de voisins non colorés
                    else:
                        Co_NCo[j][1] += 1  # Nombre de voisins colorés
        
        # Premier placement de couleur
        if step == 1:
            minC = Co_NCo[0][0]
            indice = 0
            for i in range(len(matrix)):
                if Co_NCo[i][0] < minC:
                    minC = Co_NCo[i][0]
                    indice = i
            sol = solution_simple_vector(sol, indice, color)
            status_node[indice] = 2
            step += 1
        else:
            # Chercher le sommet ayant le plus de voisins non-coloriables
            maxNC = -1
            indice = -1
            for i in range(len(matrix)):
                if status_node[i] == 0 and Co_NCo[i][1] > maxNC:
                    maxNC = Co_NCo[i][1]
                    indice = i

            if indice != -1:
                for i in range(len(matrix)):
                    if status_node[i] == 0 and Co_NCo[i][1] == maxNC and i != indice:
                        if Co_NCo[i][0] < Co_NCo[indice][0]:
                            indice = i
                        elif Co_NCo[i][0] == Co_NCo[indice][0]:
                            indice = np.random.choice([i, indice])
                sol = solution_simple_vector(sol, indice, color)
                status_node[indice] = 2

        # Vérification de fin de boucle
        done = True
        cpt, cpt2 = 0, 0

        for i in range(len(status_node)):
            if status_node[i] == 0:
                cpt += 1
                if cpt > 1:
                    done = False
            if status_node[i] == 1:
                cpt2 += 1
        
        # Vérification si un seul sommet reste coloriable
        if cpt == 1 and cpt2 == 0:
            for i in range(len(status_node)):
                if sol[i] == 0:
                    indice = i
            for i in range(len(status_node)):
                if sol[i] == 0:
                    for j in range(len(status_node)):
                        if sol[j] == color and matrix[i, j] == 1:
                            sol[i] = color + 1
                        else:
                            sol[i] = color
            over = True

        # Fin du programme si plus de sommets à colorier
        if cpt == 0 and cpt2 == 0:
            over = True
    
    # Relance de la fonction avec la couleur suivante si la coloration n'est pas terminée
    if not over:
        return algo_glouton_2(matrix, status_node, color + 1, sol, step + 1)
    
    return sol, color


def tester_algorithmes_sur_instances(paths):
    for path in paths:
        print(f"\nInstance : {path}")

        # Charger la matrice d'adjacence
        matrix = load_file(path)
        if matrix is None:
            continue

        # Algorithme glouton aléatoire
        sol_random = algo_glouton_aleatoire(matrix)
        score_random = objectif(solution_vectors(sol_random, max(sol_random)))
        print(f"Algorithme aléatoire : Score = {score_random}, Couleurs = {max(sol_random)}")

        # Algorithme glouton 1
        candidats = [True] * len(matrix)
        sol_glouton1 = algo_glouton_1(matrix, candidats, [0] * len(matrix))
        score_glouton1 = objectif(solution_vectors(sol_glouton1, max(sol_glouton1)))
        print(f"Algorithme glouton 1 : Score = {score_glouton1}, Couleurs = {max(sol_glouton1)}")

        # Algorithme glouton 2
        status_node = [0] * len(matrix)
        sol_glouton2, color_glouton2 = algo_glouton_2(matrix, status_node, 1, [0] * len(matrix), 1)
        score_glouton2 = objectif(solution_vectors(sol_glouton2, color_glouton2))
        print(f"Algorithme glouton 2 : Score = {score_glouton2}, Couleurs = {color_glouton2}")

def main():
    path = 'instance_test.txt'
    paths = ['instance_test.txt', 'DSJC125.1.col' , 'DSJC125.5.col', 'DSJC125.9.col.txt' , 'DSJC250.1.col' , 'DSJC250.5.col' , 'DSJC250.9.col.txt' , 'DSJC500.1.col' , 'DSJC500.5.col' , 'DSJC500.9.col.txt' ]
    
    # ALGORITHME 1
    matrix = load_file(path)
    candidats = [True] * len(matrix)
    sol = [0] * len(matrix)

    # Mesure du temps d'exécution de l'algorithme 1
    t1 = t.time()
    sol = algo_glouton_1(matrix, candidats, sol)
    t2 = t.time()
    tps1 = t2 - t1
    score1 = objectif(solution_vectors(sol, max(sol)))
    
    print("Pour tester la Vitesese des algorithme gloutons\n")
    print("\nAlgorithme 1 - Résultats :")
    print("Score obtenu sur cette instance :", score1)
    print("Nombre minimum de couleurs :", max(sol))
    print("Temps d'exécution de l'algorithme 1 :", tps1, "secondes\n")

    # ALGORITHME 2
    status_node = [0] * len(matrix)
    sol2 = [0] * len(matrix)

    # Mesure du temps d'exécution de l'algorithme 2
    t1 = t.time()
    sol2, color2 = algo_glouton_2(matrix, status_node, 1, sol2, 1)
    t2 = t.time()
    tps2 = t2 - t1
    score2 = objectif(solution_vectors(sol2, color2))

    print("\nAlgorithme 2 - Résultats :")
    print("Score obtenu sur cette instance :", score2)
    print("Nombre minimum de couleurs :", color2)
    print("Temps d'exécution de l'algorithme 2 :", tps2, "secondes\n")
    
    tester_algorithmes_sur_instances(paths)
    


if __name__ == '__main__':
    main()