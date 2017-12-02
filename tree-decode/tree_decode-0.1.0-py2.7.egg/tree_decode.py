import numpy as np

from sklearn.preprocessing import normalize as normalize_values
from sklearn.utils.validation import check_is_fitted
from sklearn.tree import DecisionTreeClassifier

__all__ = ["get_tree_info", "get_decision_info"]


def get_tree_info(estimator, normalize=True, precision=3, names=None,
                  label_index=None):
    """
    Print out the structure of a decision tree.

    The print-out will consist of each node and either its leaf-node
    scores OR its decision threshold to determine which path it takes
    subsequently from the fork.

    Parameters
    ----------
    estimator : sklearn.tree.DecisionTreeClassifier
        The decision tree that we are to analyze.
    normalize : bool, default True
        Whether to normalize the label scores at the leaves so that they
        fall into the range [0, 1].
    precision : int or None, default 3
        The decimal precision with which we display our cutoffs and leaf
        scores. If None is passed in, no rounding is performed.
    names : dict, default None
        A mapping from feature indices to string names. By default, when we
        display the non-leaf node forks, we write "go left if feature {i}
        <= {cutoff}," where "i" is an integer. If names are provided, we will
        map "i" to a particular string name and write instead, "go left if
        {feature-name} <= {cutoff}."
    label_index : int, default None
        Whether we want to display the leaf score for a particular label (i.e.
        classification). If an integer is provided, we will index into the
        scores array at each leaf and only display that score. Otherwise, the
        entire scores array will be displayed. Note that labels are 0-indexed.

    Raises
    ------
    NotImplementedError : the estimator was not a DecisionTreeClassifier.
                          Note that this restriction is temporary. Support
                          for other trees is forthcoming.
    IndexError : the label index provided was out of bounds on the array of
                 label scores provided at each node.
    """

    if not isinstance(estimator, DecisionTreeClassifier):
        raise NotImplementedError("get_tree_info is only implemented for "
                                  "DecisionTreeClassifier. Support for "
                                  "other trees is forthcoming.")

    names = names or {}

    check_is_fitted(estimator, "tree_")
    tree = estimator.tree_

    n_nodes = tree.node_count
    children_left = tree.children_left
    children_right = tree.children_right

    features = tree.feature
    thresholds = tree.threshold

    node_depths = np.zeros(shape=n_nodes, dtype=np.int64)
    is_leaves = np.zeros(shape=n_nodes, dtype=bool)

    stack = [(0, -1)]

    while len(stack) > 0:
        node_id, parent_depth = stack.pop()
        node_depths[node_id] = parent_depth + 1

        # Check if we are at a leaf or not.
        if children_left[node_id] != children_right[node_id]:
            stack.append((children_left[node_id], parent_depth + 1))
            stack.append((children_right[node_id], parent_depth + 1))
        else:
            is_leaves[node_id] = True

    print_tab = " " * 5

    previous_leaf = False
    previous_depth = -1

    for i in range(n_nodes):
        node_depth = node_depths[i]
        tabbing = node_depth * print_tab

        if is_leaves[i]:
            if previous_leaf:
                if previous_depth > 0 and previous_depth > node_depth:
                    print("")  # Readability

            probs = tree.value[i][:]

            if normalize:
                probs = normalize_values(probs, norm="l1")

            if precision is not None:
                probs = probs.round(precision)

            if label_index is not None:
                try:
                    prob = probs[0][label_index]
                    score = "score = {score}".format(score=prob)
                except IndexError:
                    msg = ("Index {label_index} is out of bounds on a "
                           "decision tree with {n} possible labels")
                    prob_counts = probs.shape[1]

                    raise IndexError(msg.format(n=prob_counts,
                                                label_index=label_index))
            else:
                score = "scores = {scores}".format(scores=probs)

            leaf_info = "{tabbing}node={label} left node: {score}"
            print(leaf_info.format(tabbing=tabbing, label=i, score=score))

            previous_depth = node_depth
            previous_leaf = True
        else:
            if previous_leaf:
                previous_leaf = False
                print("")  # Readability

            feature = features[i]
            threshold = thresholds[i]
            cutoff = (threshold if precision is None
                      else round(threshold, precision))

            default = "feature {name}".format(name=feature)
            name = names.get(feature, default)

            node_info = ("{tabbing}node={label}: go to node {left} if "
                         "{name} <= {cutoff} else to node {right}.")
            print(node_info.format(tabbing=tabbing, label=i,
                                   left=children_left[i],
                                   name=name, cutoff=cutoff,
                                   right=children_right[i]))


