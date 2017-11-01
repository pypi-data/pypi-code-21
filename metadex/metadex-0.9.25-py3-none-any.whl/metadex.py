'''
MetaDEx: The Metagenomic Data Explorer

CODE GOES HERE
'''
import glob
import math
import numpy as np
import pandas as pd
import sys
import os
import errno
from skbio.stats import subsample_counts
from functools import reduce
from Bio import Entrez
import time
import re
#import requests
from scipy import stats
from bokeh.charts import Donut, show, output_file
from bokeh.layouts import row, column
from bokeh.palettes import Set3
############################################################################################
'''
DOWNLOADING ANNOTATIONS FROM MG-RAST API
step one: get a list of all the names of metagenomes
FOR EACH METAGENOME:
type: all
determine source of annotations
determine cutoffs: evalue (default 5), identity (default 60), length (default 15)
create dictionary from steps two and three
decide between POST and GET (default to GET)
rawData = pd.read_table(io.StringIO(r.test))
pull out the columns for organism and function annotations
keep max pctID only for each query sequence
modified “get_and_save_counts” for this counts type
'''
############################################################################################
'''
def get_counts_via_API(groupName, sampleID, metagenome, source, evalue=5, identity=60, length=15):
    r = requests.get('http://api.metagenomics.anl.gove/annotation/similarity/'+ metagenome, params = {'source': source,'evalue': evalue, 'identity': identity, 'length': length})
    rawData = pd.read_table(io.StringIO(r.text))
    rawData['organism'] = rawData['semicolon separated list of annotations'].str.extract("o\w+\= \[([A-z]\w+)\]", expand = False)
    rawData['function'] = rawData['semicolon separated list of annotations'].str.extract("f\w+\= \[([A-z]\w+)\]", expand = False)
    #TO DO 7 JUN 2017: fix regex for pulling out annotations and then continue with above
    rawData = keep_max_pctID_only(rawData)
    counts = get_and_save_counts(rawData, groupName, sampleID)
    return counts

def get_group_counts_API(metagenomeGroupDict, source, evalue=5, identity=60, length=15):
    metagenomeGroupDF = pd.DataFrame({'metagenome ID' : list(metagenomeGroupDict.keys()),'group' : list(metagenomeGroupDict.values())})
    return grpCountsList
'''
############################################################################################
'''
TRANSFORMING ANNOTATIONS INTO NORMALISED COUNTS DATA











'''
############################################################################################
'''
####CREATE PATH IN DIRECTORY##
def create_path(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise

####READ CSV FILE INTO PANDAS DATAFRAME####
def make_df(filename):
    df = pd.read_csv(filename, header=None)
    return df

###
def make_df_normCounts(filename):
    df = pd.read_csv(filename) #index_col=[0,1]
    return df

####MERGE TWO DATAFRAMES####
def merge_dfs(ldf, rdf):
    print("merging...")
    return ldf.merge(rdf, how='outer', on=['gene function', 'organism'])


###KEEP ANNOTATIONS WITH MAX PERCENT IDENTITY###
def keep_max_pctID_only(table):
    mask = table.groupby('query sequence id').agg('idxmax')
    maxPctID = table.loc[mask['percentage identity']].reset_index()
    return maxPctID

###MERGE FUNCTION AND ORGANISM ANNOTATION TABLES###
def merge_annotation_tables(table1, table2):
    mergedTable = pd.merge(table1, table2, on = 'query sequence id').sort_values(['semicolon separated list of annotations_x', 'semicolon separated list of annotations_y'], ascending = [0,0])
    mergedTable.rename(columns={'semicolon separated list of annotations_x':'gene function','semicolon separated list of annotations_y':'organism'})
    groupByQuery = mergedTable.groupby('query sequence id')
    return mergedTable

###GET RAW COUNTS FOR MERGED ANNOTATION TABLES###
def get_and_save_counts(mergedTable, groupName, sampleID):
    counts1 = mergedTable.sort_values(['gene function', 'organism']).groupby(['gene function', 'organism']).size()
    newFileName = '%(group)s_%(sample)s.csv' % \
        {"group": groupName, "sample": sampleID}
    create_path('counts')
    counts1.to_csv(os.path.join('counts', newFileName))
    counts = pd.read_csv(os.path.join('counts', newFileName))
    counts.columns = ['gene function', 'organism', groupName + '_' + sampleID]
    return counts

####GO FROM TWO TABLES (FXN AND ORG) TO COUNTS####
def counts_within_metagenome(fxnTable, orgTable, groupName, sampleID):
    mergedTable = merge_annotation_tables(fxnTable, orgTable)
    counts = get_and_save_counts(mergedTable, groupName, sampleID)
    return counts


#####CONVERTING TAB ANNOTATIONS FROM MG-RAST INTO RAW COUNTS DATA#####
def get_counts_within_metagenome(fxnTable, orgTable, groupName, sampleID):
    fxnData = pd.read_csv(fxnTable, delimiter = '\t', usecols=['query sequence id', 'percentage identity', 'bit score', 'semicolon separated list of annotations'])
    orgData = pd.read_csv(orgTable, delimiter = '\t', usecols=['query sequence id', 'percentage identity', 'bit score', 'semicolon separated list of annotations'])

    fxnDataMax = keep_max_pctID_only(fxnData)
    orgDataMax = keep_max_pctID_only(orgData)

    counts = counts_within_metagenome(fxnDataMax, orgDataMax, groupName, sampleID)

    return counts

###CONVERT TAB ANNOTATIONS TO COUNTS WITHIN A GROUP####
def get_counts_within_group(studyName, groupName):
    fxnDataList = glob.glob(os.path.join(studyName + '/' + groupName, '*function*.tab'))
    orgDataList = glob.glob(os.path.join(studyName + '/' + groupName, '*organism*.tab'))
    grpCountsList = [get_counts_within_metagenome(fxnDataList[i], orgDataList[i], groupName, str(i+1)) for i in range(len(fxnDataList))]
    return grpCountsList

#####GET ALL THE COUNTS (FROM TAB ANNOTATIONS) OF ALL THE GROUPS IN A STUDY#####
def get_all_group_counts(studyName):
    grpsList = [poo.split('/')[1] for poo in glob.glob(os.path.join(studyName, '*'))]
    fullCountsList = [get_counts_within_group(studyName, grp) for grp in grpsList]
    return fullCountsList

###FIND SAMPLING DEPTH FOR SUBSAMPLING###
def find_sampling_depth(rawCounts):
    sums = []
    for i in range(len(rawCounts)):
        rawCounts[i] = rawCounts[i].set_index(['gene function', 'organism'])
        sums.insert(i, int(rawCounts[i].sum()))
    lenSeries = pd.Series(sums)
    samplingDepth = int(lenSeries.median())
    return samplingDepth

####WRITE RAREFIED AND RECODED COUNTS TO FILE####
def rarefy_and_recode(filenames, rawCounts, samplingDepth):
    for i in range(len(rawCounts)):
        subsampleList = []
        if int(rawCounts[i].sum()) < samplingDepth:
            meanSubsample = rawCounts[i]
        else:
            for j in range(100):
                sample = subsample_counts(rawCounts[i].transpose().values[0], samplingDepth)
                subsampleList.insert(j, sample)
            print("completed 100 subsamples for sample number " + str(i))
            meanSubsample = pd.Series(subsampleList).mean()
            #recodification: setting all values less than 1.01 to zero
            meanSubsample[meanSubsample < 1.01] = 0
        sampleName = filenames[i].split('/')[1].split('.')[0]
        rawCounts[i][sampleName] = meanSubsample
        newFileName = sampleName + "_norm.csv"
        create_path('normalised_counts')
        rawCounts[i].to_csv(os.path.join('normalised_counts', newFileName))
        print("written " + newFileName + " to file.")
    return

#####NORMALISE BY R&R (TO MEDIAN)#####
def normalise_rnr(fullCountsList):
    flatCountsList = sum(fullCountsList, [])
    samplingDepth = find_sampling_depth(flatCountsList)
    filenames = glob.glob(os.path.join('counts/*.csv'))
    rarefy_and_recode(filenames, flatCountsList, samplingDepth)
    return
'''
############################################################################################
'''
ANNOTATING COUNTS DATA

Communicates with Entrez E-utilities to annotate hierarchies









'''
############################################################################################
''' Insert the proper version of the get_taxid function '''
'''
def get_taxid(species):
    species = species.split(';')[0].replace(" ", "+").replace("''", " ") #.split('+')
    search = Entrez.esearch(term = species, db = "taxonomy", retmode = "xml", usehistory = "y")
    record = Entrez.read(search)
    if (record['IDList'] == []):
        name_fixed = record['ErrorList']['PhraseNotFound'][0].split("+")
        redo = get_taxid(name_fixed[0] + " " + name_fixed[1])
        search2 = Entrez.esearch(term = name_fixed, db = "taxonomy", retmode = "xml")
        record = Entrez.read(search2)
    else:
        record = record

    return record['IDList'][0]

def get_tax_data(taxid):
    search = Entrez.efetch(id = taxid, db = "taxonomy", retmode = "xml")
    return Entrez.read(search)


def get_tax_hierarchy(species):
    try:
        taxid = get_taxid(species)
        data = get_tax_data(taxid)
    except:
        time.sleep(50)
        taxid = get_taxid(species)
        data = get_tax_data(taxid)
    lineage = {d['Rank']:d['ScientificName'] for d in data[0]['LineageEx'] if d['Rank'] in ['phylum', 'class', 'order', 'family', 'genus']}
    return lineage





#HIERARCHY ANNOTATION#
#input is a series of species names







def get_taxonomic_hierarchy(organismSeries, userEmail):

    Entrez.email = userEmail
    Entrez.tool = "Vibhu-species2taxon"
    if not Entrez.email:
        print("you must add your email address")
        sys.exit(2)

    lineage_list = []

    print('parsing taxonomic data...') #starting the parser

    for species in organismSeries:
        print ('\t' + species.split(";")[0]) #print progress
        lineage = get_tax_hierarchy(species)
        lineage_list.append(str(lineage))
        time.sleep(5)

    return lineage_list


##ANNOTATE ENTIRE METAGENOMES DATA FRAME WITH HIERARCHY##
#input is a dataframe in which the numerical columns are each samples
def annotate_with_hierarchy(dfCounts):

    dfCounts['lineage'] = dfCounts['organism'].str.split(";").str[0]

    speciesList = dfCounts['lineage'].unique().tolist()
    speciesSeries = pd.Series(speciesList)
    lineageDF = pd.read_csv('lineage_dict.csv')
    lineageDict = dict(zip(lineageDF['species'].tolist(), lineageDF['lineage'].tolist()))


    #lineageList = get_taxonomic_hierarchy(speciesSeries, 'vibhuc@me.com')

    #lineageDict = dict(zip(speciesList, lineageList))

    dfCounts['lineage'].replace(lineageDict, inplace = True)

    dfCounts['phylum'] = dfCounts['lineage'].str.extract("'p\w+\'\: \'([A-z]\w+)\'", expand = False)
    dfCounts['class'] = dfCounts['lineage'].str.extract("'c\w+\'\: \'([A-z]\w+)\'", expand = False)
    dfCounts['order'] = dfCounts['lineage'].str.extract("'o\w+\'\: \'([A-z]\w+)\'", expand = False)
    dfCounts['family'] = dfCounts['lineage'].str.extract("'f\w+\'\: \'([A-z]\w+)\'", expand = False)
    dfCounts.pop('lineage')
    return dfCounts
'''
############################################################################################
'''
DETERMING THE RELATIONSHIP BETWEEN CHANGE IN DIVERSITY AND CHANGE IN FUNCTION











'''
############################################################################################


