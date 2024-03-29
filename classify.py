from typing import Iterator, Iterable, Tuple, Text, Union

import numpy as np
from scipy.sparse import spmatrix

NDArray = Union[np.ndarray, spmatrix]


def read_smsspam(smsspam_path: str) -> Iterator[Tuple[Text, Text]]:
    """Generates (label, text) tuples from the lines in an SMSSpam file.

    SMSSpam files contain one message per line. Each line is composed of a label
    (ham or spam), a tab character, and the text of the SMS. Here are some
    examples:

      spam	85233 FREE>Ringtone!Reply REAL
      ham	I can take you at like noon
      ham	Where is it. Is there any opening for mca.

    :param smsspam_path: The path of an SMSSpam file, formatted as above.
    :return: An iterator over (label, text) tuples.
    """
    TexLab = []
    with open(smsspam_path) as f:
        for line in f:
            line = line.strip().split("\t")
            label = line[0]
            text = line[1]
            TexLab.append((label, text))
    
    return iter(TexLab)

from sklearn.feature_extraction.text import CountVectorizer

class TextToFeatures:
    def __init__(self, texts: Iterable[Text]):
        """Initializes an object for converting texts to features.

        During initialization, the provided training texts are analyzed to
        determine the vocabulary, i.e., all feature values that the converter
        will support. Each such feature value will be associated with a unique
        integer index that may later be accessed via the .index() method.

        It is up to the implementer exactly what features to produce from a
        text, but the features will always include some single words and some
        multi-word expressions (e.g., "need" and "to you").

        :param texts: The training texts.
        """
        self.vec = CountVectorizer(analyzer = 'char', ngram_range=(1, 6))
       # self.X = self.vec.fit_transform(texts)
        self.vec.fit(texts)
        
    def index(self, feature: Text):
        """Returns the index in the vocabulary of the given feature value.

        :param feature: A feature
        :return: The unique integer index associated with the feature.
        """
        #n = self.vec.get_feature_names().index(feature)
        n = self.vec.vocabulary_[feature]

        return n

    def __call__(self, texts: Iterable[Text]) -> NDArray:
        """Creates a feature matrix from a sequence of texts.

        Each row of the matrix corresponds to one of the input texts. The value
        at index j of row i is the value in the ith text of the feature
        associated with the unique integer j.

        It is up to the implementer what the value of a feature that is present
        in a text should be, though a common choice is 1. Features that are
        absent from a text will have the value 0.

        :param texts: A sequence of texts.
        :return: A matrix, with one row of feature values for each text.
        """
        x = self.vec.transform(texts)
        return x

from sklearn import preprocessing

class TextToLabels:
    def __init__(self, labels: Iterable[Text]):
        """Initializes an object for converting texts to labels.

        During initialization, the provided training labels are analyzed to
        determine the vocabulary, i.e., all labels that the converter will
        support. Each such label will be associated with a unique integer index
        that may later be accessed via the .index() method.

        :param labels: The training labels.
        """
        self.le = preprocessing.LabelEncoder()
        self.le.fit(labels)

    def index(self, label: Text) -> int:
        """Returns the index in the vocabulary of the given label.

        :param label: A label
        :return: The unique integer index associated with the label.
        """
        #pam = list(self.le.classes_).index(label)
        pam = self.le.transform([label])[0]

        return pam

    def __call__(self, labels: Iterable[Text]) -> NDArray:
        """Creates a label vector from a sequence of labels.

        Each entry in the vector corresponds to one of the input labels. The
        value at index j is the unique integer associated with the jth label.

        :param labels: A sequence of labels.
        :return: A vector, with one entry for each label.
        """
        x = self.le.transform(labels)
        return x

from sklearn.linear_model import LogisticRegression

class Classifier:
    def __init__(self):
        """Initalizes a logistic regression classifier.
        """
        self.clf = LogisticRegression(penalty = 'l1', solver = 'liblinear', C = 1.5)


    def train(self, features: NDArray, labels: NDArray) -> None:
        """Trains the classifier using the given training examples.

        :param features: A feature matrix, where each row represents a text.
        Such matrices will typically be generated via TextToFeatures.
        :param labels: A label vector, where each entry represents a label.
        Such vectors will typically be generated via TextToLabels.
        """
        self.clf.fit(features, labels)

    def predict(self, features: NDArray) -> NDArray:
        """Makes predictions for each of the given examples.

        :param features: A feature matrix, where each row represents a text.
        Such matrices will typically be generated via TextToFeatures.
        :return: A prediction vector, where each entry represents a label.
        """
        pred = self.clf.predict(features)
        return pred
