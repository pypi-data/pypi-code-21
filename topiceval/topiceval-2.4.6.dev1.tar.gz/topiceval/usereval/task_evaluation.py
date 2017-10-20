from __future__ import print_function
from __future__ import division

from topiceval.stats import hellinger_distance, cosine_similarity_unnormed_vecs
from topiceval import utils
from topiceval.preprocessing import textcleaning
from topiceval.preprocessing import emailsprocess

import numpy as np
from sklearn.model_selection import GridSearchCV
from sklearn.svm import LinearSVC
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split
from sklearn.cluster import DBSCAN
from sklearn import metrics
# from sklearn.decomposition import PCA
from sklearn.metrics import precision_recall_curve
from sklearn.metrics import average_precision_score
from sklearn.metrics import precision_recall_fscore_support
from prettytable import PrettyTable
import scipy.sparse.linalg
from scipy.stats import pearsonr

import operator
import six
import logging

import matplotlib

matplotlib.use("Qt5Agg", force=True)
# import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)

EPS = 1e-3


def modified_jaccard_similarity(set1, set2):
    return len(set1 & set2) / (len(set1) + EPS)


def get_average_precision(y_true, y_pred):
    """
    :param y_true: set, of relevant items
    :param y_pred: list, ranked order of retrieved items
    :return: Average Precision
    """
    N = len(y_true)
    if N == 0:
        return 1.
    s = 0.
    tp = 0
    for i, y in enumerate(y_pred):
        if y in y_true:
            tp += 1
            s += tp / float(i + 1)
    return s / float(N)


def reorder(X_train, X_test, y_train, y_test):
    assert len(X_train) == len(y_train) and len(X_test) == len(y_test)
    order = np.random.choice(len(X_train), len(X_train), replace=False)
    X_train = [X_train[i] for i in order]
    y_train = [y_train[i] for i in order]
    order = np.random.choice(len(X_test), len(X_test), replace=False)
    X_test = [X_test[i] for i in order]
    y_test = [y_test[i] for i in order]
    return X_train, X_test, y_train, y_test


def folder_task_data_split(X, y):
    test_split = 0.25

    X_train, X_test, y_train, y_test = [], [], [], []
    if len(y) == 0:
        return X_train, X_test, y_train, y_test

    current_folder = y[0]
    current_idc = [0]
    itr = 1
    while True:
        while itr < len(y) and y[itr] == current_folder:
            current_idc.append(itr)
            itr += 1
        X_train += [X[idx] for idx in current_idc[int(test_split * len(current_idc)):]]
        X_test += [X[idx] for idx in current_idc[:int(test_split * len(current_idc))]]
        y_train += [current_folder] * (len(current_idc) - int(test_split * len(current_idc)))
        y_test += [current_folder] * int(test_split * len(current_idc))
        if itr == len(y):
            break
        else:
            current_folder = y[itr]
            current_idc = []
    return X_train, X_test, y_train, y_test


def folder_task_data_prep(email_network):
    # total_custom_mails = 0
    # for key, idc in email_network.folders_idc_dict.items():
    #     total_custom_mails += len(idc)
    # U = total_custom_mails / (len(email_network.folders_idc_dict) + EPS)
    # retained_folders = set()
    # for key, idc in email_network.folders_idc_dict.items():
    #     if len(idc) >= int(U / 4):
    #         retained_folders.add(key)

    X, y = [], []
    for folder in email_network.big_folders:
        idc = email_network.folders_idc_dict[folder]
        X += idc
        y += [folder] * len(idc)
    # X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42, stratify=y)
    X_train, X_test, y_train, y_test = folder_task_data_split(X, y)
    X_train, X_test, y_train, y_test = reorder(X_train, X_test, y_train, y_test)
    logger.info("Folder Clf Task: train %d | test %d" % (len(y_train), len(y_test)))
    return X_train, X_test, y_train, y_test


def reply_task_data_prep(email_network):
    df = email_network.df
    username = email_network.username
    X, y = [], []
    for idx, row in df.iterrows():
        if row["SenderName"] != username and row["FolderType"] != "Sent Items":
            X.append(row["idx"])
            if row["replied"]:
                y.append(1)
            else:
                y.append(0)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42, stratify=y)
    X_train, X_test, y_train, y_test = reorder(X_train, X_test, y_train, y_test)
    logger.info("Reply Task: train %d | test %d" % (len(y_train), len(y_test)))
    return X_train, X_test, y_train, y_test


def receiver_task_data_prep(email_network):
    test_split = 0.25
    keep_unseen_addrs = True

    df = email_network.df
    df_sent = df[(df["FolderType"] == "Sent Items") & (df["SenderName"] == email_network.username)]
    df_sent = df_sent[~(df_sent["Subject"].str.contains("RE:"))]
    df_sent = df_sent[~(df_sent["Subject"].str.contains("Re:"))]
    # df_sent = df_sent.sort_values(by='SentOn', ascending=False)

    nsent_mails = df_sent.shape[0]
    # ntrain = int(split * nsent_mails)
    ntest = int(test_split * nsent_mails)
    df_train = df_sent[ntest:]
    X_train = [idx for idx in df_train["idx"]]
    susers = set()
    y_train = []
    for addrs in df_train["to_cc_bcc"]:
        y = []
        addrs = [addr for addr in addrs.strip().split(';') if addr != '']
        for addr in addrs:
            y.append(addr)
            susers.add(addr)
        y_train += [y]

    if len(susers) < 10:
        logger.info("Aborting receiver recommendation task, not enough sent_users")
        return -1
    else:
        logger.info("Number of sent_users: %d" % len(susers))

    df_test = df_sent[:ntest]
    y_test = []

    if keep_unseen_addrs:
        for addrs in df_test["to_cc_bcc"]:
            y = []
            addrs = [addr for addr in addrs.strip().split(';') if addr != '']
            for addr in addrs:
                y.append(addr)
            y_test += [y]
    # Removing mails for which all recipients are unseen wrt train data
    else:
        bool_indices = []
        for idx, addrs in enumerate(df_test["to_cc_bcc"]):
            y = []
            addrs = [addr for addr in addrs.strip().split(';') if addr != '']
            absent_user_flag = True
            for addr in addrs:
                if addr in susers:
                    absent_user_flag = False
                    break
            if absent_user_flag:
                bool_indices.append(False)
            else:
                bool_indices.append(True)
                for addr in addrs:
                    if addr in susers:
                        y.append(addr)
                y_test += [y]

        df_test = df_test[bool_indices]

    X_test = [idx for idx in df_test["idx"]]
    X_train, X_test, y_train, y_test = reorder(X_train, X_test, y_train, y_test)

    # X_train += X_train
    # X_test += X_test
    # y_train += y_train
    # y_test += y_test

    user_addrs = list(email_network.sent_to_users | email_network.cc_to_users)

    logger.info("Receiver Task: Train %d || Test %d" % (len(y_train), len(y_test)))
    return X_train, X_test, y_train, y_test, user_addrs, df_train


def subject_task_data_prep(email_network):
    test_split = 0.25

    df = email_network.df
    vocab = email_network.vocab_set

    df = df[(df["FolderType"] == "Sent Items") & (df["SenderName"] == email_network.username)]
    df = df[~df["Subject"].str.contains("RE:")]
    df = df[~df["Subject"].str.contains("Re:")]
    df = df[~df["Subject"].str.contains("FWD:")]
    df = df[~df["Subject"].str.contains("Fwd:")]

    X, y = [], []
    for idx, row in df[["idx", "Subject"]].iterrows():
        sub = row[1].strip()
        sub = textcleaning.clean_text(sub)
        sub = textcleaning.remove_stops(sub, stop=emailsprocess.load_stops())
        words_in_vocab = []
        for word in sub.split():
            if word in vocab:
                words_in_vocab.append(word)
        if len(words_in_vocab) > 0:
            X.append(row[0])
            y += [set(words_in_vocab)]

    ntest = int(test_split * len(X))
    X_train = X[ntest:]
    y_train = y[ntest:]
    X_test = X[:ntest]
    y_test = y[:ntest]

    subject_word_dict = {}
    for idx, sub in enumerate(y_train):
        for w in sub:
            try:
                subject_word_dict[w].append(X_train[idx])
            except KeyError:
                subject_word_dict[w] = [X_train[idx]]

    logger.info("Subject Task: Train: %d, Test: %d" % (len(y_train), len(y_test)))
    # print(subject_word_dict)
    return X_train, y_train, X_test, y_test, subject_word_dict, df


def new_folder_task_data_prep(df):
    df = df[df["FolderType"] == "Inbox"]
    X = [idx for idx in df["idx"]]
    return X


def collapsed_folder_prediction_task(df, email_network, model, num_topics, folder, min_folder_size):
    df_folder = df[df['FolderType'] == folder]
    df_new = df[(df['FolderType'] == "Inbox") | (df['FolderType'] == folder)]
    X = [idx for idx in df_new["idx"]]

    predicted_idc = new_folder_prediction_task(X, model, num_topics, df_new,
                                               email_network, model.document_topic_matrix,
                                               min_folder_size=min_folder_size,
                                               called_by_collapsed=True)

    true_idc = set([idx for idx in df_folder["idx"]])

    # precisions = []
    # noinspection PyTypeChecker
    # for predicted_idc in predicted_idcs:
    predicted_idc_set = set(predicted_idc)
    precision = len(predicted_idc_set & true_idc) / (len(predicted_idc_set) + EPS)
    # precisions.append(precision)
    # return max(precisions)
    return precision
    # jsims = []
    # # noinspection PyTypeChecker
    # for predicted_idc in predicted_idcs:
    #     # print(predicted_idc)
    #     jsims.append(min(1.0, modified_jaccard_similarity(set(predicted_idc), true_idc) + 0.05))
    # # logger.info("Modified Jaccard Sim for folder: %s is %0.3f" % (folder, max(jsims)))
    # return max(jsims)


def collapsed_folder_prediction_task_bow_w2v_pvdbow(df, email_network, matrix, num_topics, folder, min_folder_size):
    df_folder = df[df['FolderType'] == folder]
    df_new = df[(df['FolderType'] == "Inbox") | (df['FolderType'] == folder)]
    X = [idx for idx in df_new["idx"]]
    # noinspection PyTypeChecker
    true_idc = set([idx for idx in df_folder["idx"]])
    predicted_idc = new_folder_prediction_task(X, None, num_topics, df_new, email_network, matrix,
                                               min_folder_size=min_folder_size,
                                               called_by_collapsed=True)

    # precisions = []
    # noinspection PyTypeChecker
    # for predicted_idc in predicted_idcs:
    # print(len(predicted_idc), end=', ')
    predicted_idc_set = set(predicted_idc)
    precision = len(predicted_idc_set & true_idc) / (len(predicted_idc_set) + EPS)
    # precisions.append(precision)
    # print('---------------------------------------------------------------------------')
    # return max(precisions)
    return precision

    # jsims = []
    # # noinspection PyTypeChecker
    # for predicted_idc in predicted_idcs:
    #     # print(predicted_idc)
    #     jsims.append(modified_jaccard_similarity(set(predicted_idc), true_idc))
    # # logger.info("Modified Jaccard Sim for folder: %s is %0.3f" % (folder, max(jsims)))
    # return max(jsims)


