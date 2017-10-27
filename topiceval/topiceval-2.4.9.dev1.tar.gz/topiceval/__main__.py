"""
Author: Avikalp Srivastava

This forms the main file for an application that extracts user emails from outlook, cleans and preprocesses them,
applies three topic models, namely LDA, Thresholded SVD and Sparse Dictionary Learning + Sparse Coding,
to show topics to users for interpretability and quality evalution. After that it runs some downstream
assistance tasks using document representations obtained from topic models as well as BOW, averaged word2vec,
and pv-dbow

For running the application, you have to run the command "python -m topiceval" from the topiceval directory
"""


# TODO: Recipient prediction check and confirm
# TODO: Importance score correction
# TODO: In main.py, removing loading of pre-saved topic models
# TODO: In params, revert big folder sizes to original
# TODO: In subject task, decide number of closest docs to include (currently its 20)
# TODO: Ensure no personal info shows up in the report
# TODO: Ensure all tasks are running in downstream in main.py, remove False from if conditions
# TODO: In allparams.py, big_folder_size to be set back to 50
# TODO: In taskeval, Adjust fraction (line 54), adjust test splits, in params go back to default, remove df.to_pickle
# TODO: In evalapplication, uncomment call to othercoherence, below uncomment all tasks
# TODO: In emailprocess, uncomment line 70; if threaded: word_min_doc_freq *= 2


from __future__ import division
from __future__ import print_function

import argparse
import logging
import webbrowser
import os
import warnings
import sys
import time
import traceback
import six
from time import sleep

try:
    import win32com.client as win32
except ImportError:
    win32 = None

from topiceval import emailextraction as emailextraction
from topiceval.lda.gensimlda import LDA
from topiceval.dictionarylearning.bcd import BCD
from topiceval.thresholdedsvd.tsvd import TSVD
from topiceval.usereval import task_evaluation
from topiceval.usereval import topiceval_application as application

import pyLDAvis.gensim
import numpy as np
from prettytable import PrettyTable

logger = logging.getLogger('topiceval')

# Will be decided based on the arguments passed
logging_filename = ''

# All reports will be sent here
send_reports_at_address = 'ssrajan@microsoft.com'


