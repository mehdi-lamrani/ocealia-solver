import pandas as pd
import json
import logging

# Configuration de base pour le logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(message)s', 
                    datefmt='%Y-%m-%d %H:%M:%S')

p = logging.info

def preprocess_data(input_file, output_file):
    p("Chargement des données...")
    df = pd.read_csv(input_file, sep=';')
    
    total_rows = len(df)
    p(f"Nombre total de lignes à traiter : {total_rows}")

    p("Création du dictionnaire des coûts...")
    cost_dict = {}
    for index, row in df.iterrows():
        # Création de la clé en combinant les codes produit, site d'origine et site de destination
        key = f"{row['CODE_PRODUIT_STOCKAGE']}_{row['CODE_SITE_ORIGINE']}_{row['CODE_SITE_DESTINATION']}"
        cost_dict[key] = row['COUT_TOTAL']
        
        # Affichage du progrès toutes les 1000 lignes
        if (index + 1) % 1000 == 0:
            p(f"Traité {index + 1} lignes sur {total_rows}")
            break  # Arrêt du traitement après 1000 lignes
    
    p("Sauvegarde des données prétraitées...")
    # Écriture du dictionnaire des coûts dans un fichier JSON
    with open(output_file, 'w') as f:
        json.dump(cost_dict, f)
    
    p(f"Données prétraitées sauvegardées dans {output_file}")

if __name__ == "__main__":
    # Appel de la fonction de prétraitement avec les noms de fichiers appropriés
    preprocess_data('out_prod_cartesien.csv', 'preprocessed_costs.json')