"""
This module use the win32com.client library for python to extract user emails
from outlook and organize them in a pandas dataframe structure.
"""

from __future__ import division
from __future__ import print_function

from topiceval.preprocessing import textcleaning
from topiceval import makewordvecs
import topiceval.preprocessing.emailsprocess as emailprocess
import topiceval.allparams as allparams

import pandas as pd
from gensim.models.keyedvectors import KeyedVectors

try:
    import win32com.client
except ImportError:
    win32com = None
import os
import logging
import pickle

logger = logging.getLogger(__name__)


def extract_usermails(threaded, num_topics, save, load, excludefolders):
    """
    Extract mails from inbox, store as a dataframe and return the directory name and the dataframe.

    The steps followed are:

    1. Make a data directory at current location to store temporary data

    2. Extract user mails from outlook using win32.client API. Always extracts from all folders except
        some default one. Private folders that the users want not to be explored can be mentioned
        explicitly via the command-line. These are stored in a dataframe with their meta-data information.
        Additional fields like message replied to or not, message importance etc are also appended.

    3. If threaded option is True, then from all mails belonging to a single mail thread, only
        the largest is retained and the rest are discarded.
        If threaded is False, then previous conversation content is removed from all mails, maintaining
        only the most recent message in the extracted mail => all mails in a conversation form separate
        docs

    4. Signature Removal: Some common phrases that form signatures are removed

    5. The clean_text() function of textcleaning.py module is applied. It tokenizes text, removes special
        characters, identifies metadata info, url's, email addresses, numbers, money figures, weekdays etc.,
        along with additional option of lemmatization. Some effort is made to remove template text by removing
        information that folllows multiple special character of the same kind (like --------)

    6. Phrase Detection: Gensim's phrase detection module is used to form bigrams # TODO: Trigrams etc

    7. Next step is removal of stopwords. The popular extended list of stopwords available online is used
        for this task since we aim at removal of topically poor words.

    Parameters
    ----------
    :param threaded: bool, if True, treats threaded conversation as a single document
    :param num_topics: number of topics for topic model, used for setting dimensions for word2vec learning
    :param save: bool, if True, stores extracted emails, df and wordvecs in cwd
    :param load: bool, if True, loads extracted emails, df and wordvecs from cwd
    :param excludefolders: string, comma separated list of extra folders to exclude

    :return: string, pandas.DataFrame corresponding to the directory path to store temporary data
        and dataframe holding user's email information
    """
    # Make temporary data directory at current location for temporary storage of data, and get its path in dirname
    dirname = make_user_dir()

    # Get email items from inbox, Sent items and any extrafolders mentioned through command line
    # Currently configured to use 2 processes for parallel extraction of mails from inbox and sent mails
    # extrafolders are traversed serially
    # TODO: Turn on multiprocessing after sufficient testing and benchmarking

    # preload_flag is used to determine whether email items are loaded from previously saved items (flag=True)
    # or freshly extracted from outlook
    preload_flag = False

    # If load=True and items file exists in current directory, load mails from that instead of extracting again
    if (load or True) and os.path.isfile("./topiceval_items.pickle"):
        try:
            with open("./topiceval_items.pickle", "rb") as handle:
                items = pickle.load(handle)
            preload_flag = True
        except Exception as e:
            logger.error("Could not load email items from pickle file, ERROR: {}".format(e))
            os.remove("./topiceval_items.pickle")
            logger.info("Extracting fresh from outlook, discarding the existing pickle items file...")
            items = extract(excludefolders)
    else:
        items = extract(excludefolders)

    logger.info("Total number of user emails extracted : %d" % len(items))

    # If save option is on, we save the extracted mails to a file in the current directory
    if save and not preload_flag:
        logger.debug("Save option is on, saving items in current directory...")
        try:
            with open("./topiceval_items.pickle", "wb") as handle:
                pickle.dump(items, handle, protocol=pickle.HIGHEST_PROTOCOL)
        except Exception as e:
            os.remove("./topiceval_items.pickle")
            logger.error("COULD NOT STORE EMAIL ITEMS, PICKLE ERROR: {}".format(e))

    # If load option is on and dataframe file and wordvecs are present, load them, else construct them
    if False and load and os.path.isfile("./df.pkl") and os.path.isfile("./wordvecs"):
        logger.info("Reading presaved dataframe and trained wordvecs..")
        df = pd.read_pickle('./df.pkl')
        wordvecs = KeyedVectors.load('./wordvecs')
    else:
        # df is a pandas dataframe consisting of various email header information with the email body
        # wordvecs is a gensim.models.keyedvectors.KeyedVector instance
        df, wordvecs = makedf(items, threaded, num_topics)
        # If reuse option is on, save the computed df and wordvecs in current directory
        if save:
            df.to_pickle('./df.pkl')
            wordvecs.save('./wordvecs')

    # A is the doc-term BoW matrix, email_network is a preprocessing.emailstructure.EmailNetwork instance
    A, email_network = emailprocess.make_doc2bow(df, dirname, threaded, wordvecs)

    # Compute the replied-to-or-not boolean field and append to the email_network's dataframe
    # email_network.df = emailprocess.add_reply_field(email_network.df, email_network)

    # Compute the combined to-cc-bcc field and append to the email_network's dataframe
    email_network.df = emailprocess.add_to_cc_bcc_field(email_network.df)
    # Compute the num_days from today field and append to the email_network's dataframe
    email_network.df["diff"] = (pd.datetime.now() - email_network.df['SentOn'])

    email_network.df["diffdays"] = email_network.df["diff"].apply(get_days)
    # Compute the email importance field and append to the email_network's dataframe
    email_network.make_user_importance_score_dict()
    email_network.make_importance_field()
    # Make the email_network object compute some extra things now that email importance and other fields are available
    email_network.make_three_imp_folders()
    email_network.make_three_time_periods()
    return dirname, email_network, A


