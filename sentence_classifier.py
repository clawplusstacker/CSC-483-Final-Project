"""

Text Classification For Dialog Recognition on English and American Corpora

Author: Colby Beach, James Gaskell, Kevin Welch and Kristina Streignitz

We affirm that we have carried out my academic endeavors with full
academic honesty. Colby Beach, James Gaskell, Kevin Welch

"""


from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC

import random
from collections import Counter
import numpy as np

from evaluation import evaluate
import os

# Load data

amerWords = []
my_file = open("spellingList/AmericanSpelling.txt", "r")
data = my_file.read()
amerWords.extend(data.split("\n"))
my_file.close()


britWords = []
my_file = open("spellingList/BritishSpelling.txt", "r")
data = my_file.read()
britWords.extend(data.split("\n"))
my_file.close()

amerSlang = []
my_file = open("slangList/americanSlang.txt", "r")
data = my_file.read()
amerWords.extend(data.split("\n"))
my_file.close()


britSlang = []
my_file = open("slangList/britishSlang.txt", "r")
data = my_file.read()
britWords.extend(data.split("\n"))
my_file.close()


def create_training_and_dev_sets():


    #looping through American data files
    amerSent = []
    directory = os.fsencode("sentenceTrain/America")
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        my_file = open("sentenceTrain/America/" + filename, "r")
        data = my_file.read()
        amerSent.extend(data.split("\n"))
        my_file.close()


    #looping through British data files
    britSent = []
    directory = os.fsencode("sentenceTrain/British")
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        my_file = open("sentenceTrain/British/" + filename, "r")
        data = my_file.read()
        britSent.extend(data.split("\n"))
        my_file.close()


    labels = [1 for sent in amerSent]
    labels += [0 for sent in britSent]


    sentences = []
    sentences.extend(amerSent)
    sentences.extend(britSent)


    # Split into training set and development set
    dev_selection = random.sample(range(0, len(sentences)), 2000)
    dev_reviews = [sentences[i] for i in dev_selection]

    training_reviews = [sentences[i] for i in range(len(sentences)) if i not in dev_selection]

    training_word_counts = Counter([w.lower() for review in training_reviews for w in review])
    vocab = [word_count[0] for word_count in training_word_counts.most_common(2000)]

    training_x = np.array([create_features(r, vocab) for r in training_reviews])
    dev_x = np.array([create_features(r, vocab) for r in dev_reviews])

    training_y = np.array([labels[i] for i in range(len(labels)) if i not in dev_selection])
    dev_y = np.array([labels[i] for i in dev_selection])

    return training_x, training_y, dev_x, dev_y


def create_features(sentence, vocab):
    features = [] 

    #Given feature
    word_counts = Counter(sentence)
    features.extend([int(word_counts[w] > 0) for w in vocab])
    #
    # #If a british or american spelling or slang appears in the sentence
    features.extend(checkSpellings(sentence))
    features.extend(checkSlang(sentence))
    features.extend(finalThree(sentence))
    features.append(checkApostraphes(sentence))
    features.append(checkDoubleChar(sentence))

    return features

# Americans more likely to conjugate words as they are exceedingly dumb
def checkApostraphes(sentence):
    apostrapheCount = 0
    for char in sentence:
        if char == "'":
            apostrapheCount += 1
    return apostrapheCount

# British written words tend to contain more double characters due to differences in pronunciation
def checkDoubleChar(sentence):
    sentence.split(" ")
    doubleCharCount = 0
    for word in sentence:
        for i in range (0, len(word)-1):
            if word[i] == word[i+1]:
                doubleCharCount += 1
    return doubleCharCount


def finalThree(sentence):
    british = 0
    american = 0
    for word in sentence.split():
        finalthree = word[-3:]
        if finalthree == 'our':
            british += 1
        elif finalthree == 'ise':
            british += 1
        elif finalthree == 'ize':
            american += 1
        elif word[-2:] == 'or':
            american += 1

    return [british, american]

def checkSlang(sentence):
    british = 0
    american = 0
    for word in sentence.split():
        if word.title() in amerSlang:
            american += 1
        elif word.title() in britSlang:
            british += 1
    
    return [british, american]

def checkSpellings(sentence):
    
    british = 0
    american = 0

    for word in sentence.split():
        if word.lower() in amerWords:
            american += 1
        elif word.lower() in britWords:
            british += 1
    
    return [british, american]


if __name__ == "__main__":
    # Create training and development/test set
    training_x, training_y, dev_x, dev_y = create_training_and_dev_sets()
    # Train scikit-learn naive Bayes classifier
    clf = SVC()
    clf.fit(training_x, training_y)
    # Evaluate on dev set

    dev_y_predicted = clf.predict(dev_x)

    for i in range(len(dev_y)):
        print("predicted:", dev_y_predicted[i], " actual:", dev_y[i])

    print(evaluate(dev_y_predicted, dev_y))