def new_folder_prediction_task(datasplits, model, num_topics, df, email_network, matrix, min_folder_size,
                               called_by_collapsed=False):
    X = datasplits
    W = matrix
    X_matrix = W[:, X].T
    if scipy.sparse.issparse(X_matrix):
        X_matrix = utils.l2_normalize_lil_matrix(scipy.sparse.lil_matrix(X_matrix))
    else:
        X_matrix = utils.l2_normalize_2d_array_copy(X_matrix)
    # avg_folder_len = email_network.avg_folder_len
    # df = email_network.df
    # min_folder_size = min(max(30, int(avg_folder_len / 3)), 100)
    eps = 0.015
    # biggest_cluster_size = 0
    # current_nclusters = 0
    # document_idcs = []
    # seen_labels = set()
    min_samples = min_folder_size
    eps_acc = True
    while True:
        if eps > 100:
            return []
        # noinspection PyTypeChecker
        if eps_acc:
            eps *= 2
        else:
            if eps == 0.:
                eps += 0.03
            else:
                eps *= 1.15
                # elif biggest_cluster_size < int(min_folder_size / 5):
                #     eps += 0.09
                # elif biggest_cluster_size < int(min_folder_size / 3):
                #     eps += 0.06
                # else:
                #     eps += 0.03

        db = DBSCAN(eps=eps, min_samples=min_samples).fit(X_matrix)
        core_samples_mask = np.zeros_like(db.labels_, dtype=bool)
        core_samples_mask[db.core_sample_indices_] = True
        labels = db.labels_
        # Number of clusters in labels, ignoring noise if present.
        n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)

        if n_clusters_ == 0:
            continue

        # values :: label_values
        values, counts = np.unique(labels, return_counts=True)
        # for label, count in zip(values, counts):
        #     print(label, count)
        cluster_size_sort = np.argsort(counts)[::-1]

        sorted_labels = [values[cluster_size_sort[index]] for index in range(len(cluster_size_sort))]

        labelmax = sorted_labels[0]
        if labelmax == -1:
            biggest_cluster_size = counts[cluster_size_sort[1]]
            labelmax = values[cluster_size_sort[1]]
        else:
            biggest_cluster_size = counts[cluster_size_sort[0]]

        if biggest_cluster_size < min_folder_size:
            continue
        elif eps_acc:
            eps /= 2
            eps_acc = False
            continue

        # print(values, counts)
        if not called_by_collapsed:
            logger.info("New Folder possible with %d number of mails, at eps=%0.2f" % (biggest_cluster_size, eps))

        else:
            doc_idc = [X[label_idx] for label_idx, label in enumerate(labels) if label == labelmax]
            return doc_idc

            # for label_idx in cluster_size_sort:
            #     label_num = values[label_idx]
            #     if label_num == -1:
            #         continue
            #     else:
            #         # seen_labels.add(label_num)
            #         count = counts[label_idx]
            #         if count > min_folder_size:
            #             doc_idc = []
            #             for itr_idx, label in enumerate(labels):
            #                 if label == label_num:
            #                     doc_idc.append(X[itr_idx])
            #             document_idcs.append(doc_idc)
            # if eps > 5.:
            #     print(eps, document_idcs[:3], values, counts)
            #     return document_idcs[:3]
            # doc_idc = []
            # for i, label in enumerate(labels):
            #     if label == labelmax:
            #         doc_idc.append(X[i])
            # print(eps)
            # return [doc_idc, doc_idc, doc_idc]
            # if n_clusters_ < 3:
            #     continue
            # if len(document_idcs) < 3:
            #     continue
            # else:
            #     print(eps, document_idcs[:3], values, counts)
            #     return document_idcs[:3]
            # ngrtr = 0
            # labelmaxes = []
            # for i in range(4):
            #     if values[cluster_size_sort[i]] == -1:
            #         continue
            #     cl_size = counts[cluster_size_sort[i]]
            #     if cl_size >= min_folder_size:
            #         ngrtr += 1
            #         labelmaxes.append(values[cluster_size_sort[i]])
            # if ngrtr >= 3:
            #     document_idcs = [[], [], []]
            #     for i, label in enumerate(labels):
            #         if label == labelmaxes[0]:
            #             document_idcs[0].append(X[i])
            #         elif label == labelmaxes[1]:
            #             document_idcs[1].append(X[i])
            #         elif label == labelmaxes[2]:
            #             document_idcs[2].append(X[i])
            #     print(eps)
            #     return document_idcs
            # else:
            #     continue

        topic_sum = np.zeros(num_topics)
        document_idc = []
        subjects = []
        senders = []
        seen_idc = set()
        for idx in db.core_sample_indices_:
            if labels[idx] == labelmax:
                seen_idc.add(idx)
                subject = df.loc[X[idx]]["Subject"].replace("RE:", "")
                subject = subject.replace("FW:", "")
                if len(subject) <= 75:
                    subjects.append(subject)
                else:
                    subjects.append(subject[0:72] + "...")
                sender = df.loc[X[idx]]["SenderName"]
                senders.append(sender)
                document_idc.append(X[idx])
                if model is not None:
                    topic_sum += X_matrix[idx, :]
        logger.info("Number of core points: %d" % len(subjects))

        for label_idx, label in enumerate(labels):
            if label_idx in seen_idc:
                continue
            if len(subjects) >= 15:
                break
            if label == labelmax:
                subject = df.loc[X[label_idx]]["Subject"].replace("RE:", "")
                subject = subject.replace("Re:", "")
                subject = subject.replace("Fwd:", "")
                subject = subject.replace("FW:", "")
                if len(subject) <= 75:
                    subjects.append(subject)
                else:
                    subjects.append(subject[0:72] + "...")
                sender = df.loc[X[label_idx]]["SenderName"]
                senders.append(sender)
                document_idc.append(X[label_idx])
                if model is not None:
                    topic_sum += X_matrix[label_idx, :]

        # for i, label in enumerate(labels):
        #     if label == labelmax:
        #         subject = df.loc[X[i]]["Subject"].replace("RE:", "")
        #         subject = subject.replace("FW:", "")
        #         if len(subject) <= 45:
        #             subjects.append(subject)
        #         else:
        #             subjects.append(subject[0:42] + "...")
        #         document_idc.append(X[i])
        #         topic_sum += X_matrix[i, :]
        folder_description = None
        if model is not None:
            word_scores, term_scores = __word_term_naive_scores(topic_sum, model, num_top_topics=3)
            weighted_word_scores, weighted_term_scores = \
                __word_term_multidocs_weighted_scores(word_scores, term_scores,
                                                      email_network.tfidf_matrix,
                                                      email_network.word2id,
                                                      document_idc,
                                                      np.ones(len(document_idc)),
                                                      range(len(document_idc)))
            top_words = [tup[0] for tup in weighted_word_scores[0:10]]
            top_terms = [tup[0] for tup in weighted_term_scores[0:10]]
            folder_description = list(set(top_words) | set(top_terms))
        # logger.info("\nFOLDER LABELS BY WORDS: {}".format(top_words))
        table = PrettyTable(["Subject", "Sender"])
        for i in range(min(len(subjects), 15)):
            table.add_row([subjects[i], senders[i]])
        # table_ht = min(5, int(len(subjects) / 3))
        # table = PrettyTable(header=False)
        # for i in range(table_ht):
        #     start = i * 3
        #     table.add_row([subjects[]])

        print("\n\n\nSujects & Senders of some of the mails predicted to be in a new folder:\n{0}\n".format(table))
        if model is not None:
            print("The content of mails is mostly about: {0}\n".format(', '.join(folder_description)))

        print("\nThe emails, represented above by their subj+senders, have been identified from your inbox "
              "to be close enough"
              " to be identified as a \"Folder\"")
        print("\nYour action could be to make them into new folder; or trash them to reduce inbox clutter;"
              " merge them with an existing folder; "
              "or archive them together. Based on this, please decide the merit of the recognized \"Folder\":\n")

        rating = str(
            six.moves.input("Enter agreement level with the suggested set of mails:\n1: Folder doesn't make sense - "
                            "emails with dissimilar content have been grouped"
                            "\n2: Folder makes sense in terms of similar mails, but suggested folder is of no "
                            "practical use. "
                            "\n3: Folder makes sense and on apt action - helps in organization and reducing inbox "
                            "clutter."
                            "\nEnter score [1-3] here: "))
        while not rating.isdigit() or int(rating) not in range(1, 11):
            rating = str(six.moves.input("Please enter a valid score [1-3]: "))
        logger.info("User score: %d" % int(rating))
        logger.info('Estimated number of clusters: %d' % n_clusters_)
        try:
            logger.info("Silhouette Coefficient: %0.3f" % metrics.silhouette_score(X_matrix, labels))
        except ValueError:
            pass
        # pca = PCA(n_components=2, whiten=False, random_state=42)
        # X_reduced = pca.fit_transform(X_matrix)
        # # Black removed and is used for noise instead.
        # unique_labels = set(labels)
        # colors = [plt.cm.Spectral(each)
        #           for each in np.linspace(0, 1, len(unique_labels))]
        # for k, col in zip(unique_labels, colors):
        #     if k == -1:
        #         # Black used for noise.
        #         col = [0, 0, 0, 1]
        #     if k == labelmax:
        #         col = [255 / 255, 165 / 255, 0, 0.8]  # Orange
        #     class_member_mask = (labels == k)
        #     # xy = X_matrix[class_member_mask & core_samples_mask]
        #     # plt.plot(xy[:, top_topic_idc[0]], xy[:, top_topic_idc[1]], 'o', markerfacecolor=tuple(col),
        #     #          markeredgecolor='k', markersize=14)
        #     xy = X_reduced[class_member_mask & core_samples_mask]
        #     plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=tuple(col),
        #              markeredgecolor='k', markersize=14)
        #     # xy = X_matrix[class_member_mask & ~core_samples_mask]
        #     # plt.plot(xy[:, top_topic_idc[0]], xy[:, top_topic_idc[1]], 'o', markerfacecolor=tuple(col),
        #     #          markeredgecolor='k', markersize=6)
        #     xy = X_reduced[class_member_mask & ~core_samples_mask]
        #     plt.plot(xy[:, 0], xy[:, 1], 'o', markerfacecolor=tuple(col),
        #              markeredgecolor='k', markersize=6)
        #
        # plt.title('Estimated number of clusters: %d' % n_clusters_)
        # plt.show()
        break
    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    return


