import pulp
import csv
import pandas as pd
from collections import defaultdict
from datetime import datetime
import time
import json
import logging

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(message)s', 
                    datefmt='%Y-%m-%d %H:%M:%S')

p = logging.info

def solve_transportation_problem(df):
    global p
    p(f"[Start] création du problème")
    
    # Création du problème
    prob = pulp.LpProblem("Transportation_Problem", pulp.LpMinimize)

    # Ensembles
    origines = df['CODE_SITE_ORIGINE'].unique()
    destinations = df['CODE_SITE_DESTINATION'].unique()
    produits = df['CODE_PRODUIT_STOCKAGE'].unique()
    
    p(f"Nombre de produits : {len(produits)}")
    p(f"Nombre d'origines : {len(origines)}")
    p(f"Nombre de destinations : {len(destinations)}")

    p("Création des variables de décision...")
    start_time = time.time()
    # Variables de décision
    vars = pulp.LpVariable.dicts("Transport", 
                                 ((prd, o, d) for prd in produits for o in origines for d in destinations),
                                 lowBound=0,
                                 cat='Integer')
    p(f"Création des variables terminée en {time.time() - start_time:.2f} secondes")

    p("Préparation des données pour la fonction objectif...")
    start_time = time.time()

    # Créer un dictionnaire pour stocker les coûts
    p("Chargement des coûts prétraités...")
    with open('preprocessed_costs.json', 'r') as f:
        cost_dict = json.load(f)
    
    p(f"Données chargées. Nombre de lignes : {len(df)}")

    p("Définition de la fonction objectif...")
    start_time = time.time()

    # Fonction objectif optimisée
    prob += pulp.lpSum(vars[prd, o, d] * cost_dict.get((prd, o, d), 0)
                    for p in produits for o in origines for f in destinations)

    p(f"Fonction objectif définie en {time.time() - start_time:.2f} secondes")

    p("Ajout des contraintes...")
    start_time = time.time()
    # Contraintes
    # 1 - Ne pas dépasser les stocks disponibles dans les sites d'origine
    # 2 - Ne pas dépasser les capacités de réception ou de stockage des sites de destination

    # Contrainte 1 :
    # la somme des quantités transportées de ce produit depuis ce site d'origine vers toutes les destinations 
    # ne doit pas dépasser la quantité prévue disponible à l'origine ('QTE_PREV')
    for prd in produits:
        for o in origines:
            matching_rows = df[(df['CODE_PRODUIT_STOCKAGE'] == prd) & (df['CODE_SITE_ORIGINE'] == o)]
            if not matching_rows.empty:
                prob += pulp.lpSum(vars[prd, o, d] for d in destinations) <= matching_rows['QTE_PREV'].iloc[0]
            else:
                p(f"Warning: No data found for product {prd} at origin {o}")

    # Contrainte 2 :
    # la somme des quantités transportées de ce produit vers cette destination, en provenance de toutes les origines, 
    # ne doit pas dépasser la capacité de la destination ('CAPACITE')
    for prd in produits:
        for d in destinations:
            matching_rows = df[(df['CODE_SITE_DESTINATION'] == d)]
            if not matching_rows.empty:
                prob += pulp.lpSum(vars[prd, o, d] for o in origines) <= matching_rows['CAPACITE'].iloc[0]
            else:
                p(f"Warning: No data found for destination {d}")

    p(f"Contraintes ajoutées en {time.time() - start_time:.2f} secondes")

    # Résolution
    p(f"Début de la résolution : {datetime.now().strftime('%H:%M:%S')}")
    start_time = time.time()
    
    # Créer un solveur avec logs activés
    solver = pulp.PULP_CBC_CMD(msg=True, maxSeconds=600, fracGap=0.01, threads=8)

    # Résoudre le problème avec le solveur configuré
    status = prob.solve(solver)
    
    p(f"Fin de la résolution : {datetime.now().strftime('%H:%M:%S')}")
    p(f"Temps de résolution : {time.time() - start_time:.2f} secondes")
    p(f"Statut de la solution : {pulp.LpStatus[status]}")

    if status != pulp.LpStatusOptimal:
        p("Le problème n'a pas été résolu de manière optimale.")
        return None

    p("Récupération des résultats...")
    start_time = time.time()
    # Récupération des résultats
    resultats = defaultdict(float)
    for (prd, o, d), v in vars.items():
        if v.value() > 0:
            resultats[(prd, o, d)] += v.value()
    p(f"Résultats récupérés en {time.time() - start_time:.2f} secondes")

    return resultats, prob.objective.value()

def write_results_to_csv(resultats, cout_total, filename):
    global p
    p(f"Écriture des résultats dans {filename}")
    start_time = time.time()
    with open(filename, 'w', newline='') as fichier:
        writer = csv.writer(fichier, delimiter=';')
        writer.writerow(['Code Produit', 'Origine', 'Destination', 'Quantite'])

        for (code_produit, origine, destination), quantite in resultats.items():
            writer.writerow([code_produit, origine, destination, quantite])

        writer.writerow(['TOTAL', '', '', cout_total])

    p(f"Résultats écrits en {time.time() - start_time:.2f} secondes")
    p(f"\nCoût total: {cout_total}")
    p(f"Résultats sauvegardés dans {filename}")

def main():
    global p
    p("[Démarrage]")
    start_time = time.time()
    
    p("Chargement des données...")
    df = pd.read_csv('out_prod_cartesien.csv', sep=';')  # Assurez-vous que le chemin est correct
    p(f"Données chargées. Nombre de lignes : {len(df)}")

    # Résolution du problème
    resultats, cout_total = solve_transportation_problem(df)

    if resultats is not None:
        # Écriture des résultats
        nom_fichier = f'resultats_optimisation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        write_results_to_csv(resultats, cout_total, nom_fichier)
    
    p(f"Temps total d'exécution : {time.time() - start_time:.2f} secondes")
    p("Fin du programme")

if __name__ == "__main__":
    main()