def main():
    """
    Learn topic models with given parameters on user emails and launch evaluation application
    :return: None
    """
    global logging_filename

    # Parsing command line arguments
    parser = argparse.ArgumentParser(description='topic-model-evaluation-package')
    parser.add_argument('-numtopics', help='specify number of topics to learn', type=int, default=100)
    parser.add_argument('-numtopicseval', help='specify number of topics to evaluate per model', type=int, default=15)
    parser.add_argument('-usethreads', help='whether to use threaded mails or single ones', type=int, default=0)
    parser.add_argument('-makeWtsvd', help='whether to make W matrix for TSVD model', type=int, default=1)
    parser.add_argument('-excludefolders', help='comma separated folder names to exclude', type=str, default="")
    parser.add_argument('-skipeval', help='skip user evaluation part', type=int, default=0)
    # parser.add_argument('-reuse', help='store items for reuse', type=int, default=0)
    parser.add_argument('-save', help='save computed items', type=int, default=1)
    parser.add_argument('-load', help='load from previously saved items', type=int, default=0)
    parser.add_argument('-smalleval', help='small evaluation', type=int, default=0)

    args = vars(parser.parse_args())
    num_topics = args['numtopics']
    num_topics_eval = args['numtopicseval']
    threaded = args['usethreads']
    makeWtsvd = args['makeWtsvd']
    excludefolders = args['excludefolders']
    save = args['save']
    load = args['load']
    skipeval = args['skipeval']
    smalleval = args['smalleval']

    if num_topics_eval > num_topics:
        logger.info("Number of topics to be evaluated can't be > total topics, clipping num_topics_eval")
        num_topics_eval = num_topics

    # Changing 0/1 values to boolean
    threaded = bool(threaded)
    makeWtsvd = bool(makeWtsvd)
    save = bool(save)
    load = bool(load)
    skipeval = bool(skipeval)
    smalleval = bool(smalleval)

    # Now we have the parameters to name the file where we'll save the results
    logging_filename = '/topiceval_results_%dthreaded_%dtopics_%dtopicsEval.log' % \
                       (threaded, num_topics, num_topics_eval)

    if not smalleval:
        print("\nWelcome! Email extraction + Learning models will take 15-25 minutes, after which you'll be shown a brief"
              " summary of evaluation procedure.")
        print("\nPlease feel free to let the application running in background, and check after some time to provide "
              "evaluation!")
        time.sleep(5)

    # Extract emails and get directory name where temporary data is stored, and EmailNetwork object storing information
    # about user mailbox
    dirname, email_network, A = \
        emailextraction.extract_usermails(threaded=threaded, save=save, load=load, excludefolders=excludefolders,
                                          num_topics=num_topics)

    datasetname = "userdata"

    with open('.' + logging_filename, 'r') as file_handle:
        initial_logging_info = file_handle.read()
    # sendmail(exception_str='', traceback_str='', addr=send_reports_at_address)

    ''' Learn all 3 models '''
    logger.debug("Starting to learn all 3 topic models on emails...")
    logger.debug("Started LDA")
    import pickle
    if load and os.path.isfile('./lda.pickle'):
        with open("./lda.pickle", "rb") as handle:
            ldamodel = pickle.load(handle)
    else:
        ldamodel = LDA(datasetname=datasetname, id2word_dict_path=dirname + "id2word_dict.pickle",
                       corpus_path=dirname + "corpus.npy", num_topics=num_topics, evaluation_mode=True)
        if save:
            with open("./lda.pickle", "wb") as handle:
                pickle.dump(ldamodel, handle, protocol=pickle.HIGHEST_PROTOCOL)
    logger.debug("Finished LDA")
    logger.debug("Started TSVD")
    if load and os.path.isfile('./tsvd.pickle'):
        with open("./tsvd.pickle", "rb") as handle:
            tsvdmodel = pickle.load(handle)
    else:
        tsvdmodel = TSVD(datasetname=datasetname, id2word_dict_path=dirname + "id2word_dict.pickle",
                         corpus_path=dirname + "corpus.npy", num_topics=num_topics, evaluation_mode=makeWtsvd)
        if save:
            with open("./tsvd.pickle", "wb") as handle:
                pickle.dump(tsvdmodel, handle, protocol=pickle.HIGHEST_PROTOCOL)
    logger.debug("Finished TSVD")
    logger.debug("Started BCD")
    if load and os.path.isfile('./bcd.pickle'):
        with open("./bcd.pickle", "rb") as handle:
            bcdmodel = pickle.load(handle)
    else:
        bcdmodel = BCD(datasetname=datasetname, id2word_dict_path=dirname + "id2word_dict.pickle",
                       corpus_path=dirname + "corpus.npy", num_topics=num_topics, evaluation_mode=True)
        if save:
            with open("./bcd.pickle", "wb") as handle:
                pickle.dump(bcdmodel, handle, protocol=pickle.HIGHEST_PROTOCOL)
    logger.debug("Finished BCD")
    # sendmail(exception_str='', traceback_str='', addr=send_reports_at_address)
    logger.debug("Completed all 3 topic models successfully, launching application...")

    models = [ldamodel, tsvdmodel, bcdmodel]

    if smalleval:
        for model in models:
            topic_model_to_csv(model)

    if not skipeval:
        print('\n----------------------------------------------------------------------------------')
        print("USER EVALUATION CONCISE SUMMARY")
        print("\n*** PHASE 1 ***")
        print("-> 100 topic visualization will open in browser")
        print("-> 3 different windows, each showing a selection 16 topics chosen from above 100 based on diff algos, "
              "have to be ranked on defined parameters")
        print("\n*** PHASE 2 ***")
        print("-> After 5-10 minutes of background calculation after PHASE 1, an IPython window will open")
        print("-> Max 24 set of topics will have to be evaluated on coherence & relevance. Intruder words to be "
              "selected")
        print("\n*** PHASE 3 ***")
        print("-> Given recent inbox mails, some set of emails will be suggested, for which actions such as deletion, "
              "new folder creation etc. can be taken")
        print("-> The utility & coherence of these sets of emails have to scored. Total 6 sets.")
        print('----------------------------------------------------------------------------------\n')
        six.moves.input("\nPress Enter to continue")

        print("\n***Preparing topic visualization, please wait (5-10s) till a new tab opens in your browser...***\n")
        print("-> Highly recommended to see *Guide Phase-1 Part-1* for more information")

        # This shows all topics learned using the pyLDAvis tool
        if sys.version_info[0] < 3:  # If python version less than 3
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                lda = models[0].lda_model
                PD = pyLDAvis.gensim.prepare(lda, models[0].corpus, models[0].id2word_dict)
                pyLDAvis.save_html(PD, './LDAVIS.html')
                webbrowser.open("file://" + os.getcwd() + "/LDAVIS.html")
                time.sleep(5)

        print("\n-> From the 100 topics shown, 3 different topic ranking algorithms will now select 16"
              " topics. Our aim is to study the comparative performance of these 3 algorithms.")
        _ = six.moves.input("\nPress Enter to continue")
        print("\n-> You will be shown the selected 16 topics from each algorithm one by one.")
        print("-> On closing the window displaying the 16 topics, "
              "you\'ll be asked to score(1-3) on three factors: Minimal Redundancy || 'Coverage of you mailbox "
              "contents || overall satisfiability")
        print("-> Highly recommended to see *Guide Phase-1 Part-2* for information on scoring")
        os.remove(os.getcwd() + "/LDAVIS.html")
        _ = six.moves.input("\nPress Enter to continue")

        # logger.info("\n########## STARTING PHASE 1 EVALUATION ##########\n")
        # logger.debug("On closing the Ipython window, you\'ll be asked to score(1-3): Minimal Redundancy || ' \
        #         'Coverage of you mailbox contents || overall satisfiability")
        # logger.debug("See *Guide Section II* for more information")
        # _ = six.moves.input("Press E ")

        title = 'On closing this window, you\'ll be asked (on terminal) to score(1-3): Minimal Redundancy || ' \
                'Coverage of you mailbox contents || overall satisfiability'
        redundancy_scores, coverage_scores, overall_scores = [], [], []
        topic_marginal_distr_order = np.argsort(np.sum(models[0].document_topic_matrix, axis=1))[::-1]
        print("\n-----> Please tend to the *IPython Window* that opened, close & enter the scores below <-----\n")
        models[0].plot_topic_topwords(topicid_list=topic_marginal_distr_order[:min(num_topics, 16)], title=title)
        red_score, cov_score, ov_score = scores_input()
        redundancy_scores.append(red_score)
        coverage_scores.append(cov_score)
        overall_scores.append(ov_score)
        logger.info("Case 1: User's redundancy, coverage, overall scores: %d  %d  %d" % (red_score, cov_score,
                                                                                         ov_score))

        # pmis = semantic.umass_coherence(dirname, models[0].topic_tuples, models[0], numwords=10, main_call=True)
        # sem_coherence_order = np.argsort(pmis)[-min(16, num_topics):][::-1]
        # models[0].plot_topic_topwords(topicid_list=list(sem_coherence_order), title=title)
        baseline_coverage_scores = task_evaluation.baseline_coverage(models[0], email_network.df)
        baseline_coverage_order = np.argsort(baseline_coverage_scores)[-min(16, num_topics):][::-1]
        print("\n-----> Please tend to the *IPython Window* that opened, close & enter the scores below <-----\n")
        models[0].plot_topic_topwords(topicid_list=list(baseline_coverage_order), title=title)
        red_score, cov_score, ov_score = scores_input()
        redundancy_scores.append(red_score)
        coverage_scores.append(cov_score)
        overall_scores.append(ov_score)
        logger.info("Case 2: User's redundancy, coverage, overall scores: %d  %d  %d" % (red_score, cov_score,
                                                                                         ov_score))
        i = 0
        document_topic_membership_dict = task_evaluation.get_document_topic_membership_dict(models[i], email_network.df)
        max_cover_topics = task_evaluation.max_coverage_greedy(models[i],
                                                               document_topic_membership_dict,
                                                               sel_topics=min(num_topics, 16), df=email_network.df)
        # pmis = [pmis[max_cover_topics[idx]] for idx in xrange(len(max_cover_topics))]
        # order = np.argsort(pmis)[::-1]
        # max_cover_topics = [max_cover_topics[idx] for idx in order]
        print("\n-----> Please tend to the *IPython Window* that opened, close & enter the scores below <-----\n")
        models[i].plot_topic_topwords(max_cover_topics, title=title)
        red_score, cov_score, ov_score = scores_input()
        redundancy_scores.append(red_score)
        coverage_scores.append(cov_score)
        overall_scores.append(ov_score)
        logger.info("Case 3: User's redundancy, coverage, overall scores: %d  %d  %d" % (red_score, cov_score,
                                                                                         ov_score))

        # Deciding which ranking algo to choose for the evaluation application
        overall_scores_argsorted = np.argsort(overall_scores)[::-1]
        if overall_scores[overall_scores_argsorted[0]] > overall_scores[overall_scores_argsorted[1]]:
            order = overall_scores_argsorted[0]
        else:
            overall_scores = [s1+s2+s3 for s1, s2, s3 in zip(redundancy_scores, coverage_scores, overall_scores)]
            order = np.argmax(overall_scores)

        print("\n\n Completed ***PHASE 1*** evaluation! Next step may take 3-4 mins before evaluation requirement.\n")

        if smalleval:
            print("smalleval option is on: program only to be run till this point. Exiting with successful completion.")
            return

        # model.plot_dominant_topic_document_distribution(kind='colormap')
        # logger.info("Starting application ...")
        ''' Launch user evaluation application '''
        application.main(models=models, dirname=dirname, num_topics=num_topics_eval, threaded=threaded,
                         email_network=email_network, order=order, A=A)

    downstream_tasks(threaded, models, email_network, A)

    with open('.' + logging_filename, 'a') as file_handle:
        file_handle.write(initial_logging_info)

    choice = \
        six.moves.input("\n\nEvaluation completed! Automatically email the report to "
                        "ssrajan@microsoft.com? [Y|n]: ")
    if choice == 'y' or choice == 'Y':
        sendmail(exception_str='', traceback_str='', addr=send_reports_at_address)
    else:
        print("\n\nPlease send the file %s in your current working directory to "
              "ssrajan@microsoft.com" % logging_filename)
        six.moves.input("\nPress Enter to exit the application.")
    logger.debug("\nBye! Application proceeded to completion.")
    return