def accuracy_report(name, X_train_matrix, y_train, X_test_matrix, y_test):
    param_grid = [{'C': np.arange(0.05, 8, 0.2)}]
    scores = ['accuracy']
    accuracy = -1
    for score in scores:
        clf = GridSearchCV(LinearSVC(), param_grid, cv=5, scoring='%s' % score)
        clf.fit(X_train_matrix, y_train)
        logger.debug("Best parameters set found on development set: {}".format(clf.best_params_))
        # print("Best value for ", score, ":\n") # print(clf.best_score_)
        Y_true, Y_pred = y_test, clf.predict(X_test_matrix)
        logger.info("Report %s:" % name.upper())
        logger.info("\n{}".format(classification_report(Y_true, Y_pred, digits=4)))
        accuracy = clf.score(X_test_matrix, y_test)
    return accuracy * 100


def accuracy_and_auc_report(name, X_train_matrix, y_train, X_test_matrix, y_test):
    param_grid = [{'C': np.arange(0.05, 8, 0.2)}]
    scores = ['recall_weighted']
    accuracy = -1
    average_precision, precision, recall, fscore = None, None, None, None
    for score in scores:
        print("# Tuning hyper-parameters for", score, "\n")
        clf = GridSearchCV(LinearSVC(C=1, class_weight='balanced'), param_grid, cv=5, scoring='%s' % score)
        clf.fit(X_train_matrix, y_train)
        print("Best score: ", clf.best_score_)

        y_scores = clf.decision_function(X_test_matrix)
        precision, recall, _ = precision_recall_curve(y_test, y_scores, pos_label=1)
        average_precision = average_precision_score(y_test, y_scores, average='micro')
        # # Plot Precision-Recall curve
        # plt.clf()
        # plt.plot(recall, precision, lw=2, color='navy',
        #          label='Precision-Recall curve')
        # plt.xlabel('Recall')
        # plt.ylabel('Precision')
        # plt.ylim([0.0, 1.05])
        # plt.xlim([0.0, 1.0])
        # plt.title('Precision-Recall example: AUC={0:0.2f}'.format(average_precision))
        # plt.legend(loc="lower left")
        # plt.show()

        print("Best parameters set found on development set:\n")
        print(clf.best_params_)
        print("Best value for ", score, ": ", clf.best_score_)
        Y_true, Y_pred = y_test, clf.predict(X_test_matrix)
        precision, recall, fscore, _ = precision_recall_fscore_support(Y_true, Y_pred, pos_label=1, average='binary')
        print("Report %s:" % name.upper())
        print(classification_report(Y_true, Y_pred, digits=4))
        accuracy = clf.score(X_test_matrix, y_test)
    return accuracy * 100, average_precision * 100, precision * 100, recall * 100, fscore * 100


def folder_prediction_task(datasplits, model):
    X_train, X_test, y_train, y_test = datasplits
    W = model.document_topic_matrix
    X_train_matrix = np.zeros((len(X_train), model.num_topics))
    for i, idx in enumerate(X_train):
        X_train_matrix[i, :] = W[:, idx]
    X_test_matrix = np.zeros((len(X_test), model.num_topics))
    for i, idx in enumerate(X_test):
        X_test_matrix[i, :] = W[:, idx]

    # start = time.time()
    param_grid = [{'C': np.arange(0.05, 8, 0.2)}]
    # scores = ['accuracy', 'recall_micro', 'f1_micro', 'precision_micro', 'recall_macro', 'f1_macro',
    # 'precision_macro',
    #           'recall_weighted', 'f1_weighted', 'precision_weighted']  # , 'accuracy', 'recall', 'f1']
    scores = ['accuracy']
    accuracy = -1
    for score in scores:
        # substart = time.time()
        # print("# Tuning hyper-parameters for", score, "\n")
        clf = GridSearchCV(LinearSVC(), param_grid, cv=5, scoring='%s' % score)
        clf.fit(X_train_matrix, y_train)
        logger.debug("Best parameters set found on development set:", clf.best_params_)
        # print("Best value for ", score, ":\n")
        # print(clf.best_score_)
        Y_true, Y_pred = y_test, clf.predict(X_test_matrix)
        logger.info("Report %s:" % model.modelname.upper())
        logger.info('\n{}'.format(classification_report(Y_true, Y_pred, digits=6)))
        # print(Y_true, Y_pred)
        accuracy = clf.score(X_test_matrix, y_test)
        # print("Time taken:", time.time() - substart, "\n")
    # endtime = time.time()
    # print("Total time taken: ", endtime - start, "seconds.")
    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n")
    return accuracy * 100


def folder_prediction_task_bow(datasplits, tfidf_matrix_normed, sim):
    X_train, X_test, y_train, y_test = datasplits
    Wt = tfidf_matrix_normed
    # X_train_matrix = Wt[X_train, :]
    X_test_matrix = Wt[X_test, :]

    # accuracy = accuracy_report("BOW", X_train_matrix, y_train, X_test_matrix, y_test)

    folders_idc = {}
    for itr in range(len(y_train)):
        try:
            folders_idc[y_train[itr]].append(X_train[itr])
        except KeyError:
            folders_idc[y_train[itr]] = [X_train[itr]]
    folders = [folder for folder in folders_idc]
    folders_matrix = {}
    folders_centroid_matrix = np.zeros((len(folders), Wt.shape[1]))
    for idx, folder in enumerate(folders):
        folders_matrix[folder] = Wt[folders_idc[folder]]
        folders_centroid_matrix[idx] = np.mean(folders_matrix[folder], axis=0)
        if sim == 'cosine':
            norm = np.linalg.norm(folders_centroid_matrix[idx], ord=2)
            if norm > 0:
                folders_centroid_matrix[idx] /= np.linalg.norm(folders_centroid_matrix[idx], ord=2)
            else:
                n = len(folders_centroid_matrix[idx])
                folders_centroid_matrix[idx] = np.array([1 / (n ** 0.5) * n])
    if sim == 'cosine':
        folder_sim_matrix = X_test_matrix.dot(folders_centroid_matrix.T)
    elif sim == 'hellinger':
        folder_sim_matrix = np.zeros((X_test_matrix.shape[0], len(folders)))
        for idx, x_test in enumerate(X_test_matrix):
            folder_sim_matrix[idx] = __get_helinger_sim_array(x_test, folders_centroid_matrix)
    else:
        folder_sim_matrix = None

    correct = 0
    incorrect = 0
    for idx, y_true in enumerate(y_test):
        # noinspection PyTypeChecker
        y_pred = folders[np.argmax(folder_sim_matrix[idx])]
        if y_pred == y_true:
            correct += 1
        else:
            incorrect += 1

    if correct + incorrect > 0:
        accuracy_centroid = (correct / (correct + incorrect)) * 100
    else:
        accuracy_centroid = 100.

    result_array = np.zeros((len(folders), len(y_test)))
    for fidx, folder in enumerate(folders):
        if sim == 'cosine':
            sim_array = X_test_matrix.dot(folders_matrix[folder].T)
        elif sim == 'hellinger':
            sim_array = np.zeros((X_test_matrix.shape[0], folders_matrix[folder].shape[0]))
            for idx, x_test in enumerate(X_test_matrix):
                sim_array[idx] = __get_helinger_sim_array(x_test, folders_matrix[folder])
        if scipy.sparse.issparse(sim_array):
            sim_array = sim_array.toarray()
        a = np.array([sum(sorted(row)[-10:]) for row in sim_array])
        result_array[fidx] = a
    result_array = result_array.T

    accuracies = {}
    # For each folder, we have a 3 element list: TP, FP, FN
    for folder in folders:
        accuracies[folder] = [0] * 4

    for idx, y_true in enumerate(y_test):
        # noinspection PyTypeChecker
        y_pred = folders[np.argmax(result_array[idx])]
        if y_pred == y_true:
            correct += 1
            accuracies[y_true][0] += 1
        else:
            incorrect += 1
            accuracies[y_pred][1] += 1
            accuracies[y_true][2] += 1
    if correct + incorrect > 0:
        accuracy_10closest = (correct / (correct + incorrect)) * 100
    else:
        accuracy_10closest = 100.

    table = PrettyTable()
    precisions = []
    recalls = []
    fscores = []
    supports = []
    for folder in folders:
        mat = accuracies[folder]
        if mat[0] + mat[1] > 0:
            precision = mat[0] / (mat[0] + mat[1])
        else:
            precision = 0.
        if mat[0] + mat[2] > 0:
            recall = mat[0] / (mat[0] + mat[2])
        else:
            recall = 0.
        precisions.append(precision)
        recalls.append(recall)
        if (precision + recall) == 0:
            fscores.append(0.)
        else:
            fscores.append((2 * precision * recall) / (precision + recall))
        supports.append(mat[0] + mat[2])

    sum_supports = sum(supports)
    sum_supports = sum_supports if sum_supports > 0 else 1
    macro_avg_precision = sum([p * s for p, s in zip(precisions, supports)]) / sum_supports
    macro_avg_recall = sum([p * s for p, s in zip(recalls, supports)]) / sum_supports
    macro_avg_fscore = sum([p * s for p, s in zip(fscores, supports)]) / sum_supports
    table.add_column('Folder', [str(i) for i in range(1, len(folders) + 1)] + ['', 'Average'])
    table.add_column('Precision', precisions + ['', macro_avg_precision])
    table.add_column('Recall', recalls + ['', macro_avg_recall])
    table.add_column('F-Score', fscores + ['', macro_avg_fscore])
    table.add_column('Support', supports + ['', sum(supports)])
    logger.info('\nFolder Clf Report (10-Closest): \n{}'.format(table))
    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n")
    return accuracy_centroid, accuracy_10closest


def folder_prediction_task_w2v(datasplits, avg_word2vec_matrix):
    X_train, X_test, y_train, y_test = datasplits
    W = avg_word2vec_matrix.T
    X_train_matrix = np.zeros((len(X_train), W.shape[0]))
    for i, idx in enumerate(X_train):
        X_train_matrix[i, :] = W[:, idx]
    X_test_matrix = np.zeros((len(X_test), W.shape[0]))
    for i, idx in enumerate(X_test):
        X_test_matrix[i, :] = W[:, idx]
    accuracy = accuracy_report("W2V", X_train_matrix, y_train, X_test_matrix, y_test)
    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n")
    return accuracy


def folder_prediction_task_pvdbow(datasplits, pvdbow_matrix):
    X_train, X_test, y_train, y_test = datasplits
    Wt = pvdbow_matrix
    X_train_matrix = Wt[X_train, :]
    X_test_matrix = Wt[X_test, :]
    accuracy = accuracy_report("PV-DBOW", X_train_matrix, y_train, X_test_matrix, y_test)
    print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n")
    return accuracy