def encodeit(s):
    if isinstance(s, str):
        return (s.encode('utf-8')).decode('utf-8')
    else:
        return s


def extract_helper(messages, itr, folder_type, items, max_days):
    """
    Given message items of a folder, the name of the folder, the list to which to append,
    and the maximum number of items to be appended, return the items list with these
    messages appended as dictionaries.
    """
    if folder_type == "Sent Mail":
        folder_type = "Sent Items"
    # message = messages.GetLast()
    count_extracted = 0
    # while message and (max_items is None or count_extracted < max_items):
    # for message in messages:
    while itr >= 0:
        message = messages[itr]
        itr -= 1
        try:
            d = dict()
            d['Subject'] = encodeit(getattr(message, 'Subject', '<UNKNOWN>'))
            d['SentOn'] = str(encodeit(getattr(message, 'SentOn', '<UNKNOWN>')))
            d['SenderName'] = encodeit(getattr(message, 'SenderName', '<UNKNOWN>'))
            d['CC'] = encodeit(getattr(message, 'CC', '<UNKNOWN>'))
            d['BCC'] = encodeit(getattr(message, 'BCC', '<UNKNOWN>'))
            d['To'] = encodeit(getattr(message, 'To', '<UNKNOWN>'))
            d['Body'] = encodeit(getattr(message, 'Body', '<UNKNOWN>'))
            d['ConversationID'] = encodeit(getattr(message, 'ConversationID', '<UNKNOWN>'))
            d['ConversationIndex'] = encodeit(getattr(message, 'ConversationIndex', '<UNKNOWN>'))
            d['UnRead'] = encodeit(getattr(message, 'UnRead', '<UNKNOWN>'))
            d['FolderType'] = folder_type
            # Final check: Should have values for convID and SentOn
            if d['SentOn'] != '<UNKNOWN>' and d['ConversationID'] != '<UNKNOWN>' and d['ConversationID'].strip() != '':
                if max_days is not None and (pd.datetime.now() - pd.to_datetime(d['SentOn'])).days > max_days:
                    break
                items.append(d)
                count_extracted += 1
        # TODO: Identify broad classes of exception possible
        except Exception as inst:
            logger.error("Error processing mail: {}".format(inst))
        # message = messages.GetPrevious()

    return items, count_extracted, itr