# noinspection PyBroadException
def downstream_tasks(threaded, models, email_network, A):
    # COLLAPSED & NEW FOLDER RETRIEVAL TASK
    df = email_network.df[(email_network.df["diffdays"] < 31)].copy()

    # NEW FOLDER SUGGESTION TASK
    if True:
        try:
            print("\n\n***FINAL PHASE EVALUATION: 6 instances of suggested email sets to be scored***")
            six.moves.input("\nPress Enter to continue.")
            # min_folder_size = min(max(30, int(email_network.avg_folder_len / 2)), 100)
            min_folder_size = 15
            logger.info("New Folder Task: Folder Size to achieve: %d" % min_folder_size)
            datasplits = task_evaluation.new_folder_task_data_prep(df)
            for model in models:
                logger.info("\n************** NEW FOLDER PREDICTION TASK USING MODEL %s **************" %
                            model.modelname.upper())
                task_evaluation.new_folder_prediction_task(datasplits, model, model.num_topics, df, email_network,
                                                           model.document_topic_matrix,
                                                           min_folder_size=min_folder_size,
                                                           called_by_collapsed=False)

            logger.info("\n************** NEW FOLDER PREDICTION TASK USING BoW **************")
            task_evaluation.new_folder_prediction_task(datasplits, None, models[0].num_topics, df, email_network,
                                                       email_network.tfidf_matrix.transpose(),
                                                       min_folder_size=min_folder_size,
                                                       called_by_collapsed=False)

            logger.info("\n************** NEW FOLDER PREDICTION TASK USING W2V **************")
            task_evaluation.new_folder_prediction_task(datasplits, None, models[0].num_topics, df, email_network,
                                                       email_network.avg_word2vec_matrix.T,
                                                       min_folder_size=min_folder_size,
                                                       called_by_collapsed=False)

            logger.info("\n************** NEW FOLDER PREDICTION TASK USING PV-DBOW **************")
            task_evaluation.new_folder_prediction_task(datasplits, None, models[0].num_topics, df, email_network,
                                                       email_network.pvdbow_matrix.T,
                                                       min_folder_size=min_folder_size,
                                                       called_by_collapsed=False)
        except:
            trb = traceback.format_exc()
            logger.info(str(trb))

        print("\n\n** Manual evaluation part is done! Thank you! **")
        print("\n** Automated evaluation for other task will now start (in 10s)."
              "  After completion, you'll be prompted to mail the report **")
        sleep(7)
        # print("\n\n**** PLEASE FEEL FREE TO LEAVE THE PROGRAMMING RUNNING, NO MORE MANUAL EVALUATION IS REQUIRED "
        #       "****\n\n")

        # COLLAPSED FOLDER RETRIEVAL TASK
        try:
            logger.info("\n************** COLLAPSED FOLDER PREDICTION TASK ***************")
            # min_folder_size = min(max(30, int(email_network.avg_folder_len / 3)), 100)
            min_folder_size = 15
            logger.info("Collapsed Folder Task: Folder Size to achieve: %d" % min_folder_size)

            big_folders = []
            big_folders_len = []
            for folder in email_network.big_folders:
                # if len(df[df["FolderType"] == folder]) > max(30, int(email_network.avg_folder_len / 3)):
                len_folder = len(df[df["FolderType"] == folder])
                if len_folder > min_folder_size:
                    big_folders.append(folder)
                    big_folders_len.append(len_folder)
            table = PrettyTable()

            table.add_column('FolderNum', [str(i) for i in range(1, len(big_folders) + 1)] + ["Average"])

            if len(big_folders_len) > 0:
                # noinspection PyTypeChecker
                table.add_column('Support', big_folders_len + [int(np.mean(big_folders_len))])

            for model in models:
                precisions = []
                for folder in big_folders:
                    precision = task_evaluation.collapsed_folder_prediction_task(df, email_network, model,
                                                                                 model.num_topics, folder,
                                                                                 min_folder_size=min_folder_size)
                    precisions.append(precision)
                if sum(big_folders_len) > 0:
                    macro_weighted_avg = sum([p * n for p, n in zip(precisions, big_folders_len)]) / sum(
                        big_folders_len)
                else:
                    macro_weighted_avg = 0.
                table.add_column(model.modelname, ['%0.3f' % p for p in precisions] + ['%0.3f' % macro_weighted_avg])

                logger.debug("Completed task for %s" % model.modelname)

            precisions = []
            for folder in big_folders:
                precision = \
                    task_evaluation.collapsed_folder_prediction_task_bow_w2v_pvdbow(df, email_network,
                                                                                    email_network.tfidf_matrix.T,
                                                                                    models[0].num_topics, folder,
                                                                                    min_folder_size=min_folder_size)
                precisions.append(precision)
            if sum(big_folders_len) > 0:
                macro_weighted_avg = sum([p * n for p, n in zip(precisions, big_folders_len)]) / sum(big_folders_len)
            else:
                macro_weighted_avg = 0.
            table.add_column('BOW', ['%0.3f' % p for p in precisions] + ['%0.3f' % macro_weighted_avg])
            logger.debug("Completed task for BoW")

            precisions = []
            for folder in big_folders:
                precision = \
                    task_evaluation.collapsed_folder_prediction_task_bow_w2v_pvdbow(df, email_network,
                                                                                    email_network.avg_word2vec_matrix.T,
                                                                                    models[0].num_topics, folder,
                                                                                    min_folder_size=min_folder_size)
                precisions.append(precision)
            if sum(big_folders_len) > 0:
                macro_weighted_avg = sum([p * n for p, n in zip(precisions, big_folders_len)]) / sum(big_folders_len)
            else:
                macro_weighted_avg = 0.
            table.add_column('W2V', ['%0.3f' % p for p in precisions] + ['%0.3f' % macro_weighted_avg])
            logger.debug("Completed task for Avg W2V")

            precisions = []
            for folder in big_folders:
                precision = \
                    task_evaluation.collapsed_folder_prediction_task_bow_w2v_pvdbow(df, email_network,
                                                                                    email_network.pvdbow_matrix.T,
                                                                                    models[0].num_topics, folder,
                                                                                    min_folder_size=min_folder_size)
                precisions.append(precision)
            if sum(big_folders_len) > 0:
                macro_weighted_avg = sum([p * n for p, n in zip(precisions, big_folders_len)]) / sum(big_folders_len)
            else:
                macro_weighted_avg = 0.
            table.add_column('PV-DBOW', ['%0.3f' % p for p in precisions] + ['%0.3f' % macro_weighted_avg])
            logger.debug("Completed task for PV-DBOW")
            logger.info("\nCOLLAPSED FOLDER PREDICTION TASK:\n{}".format(table))
        except:
            trb = traceback.format_exc()
            logger.info(str(trb))

    # sendmail(exception_str='', traceback_str='', addr=send_reports_at_address)

    if len(email_network.big_folders) >= 3:
        try:
            table = PrettyTable(['BOW', 'W2V', 'PV-DBOW', 'LDA', 'TSVD', 'BCD1', 'BCD2'])
            datasplits = task_evaluation.folder_task_data_prep(email_network)
            logger.debug("\n************* FOLDER CLASSIFICATION TASK USING BOW **************")
            bow_accuracy = \
                task_evaluation.folder_prediction_task_bow(datasplits, email_network.tfidf_matrix_normed, sim='cosine')
            # logger.info("\nFolder Clf BOW Accuracy: Centroid:%0.2f\t10-Closest:%0.2f" % (bow_accuracy[0],
            #                                                                              bow_accuracy[1]))
            logger.debug("\n************* FOLDER CLASSIFICATION TASK USING AVG WORD2VEC **************")
            w2v_accuracy = \
                task_evaluation.folder_prediction_task_bow(datasplits, email_network.avg_word2vec_matrix, sim='cosine')
            # logger.info("\nFolder Clf W2V Accuracy: Centroid:%0.2f\t10-Closest:%0.2f" % (w2v_accuracy[0],
            #                                                                              w2v_accuracy[1]))
            # w2v_accuracy = task_evaluation.folder_prediction_task_w2v(datasplits, email_network.avg_word2vec_matrix)
            # logger.debug("Folder Clf W2V Accuracy: %f" % w2v_accuracy)
            logger.debug("\n************* FOLDER CLASSIFICATION TASK USING PVDBOW **************")
            pvdbow_accuracy = \
                task_evaluation.folder_prediction_task_bow(datasplits, email_network.pvdbow_matrix, sim='cosine')
            # logger.info("\nFolder Clf PVDBOW Accuracy: Centroid:%0.2f\t10-Closest:%0.2f" % (pvdbow_accuracy[0],
            #                                                                                 pvdbow_accuracy[1]))
            tm_accuracies = []
            for model in models:
                logger.debug("\n************* FOLDER CLASSIFICATION TASK USING MODEL %s **************" %
                             model.modelname.upper())
                accuracy = task_evaluation.folder_prediction_task_bow(datasplits, model.document_topic_matrix.T,
                                                                      sim='hellinger')
                tm_accuracies.append(accuracy)
            accuracy = task_evaluation.folder_prediction_task_bow(datasplits,
                                                                  models[2].topic_document_matrix_l2normed,
                                                                  sim='cosine')
            tm_accuracies.append(accuracy)
            for i in range(2):
                table.add_row([bow_accuracy[i], w2v_accuracy[i], pvdbow_accuracy[i], tm_accuracies[0][i],
                               tm_accuracies[1][i], tm_accuracies[2][i], tm_accuracies[3][i]])
            logger.info('\n************* FOLDER CLASSIFICATION TASK ACCURACY **************\n{}'.format(table))
        except:
            trb = traceback.format_exc()
            logger.info(str(trb))
    else:
        logger.warning("****** DID NOT RUN FOLDER PREDICTION TASK, USER NOT A FREQUENT FILER! ******")

    #
    # if not threaded:
    #     try:
    #         table = PrettyTable()
    #         datasplits = task_evaluation.reply_task_data_prep(email_network)
    #         logger.debug("\n************* REPLY PREDICTION TASK USING BOW **************")
    #         bow = task_evaluation.reply_prediction_task_bow(datasplits, email_network.tfidf_matrix)
    #         logger.debug("\n************* REPLY PREDICTION TASK USING AVG WORD2VEC **************")
    #         w2v = task_evaluation.reply_prediction_task_w2v(datasplits, email_network.avg_word2vec_matrix)
    #         logger.debug("\n************* REPLY PREDICTION TASK USING PVDBOW **************")
    #         pvdbow = task_evaluation.reply_prediction_task_pvdbow(datasplits, email_network.pvdbow_matrix)
    #         tm_vals = []
    #         for model in models:
    #             logger.debug("\n************** REPLY PREDICTION TASK USING MODEL %s **************" %
    #                          model.modelname.upper())
    #             accuracy = task_evaluation.reply_prediction_task(datasplits, model)
    #             tm_vals.append(accuracy)
    #         table.add_column('Model', ['BOW', 'W2V', 'PV-DBOW', 'LDA', 'TSVD', 'BCD'])
    #         measures = ['Accuracy', 'Average Precision', 'Precision', 'Recall', 'f-score']
    #         for i, measure in enumerate(measures):
    #             table.add_column(measure, ['%0.2f' % bow[i], '%0.2f' % w2v[i], '%0.2f' % pvdbow[i],
    #                                        '%0.2f' % tm_vals[0][i], '%0.2f' % tm_vals[1][i], '%0.2f' % tm_vals[2][i]])
    #         logger.info('\n************* REPLY BINARY CLASSIFICATION TASK ACCURACY **************"\n{}'.format(table))
    #     except:
    #         trb = traceback.format_exc()
    #         logger.info(str(trb))
    # else:
    #     logger.warning("****** DID NOT RUN REPLY PREDICTION TASK, THREADED OPTION IS ON! ******")
    #
    if not threaded:
        try:
            table = PrettyTable(['Method', 'BOW', 'W2V', 'PVDBOW', 'LDA', 'TSVD', 'BCD1', 'BCD2'])
            # npred: Number of recipients recommended. This means MAP will be calculated @npred
            npred = 10

            datasplits = task_evaluation.receiver_task_data_prep(email_network)

            cgec_MAP = task_evaluation.receiver_task_full_cgec(datasplits, A, email_network, npred)

            bow_MAP = task_evaluation.receiver_task_bow(datasplits, email_network.tfidf_matrix_normed,
                                                        sim='cosine', npred=npred)

            w2v_MAP = task_evaluation.receiver_task_w2v_pvdbow(datasplits, email_network.avg_word2vec_matrix,
                                                               npred)
            pvdbow_MAP = task_evaluation.receiver_task_w2v_pvdbow(datasplits, email_network.pvdbow_matrix, npred)

            # print('BOW_MAP: ', bow_MAP, '\tW2V_MAP: ', w2v_MAP, '\tPVDBOW_MAP: ', pvdbow_MAP)

            tm_MAPs = []
            for model in models:
                tm_MAPs.append(task_evaluation.receiver_prediction_task(datasplits, model, npred))
            for model in models[2:]:
                tm_MAPs.append(task_evaluation.receiver_task_w2v_pvdbow(datasplits,
                                                                        model.topic_document_matrix_l2normed, npred))

            table.add_row(['KNN', '%0.3f' % bow_MAP, '%0.3f' % w2v_MAP, '%0.3f' % pvdbow_MAP, '%0.3f' % tm_MAPs[0],
                           '%0.3f' % tm_MAPs[1], '%0.3f' % tm_MAPs[2], '%0.3f' % tm_MAPs[3]])

            try:
                # bow_MAP_full_old = task_evaluation.receiver_task_full_knn(datasplits, email_network.tfidf_matrix,
                #                                                           email_network, npred, sim='euclidean')
                bow_MAP_full_old2 = task_evaluation.receiver_task_full_knn(datasplits,
                                                                           email_network.tfidf_matrix_normed,
                                                                           email_network, npred, sim='cosine')
                pvdbow_MAP_full_old = task_evaluation.receiver_task_full_knn(datasplits, email_network.pvdbow_matrix,
                                                                             email_network, npred, sim='cosine')
                w2v_MAP_full_old = task_evaluation.receiver_task_full_knn(datasplits, email_network.avg_word2vec_matrix,
                                                                          email_network, npred, sim='cosine')
                tm_MAPs = []
                for model in models:
                    tm_MAPs.append(task_evaluation.receiver_task_full_knn(datasplits, model.document_topic_matrix.T,
                                                                          email_network, npred, sim='hellinger'))
                tm_MAPs.append(task_evaluation.receiver_task_full_knn(datasplits,
                                                                      models[2].topic_document_matrix_l2normed,
                                                                      email_network, npred, sim='cosine'))

                # print('MAP for w2v reciever task: ', w2v_MAP_full_old)
                # print('MAP for pvdbow reciever task: ', pvdbow_MAP_full_old)
                # print('MAP for bow receiver task: ', bow_MAP_full_old, '  2nd: ', bow_MAP_full_old2)
                # print('MAP for tms: ', tm_MAPs)
                table.add_row(['Full KNN', '%0.3f' % bow_MAP_full_old2, '%0.3f' % w2v_MAP_full_old,
                               '%0.3f' % pvdbow_MAP_full_old, '%0.3f' % tm_MAPs[0], '%0.3f' % tm_MAPs[1],
                               '%0.3f' % tm_MAPs[2], '%0.3f' % tm_MAPs[3]])
            except:
                trb = traceback.format_exc()
                logger.info(str(trb))

            logger.info('\n************* RECEIVER RECOMMENDATION TASK  **************"\n{}'.format(table))
            logger.info("\nCGEC Baseline MAP for Receiver Prediction: {}".format(cgec_MAP))
        except:
            trb = traceback.format_exc()
            logger.info(str(trb))
    else:
        logger.warning("****** DID NOT RUN RECEIVER PREDICTION TASK, THREADED OPTION IS ON! ******")

    # SUBJECT WORD RECOMMENDATION
    try:
        npred = 10
        datasplits = task_evaluation.subject_task_data_prep(email_network)
        subject_cgec_MAP = task_evaluation.subject_prediction_task_cgec(datasplits, A, npred=npred)
        tm_MAPs = []
        for model in models:
            tm_MAP = task_evaluation.subject_prediction_task_bayes(datasplits, model.document_topic_matrix.T,
                                                                   model,
                                                                   email_network, sim='hellinger', npred=npred)

            tm_MAPs.append(tm_MAP)
        for model in models[2:]:
            tm_MAP = task_evaluation.subject_prediction_task_bayes(datasplits, model.topic_document_matrix_l2normed,
                                                                   model,
                                                                   email_network, sim='cosine', npred=npred)
            tm_MAPs.append(tm_MAP)
        table = PrettyTable(['LDA', 'TSVD', 'BCD1', 'BCD2'])
        table.add_row(['%0.3f' % tm_MAP for tm_MAP in tm_MAPs])
        # for model in models[:1]:
        #     precions_list = task_evaluation.subject_prediction_task(datasplits, model, email_network)
        #     table = PrettyTable(['', 'P@3', 'P@5', 'P@10'])
        #     methods = ['Word Prob.', 'Term Prob', 'Weighted Word', 'Weighted Term', 'NN Weighted Word',
        #                'NN Weighted Term']
        #     for i, method in enumerate(methods):
        #         table.add_row([method, '%0.2f' % precions_list[i][0], '%0.2f' % precions_list[i][1],
        #                        '%0.2f' % precions_list[i][2]])
        #     logger.info("\n************** SUBJECT PREDICTION TASK USING MODEL {0} "
        #                 "**************\n{1}".format(model.modelname.upper(), table))
        # tfidf_nn_prec, tfidf_prec = task_evaluation.subject_prediction_task_bow(datasplits,
        #                                                                         email_network.tfidf_matrix,
        #                                                                         email_network)
        # w2v_prec = task_evaluation.subject_prediction_task_w2v_pvdbow(datasplits, email_network.avg_word2vec_matrix,
        #                                                               email_network.tfidf_matrix, email_network)
        # pvdbow_prec = task_evaluation.subject_prediction_task_w2v_pvdbow(datasplits, email_network.pvdbow_matrix,
        #                                                                  email_network.tfidf_matrix, email_network)
        # all_precs = [tfidf_prec, tfidf_nn_prec, w2v_prec, pvdbow_prec]
        # all_prec_names = ['BOW', 'BOW-NN', 'W2V-NN', 'PVDBOW-NN']
        # table = PrettyTable(['', 'P@3', 'P@5', 'P@10'])
        # for i, prec in enumerate(all_precs):
        #     table.add_row([all_prec_names[i], '%0.2f' % prec[0], '%0.2f' % prec[1], '%0.2f' % prec[2]])
        logger.info("\n************** SUBJECT PREDICTION TASK **************\n{0}".format(table))
        logger.info("\n SUBJECT PREDICTION TASK CGEC MAP: %0.3f" % subject_cgec_MAP)
    except:
        trb = traceback.format_exc()
        logger.info(str(trb))

    return