def get_decision_info(estimator, data, precision=3, names=None):
    """
    Get the decision process for a tree on a piece of data.

    Parameters
    ----------
    estimator : sklearn.tree.DecisionTreeClassifier
        The decision tree that we are to analyze.
    data : np.ndarray
        A 2-D array compromising ONE piece of input data.
    precision : int or None, default 3
        The decimal precision with which we display our cutoffs and leaf
        scores. If None is passed in, no rounding is performed.
    names : dict, default None
        A mapping from feature indices to string names. By default, when we
        display the non-leaf node forks, we write something liek "Feature {i}
        Score <= {cutoff}," where "i" is an integer. If names are provided,
        we will map "i" to a particular string name and write instead,
        "{feature-name} <= {cutoff}."

    Raises
    ------
    NotImplementedError : the estimator was not a DecisionTreeClassifier.
                          Note that this restriction is temporary. Support
                          for other trees is forthcoming.
    """

    if not isinstance(estimator, DecisionTreeClassifier):
        raise NotImplementedError("get_tree_info is only implemented for "
                                  "DecisionTreeClassifier. Support for "
                                  "other trees is forthcoming.")

    names = names or {}
    check_is_fitted(estimator, "tree_")

    node_indicator = estimator.decision_path(data)
    node_index = node_indicator.indices[node_indicator.indptr[0]:
                                        node_indicator.indptr[1]]

    probs = estimator.predict_proba(data)[0]
    probs = probs.round(precision) if precision is not None else probs

    tree = estimator.tree_
    features = tree.feature
    thresholds = tree.threshold

    output = "Decision Path for Tree:\n"
    leaf_id = estimator.apply(data)

    for node_id in node_index:
        if leaf_id[0] != node_id:
            feature = features[node_id]
            feature_score = data[0, feature]
            feature_threshold = thresholds[node_id]

            default = "Feature {name} Score".format(name=feature)
            name = names.get(feature, default)

            if feature_score <= thresholds[node_id]:
                threshold_sign = "<="
            else:
                threshold_sign = ">"

            if precision is not None:
                feature_score = round(feature_score, precision)
                feature_threshold = round(feature_threshold, precision)

            output += ("    Decision ID Node {node_id} : {name} = "
                       "{score} {sign} {threshold}\n".format(
                        node_id=node_id, score=feature_score, name=name,
                        sign=threshold_sign, threshold=feature_threshold))
        else:
            output += ("    Decision ID Node {node_id} : "
                       "Scores = {scores}".format(node_id=node_id,
                                                  scores=probs))
    print(output)


def demo():
    from sklearn.model_selection import train_test_split
    from sklearn.datasets import load_iris

    iris = load_iris()
    y = iris.target
    x = iris.data

    x_train, x_test, y_train, y_test = train_test_split(x, y, random_state=0)
    estimator = DecisionTreeClassifier(max_leaf_nodes=3, random_state=0)

    estimator.fit(x_train, y_train)
    get_tree_info(estimator)
    print("")

    names = {0: "Sepal Length", 1: "Sepal Width",
             2: "Petal Length", 3: "Petal Width"}
    get_tree_info(estimator, names=names)
    print("")

    get_tree_info(estimator, precision=None)
    print("")

    get_tree_info(estimator, normalize=False)
    print("")

    get_tree_info(estimator, label_index=2)
    print("")

    index = 1
    data = x_test[[index]]
    print("Analyzing: " + str(data) + "\n")

    get_decision_info(estimator, data)
    print("")

    index = 2
    data = x_test[[index]]
    print("Analyzing: " + str(data) + "\n")

    get_decision_info(estimator, data, precision=None)
    print("")

    index = 3
    data = x_test[[index]]
    print("Analyzing: " + str(data) + "\n")

    get_decision_info(estimator, data, names=names)
    print("")


if __name__ == "__main__":
    demo()