###SEARCH BY GENE###
#takes dataframe
def search_by_gene(query, dfCounts):
    queryList = query.replace(" ", "|").replace("+", " ")
    geneSorted = dfCounts[dfCounts['gene function'].str.contains(queryList)]
    return geneSorted

from metadex import *
annotatedCountsList = glob.glob('lagoon study/*taxonomy.csv')
annotatedDFsList = [pd.read_csv(count) for count in annotatedCountsList]
[annDF.pop('Unnamed: 0') for annDF in annotatedDFsList]

def merge_dfs2(ldf, rdf):
    print('yep, again...')
    return ldf.merge(rdf, how='outer', on=['gene function', 'organism', 'phylum', 'class', 'order', 'family'])

def merge_all_counts(studyName):
    annotatedCountsList = glob.glob(studyName + '/*taxonomy.csv')
    annotatedDFsList = [pd.read_csv(count) for count in annotatedCountsList]
    [annDF.pop('Unnamed: 0') for annDF in annotatedDFsList]
    mergedCounts  = reduce(merge_dfs2, annotatedDFsList)
    mergedCounts.to_csv(str(studyName) + '_allcounts.csv')
    return mergedCounts

def split_hierarchically(geneSorted):
    taxList = []
    taxList.append(geneSorted.groupby('phylum').sum())
    taxList.append(geneSorted.groupby('class').sum())
    taxList.append(geneSorted.groupby('order').sum())
    taxList.append(geneSorted.groupby('family').sum())
    return taxList