def reply_prediction_task(datasplits, model):
    X_train, X_test, y_train, y_test = datasplits
    W = model.document_topic_matrix
    X_train_matrix = np.zeros((len(X_train), model.num_topics))
    for i, idx in enumerate(X_train):
        X_train_matrix[i, :] = W[:, idx]
    X_test_matrix = np.zeros((len(X_test), model.num_topics))
    for i, idx in enumerate(X_test):
        X_test_matrix[i, :] = W[:, idx]
    accuracy, ap, p, r, f = accuracy_and_auc_report(model.modelname, X_train_matrix, y_train, X_test_matrix, y_test)
    print("++++++++++++++++++++++++++++++++++++++++++++++++++++")
    return accuracy, ap, p, r, f


def reply_prediction_task_bow(datasplits, tfidf_matrix):
    X_train, X_test, y_train, y_test = datasplits
    Wt = tfidf_matrix
    X_train_matrix = Wt[X_train, :]
    X_test_matrix = Wt[X_test, :]
    accuracy, ap, p, r, f = accuracy_and_auc_report("BOW", X_train_matrix, y_train, X_test_matrix, y_test)
    print("++++++++++++++++++++++++++++++++++++++++++++++++++++")
    return accuracy, ap, p, r, f


def reply_prediction_task_w2v(datasplits, avg_word2vec_matrix):
    X_train, X_test, y_train, y_test = datasplits
    W = avg_word2vec_matrix.T
    X_train_matrix = np.zeros((len(X_train), W.shape[0]))
    for i, idx in enumerate(X_train):
        X_train_matrix[i, :] = W[:, idx]
    X_test_matrix = np.zeros((len(X_test), W.shape[0]))
    for i, idx in enumerate(X_test):
        X_test_matrix[i, :] = W[:, idx]
    accuracy, ap, p, r, f = accuracy_and_auc_report("W2V", X_train_matrix, y_train, X_test_matrix, y_test)
    print("++++++++++++++++++++++++++++++++++++++++++++++++++++")
    return accuracy, ap, p, r, f


def reply_prediction_task_pvdbow(datasplits, pvdbow_matrix):
    X_train, X_test, y_train, y_test = datasplits
    Wt = pvdbow_matrix
    X_train_matrix = Wt[X_train, :]
    X_test_matrix = Wt[X_test, :]
    accuracy, ap, p, r, f = accuracy_and_auc_report("PV-BOW", X_train_matrix, y_train, X_test_matrix, y_test)
    print("++++++++++++++++++++++++++++++++++++++++++++++++++++")
    return accuracy, ap, p, r, f


def receiver_prediction_task(datasplits, model, npred):
    X_train, X_test, y_train, y_test, _, _ = datasplits
    W = model.document_topic_matrix
    X_train_matrix = np.zeros((len(X_train), model.num_topics))
    for i, idx in enumerate(X_train):
        X_train_matrix[i, :] = W[:, idx]
    X_test_matrix = np.zeros((len(X_test), model.num_topics))
    for i, idx in enumerate(X_test):
        X_test_matrix[i, :] = W[:, idx]
    Nparam = min(len(X_train), 30)

    average_precision_vals = []
    for i, Xi_test in enumerate(X_test_matrix):
        hellinger_sim_array = __get_helinger_sim_array(Xi_test, X_train_matrix)
        best_args = np.argsort(hellinger_sim_array)[-Nparam:][::-1]
        user_scores_dict = {}
        for arg in best_args:
            for user in y_train[arg]:
                try:
                    user_scores_dict[user] += hellinger_sim_array[arg]
                except KeyError:
                    user_scores_dict[user] = hellinger_sim_array[arg]
        sorted_users = sorted(user_scores_dict.items(), key=operator.itemgetter(1), reverse=True)
        y_pred = [itr[0] for itr in sorted_users[:npred]]
        y_true = set(y_test[i])
        AP = get_average_precision(y_true=y_true, y_pred=y_pred)
        average_precision_vals.append(AP)

    MAP = np.mean(average_precision_vals)
    return MAP

    #     precision_at_135 = [0, 0, 0]
    #     y_true = set(y_test[i])
    #     if len(y_true) == 0:
    #         continue
    #     # print("SUBJECT: ", df.iloc[X_test[i]]["Subject"])
    #     # print("PREDICTED ANSWERS: ", sorted_users[0][0], sorted_users[1][0], sorted_users[2][0])
    #     if sorted_users[0][0] in y_true:
    #         precision_at_135[0] = 1
    #     tp = 0
    #     for tup in sorted_users[:3]:
    #         if tup[0] in y_true:
    #             tp += 1
    #     precision_at_135[1] = tp / min(3, len(y_true))
    #     tp = 0
    #     for tup in sorted_users[:5]:
    #         if tup[0] in y_true:
    #             tp += 1
    #     precision_at_135[2] = tp / min(5, len(y_true))
    #     precision_vals += [precision_at_135]
    # precision_vals = np.array(precision_vals)
    # n_samples = precision_vals.shape[0]
    # if n_samples != 0:
    #     precision_vals = np.sum(precision_vals, axis=0) / n_samples
    #     precision_vals = [min(1.0, x + 0.08) for x in precision_vals]
    # else:
    #     logger.warning("Zero samples in receiver recommendation task's precision calculations")
    #     precision_vals = np.zeros(precision_vals.shape[1])
    # return precision_vals


def receiver_task_bow(datasplits, matrix, sim, npred):
    # npred: Number of recipients recommended. This means MAP will be calculated @npred

    X_train, X_test, y_train, y_test, _, _ = datasplits
    Wt = matrix
    X_train_matrix = Wt[X_train, :]
    X_test_matrix = Wt[X_test, :]
    Nparam = min(len(X_train), 30)
    average_precision_vals = []
    for i, Xi_test in enumerate(X_test_matrix):
        if sim == 'euclidean':
            l2_dist_array = get_l2_dist_docs(y=Xi_test, X=X_train_matrix)
            max_l2_dist_array = max(l2_dist_array)
            if max_l2_dist_array == 0:
                continue
            sim_array = np.ones(len(l2_dist_array)) - (l2_dist_array / max_l2_dist_array)
        elif sim == 'cosine':
            sim_array = X_train_matrix.dot(Xi_test.T).toarray().reshape(-1, )
        best_args = np.argsort(sim_array)[-Nparam:][::-1]
        user_scores_dict = {}
        for arg in best_args:
            for user in y_train[arg]:
                try:
                    user_scores_dict[user] += sim_array[arg]
                except KeyError:
                    user_scores_dict[user] = sim_array[arg]
        sorted_users = sorted(user_scores_dict.items(), key=operator.itemgetter(1), reverse=True)
        y_pred = [itr[0] for itr in sorted_users[:npred]]
        y_true = set(y_test[i])
        AP = get_average_precision(y_true=y_true, y_pred=y_pred)
        average_precision_vals.append(AP)

    MAP = np.mean(average_precision_vals)
    return MAP

    #     precision_at_135 = [0, 0, 0]
    #     if len(y_true) == 0:
    #         continue
    #     # print("SUBJECT: ", df.iloc[X_test[i]]["Subject"])
    #     # print("PREDICTED ANSWERS: ", sorted_users[0][0], sorted_users[1][0], sorted_users[2][0])
    #     if sorted_users[0][0] in y_true:
    #         precision_at_135[0] = 1
    #     tp = 0
    #     for tup in sorted_users[:3]:
    #         if tup[0] in y_true:
    #             tp += 1
    #     precision_at_135[1] = tp / min(3, len(y_true))
    #     tp = 0
    #     for tup in sorted_users[:5]:
    #         if tup[0] in y_true:
    #             tp += 1
    #     precision_at_135[2] = tp / min(5, len(y_true))
    #     precision_vals += [precision_at_135]
    # precision_vals = np.array(precision_vals)
    # n_samples = precision_vals.shape[0]
    # if n_samples != 0:
    #     precision_vals = np.sum(precision_vals, axis=0) / n_samples
    # else:
    #     precision_vals = np.zeros(precision_vals.shape[1]) / n_samples
    # return precision_vals


def receiver_task_w2v_pvdbow(datasplits, matrix, npred):
    X_train, X_test, y_train, y_test, _, _ = datasplits
    Wt = matrix
    X_train_matrix = Wt[X_train, :]
    X_test_matrix = Wt[X_test, :]
    Nparam = min(len(X_train), 30)
    # precision_vals = []
    average_precision_vals = []
    for i, Xi_test in enumerate(X_test_matrix):
        cosine_sim_array = np.dot(X_train_matrix, Xi_test)
        best_args = np.argsort(cosine_sim_array)[-Nparam:][::-1]
        user_scores_dict = {}
        for arg in best_args:
            for user in y_train[arg]:
                try:
                    user_scores_dict[user] += cosine_sim_array[arg]
                except KeyError:
                    user_scores_dict[user] = cosine_sim_array[arg]
        sorted_users = sorted(user_scores_dict.items(), key=operator.itemgetter(1), reverse=True)
        y_pred = [itr[0] for itr in sorted_users[:npred]]
        y_true = set(y_test[i])
        AP = get_average_precision(y_true=y_true, y_pred=y_pred)
        average_precision_vals.append(AP)

    MAP = np.mean(average_precision_vals)
    return MAP

    #     precision_at_135 = [0, 0, 0]
    #     y_true = set(y_test[i])
    #     # print("SUBJECT: ", df.iloc[X_test[i]]["Subject"])
    #     # print("PREDICTED ANSWERS: ", sorted_users[0][0], sorted_users[1][0], sorted_users[2][0])
    #     if len(y_true) == 0:
    #         continue
    #     if sorted_users[0][0] in y_true:
    #         precision_at_135[0] = 1
    #     tp = 0
    #     for tup in sorted_users[:3]:
    #         if tup[0] in y_true:
    #             tp += 1
    #     precision_at_135[1] = tp / min(3, len(y_true))
    #     tp = 0
    #     for tup in sorted_users[:5]:
    #         if tup[0] in y_true:
    #             tp += 1
    #     precision_at_135[2] = tp / min(5, len(y_true))
    #     precision_vals += [precision_at_135]
    # precision_vals = np.array(precision_vals)
    # n_samples = precision_vals.shape[0]
    # if n_samples != 0:
    #     precision_vals = np.sum(precision_vals, axis=0) / n_samples
    # else:
    #     precision_vals = np.zeros(precision_vals.shape[1])
    # return precision_vals


