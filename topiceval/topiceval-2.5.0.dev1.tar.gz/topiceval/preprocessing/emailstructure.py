"""
This module explores the structure in user's inbox.
"""

from __future__ import division
from __future__ import print_function

from topiceval import makewordvecs
from topiceval import allparams
from topiceval import utils

# import pandas
import numpy as np
import scipy.sparse
from sklearn.feature_extraction.text import TfidfVectorizer

import operator
import logging
import warnings
from six.moves import xrange
warnings.filterwarnings("ignore", 'This pattern has match groups')

logger = logging.getLogger(__name__)


class EmailUser(object):
    def __init__(self, name, nsent_to, nsent_cc, nrecvd_from):
        self.name = name
        self.nsent_to = nsent_to
        self.nsent_cc = nsent_cc
        self.recvd_from = nrecvd_from


class EmailNetwork(object):
    def __init__(self, df, id2word_dict, wordvecs):
        self.df = df
        self.username = self.__get_username()
        self.id2word_dict = id2word_dict
        vocabulary = list(self.id2word_dict.values())
        self.vocab_set = set(vocabulary)

        tfidfvectorizer = TfidfVectorizer(vocabulary=vocabulary)
        self.tfidf_matrix = tfidfvectorizer.fit_transform(list(df["CleanBody"]))
        assert scipy.sparse.isspmatrix_csr(self.tfidf_matrix)

        self.tfidf_matrix_normed = \
            scipy.sparse.csr_matrix(utils.l2_normalize_lil_matrix(scipy.sparse.lil_matrix(self.tfidf_matrix)))

        self.word2id = tfidfvectorizer.vocabulary_
        # self.idf = tfidfvectorizer.idf_
        self.id2word_dict = {}
        for word in self.word2id:
            self.id2word_dict[self.word2id[word]] = word

        # wordvec_dict[word] = it's vector
        self.wordvec_dict = self.__make_word2vec_dict(wordvecs)
        # TF-IDF averaged word2vec for each document
        self.avg_word2vec_matrix = self.__make_avg_word2vec_matrix(wordvecs)
        num_topics = len(list(self.wordvec_dict.values())[0])

        # Making PV-DBOW matrix
        self.pvdbow_matrix = makewordvecs.make_pvdbow(df["CleanBody"], num_topics)

        self.sent_to_users, self.cc_to_users, self.recvd_from_users, self.sent_to_users_dict, \
            self.cc_to_users_dict, self.recvd_from_users_dict = self.__get_all_users()
        self.all_users = self.sent_to_users | self.cc_to_users | self.recvd_from_users
        self.user_importance_score_dict = {}
        self.top3_users = self.__get_top3_users()

        self.custom_folders, self.folders_idc_dict = self.__get_custom_folders()
        self.avg_folder_len = self.__get_avg_folder_len()
        self.big_folders = self.__get_big_folders()

        self.three_imp_folders = None
        self.three_time_periods = None
        self.temporally_sound = False
        # if len(self.custom_folders) < 3 or self.avg_folder_len < allparams.frequent_filer_folder_len \
        #         or len(self.big_folders) < 3:
        #     self.frequent_filer = False
        if len(self.big_folders) < 3:
            self.frequent_filer = False
        else:
            self.frequent_filer = True
        return

    def __get_username(self):
        """ Assign the sender with most emails sent as the user name """
        sender_stats = self.df[self.df["FolderType"] == "Sent Items"].groupby("SenderName")["SentOn"].count()
        sender_stats_dict = dict(zip(sender_stats.index, sender_stats.data))
        sorted_sender_stats = sorted(sender_stats_dict.items(), key=operator.itemgetter(1), reverse=True)
        username = str(sorted_sender_stats[0][0])
        if username.upper() == "<UNKNOWN>":
            logger.warning("Username detected as <UNKNOWN>! Changing to second highest sender...")
            try:
                username = str(sorted_sender_stats[1][0])
            except IndexError:
                logger.error("Username could not be detected!")
        return username

    def __get_all_users(self):
        sent_to_users = set()
        cc_to_users = set()
        recvd_from_users = set()

        emails_sent = self.df[self.df["SenderName"] == self.username]
        sent_to_users_dict = {}
        for _, row in emails_sent[["To", "idx"]].iterrows():
            text = row[0]
            idx = row[1]
            to = [user.strip() for user in text.split(";") if user != '']
            for item in to:
                if item == self.username or item.upper() == "<UNKNOWN>":
                    continue
                sent_to_users.add(item)
                try:
                    sent_to_users_dict[item] += [idx]
                except KeyError:
                    sent_to_users_dict[item] = [idx]

        cc_to_users_dict = {}
        for _, row in emails_sent[["CC", "idx"]].iterrows():
            text = row[0]
            idx = row[1]
            cc = [user.strip() for user in text.split(";") if user != '']
            for item in cc:
                if item == self.username or item.upper() == "<UNKNOWN>":
                    continue
                cc_to_users.add(item)
                try:
                    cc_to_users_dict[item] += [idx]
                except KeyError:
                    cc_to_users_dict[item] = [idx]

        emails_except_sent = self.df[self.df["FolderType"] != "Sent Items"]
        recvd_from_users_dict = {}
        for _, row in emails_except_sent[["SenderName", "idx"]].iterrows():
            text = row[0]
            idx = row[1]
            text = text.strip()
            if text == self.username or text.upper() == "<UNKNOWN>" or text == '':
                continue
            recvd_from_users.add(text)
            try:
                recvd_from_users_dict[text] += [idx]
            except KeyError:
                recvd_from_users_dict[text] = [idx]

        # all_recvd_counts = emails_except_sent.groupby("SenderName")["SentOn"].count()
        # recvd_from_users_dict = dict(zip(all_recvd_counts.index, all_recvd_counts.data))
        # recvd_from_users_dict.pop('<UNKNOWN>', None)
        # for user in all_recvd_counts.index:
        #     if user != self.username and user.upper() != "<UNKNOWN>":
        #         recvd_from_users.add(user)

        all_users = sent_to_users | cc_to_users | recvd_from_users
        for user in all_users:
            try:
                _ = sent_to_users_dict[user]
            except KeyError:
                sent_to_users_dict[user] = []
            try:
                _ = cc_to_users_dict[user]
            except KeyError:
                cc_to_users_dict[user] = []
            try:
                _ = recvd_from_users_dict[user]
            except KeyError:
                recvd_from_users_dict[user] = []

        return sent_to_users, cc_to_users, recvd_from_users, sent_to_users_dict, cc_to_users_dict, recvd_from_users_dict

    def __get_top3_users(self):
        sent_to_users_len_dict = {}
        for key in self.sent_to_users_dict:
            sent_to_users_len_dict[key] = len(self.sent_to_users_dict[key])
        sorted_sent_to_users = sorted(sent_to_users_len_dict.items(), key=operator.itemgetter(1), reverse=True)
        top_users = []
        for tup in sorted_sent_to_users[:3]:
            top_users.append(tup[0])
        return top_users

    def __get_custom_folders(self):
        all_folders = set(list(self.df["FolderType"].unique()))
        try:
            all_folders.remove('Inbox')
        except KeyError:
            pass
        try:
            all_folders.remove('Sent Items')
        except KeyError:
            pass
        try:
            all_folders.remove('Archive')
        except KeyError:
            pass
        folders_idc_dict = {}
        for folder in all_folders:
            folders_idc_dict[folder] = []
        for _, row in self.df[["FolderType", "idx"]].iterrows():
            folder = row[0]
            if folder not in all_folders:
                continue
            idx = row[1]
            folders_idc_dict[folder] += [idx]
        return all_folders, folders_idc_dict

    def __get_avg_folder_len(self):
        folder_idc = list(self.folders_idc_dict.values())
        total_len = 0
        for idc_list in folder_idc:
            total_len += len(idc_list)
        if len(folder_idc) > 0:
            return total_len / len(folder_idc)
        else:
            return 0

    def __get_big_folders(self):
        big_folders = set()
        for folder in self.folders_idc_dict:
            # noinspection PyTypeChecker
            # if len(self.folders_idc_dict[folder]) > max(allparams.big_folder_abs_size,
            #                                             self.avg_folder_len*allparams.big_folder_rel_fraction):
            if len(self.folders_idc_dict[folder]) > allparams.big_folder_abs_size:
                big_folders.add(folder)
        return big_folders

    def __make_word2vec_dict(self, wordvecs):
        wordvec_dict = {}
        for word in self.vocab_set:
            try:
                vec = wordvecs[word]
                wordvec_dict[word] = vec
            except KeyError:
                pass
        return wordvec_dict

    def __make_avg_word2vec_matrix(self, wordvecs):
        w2v = wordvecs.syn0
        indices = [idx for idx in range(len(self.id2word_dict)) if self.id2word_dict[idx] in wordvecs]
        w2v = w2v[indices, :]
        eps = 1e-9
        tfidf_matrix_l1normed = self.tfidf_matrix.copy()
        indptr = tfidf_matrix_l1normed.indptr
        for rownum in xrange(tfidf_matrix_l1normed.shape[0]):
            tfidf_matrix_l1normed.data[indptr[rownum]:indptr[rownum + 1]] /= \
                (sum(tfidf_matrix_l1normed.data[indptr[rownum]:indptr[rownum + 1]]) + eps)
        avg_matrix = tfidf_matrix_l1normed.dot(w2v)
        avg_matrix = utils.l2_normalize_2d_array(avg_matrix)
        return avg_matrix

    def make_user_importance_score_dict(self):
        eps = 1e-3
        user_importance_score_dict = {}
        df = self.df
        for user in self.all_users:
            # noinspection PyBroadException
            try:
                usent = len(df[(df["FolderType"] == "Sent Items") & (df["to_cc_bcc"].str.contains(user))])
                urecvd = len(df[(df["FolderType"] != "Sent Items") & (df["SenderName"] == user)])
                user_importance_score_dict[user] = (usent + 1)*(usent + urecvd)/(urecvd + 1)
            except:
                user_importance_score_dict[user] = eps
        user_imp_maxval = max(list(user_importance_score_dict.values()))
        for key in user_importance_score_dict:
            user_importance_score_dict[key] = user_importance_score_dict[key]/user_imp_maxval
        self.user_importance_score_dict = user_importance_score_dict
        return

    def make_importance_field(self):
        df = self.df
        importance_field = []
        user_importance_dict = self.user_importance_score_dict
        read_reply_fraction = self.__get_read_reply_fraction()
        for idx, row in df.iterrows():
            imp = 0.
            if row["FolderType"] == 'Sent Items':
                imp += 1
                nusers = 0
                userimp = 0.
                for user in row["to_cc_bcc"].strip().split(';'):
                    try:
                        userimp += user_importance_dict[user]
                        nusers += 1
                    except KeyError:
                        pass
                if nusers > 0:
                    imp += userimp / nusers
            else:
                if row["UnRead"] == "True":
                    imp = 0.
                else:
                    if row['replied'] or row['thread_replied']:
                        imp += 1.
                    # if row["UnRead"] == "False":
                    #     imp += read_reply_fraction
                    userimp = 0.
                    user = row["SenderName"].strip()
                    try:
                        userimp += user_importance_dict[user]
                        imp += userimp
                    except KeyError:
                        pass

            importance_field.append(imp)
        self.df["importance"] = importance_field
        return

    def __get_read_reply_fraction(self):
        eps = 1e-3
        df = self.df[self.df["FolderType"] != "Sent Items"]
        read = len(df[df["UnRead"] == "False"])
        replied = len(df[df["replied"] == True])
        fraction = replied / (read+eps)
        logger.info("Read-reply fraction = %d/%d = %0.4f" % (replied, read, fraction))
        return fraction

    def make_three_imp_folders(self):
        big_folders_arr = np.array(list(self.big_folders))
        imp = np.array([sum(self.df[self.df['FolderType'] == folder]['importance']) for folder in big_folders_arr])
        maximparg = np.argsort(imp)[-3:][::-1]
        three_imp_folders = big_folders_arr[maximparg]
        self.three_imp_folders = three_imp_folders
        return

    def make_three_time_periods(self):
        months = [[], [], []]
        for idx, row in self.df.iterrows():
            if row["diff"].days < 60:
                months[0].append(idx)
            elif row["diff"].days < 120:
                months[1].append(idx)
            elif row["diff"].days < 180:
                months[2].append(idx)
        if min(len(months[0]), len(months[1]), len(months[2])) > 20:
            self.temporally_sound = True
        self.three_time_periods = months
        return
