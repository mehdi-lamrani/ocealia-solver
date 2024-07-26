import pandas as pd

def produit_cartesien():
    # Chargement des données
    collecte = pd.read_csv('out_collecte_prev_eq_ble.csv', sep=';')
    cellule = pd.read_csv('cellule.csv', sep=';')
    cout_transport = pd.read_csv('cout_transport.csv', sep=';')

    # Produit cartésien de collecte et cellule
    resultat = collecte.merge(cellule, how='cross')

    # Calcul du coût total
    resultat = resultat.merge(cout_transport, 
                            left_on=['CODE_SITE_x', 'CODE_SITE_y'], 
                            right_on=['CODE_SITE_ORIGINE', 'CODE_SITE_DESTINATION'])

    resultat['COUT_TOTAL'] = round(resultat['QTE_PREV'] * resultat['COUT'], 0).astype(int)
    resultat['CAPACITE'] = resultat['CAPACITE'].round(0).astype(int)
    resultat['QTE_PREV_EQ_BLE'] = resultat['QTE_PREV_EQ_BLE'].round(2)
    resultat['QTE_PREV'] = resultat['QTE_PREV'].round(2)
    
    # Sélection des colonnes pertinentes
    resultat_final = resultat[['CODE_PRODUIT_STOCKAGE', 'CODE_SITE_x', 'CODE_SITE_y', 'CODE_CELLULE', 'CAPACITE', 'COUT','QTE_PREV_EQ_BLE', 'QTE_PREV', 'COUT_TOTAL']]

    # Renommage des colonnes pour plus de clarté
    resultat_final = resultat_final.rename(columns={
        'CODE_SITE_x': 'CODE_SITE_ORIGINE',
        'CODE_SITE_y': 'CODE_SITE_DESTINATION',
        'COUT': 'COUT_UNITAORE'
    })

    # Affichage des premières lignes du résultat
    #print(resultat_final.head())

    resultat_final.to_csv('/workspace/gitpod2/out_prod_cartesien.csv', index=False, sep=';')

produit_cartesien()