def scores_input():
    """
    Take user input through terminal input for different scores of the top topics displayed.
    :return: int, int, int: minimal redundancy score, coverage score and overall satisfaction score
    """
    print("\n\n---------------------------------------------------------------------------------------------")
    print("REDUNDANCY: Topics with overlapping concepts/words, high redundancy is bad for the model, "
          "and so deserves a lower score")
    redundancy_score = str(
        six.moves.input("\n=>Enter score for minimal redundancy-> high redundancy: 1, med redundancy: 2, "
                        "low redundancy: 3 -> "))
    while not redundancy_score.isdigit() or int(redundancy_score) not in range(1, 4):
        redundancy_score = str(six.moves.input("Please enter a valid score [1-3]: "))

    print("\n\n---------------------------------------------------------------------------------------------")
    print("COVERAGE: Given the 100 topics you saw in your browser, how well do the 16 displayed topics do in "
          "covering most of the important/interesting topics")
    coverage_score = str(six.moves.input("\n=>Enter intuition of coverage of important themes [1-3] -> "))
    while not coverage_score.isdigit() or int(coverage_score) not in range(1, 4):
        coverage_score = str(six.moves.input("Please enter a valid score [1-3]: "))
    print("\n\n---------------------------------------------------------------------------------------------")
    print("OVERALL: Given the 100 topics, how well do the 16 topics do overall: covering interesting concepts/topics,"
          "with low redundancy.")
    overall_score = str(six.moves.input("\n=>Enter intuition of overall score [1-5] -> "))
    while not overall_score.isdigit() or int(overall_score) not in range(1, 6):
        overall_score = str(six.moves.input("Please enter a valid score [1-5]: "))
    return int(redundancy_score), int(coverage_score), int(overall_score)