def receiver_task_full_knn(datasplits, matrix, email_network, npred, sim):
    X_train, X_test, y_train, y_test, user_addrs, df_train = datasplits

    user_addrs_pos = {}
    for idx, user in enumerate(user_addrs):
        user_addrs_pos[user] = idx

    Wt = matrix
    X_train_matrix = Wt[X_train, :]
    X_test_matrix = Wt[X_test, :]
    knn_scores = __receiver_task_knn_cv(X_train, y_train, Wt, user_addrs, user_addrs_pos, sim)
    frequency_scores_sent, frequency_scores_recvd = __receiver_frequency_scores(user_addrs, email_network)
    all_recency_scores = __receiver_recency_scores(user_addrs, df_train)

    rx_train = []
    ry_train = []

    for idx, x in enumerate(X_train):
        true_recipients = [user for user in y_train[idx]]
        true_recipients_set = set(true_recipients)
        non_recipients = [user for user in user_addrs if user not in true_recipients_set]
        # sample 20%
        num_neg = int(len(non_recipients) / 5)
        non_recipients_idc = np.random.choice(len(non_recipients), num_neg, replace=False)
        non_recipients = [non_recipients[sample_idx] for sample_idx in non_recipients_idc]
        for recipient in true_recipients:
            try:
                recipient_idx = user_addrs_pos[recipient]
            except KeyError:
                continue
            feature_vec = [knn_scores[idx, recipient_idx], frequency_scores_sent[recipient_idx],
                           frequency_scores_recvd[recipient_idx]]
            feature_vec += [recency_scores[recipient_idx] for recency_scores in all_recency_scores]
            rx_train.append(feature_vec)
            ry_train.append(True)
        for recipient in non_recipients:
            try:
                recipient_idx = user_addrs_pos[recipient]
            except KeyError:
                continue
            feature_vec = [knn_scores[idx, recipient_idx], frequency_scores_sent[recipient_idx],
                           frequency_scores_recvd[recipient_idx]]
            feature_vec += [recency_scores[recipient_idx] for recency_scores in all_recency_scores]
            rx_train.append(feature_vec)
            ry_train.append(False)

    param_grid = [{'C': np.arange(0.05, 8, 0.4)}]
    score = 'accuracy'
    clf = GridSearchCV(LinearSVC(), param_grid, cv=5, scoring='%s' % score)
    clf.fit(rx_train, ry_train)
    logger.debug("Best parameters set found on development set: {}".format(clf.best_params_))

    average_precisions = []
    for test_idx, x_test in enumerate(X_test_matrix):
        y_true = y_test[test_idx]
        if sim == 'euclidean' and scipy.sparse.issparse(X_train_matrix):
            l2_dist_array = get_l2_dist_docs(y=x_test, X=X_train_matrix)
            max_l2_dist_array = max(l2_dist_array)
            if max_l2_dist_array != 0:
                l2_dist_array /= max_l2_dist_array
            else:
                continue
            sim_array = 1 - l2_dist_array
        elif sim == 'cosine':
            if scipy.sparse.issparse(X_train_matrix):
                sim_array = [x_test.dot(vec.T)[0, 0] for vec in X_train_matrix]
            else:
                sim_array = [cosine_similarity_unnormed_vecs(vec, x_test) for vec in X_train_matrix]
        elif sim == 'hellinger':
            sim_array = [1 - hellinger_distance(vec, x_test) for vec in X_train_matrix]
        else:
            raise ValueError("Unidentified sim value in receiver task full knn")
        sim_idc = list(np.argsort(sim_array)[-30:][::-1])
        recipient_knn_scores = np.zeros(len(user_addrs))
        for sim_idx in sim_idc:
            recipients = y_train[sim_idx]
            for recipient in recipients:
                try:
                    recipient_idx = user_addrs_pos[recipient]
                except KeyError:
                    continue
                recipient_knn_scores[recipient_idx] += sim_array[sim_idx]

        recipient_final_scores = np.zeros(len(user_addrs))
        for r_idx, recipient in enumerate(user_addrs):
            score = clf.decision_function([[recipient_knn_scores[r_idx], frequency_scores_sent[r_idx],
                                            frequency_scores_recvd[r_idx],
                                            all_recency_scores[0][r_idx], all_recency_scores[1][r_idx],
                                            all_recency_scores[2][r_idx]]])
            recipient_final_scores[r_idx] = score if clf.best_estimator_.classes_[1] == True else (1 - score)

        final_recommendation_idc = np.argsort(recipient_final_scores)[-npred:][::-1]
        final_recommendation = [user_addrs[r_idx] for r_idx in final_recommendation_idc]

        average_precision = get_average_precision(y_true=y_true, y_pred=final_recommendation)
        average_precisions.append(average_precision)

    if len(average_precisions) > 0:
        return np.mean(average_precisions)
    else:
        return 0.


def receiver_task_full_cgec(datasplits, A_csr, email_network, npred):
    X_train, X_test, y_train, y_test, user_addrs, _ = datasplits
    X_train_set = set(X_train)

    A = scipy.sparse.csc_matrix(A_csr)
    A_train = A[:, X_train]

    word_freqs = np.array(A_train.sum(axis=1)).reshape(-1,)
    total_words = sum(word_freqs)

    prob_words = word_freqs/total_words

    prob_receivers = np.zeros(len(user_addrs))
    # receiver_word_prob = scipy.sparse.dok_matrix((len(user_addrs), A.shape[0]), dtype=np.float32)
    word_receiver_prob = scipy.sparse.dok_matrix((A.shape[0], len(user_addrs)), dtype=np.float32)

    for idx, user in enumerate(user_addrs):
        try:
            user_idc = email_network.sent_to_users_dict[user] + email_network.cc_to_users_dict[user]
        except KeyError:
            continue

        user_idc = [user_idx for user_idx in user_idc if user_idx in X_train_set]

        prob_receivers[idx] = len(user_idc) / len(X_train)

        A_receiver = A[:, user_idc]
        receiver_word_freqs = np.array(A_receiver.sum(axis=1)).reshape(-1,)
        total_receiver_words = sum(receiver_word_freqs)
        if total_receiver_words > 0:
            receiver_prob_words = receiver_word_freqs/total_receiver_words
        else:
            receiver_prob_words = receiver_word_freqs
        for elem_idx, elem in enumerate(receiver_prob_words):
            if elem > 0:
                word_receiver_prob[elem_idx, idx] = elem

    word_receiver_prob = scipy.sparse.csr_matrix(word_receiver_prob)

    MAPs = []
    for beta in np.arange(0.1, 1.0, 0.1):
        MAPs.append(receiver_task_full_cgec_helper(beta, X_train, y_train, A, user_addrs, word_receiver_prob,
                                                   prob_words, prob_receivers, npred))
    max_idx = np.argmax(MAPs)
    max_beta = (max_idx + 1)*0.1

    # noinspection PyStringFormat
    logger.info("Best beta parameter for cgec receiver pred: %0.2f" % max_beta)

    MAP_test = receiver_task_full_cgec_helper(max_beta, X_test, y_test, A, user_addrs, word_receiver_prob, prob_words,
                                              prob_receivers, npred)

    return MAP_test


def receiver_task_full_cgec_helper(beta, X, y, A, user_addrs, word_receiver_prob, prob_words, prob_receivers, npred):
    average_precisions = []
    for itr_idx, x in enumerate(X):
        y_true = y[itr_idx]
        word_idc = A[:, x].indices

        receiver_probs = prob_receivers[:]
        for word_idx in word_idc:
            mul = (1-beta)*prob_words[word_idx] + (beta*word_receiver_prob[word_idx, :]).toarray()[0]
            receiver_probs = np.multiply(receiver_probs, mul)
            # for r_idx, receiver in enumerate(user_addrs):
            #     receiver_probs[r_idx] *= (beta * receiver_word_prob[r_idx, word_idx] +
            #                               (1 - beta) * prob_words[word_idx])
        top_pred_idc = np.argsort(receiver_probs)[-npred:][::-1]
        top_pred_receivers = [user_addrs[r_idx] for r_idx in top_pred_idc]
        # if test:
        #     print('+++++++++++++++++++++++++++++++++++')
        #     print(top_pred_receivers)
        #     print(y_true)
        #     print('\n\n')
        average_precision = get_average_precision(y_true, top_pred_receivers)
        average_precisions.append(average_precision)
    if len(average_precisions) > 0:
        return np.mean(average_precisions)
    else:
        return 0.


def subject_prediction_task_bayes(datasplits, Wt, model, email_network, sim, npred):
    num_closest_docs = 10
    X_train, y_train, X_test, y_test, subject_word_dict, _ = datasplits
    # This Wt has something
    # Wt = model.document_topic_wt_matrix.T
    # This is the normal W matrix
    topic_marginal_probs = np.sum(model.document_topic_matrix.T, axis=0) / model.document_topic_matrix.shape[1]
    M = model.topic_word_matrix
    word2id = model.word2id_dict
    id2word = model.id2word_dict
    X_train_matrix = Wt[X_train, :]
    X_test_matrix = Wt[X_test, :]

    eps = 1e-6
    average_precisions = []
    for idx, x_test in enumerate(X_test_matrix):
        current_doc_idx = X_test[idx]
        closest_docs = retrieve_n_closest_docs(x_test, X_train_matrix, n=num_closest_docs, sim=sim)

        doc_idc = [current_doc_idx] + [X_train[index] for index in closest_docs]
        # print(email_network.df.iloc[doc_idx]['Subject'])
        # print(email_network.df.iloc[doc_idx]['CleanBody'])
        candidates = set()

        for doc_idx in doc_idc:
            for w in email_network.df.iloc[doc_idx]['CleanBody'].split(' '):
                try:
                    candidates.add(word2id[w])
                except KeyError:
                    continue
            if doc_idx == current_doc_idx:
                continue
            for w in email_network.df.iloc[doc_idx]['Subject'].split(' '):
                try:
                    candidates.add(word2id[w])
                except KeyError:
                    continue

        dom_topics = np.argsort(model.document_topic_matrix.T[doc_idx])[-3:][::-1]
        dom_topics = [topic for topic in dom_topics if model.document_topic_matrix.T[doc_idx, topic] > 0.3]
        # for topic in dom_topics:
        #     print(model.topic_tuples[topic][:10])
        #     for tup in model.topic_tuples[topic][:10]:
        #         w = tup[0]
        #         candidates.add(word2id[w])
        candidates = list(candidates)
        scores = []
        for n_idx, w_idx in enumerate(candidates):
            try:
                pws = (len(subject_word_dict[id2word[w_idx]]) + eps) / (len(y_train) + model.vocab_size * eps)
            except KeyError:
                pws = eps / (len(y_train) + model.vocab_size * eps)
            # print('Word: ', id2word[w_idx], ' P(w_s): ', pws)
            pEws = 1
            for topic in dom_topics:
                pt = topic_marginal_probs[topic]
                pwt = M[w_idx, topic] + eps
                # pwt = __get_term_score(M[:, topic], w_idx)
                # print(pt, pwt)
                pEws *= (pwt * pt)
            # print('Word: ', id2word[w_idx], ' P(E|w_s): ', pEws)
            scores.append(pws * pEws)

        pred_indicec_ranked = np.argsort(scores)[::-1]
        cwords = [id2word[candidates[w_idx]] for w_idx in pred_indicec_ranked]
        # words_pred = [candidates[index] for index in np.argsort(scores)[-5:][::-1]]
        # y_pred = [id2word[w_idx] for w_idx in words_pred]
        y_true = y_test[idx]
        y_pred = cwords[:npred]
        average_precisions.append(get_average_precision(y_true, y_pred))
        # print('Pred: ', y_pred, '\nTrue ', y_true)
        # print('Pred: ', y_pred, '\nTrue ', y_true)

    return np.mean(average_precisions)


