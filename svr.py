#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 12 01:54:14 2021

@author: jimmytabet
"""

# imports
from sklearn.datasets import make_regression # generates example dataset
from sklearn.model_selection import train_test_split # splits data into train/test
from sklearn.svm import SVR # Support Vector Regression - regression model we will use
from sklearn.metrics import mean_squared_error # used to evaluate model performance

# generate example data: 100 samples with 10 features/inputs and 1 target/output 
# X: array of features (100 rows x 10 columns)
# y: array of outputs (100 rows x  1 column)
X, y = make_regression(n_samples = 100, n_features = 10, n_targets = 1)

# split data into train (75% = 75 samples) and test (25% = 25 samples) sets
# train data is used to ...train the model
# test data is withheld from training so we can ...test (evaluate) the model
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = 0.25)

# initialize SVR model, parameters (kernel, C, etc.) can be tuned to improve model
svr = SVR(kernel='rbf', C=100)

# fit SVR using training data only
svr.fit(X_train, y_train)

# use fitted/"trained" SVR to predict output on training data
y_train_pred = svr.predict(X_train)

# use fitted/"trained" SVR to predict output on test data
y_test_pred = svr.predict(X_test)

# use metrics to see how we did
'''
Our thought process here is that the training metrics should be better than the
test metrics since the model was fitted on the training data. Essentially the
model only saw the training examples when learning how to make the prediction.
It has never seen the test samples, so it will not do as well, but if the model
parameters are tuned correctly, it should still perform well on this new data -
the model will have learned how to make predictions.

R2 score: "goodness of fit" (perfect fit = 1.0)
mean squared error (MSE): average squared error between data points
root mean squared error (RMSE): just take square root so the error value is
                                comparable to the target values
'''
# TRAINING METRICS
train_R2score = svr.score(X_train, y_train)
train_MSE = mean_squared_error(y_train, y_train_pred)
train_RMSE = mean_squared_error(y_train, y_train_pred, squared=False)
 
print('TRAIN R2:', train_R2score)
print('TRAIN MSE:', train_MSE)
print('TRAIN RMSE:', train_RMSE)

# TEST METRICS
test_R2score = svr.score(X_test, y_test)
test_MSE = mean_squared_error(y_test, y_test_pred)
test_RMSE = mean_squared_error(y_test, y_test_pred, squared=False)

print()
print('TEST R2:', test_R2score)
print('TEST MSE:', test_MSE)
print('TEST RMSE:', test_RMSE)

'''
The train/test split is stochastic so if you run this file multiple times you'll
get different results, but generally train R2 will be higher than test R2 (the
model fit the training data better) and train RMSE will be lower than test RMSE
(the model has a lower error on the training data). There are a bunch of other
things we can do to improve our results (scale our data before fitting the SVR,
tune the model parameters, use a different model, etc.) but this gives you an
idea of the machine learning workflow.
'''