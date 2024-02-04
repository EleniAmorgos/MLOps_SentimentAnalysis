MLOps Sentiment Analysis
==============================

This project is a MLOps project based on the subject "sentiment analysis". 

Project Organization
------------

    ├── LICENSE
    ├── README.md          <- The top-level README for developers using this project.
    ├── data
    │   ├── external       <- Data from third party sources (Web scrapping)
    │   ├── interim        <- Intermediate data that has been transformed.
    │   ├── processed      <- The final, canonical data sets for modeling.
    │   └── raw            <- The original, immutable data dump.
    │
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │                         generated with `pip freeze > requirements.txt`
    │
    ├── src                <- Source code for use in this project.
    │   ├── __init__.py    <- Makes src a Python module
    │   │── api
    │   │   ├── user_db           <- User data base in jason
    │   │   │   └── users_data.json : user data base  
    │   │   │
    │   │   ├── data           <- Scripts to download or generate data
    │   │   │   └── web_scrapping.py : Scraps comments from Trustpilot
    │   │   │   └── __init__.py : fichier d'initialisation du package data
    │   │   │
    │   │   ├── features       <- Scripts to turn raw data into features for modeling
    │   │   │   └── build_features.py : Processes and archives the comments (new comments into histo)
    │   │   │   └── __init__.py : fichier d'initialisation du package features
    │   │   │
    │   │   ├── predictions         <- Scripts using trained models to make predictions
    │   │   │   └── prediction_class.py : retourne les prédictions positive (1) ou négative (0) sur le commentaire 'comment' et retourne les probabilité de chacune
    │   │   │   └── __init__.py :  fichier d'initialisation du package prediction_class
    │   │   │   └── vect_dtc.pkl : vectorization des données du modele dans un fichier pickle
    │   │   │   └── model_dtc.pkl : modèle entrainé. sert pour restituer les prédictions
    │   │   │   └── model_score_dtc : score global du modèle utilisé pour les prédictions
    │   │   │
    │   │── Streamlit        <-  Frontend pointant vers l'API pour la restitution des requêtes
    │   │   │   └── documentation : documentation sur le projet
    │   │   │   └── images :
    │   │   │   │   └──  OIP.png : photo d'une main composé des mot les + présents dans les commentaires  
    │   │   │   │   └──   style.css : police du streamlit
    │   │   │   └── predictions : model_evaluation.txt : affichage dans streamlit du score global du modèle utilisé pour les prédictions
    │   │   │   └── dockerfile : Dockerfile pour le build de l'image streamlit
    │   │   │   └── requirements.txt : packages pour le build de l'image streamlit
    │   │   │   └── streamlit-satisfaction4.py : code python du streamlit
    │   │   │
    │   │── data        <-  recupération des commentaires scrappés depuis l'api
    │   │   │
    │   │── model      <-  contient les éléments du build de l'image docker qui réentraine le modèle via une git action
    │   │   │   └── dockerfile : Dockerfile pour le build de l'image model
    │   │   │   └── requirements.txt : packages pour le build de l'image model
    │   │   │   └── accesKeys.csv : clés de connexion au bucket S3 public contenant la base de donnée de commentaires    
    │   │   │    
    │   │── scrapp    <-  contient les éléments du build de l'image docker qui scrapp les données sur truspilot et les enregistre sur S3 via une git action
    │   │   │   └── scrapping
    │   │   │   │   └── dockerfile : Dockerfile pour le build de l'image scrapping
    │   │   │   │   └── requirements.txt : packages pour le build de l'image scrapping
    │   │   │   │   └── accesKeys.csv : clés de connexion au bucket S3 public contenant la base de donnée de commentaires
    │   │   │   │   └── last30days.py : fichier python correspondant aux scrapp des nouvelles données pour MAJ de la BDD de commentaires
    │   │   │
    │   │── preprocessing   <- contient les éléments du build de l'image docker qui preprocesse les données scrappées depuis S3 via une git action
    │   │   │   └── dockerfile : Dockerfile pour le build de l'image preprocessing
    │   │   │   └── requirements.txt : packages pour le build de l'image preprocessing 
    
    │   │   │
    │   │── test_api          <-  
    │   │   │
    │   │── trainning         <-  
    │   │   │    
    │   │── Makefile          <-
    │   │   │    
    │   │── Docker-compose.yml    <-
    │   │   │        
    │   └── config            <- Describe the parameters used in train_model.py and predict_model.py

--------

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>