def topic_model_to_csv(model):
    wordspertopic = 20
    topic_tuples = model.get_all_topic_tuples(wordspertopic=wordspertopic)
    topics_arr = np.chararray((wordspertopic, model.num_topics), itemsize=20)
    for topic_num, topic in enumerate(topic_tuples):
        for tup_num, tup in enumerate(topic):
            topics_arr[tup_num, topic_num] = tup[0]
    np.savetxt('./' + model.modelname + '.csv', topics_arr, fmt='%s', delimiter=',')
    return


def sendmail(exception_str, traceback_str, addr):
    """
    Send mail to given email address with the log report, along with error traceback if any.
    :param exception_str: exception object, if any
    :param traceback_str: traceback object/string, if any
    :param addr: email address to send the mail to
    :return: None
    """
    try:
        outlook = win32.Dispatch('outlook.application')
        mail = outlook.CreateItem(0)
        mail.To = addr
        if exception_str == '':
            mail.Subject = 'Topic Model Report'
        else:
            mail.Subject = 'Topic Model Error Report'
        mail.Body = str(traceback_str) + str(exception_str) + ' __'
        attachment1 = os.getcwd() + logging_filename
        mail.Attachments.Add(Source=attachment1)
        mail.Send()
        logger.info("Mail sent")
    except Exception as excep:
        logger.error("Exception when sending mail: %s" % excep)
    return


if __name__ == '__main__':
    # noinspection PyBroadException
    try:
        # Run the main function that runs email extraction, topic models, and evaluations
        main()
        # Succesful run, send mail with report to topiceval@outlook.com
        # sendmail(exception_str='', traceback_str='', addr=send_reports_at_address)
        print('\nExiting with successful completion...')
    except Exception as e:
        # Get the traceback and exception strings, and send the error report to mail address
        tb = traceback.format_exc()
        logger.info(str(tb))
        # sendmail(exception_str=str(e), traceback_str=tb, addr=send_reports_at_address)
        print("\nExiting with error...")
    exit(0)