def subset_by_gene(studyName, geneName):
    os.chdir(studyName)
    annotatedCountsList = glob.glob('norm_taxonomy/*taxonomy.csv')
    annotatedDFsList = [pd.read_csv(count) for count in annotatedCountsList]
    [annDF.pop('Unnamed: 0') for annDF in annotatedDFsList]
    testMerge = reduce(merge_dfs2, annotatedDFsList)
    testMerge = testMerge.fillna(0)
    testMerge.to_csv(studyName+'_allcounts.csv')
    geneDF = search_by_gene(geneName, testMerge)
    geneList = split_hierarchically(geneDF)
    [geneList[i].to_csv('level'+ str(i+1) +'_counts.csv') for i in range(len(geneList))]
    os.chdir('..')
    return geneList
####PLOT RENYI PROFILE###
#input is a data frame of values with rows representing taxa (in the individual columns) and columns representing the individual samples, as labelled with [group]_[samplenumber]

###MAKE COUNTS PROPORTIONAL (FOR RENYI PROFILE ETC)###
def make_counts_proportional(counts):
        counts = counts/counts.sum()
        return counts
###CALCULATE RENYI ENTROPY###
def renyientropy(px, alpha):
    if alpha < 0:
        raise ValueError("alpha must be a non-negative real number")
    elif alpha == 0:
        renyi = np.log2(len(px[px > 0]))
    elif alpha == 1:
        renyi = -np.sum(np.nan_to_num(px*np.log2(px)))
    elif alpha == np.inf:
        renyi = -np.log2(px.max())
    else:
        renyi = 1/(1-alpha) * np.log2((px**alpha).sum())
    return renyi
