import pandas as pd
import logging
from datetime import datetime
import os

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(message)s', 
                    datefmt='%Y-%m-%d %H:%M:%S')

p = logging.info

def preprocess_dataframe(df, output_dir='.'):
    p("Début du prétraitement du DataFrame")
    
    # Créer le répertoire de sortie s'il n'existe pas
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Créer un DataFrame avec toutes les combinaisons possibles de produits et origines
    all_combinations = pd.MultiIndex.from_product([df['CODE_PRODUIT_STOCKAGE'].unique(), 
                                                   df['CODE_SITE_ORIGINE'].unique()], 
                                                  names=['CODE_PRODUIT_STOCKAGE', 'CODE_SITE_ORIGINE'])
    all_combinations_df = pd.DataFrame(index=all_combinations).reset_index()
    
    # Fusionner avec le DataFrame original
    merged_df = pd.merge(all_combinations_df, df, on=['CODE_PRODUIT_STOCKAGE', 'CODE_SITE_ORIGINE'], how='left')
    
    # Filtrer les lignes où il n'y a pas de données
    valid_df = merged_df.dropna(subset=['QTE_PREV'])
    
    # Compter combien de lignes ont été supprimées
    removed_count = len(merged_df) - len(valid_df)
    p(f"Nombre de combinaisons produit-origine supprimées : {removed_count}")
    
    # Générer un nom de fichier unique avec un horodatage
    filename = f'out_prod_cartesien_filtre.csv'
    filepath = os.path.join(output_dir, filename)
    
    # Exporter le DataFrame filtré
    valid_df.to_csv(filepath, index=False)
    p(f"DataFrame filtré exporté vers '{filepath}'")
    
    return filepath

# Utilisation :
df = pd.read_csv('project/out_prod_cartesien.csv', sep=';')  # Assurez-vous de remplacer par le nom de votre fichier
filtered_data_path = preprocess_dataframe(df)

# Vous pouvez maintenant utiliser ce chemin de fichier dans votre fonction solve_transportation_problem
print(f"Le fichier filtré a été sauvegardé à : {filtered_data_path}")
