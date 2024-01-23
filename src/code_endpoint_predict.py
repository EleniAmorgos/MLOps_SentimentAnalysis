import tensorflow as tf
print(tf.__version__)
import pickle
from keras.preprocessing.sequence import pad_sequences



# Vectorization du commentaire pour les modèles de Deep Learning
comment_DL = "génial super cool adore aime"

with open('../models/tokenizer/tokenizer.pkl', 'rb') as handle:
    tk = pickle.load(handle)

tk.fit_on_texts(comment_DL)
check_seq = tk.texts_to_sequences([comment_DL])

# # mise sous matrice numpy
max_words = 130
check_pad = pad_sequences(check_seq, maxlen=max_words, padding='post')

            
model = tf.saved_model.load('../models/model_rnn_0_1')


# Print available signatures
print("Available Signatures:")
print(model.signatures)
# Select the serving_default signature
predict_signature = model.signatures["serving_default"]

# Cast the input tensor to float32
check_pad_float32 = tf.constant(check_pad.tolist(), dtype=tf.float32)

# Make predictions
check_predict = predict_signature(embedding_input=check_pad_float32)

# Assuming the model has only one output, use the first key as the output
output_key = list(check_predict.keys())[0]
check_predict_class = check_predict[output_key].numpy().argmax(axis=1)
print(check_predict_class)

if check_predict_class[0] == 1:
    print('le commentaire est positif')
else:
    print('le commentaire est négatif')

