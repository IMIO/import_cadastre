# -- coding: utf-8 --

# Conversion fichiers cadastre Urbain (2016+) vers tables utilisée par Urban
#  génération du shape file b_capa avec les coordonnées de la parcelle
#  Prérequis : Installation de pandas + geopandas + python 3.x
#  Utilisation : décompacter le ficher Urbain.
#                Indiquer le chemin du dossier dans lequel figurent les sous-dossier Matrice/Plan dans path_to_data
# le programme génère o_da.csv, o_pe.csv, o_prc.csv, o_map.csv, o_capa.shp qu'il faut remonter ensuite dans postgres

import re
import glob
import pandas as pd
import geopandas as gpd
import os
import sys
import numpy as np

import cadutils

if os.environ["CADASTREDIR"] == "" :
    print("Environment variable CADASTREDIR must be set and pointing to a directory")
    sys.exit(0)

path_to_data = os.environ["CADASTREDIR"]

path_to_matrice = os.path.join(path_to_data,"Matrice")
path_to_matrice_doc = os.path.join(path_to_data,"Matrice_doc")
path_to_plan = os.path.join(path_to_data,"Plan")

cadutils.checkPath(path_to_matrice)
cadutils.checkPath(path_to_matrice_doc)
cadutils.checkPath(path_to_plan)

dO = pd.read_csv(path_to_matrice + '/Owner.csv', sep = ';', header=0, encoding ='latin_1', na_filter=False)
dP = pd.read_csv(path_to_matrice + '/Parcel.csv', sep = ';', header=0, encoding = 'latin_1', na_filter= False)

def convDivName (s):
    numDiv = re.findall('\d+', s)
    if len(numDiv) != 0:
        numDiv = int(numDiv[0])
    prop = s.capitalize()
    pos = s.find('DIV/')
    if pos >= 0:
        prop = prop[pos + 4:]
        pos = prop.find('/')
        if pos >= 0:
            prop = prop[:pos]
        prop = prop + ' (' + str(numDiv) + ')'
    # no locality, remove multiple spaces
    elif prop.find(' ') > 0:
        prop = ' '.join([x for x in prop.split(' ') if x])
    prop = prop.capitalize()
    return (prop)

# Récupération du nom de la division de la parcelle
fileparcels = glob.glob(path_to_matrice_doc+"/OUTPUT PARCELS*.xlsx")
divCadF = pd.read_excel (fileparcels[0], sheet_name=u'divCad ',
                        skiprows= 1, names = ['divCad', 'divName_o']).assign (divName='' )
divCadF['divName'] = divCadF['divName_o'].apply (lambda x: convDivName(x))

# Récupération du nom de la nature de la parcelle
natureF = pd.read_excel (fileparcels[0], sheet_name=u'Nature',
                       skiprows= 1, names = ['nature', 'nature_name','nature_name_nl'])

da = pd.DataFrame(data = dP.divCad.unique(), columns = ['divCad'])
da['divName'] = da['divCad'].apply (lambda x:divCadF[divCadF.divCad == x].divName.values[0])
da['dan1'] = da['divName']
print ('Divisions gérées: ')
for sections in da.loc[:,'divName'].values :
 print (sections)
pe = pd.DataFrame(
    dO[['propertySituationIdf','order','name','firstname','articleOrder']],
    columns =['propertySituationIdf','order','name', 'firstname', 'articleOrder', 'pe','daa','adr1','adr2'] )
pe.loc[:,['pe']] = pe.name.str.cat (pe.firstname.astype(str), sep =', ' ) # pe = nom, prénom
pe.loc[:,'pe'] = pe.pe.str.replace('[,] $', '') # retirer la virgule à la fin du nom isolé

dO['articleNumber'] = pd.to_numeric(dO['articleNumber'], errors ='coerce')  # crée des NaN si rien dans le champ
dO['articleNumber'] = dO['articleNumber'].fillna(0).astype(int)  # met 0 si NaN

pe.loc[:,'daa'] = dO['divCad']*100000 + dO['articleNumber']
pe.loc[:,"adr1"] = dO['zipCode'].str.cat (dO['municipality_fr'], sep = ' ')
pe.loc[:,'adr2'] = dO['street_fr'].str.cat (dO['number'], sep = ' ')
pe.rename(columns = {'order':'pos', 'articleOrder' : 'lt'}, inplace = True)

prc = pd.DataFrame (dP[['propertySituationIdf','capakey','street_situation','divCad','section','primaryNumber','bisNumber','exponentLetter','exponentNumber','articleNumber','articleOrder','surfaceTaxable','soilRent','cadastralIncome','street_code','constructionYear','order','number']],
                    columns =['propertySituationIdf','capakey','street_situation','divCad','section','primaryNumber','bisNumber','exponentLetter', 'exponentNumber','articleNumber','articleOrder','surfaceTaxable','soilRent','cadastralIncome','street_code','constructionYear','daa','order','number'])

