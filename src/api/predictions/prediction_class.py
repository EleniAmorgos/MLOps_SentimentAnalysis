import numpy as np
import pickle
import sklearn
import os


class Predict_Sentiments():
    @staticmethod
    def Predict_Sentiments_DTC(comment):
        vectorizer_path = 'predictions/vect_dtc.pkl'
        model_path = 'predictions/model_dtc.pkl'

        if os.path.exists(vectorizer_path):
            vectorizer_fit = pickle.load(open(vectorizer_path, 'rb'))

            if os.path.exists(model_path):
                model = pickle.load(open(model_path, 'rb'))

                try:
                    pred = model.predict(vectorizer_fit.transform([comment]))[0]
                    proba = model.predict_proba(vectorizer_fit.transform([comment]))[0]

                    result = {
                        "predicted class": int(pred),
                        "probabilité de négatif et positif": list(proba),
                        "message": "Prédiction fonctionnelle"
                    }

                except Exception as e:
                    result = {
                        "predicted class": -1,
                        "probabilité de négatif et positif": [0, 0],
                        "message": f"Erreur inattendue lors de la prédiction : {str(e)}"
                    }

            else:
                result = {
                    "predicted class": -1,
                    "probabilité de négatif et positif": [0, 0],
                    "message": "Erreur: Le modèle est introuvable."
                }

        else:
            result = {
                "predicted class": -1,
                "probabilité de négatif et positif": [0, 0],
                "message": "Erreur: Le vectorizer est introuvable."
            }

        return result