# def extract_helper_mp(folder_num, folder_type):
#     """
#     This function is not maintained and currently not in use
#     """
#     items = []
#     outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
#     messages = outlook.GetDefaultFolder(folder_num).Items
#     message = messages.GetFirst()
#     while message:
#         try:
#             d = dict()
#             d['Subject'] = encodeit(getattr(message, 'Subject', '<UNKNOWN>'))
#             d['SentOn'] = str(encodeit(getattr(message, 'SentOn', '<UNKNOWN>')))
#             d['SenderName'] = encodeit(getattr(message, 'SenderName', '<UNKNOWN>'))
#             d['CC'] = encodeit(getattr(message, 'CC', '<UNKNOWN>'))
#             d['BCC'] = encodeit(getattr(message, 'BCC', '<UNKNOWN>'))
#             d['To'] = encodeit(getattr(message, 'To', '<UNKNOWN>'))
#             d['Body'] = encodeit(getattr(message, 'Body', '<UNKNOWN>'))
#             d['ConversationID'] = encodeit(getattr(message, 'ConversationID', '<UNKNOWN>'))
#             d['ConversationIndex'] = encodeit(getattr(message, 'ConversationIndex', '<UNKNOWN>'))
#             d['UnRead'] = encodeit(getattr(message, 'UnRead', '<UNKNOWN>'))
#             d['FolderType'] = folder_type
#             if d['SentOn'] != '<UNKNOWN>' and d['ConversationID'] != '<UNKNOWN>':
#                 items.append(d)
#         except Exception as inst:
#             print("Error processing mail", inst)
#
#         message = messages.GetNext()
#     return items