def subject_prediction_task(datasplits, model, email_network):
    # param: *K=30* top emails retrieved for nn-based word weighting
    K = 30
    # df = email_network.df
    X, y = datasplits
    W = model.document_topic_wt_matrix
    hellinger_dist_matrix = __make_hellinger_dist_matrix(X, W)
    hellinger_dist_matrix_argsorted = np.array([np.argsort(row) for row in hellinger_dist_matrix])
    assert hellinger_dist_matrix.shape == hellinger_dist_matrix_argsorted.shape

    def to_idx(index):
        return X[index]

    vfunc = np.vectorize(to_idx)
    hellinger_dist_matrix_idxsorted = vfunc(hellinger_dist_matrix_argsorted)
    precisions_list = []
    precision_vals1, precision_vals2, precision_vals3 = [], [], []
    precision_vals1t, precision_vals2t, precision_vals3t = [], [], []
    for i in range(len(X)):
        x = W[:, X[i]]
        y_true = y[i]
        sorted_word_scores, sorted_term_scores = __word_term_naive_scores(x, model, num_top_topics=5)
        # sorted_word_scores_weighted, sorted_term_scores_weighted = \
        #     __subject_prediction_naive_weighted_scores(sorted_word_scores, sorted_term_scores,
        #                                                df.loc[X[i]]["CleanBody"])
        sorted_word_scores_weighted, sorted_term_scores_weighted = \
            __word_term_naive_weighted_scores(sorted_word_scores, sorted_term_scores,
                                              email_network.tfidf_matrix[X[i], :], email_network.word2id)
        # sorted_word_scores_weighted_nn, sorted_term_scores_weighted_nn = \
        #     __word_term_multidocs_weighted_scores(sorted_word_scores, sorted_term_scores, df,
        #                                           hellinger_dist_matrix_idxsorted[i, :][:K])
        sorted_word_scores_weighted_nn, sorted_term_scores_weighted_nn = \
            __word_term_multidocs_weighted_scores(sorted_word_scores, sorted_term_scores, email_network.tfidf_matrix,
                                                  email_network.word2id,
                                                  hellinger_dist_matrix_idxsorted[i, :][:K],
                                                  hellinger_dist_matrix[i, :],
                                                  hellinger_dist_matrix_argsorted[i, 0:K])

        print("True Subject:", end=' ')
        for w in y_true:
            print(w, end=', ')
        print("\nPred Subject:", end=' ')
        for tup in sorted_term_scores_weighted[:5]:
            print(tup[0], end=', ')
        print('\n------------------------------------------------------------------------\n')
        precision_at_3510 = __calculate_precision([3, 5, 10], y_true, sorted_word_scores)
        precision_vals1 += [precision_at_3510]
        precision_at_3510 = __calculate_precision([3, 5, 10], y_true, sorted_term_scores)
        precision_vals1t += [precision_at_3510]
        precision_at_3510 = __calculate_precision([3, 5, 10], y_true, sorted_word_scores_weighted)
        precision_vals2 += [precision_at_3510]
        precision_at_3510 = __calculate_precision([3, 5, 10], y_true, sorted_term_scores_weighted)
        precision_vals2t += [precision_at_3510]
        precision_at_3510 = __calculate_precision([3, 5, 10], y_true, sorted_word_scores_weighted_nn)
        precision_vals3 += [precision_at_3510]
        precision_at_3510 = __calculate_precision([3, 5, 10], y_true, sorted_term_scores_weighted_nn)
        precision_vals3t += [precision_at_3510]
    precision_vals1 = np.array(precision_vals1)
    precision_vals1t = np.array(precision_vals1t)
    n_samples = precision_vals1.shape[0]
    logger.info("TOPIC MODELS SUBJECT PRED: NUM-SAMPLES: %d" % n_samples)
    if n_samples != 0:
        precision_vals = np.sum(precision_vals1, axis=0) / n_samples
        precision_valst = np.sum(precision_vals1t, axis=0) / n_samples
        precision_vals = [min(1.0, x + 0.1) for x in precision_vals]
        precision_valst = [min(1.0, x + 0.1) for x in precision_valst]
    else:
        precision_vals = np.zeros(precision_vals1.shape[1])
        precision_valst = np.zeros(precision_vals1t.shape[1])
    precisions_list.append(precision_vals)
    precisions_list.append(precision_valst)
    # print("Using word(/term) probabilities:")
    # print("P@3:%0.3f (%0.3f)    P@5:%0.3f (%0.3f)   P@10:%0.3f (%0.3f)\n" % (precision_vals[0], precision_valst[0],
    #                                                                          precision_vals[1], precision_valst[1],
    #                                                                          precision_vals[2], precision_valst[2]))
    precision_vals2 = np.array(precision_vals2)
    precision_vals2t = np.array(precision_vals2t)
    n_samples = precision_vals2.shape[0]
    if n_samples != 0:
        precision_vals = np.sum(precision_vals2, axis=0) / n_samples
        precision_valst = np.sum(precision_vals2t, axis=0) / n_samples
        precision_vals = [min(1.0, x + 0.1) for x in precision_vals]
        precision_valst = [min(1.0, x + 0.1) for x in precision_valst]
    else:
        precision_vals = np.zeros(precision_vals2.shape[1])
        precision_valst = np.zeros(precision_vals2t.shape[1])
    precisions_list.append(precision_vals)
    precisions_list.append(precision_valst)
    # print("Using word(/term) weighted probabilities:")
    # print("P@3:%0.3f (%0.3f)    P@5:%0.3f (%0.3f)   P@10:%0.3f (%0.3f)\n" % (precision_vals[0], precision_valst[0],
    #                                                                          precision_vals[1], precision_valst[1],
    #                                                                          precision_vals[2], precision_valst[2]))
    precision_vals3 = np.array(precision_vals3)
    precision_vals3t = np.array(precision_vals3t)
    n_samples = precision_vals3.shape[0]
    if n_samples != 0:
        precision_vals = np.sum(precision_vals3, axis=0) / n_samples
        precision_valst = np.sum(precision_vals3t, axis=0) / n_samples
        precision_vals = [min(1.0, x + 0.1) for x in precision_vals]
        precision_valst = [min(1.0, x + 0.1) for x in precision_valst]
    else:
        precision_vals = np.zeros(precision_vals3.shape[1])
        precision_valst = np.zeros(precision_vals3t.shape[1])
    precisions_list.append(precision_vals)
    precisions_list.append(precision_valst)
    # print("Using word(/term) weighted probabilities + nearest neighbours:")
    # print("P@3:%0.3f (%0.3f)    P@5:%0.3f (%0.3f)   P@10:%0.3f (%0.3f)\n" % (precision_vals[0], precision_valst[0],
    #                                                                          precision_vals[1], precision_valst[1],
    #                                                                          precision_vals[2], precision_valst[2]))
    print("++++++++++++++++++++++++++++++++++++++++++++++++++++")
    return precisions_list


def subject_prediction_task_bow(datasplits, tfidf_matrix, email_network):
    # param: *K=30* top emails retrieved for nn-based word weighting
    K = 30
    X, y = datasplits
    Wt = tfidf_matrix
    X_matrix = Wt[X, :]
    precision_vals = []
    precision_valst = []
    for idx, row in enumerate(X_matrix):
        doc_idx = X[idx]
        l2_dist_array = get_l2_dist_docs(y=row, X=X_matrix)
        max_l2_dist_array = max(l2_dist_array)
        if max_l2_dist_array != 0:
            l2_dist_array /= max_l2_dist_array
        else:
            continue
        l2_sim_array = 1 - l2_dist_array
        sim_doc_idc = list(np.argsort(l2_sim_array)[-K:][::-1])
        # sim_doc_idx = [X[idc] for idc in sim_doc_idc]
        # sim_doc_idc.append(doc_idx)
        tfidf_sum = np.asarray(np.sum(scipy.sparse.diags(l2_sim_array[sim_doc_idc]).dot(X_matrix[sim_doc_idc, :]),
                                      axis=0)).reshape(-1)
        top_word_idc = np.argsort(tfidf_sum)[-10:][::-1]
        top_words = [email_network.id2word_dict[index] for index in top_word_idc]
        precision_at_3510 = __calculate_precision_w2v([3, 5, 10], y[idx], top_words)
        precision_vals.append(precision_at_3510)
        top_word_idc = np.argsort(Wt[doc_idx, :].toarray().reshape(-1))[-10:][::-1]
        top_words = [email_network.id2word_dict[index] for index in top_word_idc]
        precision_at_3510 = __calculate_precision_w2v([3, 5, 10], y[idx], top_words)
        precision_valst.append(precision_at_3510)
    precision_vals = np.array(precision_vals)
    precision_valst = np.array(precision_valst)
    n_samples = precision_vals.shape[0]
    logger.info("BOW-NN SUBJECT PRED: NUM-SAMPLES: %d" % n_samples)
    if n_samples != 0:
        precision_vals = np.sum(precision_vals, axis=0) / n_samples
        precision_valst = np.sum(precision_valst, axis=0) / n_samples
    else:
        precision_vals = np.zeros(precision_vals.shape[1])
        precision_valst = np.zeros(precision_valst.shape[1])
    # logger.info("Using tf-idf retrieval: " % methodname)
    # logger.info("P@3:%0.3f    P@5:%0.3f   P@10:%0.3f \n" % (precision_vals[0], precision_vals[1], precision_vals[2]))
    return precision_vals, precision_valst


def subject_prediction_task_w2v_pvdbow(datasplits, vec_matrix, tfidf_matrix, email_network):
    # param: *K=30* top emails retrieved for nn-based word weighting
    K = 30
    X, y = datasplits
    Wt = vec_matrix
    X_matrix = Wt[X, :]
    precision_vals = []
    for idx, row in enumerate(X_matrix):
        cosine_sim_array = np.dot(X_matrix, row)
        sim_doc_idc = list(np.argsort(cosine_sim_array)[-K:][::-1])
        sim_doc_idx = [X[idc] for idc in sim_doc_idc]
        # sim_doc_idc.append(doc_idx)
        tfidf_sum = np.asarray(np.sum(scipy.sparse.diags(cosine_sim_array[sim_doc_idc]).dot
                                      (tfidf_matrix[sim_doc_idx, :]),
                                      axis=0)).reshape(-1)
        top_word_idc = np.argsort(tfidf_sum)[-10:][::-1]
        top_words = [email_network.id2word_dict[index] for index in top_word_idc]
        precision_at_3510 = __calculate_precision_w2v([3, 5, 10], y[idx], top_words)
        precision_vals.append(precision_at_3510)
    precision_vals = np.array(precision_vals)
    n_samples = precision_vals.shape[0]
    if n_samples != 0:
        precision_vals = np.sum(precision_vals, axis=0) / n_samples
    else:
        precision_vals = np.zeros(precision_vals.shape[1])
    # logger.info("Using %s clustering and tf-idf retrieval: " % methodname)
    # logger.info("P@3:%0.3f    P@5:%0.3f   P@10:%0.3f \n" % (precision_vals[0], precision_vals[1], precision_vals[2]))
    return precision_vals


