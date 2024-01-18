import pandas as pd
from pathlib import Path
import numpy as np 
import matplotlib.pyplot as plt
import tensorflow as tf
import keras

# from sklearn.feature_extraction.text import CountVectorizer
from keras.preprocessing.text import Tokenizer
from keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import load_model
from joblib import dump, load
import pickle

pd.options.display.max_colwidth=800
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)

comment ="J'adore c'est super bien"

