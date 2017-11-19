from ..tools.data import get_from_csv, split_4_to_1


def load_lin_separate(num=17):

    path = 'linear_separable/data%s.csv' % str(num)
    train, test = get_from_csv(path)

    X_train, d_train, X_test, d_test = split_4_to_1(train, test)

    return X_train, d_train, X_test, d_test
