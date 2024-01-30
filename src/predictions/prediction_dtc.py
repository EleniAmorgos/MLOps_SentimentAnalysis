# -*- coding: utf-8 -*-
"""
Created on Mon Jan  9 00:30:02 2023

@author: t.fourtouill
"""

import numpy as np
import pickle

comment = 'comment transmis par streamlit dans les params'

def predict(comment):
    vectorizer_fit = pickle.load(open('files/vec_dtc.pickle', 'rb'))
    model = pickle.load(open('files/model_dtc.pickle', 'rb'))

    pred = model.predict(vectorizer_fit.transform([comment]))[0]
    
    return ("predicted class:", pred)