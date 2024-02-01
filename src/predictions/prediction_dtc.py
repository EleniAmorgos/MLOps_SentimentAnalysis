# -*- coding: utf-8 -*-
"""
Created on Mon Jan  9 00:30:02 2023

@author: t.fourtouill
"""

import numpy as np
import pickle
import sklearn

comment = 'comment transmis par streamlit'

def predict(comment):
    vectorizer_fit = pickle.load(open('files/vect_dtc.pkl', 'rb'))
    model = pickle.load(open('files/model_dtc.pkl', 'rb'))

    pred = model.predict(vectorizer_fit.transform([comment]))[0]
    proba = model.predict_proba(vectorizer_fit.transform([comment]))[0]

    return ("predicted class:", pred, 'probabilité de négatif et positif:', proba)