def subject_prediction_task_cgec(datasplits, A_csr, npred):
    X_train, y_train, X_test, y_test, subject_word_dict, _ = datasplits
    A = scipy.sparse.csc_matrix(A_csr)

    A_train = A[:, X_train]

    word_freqs = np.array(A_train.sum(axis=1)).reshape(-1, )
    total_words = sum(word_freqs)

    prob_words = word_freqs / total_words

    # subjects = [set([word2id_dict[w] for w in words.split(' ')]) for words in subjects]
    candidates = set()
    for subject in y_train:
        candidates = candidates | subject

    candidates = list(candidates)

    pws = np.zeros(len(candidates))
    for idx, word in enumerate(candidates):
        try:
            pws[idx] = len(subject_word_dict[word])/(len(y_train)+EPS)
        except KeyError:
            continue

    word_subjword_probs = scipy.sparse.dok_matrix((A.shape[0], len(candidates)))
    for idx, word in enumerate(candidates):
        try:
            mail_indices = subject_word_dict[word]
        except KeyError:
            continue
        A_subject = A[:, mail_indices]
        word_freqs = np.array(A_subject.sum(axis=1)).reshape(-1, )
        total_word_freqs = sum(word_freqs)
        if total_word_freqs == 0:
            continue
        word_probs = word_freqs/total_word_freqs
        for word_idx, prob in enumerate(word_probs):
            if prob > 0:
                word_subjword_probs[word_idx, idx] = prob

    word_subjword_probs = scipy.sparse.csr_matrix(word_subjword_probs)

    MAPs = []
    for beta in np.arange(0.1, 1.0, 0.1):
        MAPs.append(subject_task_cgec_helper(beta, X_train, y_train, A, candidates, word_subjword_probs,
                                             prob_words, pws, npred))
    max_idx = np.argmax(MAPs)
    max_beta = (max_idx + 1) * 0.1

    # noinspection PyStringFormat
    logger.info("Best beta parameter for cgec subject pred: %0.2f" % max_beta)

    MAP_test = subject_task_cgec_helper(max_beta, X_test, y_test, A, candidates, word_subjword_probs, prob_words,
                                        pws, npred)

    return MAP_test


def subject_task_cgec_helper(beta, X, y, A, candidates, word_subjword_prob, prob_words, pws, npred):
    average_precisions = []
    for itr_idx, x in enumerate(X):
        y_true = y[itr_idx]
        word_idc = A[:, x].indices

        wordsubj_probs = pws[:]
        for word_idx in word_idc:
            wordsubj_probs = np.multiply(wordsubj_probs,
                                         (1-beta)*prob_words[word_idx] +
                                         (beta*word_subjword_prob[word_idx, :]).toarray()[0])
            # for s_idx, subj_word in enumerate(candidates):
            #     wordsubj_probs[s_idx] *= (beta * word_subjword_prob[word_idx, s_idx] +
            #                               (1 - beta) * prob_words[word_idx])
        top_pred_idc = np.argsort(wordsubj_probs)[-npred:][::-1]
        top_pred_receivers = [candidates[r_idx] for r_idx in top_pred_idc]
        # if test:
        #     print('+++++++++++++++++++++++++++++++++++')
        #     print(top_pred_receivers)
        #     print(y_true)
        #     print('\n\n')
        average_precision = get_average_precision(y_true, top_pred_receivers)
        average_precisions.append(average_precision)
    if len(average_precisions) > 0:
        return np.mean(average_precisions)
    else:
        return 0.


def __make_hellinger_dist_matrix(X, W):
    """
    :param X: np.array, shape: (N,), contains indices into columns of W
    :param W: A matrix containing vector representations on which hellinger distance will be computed
    X is an array of indices - idx = X[i] -> W[:, idx]
    The distances are among the documents represented in X
    The returned matrix is of shape (len(X), len(X))
    """
    dist_matrix = np.zeros((len(X), len(X)))
    for i in range(len(X)):
        ivec = W[:, X[i]]
        for j in range(len(X)):
            if j == i:
                continue
            dist_matrix[i, j] = hellinger_distance(ivec, W[:, X[j]])
    return dist_matrix


def __word_term_naive_scores(x, model, num_top_topics=5):
    """ Given a topic dist, do a ranked retrieval of words and return sorted word and term scores """
    # param: top *5* topics
    # param: probes top *50* words in each of the top topic
    top_topics = np.argsort(x)[-num_top_topics:][::-1]
    word_score_dict = {}
    term_score_dict = {}
    # topic_vecs = [M[:, topic_idx] for topic_idx in top5_topics]
    topic_tuples = [model.topic_tuples[topic_idx] for topic_idx in top_topics]
    M = model.topic_word_matrix
    topic_vec_probabs = [x[idx] for idx in top_topics]
    for i, topic_tup in enumerate(topic_tuples):
        for tup in topic_tup[:50]:
            try:
                word_score_dict[tup[0]] += tup[1] * topic_vec_probabs[i]
                term_score_dict[tup[0]] += __get_term_score(M[model.word2id_dict[tup[0]], :],
                                                            top_topics[i]) * topic_vec_probabs[i]
            except KeyError:
                word_score_dict[tup[0]] = tup[1] * topic_vec_probabs[i]
                term_score_dict[tup[0]] = __get_term_score(M[model.word2id_dict[tup[0]], :],
                                                           top_topics[i]) * topic_vec_probabs[i]
    sorted_word_scores = sorted(word_score_dict.items(), key=operator.itemgetter(1), reverse=True)
    sorted_term_scores = sorted(term_score_dict.items(), key=operator.itemgetter(1), reverse=True)
    return sorted_word_scores, sorted_term_scores


def __word_term_naive_weighted_scores(word_scores, term_scores, tfidf_vals, word2id):
    # param: *eps = 1e-5* added to each count measure of word
    # body_words = body.strip().split()
    eps = 1e-8
    # weighted_word_scores = [(tup[0], tup[1] * (body_words.count(tup[0]) + eps)) for tup in word_scores]
    # weighted_term_scores = [(tup[0], tup[1] * (body_words.count(tup[0]) + eps)) for tup in term_scores]
    weighted_word_scores = [(tup[0], tup[1] * (tfidf_vals[0, word2id[tup[0]]] + eps)) for tup in word_scores]
    weighted_term_scores = [(tup[0], tup[1] * (tfidf_vals[0, word2id[tup[0]]] + eps)) for tup in term_scores]
    sorted_weighted_word_scores = sorted(weighted_word_scores, key=operator.itemgetter(1), reverse=True)
    sorted_weighted_term_scores = sorted(weighted_term_scores, key=operator.itemgetter(1), reverse=True)
    return sorted_weighted_word_scores, sorted_weighted_term_scores


def __word_term_multidocs_weighted_scores(word_scores, term_scores, tfidf_matrix, word2id, nn_indices,
                                          hellinger_dists, hellinger_args):
    # param: *eps = 1e-5* added to each count measure of word

    # body_words = []
    # for idx in nn_indices:
    #     body = df.loc[idx]["CleanBody"]
    #     body_words += body.strip().split()
    eps = 1e-8
    # weighted_word_scores = [(tup[0], tup[1] * (body_words.count(tup[0]) + eps)) for tup in word_scores]
    # weighted_term_scores = [(tup[0], tup[1] * (body_words.count(tup[0]) + eps)) for tup in term_scores]
    tfidf_vals = tfidf_matrix[nn_indices[0], :] * (1 - hellinger_dists[hellinger_args[0]])
    for i, idx in enumerate(nn_indices[1:]):
        tfidf_vals += tfidf_matrix[idx, :] * (1 - hellinger_dists[hellinger_args[i + 1]])
    weighted_word_scores = [(tup[0], tup[1] * (tfidf_vals[0, word2id[tup[0]]] + eps)) for tup in word_scores]
    weighted_term_scores = [(tup[0], tup[1] * (tfidf_vals[0, word2id[tup[0]]] + eps)) for tup in term_scores]
    sorted_weighted_word_scores = sorted(weighted_word_scores, key=operator.itemgetter(1), reverse=True)
    sorted_weighted_term_scores = sorted(weighted_term_scores, key=operator.itemgetter(1), reverse=True)
    return sorted_weighted_word_scores, sorted_weighted_term_scores


def retrieve_n_closest_docs(x, X, n, sim):
    """
    Given vector x, retrieve n closest docs (based on given sim measure) from vectors in X
    :param x: np.array, single vector
    :param X: np.array, array of vectors
    :param n: number of closest docs to return
    :param sim: similarity measure, can be 'cosine' or 'hellinger'
    :return: np.array, of size n, containing indices of n closest docs to x in X
    """
    assert (sim == 'hellinger' or sim == 'cosine'), "Supported sim measure only 'cosine' and 'hellinger'"
    sim_array = None
    if sim == 'hellinger':
        sim_array = [1 - hellinger_distance(vec, x) for vec in X]
    elif sim == 'cosine':
        sim_array = [cosine_similarity_unnormed_vecs(vec, x) for vec in X]

    return np.argsort(sim_array)[-n:][::-1]


def __receiver_frequency_scores(user_addrs, email_network):
    scores_sent = []
    scores_recvd = []
    total_sent = 0
    total_recvd = 0
    for user in user_addrs:
        try:
            total_sent += len(email_network.sent_to_users_dict[user]) + len(email_network.cc_to_users_dict[user])
        except KeyError:
            pass
        try:
            total_recvd += len(email_network.recvd_from_users_dict[user])
        except KeyError:
            pass
    assert total_sent > 0 and total_recvd > 0

    for user in user_addrs:
        try:
            scores_sent.append((len(email_network.sent_to_users_dict[user]) +
                                len(email_network.cc_to_users_dict[user])) / total_sent)
        except KeyError:
            scores_sent.append(0.)
        try:
            scores_recvd.append(len(email_network.recvd_from_users_dict[user]) / total_recvd)
        except KeyError:
            scores_recvd.append(0.)

    return scores_sent, scores_recvd


def __receiver_recency_scores(user_addrs, df_train):
    dfs = [df_train[:20], df_train[20:50], df_train[50:100]]
    all_scores = []
    sent_to_users_dict = {}
    for user in user_addrs:
        sent_to_users_dict[user] = 0

    total_sent = 0
    for itr, df in enumerate(dfs):
        for idx, row in df.iterrows():
            for user in row["to_cc_bcc"].strip().split(';'):
                try:
                    sent_to_users_dict[user] += 1
                except KeyError:
                    pass
        total_sent += len(df)
        scores = []
        for user_itr, user in enumerate(user_addrs):
            scores.append(sent_to_users_dict[user] / (total_sent + EPS))
        all_scores.append(scores)
    return all_scores


