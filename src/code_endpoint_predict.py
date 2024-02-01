import numpy as np
import pickle
import sklearn
print(sklearn.__version__)




# Vectorization du commentaire pour les modèles de Deep Learning
comment_DL = "génial super cool adore aime"
def predict(comment):
    vectorizer_fit = pickle.load(open('model/src/vect_dtc.pkl', 'rb'))
    model = pickle.load(open('model/src/model_dtc.pkl', 'rb'))
    pred = model.predict(vectorizer_fit.transform([comment]))[0]
    proba = model.predict_proba(vectorizer_fit.transform([comment]))[0]
    return ("predicted class:", pred, 'probabilité de négatif et positif:', proba)


print(predict(comment_DL))