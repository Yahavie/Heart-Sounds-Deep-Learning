#This classifier is going to be used as a benchmark, sort of like a control to compare my other models
#This model randomly chooses an output class based on the frequency of "abnormal" and "normal" entries in the
#Training data, in fact it doesn't even look at the feature data!

from sklearn.dummy import DummyClassifier
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

#retrieving the X and Y data stored as .npy files with pickle
pickle_filepath_X = "/Users/sreeharirammohan/Desktop/MFCCs_Data.npy"
pickle_filepath_Y = "/Users/sreeharirammohan/Desktop/MFCC_Labels.npy"

pickle_filepath_X_pi = "/media/pi/3577-249A/MFCCs_Data.npy"
pickle_filepath_Y_pi = "/media/pi/3577-249A/MFCC_Labels.npy"

USING_RASPBERRY_PI = False

if USING_RASPBERRY_PI:
    pickle_filepath_X = pickle_filepath_X_pi
    pickle_filepath_Y = pickle_filepath_Y_pi



print("Retrieving X and Y training data")
y = np.load(pickle_filepath_Y)
print("Loaded Y data")
X = np.load(pickle_filepath_X)

'''
Fix the dimensionality of the dataset, since sklearn can only take 2 dimensions
'''
nsamples, nx, ny = X.shape
X_2 = X.reshape((nsamples,nx*ny))
print(X_2.shape)

# Splitting the dataset into the Training set and Test set
from sklearn.cross_validation import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X_2, y, test_size = 0.2, random_state = 0)

# Fitting Dummy Classifier to the Training set
from sklearn.dummy import DummyClassifier
dummy_classifier = DummyClassifier(strategy="uniform")
dummy_classifier.fit(X_train, y_train)

# Predicting the Test set results
print(X_test.shape)

print("----------starting 5 time average benchmark----------")
times = []
import time
for i in range(0, 5):
    start = time.clock()
    y_pred = dummy_classifier.predict(X_test)
    time_taken = time.clock() - start
    times.append(time_taken)
    print("On iteration " + str(i + 1) + " time taken was " + str(time_taken))
print("DONE WITH 5 TESTS")
print(times)
import statistics as s
print("Average time = " + str(s.mean(times)))
print("----------ending time benchmark----------")


print(y_pred.shape)
#creating basic confusion matrix
from sklearn.metrics import confusion_matrix
cm = confusion_matrix(y_test, y_pred)
print(cm)

#Getting the basic validated accuracy of the dummy classifier
accuracy = dummy_classifier.score(X_test, y_test)
print("Accuracy is " + str(accuracy*100) + "%")



print("---------------ROC / AUC / Frequency---------------")

from sklearn.metrics import *
#store predicted probabilities for class 1
y_pred_prob = dummy_classifier.predict_proba(X_test)[:, 1]


'''
Plotting a histogram of predicted probabilities
'''
# histogram of predicted probabilities
plt.hist(y_pred_prob, bins=8)
plt.xlim(0, 1)
plt.title('Histogram of predicted probabilities')
plt.xlabel('Predicted probability of diabetes')
plt.ylabel('Frequency')
plt.show()



'''
Basic example of plotting ROC curve

ROC shows sensitivity vs (1-specificity) for all possible classification
thresholds from 0-1

'''

fpr, tpr, thresholds = roc_curve(y_test, y_pred_prob)
plt.plot(fpr, tpr)
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.0])
plt.title('ROC curve for diabetes classifier')
plt.xlabel('False Positive Rate (1 - Specificity)')
plt.ylabel('True Positive Rate (Sensitivity)')
plt.grid(True)
plt.show()


def evaluate_threshold(threshold, tpr, fpr):
    print("senitivity: " + str(tpr[threshold > threshold][-1]))
    print("Specificity " + str(float(1 - fpr[threshold > threshold][-1])))


'''
AUC is the area under the ROC curve

A higher AUC score is a better classifier

Used as single number summary of performance of classifier

best possible AUC is 1

AUC is useful even when there is a high class imbalance

'''

# IMPORTANT: first argument is true values, second argument is predicted probabilities
print(roc_auc_score(y_test, y_pred_prob))

# calculate cross-validated AUC
from sklearn.cross_validation import cross_val_score
print(cross_val_score(dummy_classifier, X_2, y, cv=10, scoring='roc_auc').mean())