prc['articleNumber'] = pd.to_numeric(prc['articleNumber'], errors = 'coerce')
prc['articleNumber'] = prc['articleNumber'].fillna(0).astype(int)

prc['daa'] = prc[['divCad']]*100000 + prc[['articleNumber']].values
prc.rename (columns = {'daa': 'daa_prc', 'articleOrder' : 'prc_ord'}, inplace = True)

print ("\nConversion natures ...")
# perf problems
def getNatureNameFromIndex(natureIndex):
    natureItem = natureF[natureF.nature == natureIndex]

    if not natureItem.empty:
        return natureItem.nature_name.values[0]
    else:
        print("Erreur lors de la récupération de la valeur de nature pour le code %s . Il faut vérifier export_parcels.xlsx page nature" % natureIndex)
        return str(natureIndex)

#prc.loc[:,'na1'] = dP.loc[:,'nature'].apply (lambda x:natureF[natureF.nature == x].nature_name.values[0])

prc.loc[:,'na1'] = dP.loc[:,'nature'].apply(getNatureNameFromIndex)
prc['prc'] = prc['section'].astype (str) + ' ' + prc['primaryNumber'].astype(str) \
            + '  ' + prc['bisNumber'].astype(str) + ' ' + prc['exponentLetter'].astype(str) + ' ' + prc['exponentNumber'].astype(str)
prc.loc[:,'prc'] = prc.prc.str.replace(' $', '') # retirer l'espace à la fin du nom isolé

prc['street_situation'] = prc['street_situation'].astype(str) + ' ' + prc['number'].astype(str)
capa = gpd.read_file (path_to_plan + "/B_CaPa.shp")
map = pd.DataFrame (capa, columns = ['CAPAKEY', 'geometry'])


map.CAPAKEY = map.CAPAKEY.astype (str)
prc.capakey = prc.capakey.astype (str)

map = map.merge (prc.drop_duplicates(subset = ['capakey']), how = 'left', left_on = 'CAPAKEY', right_on = 'capakey' )
map = map.merge (pe.drop_duplicates (subset = ['propertySituationIdf']), how = 'left', left_on = 'propertySituationIdf', right_on = 'propertySituationIdf')
map.rename (columns = {'street_situation': 'sl1'}, inplace = True)




# EXPORT CSV
# --------------- DA -------------------
print ('Génération de DA.csv')
da.rename (columns = {'divCad': 'da', 'divName':'divname'}, inplace = True)
da.to_csv (path_to_data + '/o_da.csv', sep='|', columns=['da','divname','dan1'])

# --------------- PE -------------------
print ('Génération de PE.csv')
pe.to_csv (path_to_data + '/o_pe.csv', sep='|', columns=['pe', 'pos','adr1', 'adr2','daa','lt'])

# --------------- PRC -------------------
print ('Génération de PRC.csv')
prc.rename (columns = {'street_situation': 'sl1', 'daa_prc':'daa', 'prc_ord': 'ord', 'surfaceTaxable': 'co1', 'soilRent': 'ha1', 'cadastralIncome': 'ri1', 'street_code' : 'rscod', 'constructionYear':'acj'}, inplace = True)
prc.to_csv (path_to_data + '/o_prc.csv', sep='|', columns=['capakey', 'daa', 'ord', 'sl1', 'prc','na1','co1' , 'ha1', 'ri1', 'rscod'])

# --------------- MAP -------------------
print ('Génération de MAP.csv')

#map = map.loc[map['CAPAKEY'] != 'DP'] #Pepinster has DP in capakey ..
map = map.loc[map['capakey'].str.len() == 17] #Get only capakey
# Attention Il exisiste des capakey sans PRC lié sur soignies
map.to_csv (path_to_data + '/o_map.csv', sep='|', columns=['capakey', 'pe', 'adr1','adr2','sl1','prc','na1', 'CAPAKEY'])

# --------------- CAPA -------------------
print ('Génération de B_CAPA.shp')
map.rename (columns = {'divCad':'da', 'primaryNumber':'radical','bisNumber':'bis'}, inplace = True)
map['exposant'] = map['exponentLetter']
capa['puissance'] = map['exponentNumber']
capa =  capa.merge (map.loc[:,['CAPAKEY','da','section','radical','exposant','bis']].drop_duplicates(subset = ['CAPAKEY']), how = 'left', left_on = 'CAPAKEY', right_on = 'CAPAKEY' )
capa.to_file (path_to_data + "/OB_CaPa.shp")
print ('Procédure terminée\n')
