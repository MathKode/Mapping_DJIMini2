# Mapping DJI Mini2
Projet OpenSource qui permet de rassembler des images prises aux drones DJI Mini 2/3. Il crée 1 seule image finale (permet de cartographier un lieu)
Utilisation gratuite (partage du lien officiel recommandé si possible) 
Participant au Projet : BiMathAx
V1.3

## Rendu
Ici vous avez un exemple de rendu :

*Version 1 avant réglage :*

<img src="../Illustration/test4.jpeg">

*Version 1.2 après réglage :

<img src="../Illustration/test200_26_reduce.jpeg" width=400px>

## Prise de Photo

Une fois l'emplacement choisi, le drône ne doit plus pivoter sur lui même et doit prendre **2 photos alignées** selon l'axe HORIZONTALE ou VERTICALE.

Les 2 photos sont requises pour la calibration de l'*angle*. Une fois effectué, vous pouvez vous ballader sur toutes la zone et dans tous les sens (temps que le drone **ne pivote pas** sur lui-même)

Bien-sûr, vérifier que le signal gps est fort (>12 gps) pour assurer la précision des données GPS des photos.

Les photos doivent toute être prise à la **même altitude** (pour ne pas fausser le *cota pixel/m*). Nous vous conseillons d'utiliser le mode rafale en délai 5s mais des jpeg prises individuellement fonctionnent aussi !

## Baisse de qualité

Ce code assemble des images de hautes qualités. Or Haute qualité est associé à haut temps de traitement ! Pour diminuer le temps de traitement des images pendant la phase d'ajustement, nous vous recommandons de diminuer la qualité de ces dernières...

Le script (reducer_quality.py)[../reducer_quality.py] vous permet de baisser la qualité de vos photos : 
- Vous choississez un niveau de compression (minimun 1)
- Le script traite l'image et vous en créer une nouvelle (reduce_<NOM-IMAGE>)

*Conseil: Utiliser des images réduites pour la calibration du logiciel (cota_x, cota_y et angle). Vous pourrez ensuite les remplacez par les images de bonne qualité SANS CHANGEZ LES PARAMATRES*