#####CALCULATE RENYI PROFILE#####
def calculate_renyi_profile(lvlCounts):
    profile_values = []
    if lvlCounts.sum() == 0:
        profile_values = [0,0,0,0,0,0,0,0,0,0,0]
    else:
        lvlCounts = lvlCounts/lvlCounts.sum()
        counts_distribution = lvlCounts

        profile_values.append(renyientropy(counts_distribution, 0))
        profile_values.append(renyientropy(counts_distribution, .25))
        profile_values.append(renyientropy(counts_distribution, .5))
        profile_values.append(renyientropy(counts_distribution, 1))
        profile_values.append(renyientropy(counts_distribution, 2))
        profile_values.append(renyientropy(counts_distribution, 4))
        profile_values.append(renyientropy(counts_distribution, 8))
        profile_values.append(renyientropy(counts_distribution, 16))
        profile_values.append(renyientropy(counts_distribution, 32))
        profile_values.append(renyientropy(counts_distribution, 64))
        profile_values.append(renyientropy(counts_distribution, np.inf))
    return profile_values
##step 1: create a list of four separate dataframes for counts summed by phylum, class, order, and family:

##SUBSET DATAFRAMES
def get_groups_list(dataCounts):
    grpsList =  dataCounts.columns.str.split("_").str[0].unique()
    return grpsList

