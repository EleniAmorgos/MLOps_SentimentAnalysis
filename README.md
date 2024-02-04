MLOps Sentiment Analysis
==============================

This project is a MLOps project based on the subject "sentiment analysis". 

Project Organization
------------

    │── .github
    │   ├── workflows
    │   │   ├── run-api-container.yml : git action qui build l'image puis la pousse vers dockerhub test + latest. puis déploy l'image api latest sur un serveur DS
    │   │   ├── run-model-container.yml : git action qui lance le réentraienement du modèle dtc à partir des commentaires stockés dans un bucket S3
    │   │   ├── run-preprocessing-container.yml : git action qui la lance le preprocessing des commentaires stockés dans un bucket S3
    │   │   └── run-scrapping-container.yml : git action qui la lance le scrapping des commentaires depuis le site web Trustpilot et les stocke dans un bucket S3
    │   └── depandabot.yml : schedule des git actions 
    │
    ├── LICENSE
    │
    ├── README.md          <- The top-level README for developers using this project.
    │
    ├── src                <- Source code for use in this project.
    │   │ 
    │   ├── api
    │   │   ├── user_db           <- User data base in jason
    │   │   │   └── users_data.json : user data base  
    │   │   │
    │   │   ├── data           <- Scripts to download or generate data
    │   │   │   ├── web_scrapping.py : Scraps comments from Trustpilot
    │   │   │   └── __init__.py : fichier d'initialisation du package data
    │   │   │
    │   │   ├── features       <- Scripts to turn raw data into features for modeling
    │   │   │   ├── build_features.py : Processes and archives the comments (new comments into histo)
    │   │   │   └── __init__.py : fichier d'initialisation du package features
    │   │   │
    │   │   └── predictions         <- Scripts using trained models to make predictions
    │   │       ├── prediction_class.py : retourne les prédictions positive (1) ou négative (0) sur le commentaire 'comment' et retourne les probabilité de chacune
    │   │       ├── __init__.py :  fichier d'initialisation du package prediction_class
    │   │       ├── vect_dtc.pkl : vectorization des données du modele dans un fichier pickle
    │   │       ├── model_dtc.pkl : modèle entrainé. sert pour restituer les prédictions
    │   │       └── model_score_dtc : score global du modèle utilisé pour les prédictions
    │   │   
    │   │── Streamlit        <-  Frontend pointant vers l'API pour la restitution des requêtes
    │   │   ├── documentation : documentation sur le projet
    │   │   ├── images
    │   │   │   ├──  OIP.png : photo d'une main composé des mot les + présents dans les commentaires  
    │   │   │   └──  style.css : police du streamlit
    │   │   ├── predictions : model_evaluation.txt : affichage dans streamlit du score global du modèle utilisé pour les prédictions
    │   │   ├── dockerfile : Dockerfile pour le build de l'image streamlit
    │   │   ├── requirements.txt : packages pour le build de l'image streamlit
    │   │   └── streamlit-satisfaction4.py : code python du streamlit
    │   │   
    │   │── data        <-  recupération des commentaires scrappés depuis l'api
    │   │   ├── external       <- Data from third party sources (Web scrapping)
    │   │   ├── interim        <- Intermediate data that has been transformed.
    │   │   ├── processed      <- The final, canonical data sets for modeling.
    │   │   └── raw            <- The original, immutable data dump.
    │   │  
    │   │── model      <-  contient les éléments du build de l'image docker qui réentraine le modèle via une git action
    │   │   ├── dockerfile : Dockerfile pour le build de l'image model
    │   │   ├── requirements.txt : packages pour le build de l'image model
    │   │   ├── accesKeys.csv : clés de connexion au bucket S3 public contenant la base de donnée de commentaires    
    │   │   └── model_dtc_0_1.py : réentrainement du modèle sur la BDD de commentaire dans S3. Lancé par une git action
    │   │       
    │   │── scrapp    <-  contient les éléments du build de l'image docker qui scrapp les données sur truspilot et les enregistre sur S3 via une git action
    │   │   └── scrapping
    │   │       ├── dockerfile : Dockerfile pour le build de l'image scrapping
    │   │       ├── requirements.txt : packages pour le build de l'image scrapping
    │   │       ├── accesKeys.csv : clés de connexion au bucket S3 public contenant la base de donnée de commentaires
    │   │       └── last30days.py : fichier python correspondant aux scrapp des nouvelles données pour MAJ de la BDD de commentaires
    │   │   
    │   │── preprocessing   <- contient les éléments du build de l'image docker qui preprocesse les données scrappées depuis S3 via une git action
    │   │   ├── dockerfile : Dockerfile pour le build de l'image preprocessing
    │   │   ├── requirements.txt : packages pour le build de l'image preprocessing 
    │   │   ├── accesKeys.csv : clés de connexion au bucket S3 public contenant la base de donnée de commentaires
    │   │   └── last30days.py : fichier python correspondant aux scrapp des nouvelles données pour MAJ de la BDD de commentaires     
    │   │   
    │   │── test_api          <-  contient les éléments du build de l'image docker qui test l'API via des tests unitaires
    │   │   ├── dockerfile : Dockerfile pour le build de l'image pytest
    │   │   ├── requirements.txt : packages pour le build de l'image pytest 
    │   │   └── test_request_api_OAuth.py : fichier python correspondant aux tests unitaire de l'API   
    │   │   
    │   │── trainning         <-  stockage du modèle mis à jour par le lancement du container model via une git action 
    │   │   ├── model_dtc.pkl : modèle entrainé. sert pour restituer les prédictions. issu du réentrainement du modèle par la git action
    │   │   └── vect_dtc.pkl : vectorization des données du modele. issu du réentrainement du modèle par la git action
    │   │       
    │   │── Makefile : clean les images en cours et éxécute le docker compose qui lance les containers api, pytest et streamlit
    │   │       
    │   └── Docker-compose.yml : lance les containers api, pytest et streamlit
    │              
    │── .gitignore : fichier regroupant les fichiers et dossier à ne pas aficher
    │
    └── config       <- Describe the parameters used in train_model.py and predict_model.py

--------

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>