def extract(excludefolders):
    """
    Extract emails from Outlook, while excluding folders mentioned in excludefolders string
    Each email is extracted as an object specified in the win32com library, and we extract relevant
    informtation from this, and store each email as a dictionary in a list.

    We end up with a list of dictionaries, where each element corresponds to an extracted email.
    """

    items = []

    # # 6 and 5 are linked with the inbox and Sent Items folder in win32com nomenclature
    # # Example, given outlook object, we get inbox folder object using outlook.GetDefaultFolder(6)
    # # append "deleted_items": 3 if reuired
    # folders = {"inbox": 6, "sent_items": 5}

    # Mails from folders in default folder set won't be extracted during extraction from extra-folders.
    # "archive", "inbox", "sent_items" have been removed from default folder set and will be extracted unless excluded.
    default_folder_set = {'deleted items', 'outbox', 'personmetadata', 'tasks', 'junk email', 'trash',
                          'spam', 'drafts', 'calendar', 'rss subscriptions', 'quick step settings', 'yammer root',
                          'conversation action settings', 'externalcontacts', 'important', 'journal', 'files',
                          'contacts', 'conversation history', 'social activity notifications', 'sync issues', 'notes',
                          'reminders', 'the file so that changes to the file will be reflected in your item.'}

    # Given the excludefolders string, where each foldername is separated by ",", we build a set
    # with names of excluded folders
    exclude_folder_set = set([foldername.lower() for foldername in excludefolders.split(',')])

    # # This section is not maintained, not tested. Future work.
    # if use_multiprocessing:
    #     logger.log(0, "Using multiprocessing while extracting mails...")
    #     folders_mp = [tup for tup in folders.items()]
    #     num_processes = len(folders_mp)
    #     p = mp.Pool(processes=num_processes)
    #     for i in xrange(num_processes):
    #         res = p.apply_async(extract_helper_mp, args=(folders_mp[i][1], folders_mp[i][0]))
    #         items.extend(res.get())
    #     p.close()
    #     p.join()
    #
    # else:
    #     # Get outlook object
    #     outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
    #     # Walk through inbox and sent_items
    #     for folder_type in folders:
    #         logger.debug("Extracting emails from {0}".format(folder_type))
    #         folder = outlook.GetDefaultFolder(folders[folder_type])
    #         messages = folder.Items
    #         # Limit to extracting maximum of 6000 emails per inbox/sent_items folder
    #         items = extract_helper(messages=messages, folder_type=folder_type, items=items, max_items=)
    #
    #         for subfolder in folder.Folders:
    #             logger.debug("Extracting emails from subfolder {0}".format(str(subfolder)))
    #             messages = subfolder.Items
    #             items = extract_helper(messages=messages, folder_type=str(subfolder), items=items, max_items=6000)
    #         logger.debug("done extacting messages")

    # Get Outlook object
    outlook = win32com.client.Dispatch("Outlook.Application").GetNamespace("MAPI")
    # Get all folders
    all_folders = [folder for folder in outlook.Folders[0].folders]
    # Remove unwanted defaults and the ones mentioned by the user to be excluded
    subfinal_folders = [folder for folder in all_folders if (str(folder).lower() not in default_folder_set and
                                                             str(folder).lower() not in exclude_folder_set)]
    # Add the folders + their 1-level-down subfolders
    final_folders = []
    for folder in subfinal_folders:
        if len(folder.items) > 0:
            final_folders.append(folder)
        for subfolder in folder.Folders:
            if len(subfolder.items) > 0:
                final_folders.append(subfolder)

    logger.info("Total number of folders + subfolders found: %d" % len(final_folders))

    # message_pointers = [folder.items.GetLast() for folder in final_folders]
    # folders_messages = [folder.items for folder in final_folders]

    # This dictionary stores folder names as keys and their message items in a list
    folders_messages = dict()
    # This dictionary hold the current position of message iterator for each folder
    folders_iterators = dict()
    # Stores num mails extracted per folder
    folders_numextracted = dict()

    for folder in final_folders:
        folders_messages[str(folder)] = folder.items
        folders_iterators[str(folder)] = len(folder.items) - 1
        folders_numextracted[str(folder)] = 0
        # messages = folder.items
        # message = messages.GetLast()
        # if not message:
        #     continue
        # folders_messages[str(folder)] = []
        # folders_iterators[str(folder)] = 0
        # while message:
        #     folders_messages[str(folder)].append(message)
        #     message = messages.GetPrevious()

    if len(final_folders) > 0:
        # Get estimate of total number of mails
        total_mails = 0
        for folder in final_folders:
            total_mails += len(folders_messages[str(folder)])
            # total_mails += len(folder.items)
            # for subfolder in folder.Folders:
            #     total_mails += len(subfolder.items)

        if total_mails < allparams.total_max_items:
            for idx, folder in enumerate(final_folders):
                logger.debug("Extracting emails from {0}".format(str(folder)))
                # messages = folders_messages[str(folder)][folders_iterators[str(folder)]:]
                messages = folders_messages[str(folder)]
                itr = folders_iterators[str(folder)]
                items, num_extracted, itr = extract_helper(messages=messages, itr=itr, folder_type=str(folder),
                                                           items=items, max_days=None)
                folders_iterators[str(folder)] = itr
                folders_numextracted[str(folder)] += num_extracted
        else:
            logger.debug("Extracting.... (This may take 5-10 mins depending on your mail quantity)")
            months = 1
            while len(items) < allparams.total_max_items and months <= allparams.max_months:
                # print(months, len(items))
                extracted_this_iteration = 0
                for idx, folder in enumerate(final_folders):
                    # messages = folders_messages[str(folder)][folders_iterators[str(folder)]:]
                    messages = folders_messages[str(folder)]
                    itr = folders_iterators[str(folder)]
                    items, num_extracted, itr = extract_helper(messages=messages, itr=itr, folder_type=str(folder),
                                                               items=items, max_days=months*30)
                    folders_iterators[str(folder)] = itr
                    folders_numextracted[str(folder)] += num_extracted
                    extracted_this_iteration += num_extracted
                # if extracted_this_iteration == 0:
                #     break
                months += 1
            logger.info("Number of mails extracted per folder")
            for idx, folder in enumerate(final_folders):
                logger.info("Folder " + str(idx) + " : " + str(folders_numextracted[str(folder)]) + " of " +
                            str(len(folder.items)))

        # # Start extraction folder by folder
        # for folder in final_folders:
        #     logger.debug("Extracting emails from {0}".format(folder))
        #     messages = folder.Items
        #
        #     # Max number of messages to extract
        #     if total_mails < allparams.total_max_items:
        #         items_max_limit = None
        #     elif str(folder) == "Inbox":
        #         items_max_limit = allparams.inbox_max_items
        #     elif str(folder) == "Sent Items":
        #         items_max_limit = allparams.sentitems_max_items
        #     else:
        #         items_max_limit = allparams.customfolder_max_items
        #
        #     items = extract_helper(messages=messages, folder_type=str(folder), items=items, max_items=items_max_limit)
        #
        #     for subfolder in folder.Folders:
        #         items_max_limit = allparams.subfolder_max_items if items_max_limit is not None else None
        #         logger.debug("Extracting emails from subfolder {0}".format(str(subfolder)))
        #         messages = subfolder.Items
        #         folder_type = str(subfolder)
        #         if folder_type == "Sent Mail":
        #             folder_type = 'Sent Items'
        #         items = extract_helper(messages=messages, folder_type=folder_type, items=items,
        #                                max_items=items_max_limit)
        #
        #     if len(items) > allparams.total_max_items:
        #         break

    return items