def average_by_groups(grpsList, taxListLevel):
    grpsMeanList = []
    for i in range(len(grpsList.tolist())):
        grpsMeanList.insert(i, taxListLevel.filter(like=grpsList.tolist()[i]).mean(1))
    return grpsMeanList

def sem_by_groups(grpsList, taxListLevel):
    grpsSemList = []
    for i in range(len(grpsList.tolist())):
        grpsSemList.insert(i, taxListLevel.filter(like=grpsList.tolist()[i]).sem(1))
    return grpsSemList

def avg_renyi_by_groups(grpsList, taxListLevel):
    grpsMeanList = []
    for i in range(len(grpsList.tolist())):
        grpsMeanList.insert(i, np.average(make_renyiprofile_list(taxListLevel.filter(like=grpsList.tolist()[i])), axis=0))
    return grpsMeanList

def sem_renyi_by_groups(grpsList, taxListLevel):
    grpsSemList = []
    for i in range(len(grpsList.tolist())):
        grpsSemList.insert(i, stats.sem(make_renyiprofile_list(taxListLevel.filter(like=grpsList.tolist()[i]))))
    return grpsSemList

def plot_hierarchical_renyi(taxList, geneName):
    grpsList = get_groups_list(taxList[0])

    #!/usr/bin/env python
    from scipy import stats

    import numpy as np
    import matplotlib.pyplot as plt
    avgRenyiList = []
    semRenyiList = []
    avgRenyiList1 = []
    semRenyiList1 = []
    avgRenyiList2 = []
    semRenyiList2 = []
    avgRenyiList3 = []
    semRenyiList3 = []
    # example data
    for i in range(len(grpsList.tolist())):
     avgRenyiList.insert(i, avg_renyi_by_groups(grpsList,taxList[0])[i])
     semRenyiList.insert(i, sem_renyi_by_groups(grpsList,taxList[0])[i])

     avgRenyiList1.insert(i, avg_renyi_by_groups(grpsList,taxList[1])[i])
     semRenyiList1.insert(i, sem_renyi_by_groups(grpsList,taxList[1])[i])

     avgRenyiList2.insert(i, avg_renyi_by_groups(grpsList,taxList[2])[i])
     semRenyiList2.insert(i, sem_renyi_by_groups(grpsList,taxList[2])[i])

     avgRenyiList3.insert(i, avg_renyi_by_groups(grpsList,taxList[3])[i])
     semRenyiList3.insert(i, sem_renyi_by_groups(grpsList,taxList[3])[i])






    renyi_vals = np.asarray([0, .25, .5, 1, 2, 4, 8, 16, 32, 64, np.inf])

    # First illustrate basic pyplot interface, using defaults where possible.

    import matplotlib.gridspec as gridspec
    fig = plt.figure(dpi=1600)
    # Now switch to a more OO interface to exercise more features.
    gs1 = gridspec.GridSpec(4, 1)


    ax = fig.add_subplot(gs1[0])
    for i in range(len(grpsList.tolist())):
        ax.errorbar(renyi_vals, avgRenyiList[i], label=grpsList.tolist()[i], yerr=semRenyiList[i])
    ax.set_xscale('log')
    ax.set_title('phylum')

    # With 4 subplots, reduce the number of axis ticks to avoid crowding.

    ax = fig.add_subplot(gs1[1])
    for i in range(len(grpsList.tolist())):
        ax.errorbar(renyi_vals, avgRenyiList1[i], label=grpsList.tolist()[i], yerr=semRenyiList1[i])
    ax.set_xscale('log')
    ax.set_title('class')

    ax = fig.add_subplot(gs1[2])
    for i in range(len(grpsList.tolist())):
        ax.errorbar(renyi_vals, avgRenyiList2[i], label=grpsList.tolist()[i], yerr=semRenyiList2[i])
    ax.set_xscale('log')
    ax.set_title('order')

    ax = fig.add_subplot(gs1[3])
    for i in range(len(grpsList.tolist())):
        ax.errorbar(renyi_vals, avgRenyiList2[i], label=grpsList.tolist()[i], yerr=semRenyiList2[i])
    # Here we have to be careful to keep all y values positive:
    ax.set_xscale('log')
    ax.set_title('family')

    fig.suptitle('Diversity Measures of Organisms with ' + geneName)
    fig.set_size_inches(35, 25, forward=True)
    plt.show()
    return


