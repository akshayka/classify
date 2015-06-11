'''

Logistic Regression

Training, test data format:
[ [ TEXT, LIKERT_SCORE] ... [TEXT, LIKERT_SCORE]

TODO: docs and docs and docs

'''
import clf_util
import numpy as np
from sklearn_clf import SklearnCLF
from sklearn.linear_model import LogisticRegression


class LogRegression(SklearnCLF):
    def __init__(self, token_pattern=r'(?u)\b\w\w+\b',
                 text_only=False,
                 no_text=False,
                 tfidf=False,
                 C=1.0,
                 reduce_features=False,
                 k_best_features=0):
        super(LogRegression, self).__init__(token_pattern=token_pattern,
                                            text_only=text_only,
                                            no_text=no_text ,
                                            tfidf=tfidf,
                                            reduce_features=reduce_features,
                                            k_best_features=k_best_features)
        self.binary_counts = True
        self.C = C
        self.name = 'LogisticRegression ' + self.name
        self.make_clf(LogisticRegression(C=self.C))


    def train(self, X, y):
        self.clf.fit(X, y)


    def cross_validate(self, X, y, labels):
        return clf_util.sklearn_cv(self.clf, X, y, labels)