def make_user_dir():
    """
    Create a directory that will store temporary data for this application.
    The directory is currently chosen to be in the cwd.
    :return: str, the path of the directory
    """
    path = "./temp_data_topiceval/"
    # If the temporary data folder already exists (from a previous execution), remove its files
    # P.S. This is a simple program, no need to look for race conditions etc here.
    if os.path.exists(path):
        for filename in os.listdir(path):
            os.remove(os.path.join(path, filename))
    else:
        # Else create the directory
        os.makedirs(path)
    logger.debug("Saving temp data at {0}{1}".format(os.path.dirname(os.path.abspath(__file__)), path[1:]))
    return path


def makedf(items, threaded, num_topics):
    # items.sort(key=lambda tup: tup['SentOn'])
    keys = ["ConversationID", "SentOn", "SenderName", "To", "CC", "BCC", "Subject", "Body", "UnRead",
            "FolderType"]
    df = pd.DataFrame()
    logger.log(0, "Making user-emails' dataframe...")

    for key in keys:
        try:
            df[key] = [str(d[key]) for d in items]
        except Exception as e:
            logger.log(0, "Exception: {}".format(e))
            df[key] = [d[key].encode('utf-8') for d in items]  # ERROR PRONE

    df.set_index(keys=["ConversationID"], inplace=True, drop=False)
    # df = df[(~df["Subject"].str.contains("sent you a message in Skype for Business")) &
    #         (~df["Subject"].str.contains("I've shared files with you")) &
    #         (~df["Subject"].str.contains("Missed conversation with"))]
    df['SentOn'] = pd.to_datetime(df['SentOn'], infer_datetime_format=True)
    # df = df[~(df['Subject'].isin(['sent you a message in Skype for Business', 'I\'ve shared files with you',
    #                              'Missed conversation with']))].copy()

    # These represent typical junk messages which we would like to avoid from topic modelling perspective
    df = df[~df["Subject"].str.contains("sent you a message in Skype for Business")]
    df = df[~df["Subject"].str.contains("Missed conversation with")]

    # Sort by (ConversationID, SentOn)
    df.sort_values(by=['ConversationID', 'SentOn'], ascending=[True, True], inplace=True)
    logger.log(0, "Cleaning email bodies in dataframe...")
    # names = get_names(df)

    # Adding subject to clean body
    for idx, row in df[["Subject", "Body"]].iterrows():
        body = "Subject: " + row[0] + "\n" + row[1]
        df.set_value(idx, "Body", body)

    if threaded:
        # To keep threads, only keep the most recent mail of a thread, that will contain all messages
        bool_list = emailprocess.remove_redundant_threads(df)
        df = df[bool_list]
        df['CleanBody'] = df['Body']
    else:
        # For each mail body, remove text that corresponds to previous messges in the thread
        df['CleanBody'] = df['Body'].apply(emailprocess.remove_threads)

    # Remove some email signatures, such as: sincerely, thanks, .. etc
    df['CleanBody'] = df['CleanBody'].apply(emailprocess.remove_signature)

    # Identify bigrams
    bigram_phraser = emailprocess.phrase_detection(df)

    df['CleanBody'] = df['CleanBody'].apply(textcleaning.clean_text)

    # Coalesce bigrams
    df['CleanBody'] = df['CleanBody'].apply(emailprocess.phraser, args=(bigram_phraser,))

    word_vecs = makewordvecs.make_wordvecs(df["CleanBody"], num_topics)

    stopwords = emailprocess.load_stops()

    df['CleanBody'] = df['CleanBody'].apply(textcleaning.remove_stops, args=(stopwords,))
    df['Subject'] = df['Subject'].apply(emailprocess.clean_email_header)
    df['To'] = df['To'].apply(emailprocess.clean_email_header)
    df['CC'] = df['CC'].apply(emailprocess.clean_email_header)
    df['BCC'] = df['BCC'].apply(emailprocess.clean_email_header)
    df = emailprocess.add_reply_field(df)

    # Remove mails automatically sent on sharing files
    df = df[~df["Subject"].str.contains("I've shared files with you")]

    df.sort_values(by='SentOn', ascending=False, inplace=True)

    # df['CleanBody'] = df['CleanBody'].apply(emailprocess.replace_names, args=(names, ))
    logger.log(0, "Done cleaning email bodies in dataframe")
    return df, word_vecs


def get_names(df):
    return df["SenderName"].unique().tolist()


def get_days(dt):
    return dt.days
