**Lire Final_report.pdf pour le rapport complet.**

# Objectif 

Ce projet étudiant (mené à l'ENSE3 en 2021-2022) avait pour but d’étudier les scénarios possibles pour le mix électrique français en 2050. La décarbonation rapide du secteur électrique est primordiale pour diminuer les émissions de CO2 mondiales dans le respect des Accords de Paris. Pour cela, les énergies renouvelables (EnR), et notamment le solaire et l’éolien, sont amenées à jouer un rôle prépondérant. Toutefois, elles sont souvent décriées pour leur intermittence : leur production est fortement dépendante des conditions météorologiques du moment (vitesse du vent et ensoleillement), ce qui peut compliquer la gestion du système électrique basée sur l’équilibre production-consommation à chaque instant. Elles diffèrent en cela des moyens dits “pilotables” (e.g. nucléaire, gaz, charbon et fioul) qui caractérisent les mix électriques classiques. Cette intermittence induit des coûts supplémentaires (par rapport aux moyens de production pilotables) en raison des moyens de flexibilité (stockage, ajustement de la demande, modification des habitudes de consommation, etc.) nécessaires à leur intégration. 
Tout l’objectif de ce projet est de quantifier cet éventuel surcoût économique des EnR selon divers taux de pénétration (c’est-à-dire la part de la production d’origine renouvelable dans la production d’électricité totale), en s’assurant du respect des objectifs de réductions des émissions de gaz à effet de serre. Nous avons pour cela choisi de modéliser sous Python, les différents scénarios ayant trait au système électrique français en 2050 dans son ensemble en y appliquant différentes contraintes, correspondant aux trois axes d’études qui seront présentés par la suite. Les calculs de mix énergétiques reposent au final sur la formulation et la résolution de problèmes d’optimisation représentant les objectifs et contraintes considérées.

# Méthdologie

Tout le travail se base sur les données fournies par RTE. En particulier, un fichier CSV détaille la consommation et la production par technologie pour chaque année, à pas demi-horaire. [2] L’année de référence choisie est 2019, l’année 2020 ayant été fortement marquée par l’épidémie de Covid-19 ne représente pas les tendances à venir. 

De ce fichier a notamment été extrait les courbes normalisées (comprises entre 0 et 1) de disponibilité des EnR (solaire et éolien) à des pas demi-horaires, calculées grâce à la formule. L’objectif de cette normalisation et de pouvoir tester facilement différent niveaux de pénétration de solaire ou éolien (i.e. capacités installées).

Par ailleurs, RTE fournit également les capacités installées pour chaque technologie

### Explication succincte du travail d’optimisation

Résoudre un problème d’optimisation  consiste en la minimisation/maximisation d’une fonction objectif mettant en jeu plusieurs variables. Ces variables peuvent être soumises à une ou plusieurs contraintes, qui représentent les modèles d’opération des systèmes sous la forme d’égalités ou d’inégalités. Pour le cas présent, la fonction en question est celle des coûts totaux (ou des émissions de CO2), qui fait intervenir les capacités installées pour chaque technologie de production et de stockage (coûts CAPEX) ainsi que la production de chacune de ces technologies à chaque pas de temps demi-horaire (utilisée pour le calcul des coûts OPEX). Par exemple, si nous considérons 7 technologies de production d’électricité, cela représente 7 (les capacités installées de chaque production) + 48 * 365 * 7 (un pas toutes les demies-heures fois 365 jour dans l’année, et ce pour chaque technologie de production) = 122,647 variables mises en jeu dans la fonction objectif à minimiser.
Les contraintes peuvent porter sur une ou plusieurs variables à la fois. Par exemple, la contrainte P=C (production=consommation) de stabilité du réseau, implique que pour les 48*365 =  17520 pas de temps, la somme de la production électrique doit être égale à la consommation d’électricité. 

### Hypothèses de travail

- Le système électrique est extrêmement complexe, aussi nous avons dû faire quelques simplifications pour pouvoir produire des résultats dans le temps qui nous était imparti. Les hypothèses faites sont les suivantes :

- Système initial vierge (“green field”) : on suppose que toutes les capacités sont à construire à l’année 0. Dans la réalité, il faudrait prendre en compte ce qui existe actuellement et simuler les constructions/mises hors service de chaque moyen de production chaque année jusqu’à 2050 (on parle alors de simulations dynamiques plus compliquées à mettre en œuvre).

- Année 2019 choisie comme référence : on suppose par la suite (sauf mention contraire), que le profil de consommation ainsi que le profil des EnR intermittentes sont les mêmes chaque année

- Pas de réseau électrique : pas de problématique de congestion ou de raccordement des EnR au réseau. Les lignes du réseau et les contraintes potentielles en courant/tension ne sont pas représentées.
Pas d’import/Export: toute l’électricité doit être produite/consommée dans le pays.

- Coûts d’opération et d’installation constants, facteurs d’émissions constants : nous ne prenons pas en compte les réductions de coûts des technologies, ni les diminutions des facteurs d’émissions amenés par la capture du carbone par exemple. Les coûts et facteurs d’émission utilisés sont résumés dans le tableau suivant pour les aspects installations/opérations (coûts d’opération nul pour les renouvelables).

- Une technologie = une centrale : chaque technologie de production d’électricité est considérée comme un unique générateur équivalent. En pratique, cela implique notamment que l’espace possible des capacités installées est continu. Ce n’est pas le cas dans la réalité : par exemple, la plus petite unité de puissance nucléaire est le réacteur, d’au moins 900 MWe.

- Contraintes sur l’hydraulique : l’hydraulique ne peut pas produire à sa puissance nominale tout au long de l’année, dans la mesure où le niveau d’eau dans le lac de retenue doit être assez élevé pour pouvoir produire de l’électricité.  Pour prendre en compte la saisonnalité du niveau de remplissage d’eau, nous supposons que la somme de ce qui est produit chaque mois par l’hydraulique dans l’optimisation ne peut être supérieur à l'énergie mensuelle pour l’année de référence 2019.

- Stockage générique : dans les premières simulations, un stockage générique (purement mathématique) est mis en place pour absorber les surplus d’EnR. Les technologies de stockage sont considérées dans le dernier jeu de simulation.

- Pas d’électricité d’origine biomasse.

D’autres hypothèses spécifiques ont également été prises pour chaque scénario.

### Scénarios retenus

Étant un groupe de 6, par équipe de deux, nous nous sommes répartis le travail en trois scénarios, détaillés ci-dessous :

- **Scénario 1** : différents taux de pénétration d’EnR
- **Scénario 2** : différents taux de pénétration de véhicules électriques (V2G)
- **Scénario 3** : scénario 100% EnR et étude des besoins en stockage et de la flexibilité
  


