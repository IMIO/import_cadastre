Récupération des données du cadastre (matrice et plans) dans Urban
==================================================================
Version 2018. Les version précédentes du cadastre ne sont pas compatibles avec ces scripts


Prérequis:
==========

 - python3-dev
 - CREATE EXTENSION postgis;

Variables d'environnement :
===========================

   To define in config.cfg.
 - CADASTREDIR : qui pointe vers le répertoire contenant tout les fichiers du cadastre.
 - PG_HOST : hôte de la base de données (ex: localhost)
 - DATABASE_NAME : nom de la base de données (ex: test_urban)
 - DB_USER_NAME : utilisateur ayant le droit de CREATE TABLE et INSERT (ex: propriétaire de la db)
 - DB_USER_PASSWORD : password de l'utilisateur

Structure du répertoire de données cadastrales :
================================================

dans le sous dossier ./input
 ``
 Soignies
    * Matrice
        * Owner.csv
        * Parcel.csv
    * Matrice_doc
        * OUPUT PARCELS_*.xlsx
    * Historique
        * EXTRHIS_*_2020.csv
        * ....
    * Plan
        * B_CaBu.shp
        * A_AdMu.shp
        * ....
        * les shapefiles viennent du l'url https://eservices.minfin.fgov.be/myminfin-web/pages/cadastral-plans (lambert72)
``
Exemple de valeur pour la configuration d'exemple : /Users/niko/dev_imio/import_cadastre/data/Soignies

Utilisation:
============

 - make install
 - make all

 Données nécéssaires pour urbanmap dans v_map_capa:
``
 {name: 'codeparcelle', type: 'string'}, --> ok
 {name: 'co1', type: 'string'}, --> xxx -> builtSurface from prc ?
 {name: 'prc', type: 'string'}, --> ok -> Num. Parc.
 {name: 'na1', type: 'string'}, --> ok -> "Nature"
 {name: 'sl1', type: 'string'}, --> ok
 {name: 'da', type: 'string'}, --> ok
 {name: 'ri1', type: 'string'}, --> xxx ex:'16' Revenu Cad.", CadastralIncome
 {name: 'pe' , type: 'string'}, --> ok
 {name: 'daa' , type: 'string'}, --> ok -> prc
 {name: 'ord' , type: 'string'}, --> ok -> prc
 {name: 'in' , type: 'string'}, --> xxx ??
 {name: 'ha1' , type: 'string'}, --> xxx -> RC Parc N.Batie: .. soilRent ? -> vide dans les données de test
 {name: 'rscod' , type: 'string'}, --> xxx --> Code de rue
 {name: 'acj' , type: 'string'}, --> xxx --> Année de construction -> constructionYear de la parcelle ? vide dans les données de tests
 {name: 'adr1' , type: 'string'}, --> ok
 {name: 'adr2' , type: 'string'} --> ok
``
2017 : Remplir les champs capa à partir de la capakey

update capa set
 da = substring(capakey from 1 for 5)::int,
 section = substring(capakey from 6 for 1),
 radical = substring(capakey from 7 for 4)::int,
 exposant = substring(capakey from 14 for 1),
 bis = substring(capakey from 12 for 2)::int,
 puissance = substring(capakey from 15 for 3)::int;
