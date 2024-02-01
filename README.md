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
    │   │   │   └── users_data.json : user data base    │   │
    │   │   ├── data           <- Scripts to download or generate data
    │   │   │   └── web_scrapping.py : Scraps comments from Trustpilot
    │   │   │
    │   │   ├── features       <- Scripts to turn raw data into features for modeling
    │   │   │   └── build_features.py : Processes and archives the comments (new comments into histo)
    │   │   │
    │   │   ├── predictions         <- Scripts using trained models to make predictions
    │   │   │   │                 
    │   │   │   ├── prediction_class.py
    │   │   │
    │   │── Streamlit
        
    │   └── config         <- Describe the parameters used in train_model.py and predict_model.py

--------

<p><small>Project based on the <a target="_blank" href="https://drivendata.github.io/cookiecutter-data-science/">cookiecutter data science project template</a>. #cookiecutterdatascience</small></p>
