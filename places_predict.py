# -*- coding: utf-8 -*-
"""Places_predict.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/19LcQ3NNmu-oQDCduSebR3w5SqWBNQmcm
"""

import math, os
import numpy as np
import keras
from keras.layers import Dropout, Flatten, BatchNormalization
from keras.callbacks import EarlyStopping, ModelCheckpoint
from keras.layers import Dense
from keras.models import Model, Sequential
from keras.optimizers import Adam
from keras.preprocessing import image


PATH = os.getcwd()
# Define data path
DATASET_DIR = PATH + '/my_training_data'

SIZE = (224, 224)
BATCH_SIZE = 16
VALIDATION_SPLIT = 0.3
IMG_SIZE = ( 224, 224, 3)

# How many data and classes ..
num_dataset_samples = sum([len(files) for r, d, files in os.walk(DATASET_DIR)])

num_train_steps = math.floor((num_dataset_samples*(1-VALIDATION_SPLIT))/BATCH_SIZE)
num_valid_steps = math.floor((num_dataset_samples*VALIDATION_SPLIT)/BATCH_SIZE)

generator = image.ImageDataGenerator(validation_split=VALIDATION_SPLIT)

batches = generator.flow_from_directory(DATASET_DIR, subset='training', target_size=SIZE, class_mode='categorical', shuffle=True, batch_size=BATCH_SIZE)
val_batches = generator.flow_from_directory(DATASET_DIR, subset='validation', target_size=SIZE, class_mode='categorical', shuffle=True, batch_size=BATCH_SIZE)

#  Let's use mobilenet as it is simple and needs less memory
model = keras.applications.mobilenet_v2.MobileNetV2(input_shape=(224, 224, 3),  include_top=False, weights='imagenet')

# No of classes
classes = list(iter(batches.class_indices))

# Our Model starts
x = Sequential()
x.add(model)
x.add(Flatten())
x.add(Dense(16, activation='relu'))
x.add(Dropout(0.5))
x.add(BatchNormalization())
# predictions = Dense(num_classes, activation = 'softmax')(x)
x.add(Dense(len(classes), activation="softmax"))

# Compile
x.compile(optimizer=Adam(lr=0.0001), loss='categorical_crossentropy', metrics=['accuracy'])

# Let's keep on csv file... 
for c in batches.class_indices:
    classes[batches.class_indices[c]] = c
x.classes = classes
filename='model_train_new.csv'
csv_log=keras.callbacks.CSVLogger(filename, separator=',', append=False)

# Early stopping if loss doesnt improve
early_stopping = EarlyStopping(patience=10)
checkpointer = ModelCheckpoint('resnet_best.h5', verbose=1, save_best_only=True)

tensorboard_callback = keras.callbacks.TensorBoard(log_dir='./logs', histogram_freq=0, batch_size=BATCH_SIZE, write_graph=True, write_grads=False, write_images=False, embeddings_freq=0, embeddings_layer_names=None, embeddings_metadata=None)

# Fit and save
x.fit_generator(batches, steps_per_epoch=num_train_steps, epochs=8, callbacks=[early_stopping, checkpointer, tensorboard_callback, csv_log], validation_data=val_batches, validation_steps=num_valid_steps)
x.save('resnet_final.h5')

scoreSeg = x.evaluate_generator(val_batches, num_dataset_samples*VALIDATION_SPLIT )
print("Accuracy = ",scoreSeg[1])

# pip install tensorflow==1.13.0rc1  as you may get error if u do with other versions of tensorflow!

# Converting to .tflite
model_path = '/gdrive/My Drive/Places/resnet_best.h5'
from tensorflow import lite
converter = lite.TFLiteConverter.from_keras_model_file(model_path) 
tfmodel = converter.convert() 

open ("yes.tflite" , "wb") .write(tfmodel)