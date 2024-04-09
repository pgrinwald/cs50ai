import csv
import sys
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier

TEST_SIZE = 0.4


def main():

    # Check command-line arguments
    if len(sys.argv) != 2:
        sys.exit("Usage: python shopping.py data")

    # Load data from spreadsheet and split into train and test sets
    evidence, labels = load_data(sys.argv[1])
    X_train, X_test, y_train, y_test = train_test_split(
        evidence, labels, test_size=TEST_SIZE
    )

    # Train model and make predictions
    model = train_model(X_train, y_train)
    predictions = model.predict(X_test)
    sensitivity, specificity = evaluate(y_test, predictions)

    # Print results
    print(f"Correct: {(y_test == predictions).sum()}")
    print(f"Incorrect: {(y_test != predictions).sum()}")
    print(f"True Positive Rate: {100 * sensitivity:.2f}%")
    print(f"True Negative Rate: {100 * specificity:.2f}%")


## These are my numpy converter funcs (data type=bytes)
def conv_month(col):
    months = {'Jan':0, 'Feb':1, 'Mar':2, 'Apr':3, 'May':4, 'June':5, 'Jul':6, 'Aug':7, 'Sep':8, 'Oct':9, 'Nov':10, 'Dec':11}
    import pdb; pdb.set_trace()
    return int(months[str(col, 'utf-8')])

boolean = lambda x: (int(str(x,'utf-8').lower().capitalize() == "True"))
visitor = lambda x: (int(1) if str(x, 'utf-8') == 'Returning_Visitor' else int(0))

## These are my pandas converter funcs (data type=str)
def conv_months(col):
    months = {'Jan':0, 'Feb':1, 'Mar':2, 'Apr':3, 'May':4, 'June':5, 'Jul':6, 'Aug':7, 'Sep':8, 'Oct':9, 'Nov':10, 'Dec':11}
    return int(months[col])

booleans = lambda x: (int(str(x).lower().capitalize() == "True"))
visitors = lambda x: (int(1) if str(x) == 'Returning_Visitor' else int(0))


def load_data_numpy(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
        - Administrative, an integer
        - Administrative_Duration, a floating point number
        - Informational, an integer
        - Informational_Duration, a floating point number
        - ProductRelated, an integer
        - ProductRelated_Duration, a floating point number
        - BounceRates, a floating point number
        - ExitRates, a floating point number
        - PageValues, a floating point number
        - SpecialDay, a floating point number
        - Month, an index from 0 (January) to 11 (December)
        - OperatingSystems, an integer
        - Browser, an integer
        - Region, an integer
        - TrafficType, an integer
        - VisitorType, an integer 0 (not returning) or 1 (returning)
        - Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """
    evidence = []
    labels = []

    ## Use Numpy to read the data from csv file and convert the column
    ## data into the appropriate numeric values.  Note this returns an
    ## array of tuples.
    ##
    data = np.genfromtxt(filename, delimiter=',', skip_header=1,
            usecols=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17],
            converters={
                    10:conv_month,
                    15:visitor,
                    16:boolean,
                    17:boolean
                    },
            dtype=[
                    ('Administrative',int),
                    ('Administrative_Duration',float),
                    ('Informational',int),
                    ('Informational_Duration',float),
                    ('ProductRelated',int),
                    ('ProductRelated_Duration',float),
                    ('BounceRates',float),
                    ('ExitRates',float),
                    ('PageValues',float),
                    ('SpecialDay',float),
                    ('Month',int),
                    ('OperatingSystems',int),
                    ('Browser',int),
                    ('Region',int),
                    ('TrafficType',int),
                    ('VisitorType',int),
                    ('Weekend',int),
                    ('Revenue',int)
                ])

    ## Now convert the array of tuples into two list of lists: One
    ## for the first 17 columns (evidence) and one for the labels
    ## (column 18)
    ##
    lst=np.array(data).tolist()
    for row in lst:
        l = list(row)
        label = l.pop(len(l)-1)
        evidence.append(l)
        labels.append(label)

    return (evidence, labels)


def load_data(filename):
    """
    Load shopping data from a CSV file `filename` and convert into a list of
    evidence lists and a list of labels. Return a tuple (evidence, labels).

    evidence should be a list of lists, where each list contains the
    following values, in order:
        - Administrative, an integer
        - Administrative_Duration, a floating point number
        - Informational, an integer
        - Informational_Duration, a floating point number
        - ProductRelated, an integer
        - ProductRelated_Duration, a floating point number
        - BounceRates, a floating point number
        - ExitRates, a floating point number
        - PageValues, a floating point number
        - SpecialDay, a floating point number
        - Month, an index from 0 (January) to 11 (December)
        - OperatingSystems, an integer
        - Browser, an integer
        - Region, an integer
        - TrafficType, an integer
        - VisitorType, an integer 0 (not returning) or 1 (returning)
        - Weekend, an integer 0 (if false) or 1 (if true)

    labels should be the corresponding list of labels, where each label
    is 1 if Revenue is true, and 0 otherwise.
    """
    evidence = []
    labels = []
    data = pd.read_csv(filename, header=0,
            usecols=[0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17],
            converters={'Month':conv_months,
                        'VisitorType':visitors,
                        'Weekend':booleans,
                        'Revenue':booleans},
            dtype={
                'Administrative':int,
                'Administrative_Duration':float,
                'Informational':int,
                'Informational_Duration':float,
                'ProductRelated':int,
                'ProductRelated_Duration':float,
                'BounceRates':float,
                'ExitRates':float,
                'PageValues':float,
                'SpecialDay':float,
                'OperatingSystems':int,
                'Browser':int,
                'Region':int,
                'TrafficType':int
            })

    for row in data.itertuples(index=False):
        l = list(row)
        label = l.pop(len(l)-1)
        evidence.append(l)
        labels.append(label)

    return (evidence, labels)


def train_model(evidence, labels):
    """
    Given a list of evidence lists and a list of labels, return a
    fitted k-nearest neighbor model (k=1) trained on the data.
    """
    model = KNeighborsClassifier(n_neighbors=1)
    model.fit(evidence, labels)
    return model


def evaluate(labels, predictions):
    """
    Given a list of actual labels and a list of predicted labels,
    return a tuple (sensitivity, specificity).

    Assume each label is either a 1 (positive) or 0 (negative).

    `sensitivity` should be a floating-point value from 0 to 1
    representing the "true positive rate": the proportion of
    actual positive labels that were accurately identified.

    `specificity` should be a floating-point value from 0 to 1
    representing the "true negative rate": the proportion of
    actual negative labels that were accurately identified.
    """
    tp = 0
    tn = 0
    fp = 0
    fn = 0
    for actual, predicted in zip(labels, predictions):
        if actual == 1 and actual == predicted:
            tp += 1
        elif actual == 1 and actual != predicted:
            fp += 1
        elif actual == 0 and actual == predicted:
            tn += 1
        else:  ## actual == 0 and actual != predicted
            fn += 1
    #import pdb; pdb.set_trace()

    sensitivity = tp / (tp + fp)
    specificity = tn / (tn + fn)
    return (sensitivity, specificity)


if __name__ == "__main__":
    main()