#step 2.1: create list of distributions from each column of dataframe
def  make_renyiprofile_list(countsDF):
    distributionsList = []
    renyiProfileList = []
    for i in range(len(countsDF.columns.tolist())):

        renyiProfileList.insert(i, np.array(calculate_renyi_profile(countsDF.ix[:, i])))
    return renyiProfileList


#Step 3: Calculate Renyi profile lists for all four dataframes in the taxa list
def calculate_hierarchical_renyi(taxList):
    hierRenyiList = []
    for i in range(len(taxList)):
      hierRenyiList.insert(i,make_renyiprofile_list(taxList[i]))
    return hierRenyiList


###CALCULATE DOUGHNUT (DONUT) CHARTS ####


def fractionalise_by_column(df):
    for column in df:
        if(df[column].dtype == np.float64 or df[column].dtype == np.int64):
            df[column] = df[column]/(df[column].sum())
        else:
            df[column] = df[column]
    return df


def percentify_by_column(df):
    for column in df:
        if(df[column].dtype == np.float64 or df[column].dtype == np.int64):
            df[column] = df[column] * 100
        else:
            df[column] = df[column]
    return df


def make_diversity_donut(geneSorted, geneName, inner, outer):
    cols = pd.Series([c for c in geneSorted.columns if '_'  in  c.lower()])
    grpsList = cols.str.split("_").str[0].unique()

    geneAvg = average_by_groups(grpsList, geneSorted)
    for i in range(len(geneAvg)):
        geneSorted[str(grpsList[i])] = geneAvg[i]
    cols = pd.Series([c for c in geneSorted.columns if '_' not in  c.lower()])
    geneSortedMean = geneSorted[cols]
    geneMeanList = []
    grpsList = grpsList.tolist()
    for group in grpsList:
        geneMeanList.insert(grpsList.index(group),  geneSortedMean[geneSortedMean[group] > 0])
    donutList = []
    vcColourList = ["#007892",
            "#ff6521",
            "#8c39e9",
            "#00cd1a",
            "#b900cb",
            "#b7d200",
            "#001c8e",
            "#ffd638",
            "#0045a0",
            "#efa200",
            "#41025b",
            "#a9f17a",
            "#ff92ff",
            "#548900",
            "#de0061",
            "#74f6bc",
            "#e40038",
            "#01ac95",
            "#ff65ab",
            "#008c5b",
            "#860025",
            "#00b7d5",
            "#ae4c00",
            "#82b6ff",
            "#c77300",
            "#0181c1",
            "#ffba5e",
            "#311852",
            "#d9e49f",
            "#10244e",
            "#ff8a65",
            "#003f5a",
            "#ff8492",
            "#005a25",
            "#b5aeff",
            "#5d5f00",
            "#e5d9f5",
            "#781f00",
            "#c8e2ec",
            "#500907",
            "#eaddbe",
            "#3c183b",
            "#896500",
            "#016c70",
            "#6e002f",
            "#002d1c",
            "#ffabbc",
            "#462f00",
            "#45132c",
            "#372016"]

    for k in range(len(geneMeanList)):
        donutList.insert(k, Donut(geneMeanList[k], label=[inner, outer], values=grpsList[k], palette = Set3[12], text_font_size = '1em', hover_text = grpsList[k], plot_height = 2000, plot_width = 2000, title = geneName + " by " +  inner + " and " + outer + ": group " + grpsList[k]))
    output_file(str(geneName) + "_" + str(inner) + "_" +  str(outer) + ".html")
    show(column(donutList))
    return donutList



def get_hierarchical_DD(geneSorted, geneName):
    print("generating for phylum -> class...")
    pcDonutList = make_diversity_donut(geneSorted, geneName, 'phylum', 'class')
    print("generating for class -> order...")
    coDonutList = make_diversity_donut(geneSorted, geneName, 'class', 'order')
    print("generating for order -> family...")
    ofDountList = make_diversity_donut(geneSorted, geneName, 'order', 'family')
    return