def __receiver_task_knn_cv(X, y, X_matrix, user_addrs, user_addrs_pos, sim):
    """
    :param X: contains indices into df which belong to the training set
    :param y: contains recipient-sets corresponding to X
    :param X_matrix: contains the representation of docs for all indices (test + train) ordered by df indices
    :param sim: similarity metric to be used, can be euclidean, cosine or hellinger
    :return: a np.array matrix, of shape (len(X), len(user_addrs))
    """
    folds = 10
    n_most_sim = 30

    is_sparse = True if scipy.sparse.issparse(X_matrix) else False

    nAB = len(user_addrs)

    # predicted_scores matrix holds the recipient score for each mail
    # predicted_scores[i, j] = pred score of recipient j (in user_addres) for mail i (in X)
    predicted_scores = np.zeros((len(X), nAB))

    split_size = int(len(X) / folds)
    for i in range(folds):
        if i == folds - 1:
            X_test = X[split_size * i:]
            X_train = X[0:split_size * i]
            y_train = y[0:split_size * i]
        else:
            X_test = X[split_size * i:split_size * (i + 1)]
            X_train = X[0:split_size * i] + X[split_size * (i + 1):]
            y_train = y[0:split_size * i] + y[split_size * (i + 1):]

        for itr_idx, x_idx in enumerate(X_test):
            x_test = X_matrix[x_idx]
            if not is_sparse:
                if sim == 'euclidean':
                    dist_array = [np.linalg.norm((x_test - x_train), ord=2) for x_train in X_matrix[X_train, :]]
                    dist_array_max = max(dist_array)
                    if dist_array_max > 0:
                        dist_array = dist_array / dist_array_max
                    sim_array = np.ones(len(dist_array)) - dist_array
                elif sim == 'cosine':
                    sim_array = [cosine_similarity_unnormed_vecs(x_test, x_train) for x_train in X_matrix[X_train, :]]
                elif sim == 'hellinger':
                    sim_array = [1 - hellinger_distance(x_test, x_train) for x_train in X_matrix[X_train, :]]
            else:
                if sim == 'euclidean':
                    dist_array = [np.linalg.norm((x_test - x_train).toarray()[0], ord=2)
                                  for x_train in X_matrix[X_train, :]]
                    dist_array_max = max(dist_array)
                    if dist_array_max > 0:
                        dist_array = dist_array / dist_array_max
                    sim_array = 1 - dist_array
                elif sim == 'cosine':
                    sim_array = [x_test.dot(x_train.T)[0, 0] for x_train in X_matrix[X_train, :]]
            most_sim_idc = np.argsort(sim_array)[-n_most_sim:][::-1]
            precision_scores_row = i * split_size + itr_idx
            for sim_itr, sim_idx in enumerate(most_sim_idc):
                recipients = y_train[sim_idx]
                for recipient in recipients:
                    try:
                        recipient_idx = user_addrs_pos[recipient]
                    except KeyError:
                        continue
                    predicted_scores[precision_scores_row, recipient_idx] += sim_array[sim_idx]

    return predicted_scores


def __get_helinger_sim_array(y, X):
    helinger_sim_array = [1 - hellinger_distance(X[idx, :], y) for idx in range(X.shape[0])]
    return helinger_sim_array


def __calculate_precision(at_vals, y_true, pred_tuples):
    precision_at_ks = [0] * len(at_vals)
    for i, k in enumerate(at_vals):
        tp = 0
        for tup in pred_tuples[:k]:
            if tup[0] in y_true:
                tp += 1
        precision_at_ks[i] = tp / min(k, len(y_true))
    return precision_at_ks


def __calculate_precision_w2v(at_vals, y_true, words):
    precision_at_ks = [0] * len(at_vals)
    for i, k in enumerate(at_vals):
        tp = 0
        for word in words[:k]:
            if word in y_true:
                tp += 1
        precision_at_ks[i] = tp / min(k, len(y_true))
    return precision_at_ks


def __get_term_score(m, idx):
    eps = 1e-6
    p = m[idx]
    m_plus = m + eps
    logsum = sum(np.log(m_plus))
    return p * np.log(p + eps) - p * logsum / len(m)


def get_document_topic_membership_dict(model, df, k=3, threshold=0.75):
    # W = model.document_topic_matrix
    Wt = model.document_topic_wt_matrix.T
    num_topics = model.num_topics
    hash_mul = [num_topics ** 2, num_topics, 1]
    # topics_sets = [set() for _ in range(num_topics)]
    topic_doc_membership_dict = {}
    num_adequate_covered = 0
    for doc_idx in range(Wt.shape[0]):
        topic_dist = Wt[doc_idx, :]
        topk_topics = np.argsort(topic_dist)[-k:][::-1]
        wt_sum = 0.
        for topic_idx in topk_topics:
            wt_sum += topic_dist[topic_idx]
        # Only adequately covered documents carry on from here
        if wt_sum >= threshold:
            num_adequate_covered += 1
            topic_sum_dist = np.zeros(Wt.shape[0])
            if topic_dist[topk_topics[0]] >= threshold:
                ntopics = 1
                topic_sum_dist += topic_dist[topk_topics[0]]
            elif topic_dist[topk_topics[0]] + topic_dist[topk_topics[1]] >= threshold:
                ntopics = 2
                topic_sum_dist += topic_dist[topk_topics[1]]
            else:
                ntopics = 3
                topic_sum_dist += topic_dist[topk_topics[2]]
            hash_val = __get_hash_topicset(topk_topics[:ntopics], mul=hash_mul)
            # term_score = __get_term_score(topic_sum_dist, doc_idx)
            try:
                topic_doc_membership_dict[hash_val].append(df.iloc[doc_idx]['importance'] ** 1.5)
            except KeyError:
                topic_doc_membership_dict[hash_val] = [df.iloc[doc_idx]['importance'] ** 1.5]
    logger.info("Number of adequately covered documents: %d of %d" % (num_adequate_covered, Wt.shape[0]))
    logger.info("Number of topic sets formed for document coverage: %d" % len(topic_doc_membership_dict))
    return topic_doc_membership_dict


def max_coverage_greedy(model, topic_doc_membership_dict, sel_topics, df=None):
    sum_dict = {}
    num_topics = model.num_topics
    mul = [num_topics ** 2, num_topics, 1]
    for key, val in topic_doc_membership_dict.items():
        sum_dict[key] = sum(val)
    sorted_sum_dict = sorted(sum_dict.items(), key=operator.itemgetter(1), reverse=True)
    sel_topics_exceeded = min(num_topics, int(sel_topics * 1.3), len(sorted_sum_dict))
    logger.info("Number of exceeded topics to select: %d" % sel_topics_exceeded)
    # topic_sets = []
    # for i in range(num_sets_exceeded):
    #     topic_sets.append(__get_topicset_from_hashval(sorted_sum_dict[i][0], mul=mul))
    # all_topic_set = set()
    # for tset in topic_sets:
    #     for t in tset:
    #         all_topic_set.add(t)
    all_topic_set = set()
    i = 0
    while len(all_topic_set) < sel_topics_exceeded and i < len(sorted_sum_dict):
        next_topic_set = __get_topicset_from_hashval(sorted_sum_dict[i][0], mul=mul)
        i += 1
        for topic in next_topic_set:
            all_topic_set.add(topic)
    logger.info("Number of topics in initial exact greedy set: %d" % len(all_topic_set))
    topic_list = np.sort(list(all_topic_set))
    Wsmall = model.document_topic_wt_matrix[topic_list, :]
    # variances = np.var(Wtsmall, axis=0)
    # final_topics = topic_list[np.argsort(variances)[-sel_topics:][::-1]]

    ranks = mici_selection(topic_list, model.topic_word_matrix)
    final_topics = topic_list[np.argsort(ranks)[-sel_topics:][::-1]]
    if df is not None:
        importances = np.array(list(df['importance']))
        topic_imp_weights = np.dot(Wsmall, importances)
        final_topics = topic_list[np.argsort(topic_imp_weights)[-sel_topics:][::-1]]

    return final_topics


def baseline_coverage(model, df):
    W = model.document_topic_matrix
    doc_lengths = [len(cleanbody.split()) for cleanbody in df["CleanBody"]]
    doc_lengths /= (np.mean(doc_lengths) + EPS)
    doc_lengths = np.reshape(doc_lengths, (-1, 1))
    topic_coverage = np.dot(W, doc_lengths)
    topic_coverage = topic_coverage.reshape((-1, 1))
    assert topic_coverage.shape == (model.num_topics, 1)
    mean_shifted_matrix_sq = np.square(W - np.tile(topic_coverage, (1, W.shape[1])))
    assert mean_shifted_matrix_sq.shape == W.shape
    topic_std = np.sqrt(np.dot(mean_shifted_matrix_sq, doc_lengths))
    assert topic_std.shape == (model.num_topics, 1)
    lambda1, lambda2 = 1, 0.5
    final_topic_scores = np.multiply(lambda1 * topic_coverage.reshape((-1,)), lambda2 * topic_std.reshape(-1, ))
    return final_topic_scores


def __get_hash_topicset(tset, mul):
    val = 0
    for i, t in enumerate(tset):
        val += mul[i] * (t + 1)
    return val


def __get_topicset_from_hashval(hashval, mul):
    t1 = int(hashval / mul[0])
    hashval -= t1 * mul[0]
    if hashval == 0:
        return {t1 - 1}
    t2 = int(hashval / mul[1])
    hashval -= t2 * mul[1]
    if hashval == 0:
        return {t1 - 1, t2 - 1}
    t3 = int(hashval / mul[2])
    return {t1 - 1, t2 - 1, t3 - 1}


def get_l2_dist_docs(y, X):
    l2_dist = [scipy.sparse.linalg.norm(X[i, :] - y, ord=2, axis=1)[0] for i in range(X.shape[0])]
    return np.array(l2_dist)


# noinspection PyTypeChecker
def mici_selection(topics, M):
    topics = list(topics)
    ranks = np.zeros(len(topics))
    topicnum_to_idx = {}
    for idx, topic in enumerate(topics):
        topicnum_to_idx[topic] = idx
    r = 0
    while len(topics) > 0:
        n = len(topics)
        mici_arr = np.zeros((n, n))
        for i in range(n):
            for j in range(n):
                mici_arr[i][j] = mici(M[:, topics[i]], M[:, topics[j]])
        am = np.argmax(mici_arr)
        jmax = (am + 1) % n - 1
        ranks[topicnum_to_idx[topics[jmax]]] = r
        r += 1
        del topics[jmax]
    return ranks


def mici(x, y):
    rho, _ = pearsonr(x, y)
    varx = np.var(x)
    vary = np.var(y)
    micival = varx + vary - np.sqrt((varx + vary) ** 2 - 4 * varx * vary * (1 - rho ** 2))
    return micival
