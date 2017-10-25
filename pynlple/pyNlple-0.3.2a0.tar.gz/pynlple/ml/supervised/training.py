import numpy as np
import pandas as pd
from sklearn.cross_validation import KFold, StratifiedKFold, cross_val_score
from sklearn import metrics


def cross_validation_training(data, pipeline, n_folds=6, verbose=False):
    # Partitioning a sample of data into complementary subsets for CrossValidation
    k_fold = KFold(n=len(data), n_folds=n_folds, shuffle=True)

    precision, recall = [], []
    confusion = np.array([[0, 0], [0, 0]])

    results = {
        'text': [], 'golden': [], 'predicted': [], 'p1': []
    }

    for train_indices, test_indices in k_fold:
        # Prepare training data
        train_text = data.iloc[train_indices]['Contents'].values
        train_y = data.iloc[train_indices]['Registered'].values

        # Prepare test data
        test_text = data.iloc[test_indices]['Contents'].values
        test_y = data.iloc[test_indices]['Registered'].values

        # Train the model
        pipeline.fit(train_text, train_y)

        # Make predictions
        in_training = set(train_text)
        old_t, old_y = [], []
        new_t, new_y = [], []
        for tt, ty in zip(test_text, test_y):
            if tt in in_training:
                old_t.append(tt)
                old_y.append(ty)
            else:
                new_t.append(tt)
                new_y.append(ty)
        if verbose:
            print('%d out of %d are from training' % (len(old_y), len(test_y)))
            tuples = [(np.array(new_t), np.array(new_y)),
                      (np.array(old_t), np.array(old_y))]
        else:
            tuples = [(np.array(new_t), np.array(new_y))]

        for i, (ttext, ty) in enumerate(tuples):
            predictions = pipeline.predict(ttext)
            prob = pipeline.predict_proba(ttext)
            if verbose:
                print(np.mean(predictions == ty))
            if i == 0:
                # Calculate precision and confusion matrix
                confusion += metrics.confusion_matrix(ty, predictions)
                precision.append(metrics.precision_score(ty, predictions))
                recall.append(metrics.recall_score(ty, predictions))

                results['text'] += ttext.tolist()
                results['golden'] += ty.tolist()
                results['predicted'] += predictions.tolist()
                results['p1'] += prob[:, 1].tolist()

    precision, recall = np.array(precision), np.array(recall)
    print("Precision: %0.3f (+/- %0.3f)" % (precision.mean(), precision.std() * 2))
    print("Recall: %0.3f (+/- %0.3f)" % (recall.mean(), recall.std() * 2))
    if verbose:
        print('Confusion matrix:')
        print(confusion)

    # Check predictions
    results = pd.DataFrame(results)
    return results
