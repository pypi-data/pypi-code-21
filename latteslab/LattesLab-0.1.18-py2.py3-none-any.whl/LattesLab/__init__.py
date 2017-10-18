# -*- coding: iso-8859-1 -*-
"""
Created on Tue Aug  1 18:11:54 2017

@author: thiag
"""
####The code that runs goes here
from pylab import rcParams
rcParams['figure.figsize'] = 8, 6
rcParams['figure.dpi'] = 200
rcParams['font.size'] = 22

####This variable defines the amount of years of publications and works
####collected per Lattes CV files

Nworks = 20

def word_list_to_cloud(cfolder, topwords):
    """ Word cloud generating function

    From the list of words in arg topwords generates a word cloud and saves
    in the folder passed through the arg folder.

    Args:
        folder(str): string that contains the folder address.
        topwords(list): list of the words that will generate the word cloud.

    """

    from wordcloud import WordCloud
    from datetime import datetime
    import matplotlib.pyplot as plt
    import os
    
    folder = os.path.normpath(cfolder)

    dummie = ' '.join(topwords)
    wordcloud = WordCloud().generate(dummie)
    plt.axis('off')
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.savefig(folder + 'wordcloud'+ datetime.now().strftime('%Y%m%d%H%M%S')+
                '.png')
    plt.show()

def summary_list_top_words(summarylist, nwords=50):

    """ Gets words with higher TF-IDF score

    From the summarylist list of documents, gets the quantity nwords of words
    that have the biggest score according to TF-IDF algorithm.

    Args:
        summarylist (list): list of documents with its contents.
        nwords (int): quantity of words returned by the function.

    """
    from sklearn.feature_extraction.text import TfidfVectorizer
#initialize the tf idf matrix

    tf = TfidfVectorizer(analyzer='word', ngram_range=(1, 1),
                         min_df=0, stop_words=['quot'])

#fit and transform the list of lattes cv summaries to tf idf matrix

    tfidf_matrix = tf.fit_transform(summarylist)
    feature_names = tf.get_feature_names()

    dense = tfidf_matrix.todense()

    lattessummary = dense[0].tolist()[0]

#if the score of the word is >0, add the word and its score to the wordscores
#list

    wordscores = [pair for pair in zip(range(0, len(lattessummary)),
                                       lattessummary) if pair[1] > 0]

#sort the score list by the score (second term)

    sorted_wordscores = sorted(wordscores, key=lambda t: t[1] * -1)

    topwords = []

    for word, score in [(feature_names[word_id], score) for (word_id, score)
                        in sorted_wordscores][:nwords]:
        print('{0: <40} {1}'.format(word, score))
        topwords.append(word)

    return topwords


def get_node_connections(nodelist, network, depth=1):

    """ Gets quantity of connections of first or second grade.

    From the list of nodes in arg nodelist, finds the number of direct
    connections (if depth equals 1) or of second degree connections (if depth
    equals 2) in the node network in the arg network.

    Args:
        nodelist: list of nodes to evaluate number of connections.
        network: network where the nodes will be searched and the number of
        connections will be counted.
        depth: depth of the quantity of connections. Equals 1 for direct
        connections and 2 for connections and connections of connections.

    """
    import networkx as nx
    if (depth > 2) | (depth < 1):
        print("invalid depth supplied")
    connections = []
    dummie = network.edges()

    if depth == 1:
        for i in range(0, len(nodelist)):
            x = 0
            for y in dummie:
                if nodelist[i] in y: x = x + 1
            connections.append(x)

    elif depth == 2:
        for i in range(0, len(nodelist)):
            x = 0
#list all the edges connecting to node intlist[i]
            dummie2 = network.edges(nodelist[i])
            for y in dummie2:
#verify connections of those connected to intlist[i]
                for z in dummie:
                    if y[1] in z: x = x + 1
            connections.append(x)

    return connections

def nodes_class(graph, nodeslist):

    """ Classify nodes in the graph network with reference to nodeslist.

    From the list of nodes in arg nodelist, verify if these nods are part of
    the network in arg graph. If they are, and attribute "type" is set as
    "internal". Otherwise, the attribute "type" is set as "external"

    Args:
        nodelist: list of nodes to compare with the network and to receive the
        attribute "type".
        graph: network where the nodes in nodelist will be searched and
        be considered "internal" or "external".

    """
    import networkx as nx
    nx.set_node_attributes(graph, "type", "external")
    for x in graph.nodes():
        if x in nodeslist:
            graph.node[x]["type"] = "internal"
    return graph


def lattes_owner(filename):

    """ Returns the name of the owner of the Lattes CV found in arg filename

    Args:
        filename: complete path (folder + file) of the file where the Lattes
        CV is found. The file must be a zip file containing a XML file.

    """
    import zipfile
    import xml.etree.ElementTree as ET
    #abre o arquivo zip baixado do site do lattes
    archive = zipfile.ZipFile((filename), 'r')
#cvdata = archive.read('curriculo.xml')
    cvfile = archive.open('curriculo.xml', 'r')

#inicializa o xpath
    tree = ET.parse(cvfile)
    root = tree.getroot()
#get the cv owner name
    cvowner = root[0].attrib['NOME-COMPLETO']
    return cvowner


def lattes_age(rawdata):

    """ Plots a histogram of the Lattes CV collection age

    Args:
        rawdata: dataframe containing the data for the histogram.
    """
    import numpy as np
    import matplotlib.pyplot as plt

    from datetime import datetime
    x = [datetime.today() - datetime.strptime(str(i), '%d%m%Y') \
         for i in rawdata['atualizado']]
    y = np.array([round(i.days/30) for i in x])

#histogram of Lattes CV age in months
    plt.figure(figsize=(8, 6), dpi=200)
    dummie = plt.hist(y, bins=range(0, round(max(y)+10, 2)),
                      align='left', histtype='bar', rwidth=0.95)

    plt.axvline(y.mean(), color='black', linestyle='dashed',
                linewidth=2)
    plt.text(round(max(y)+10, 2)*0.3, 0.8*max(dummie[0]),
             'Mean = ' + str(round(y.mean(), 2)))
    plt.suptitle('Age of Lattes CV in months', fontsize=20)
    plt.show()
    del dummie

def lattes_pibics(rawdata):

    """ Plots a histogram of PIBIC scholarships per student in the dataframe.

    Args:
        rawdata: dataframe containing the data for the histogram.
    """
    import matplotlib.pyplot as plt
#histogram of PIBIC scholarships per student
    plt.figure(figsize=(8, 6), dpi=200)

    plt.hist(rawdata['quantasVezesPIBIC'],
             bins=range(max(rawdata['quantasVezesPIBIC'])+2), align='left',
             histtype='bar', rwidth=0.95)

    plt.xticks(range(min(rawdata['quantasVezesPIBIC']),
                     max(rawdata['quantasVezesPIBIC'])+1), fontsize=22)

    plt.suptitle('Scientific Initiation Grants per Student', fontsize=20)
    plt.show()

def masters_rate_year(rawdata):
#Histogram of masters degrees
    """ Plots a histogram of Masters degrees started per year.

    Args:
        rawdata: dataframe containing the data for the histogram.
    """
    import matplotlib.pyplot as plt
    import numpy as np
    
    plt.figure(figsize=(8, 6), dpi=200)

#If the first year is zero, get the second smaller year
    if min(rawdata['anoPrimeiroM']):
        anomaster0 = min(rawdata['anoPrimeiroM'])
    else:
        anomaster0 = sorted(set(rawdata['anoPrimeiroM']))[1]
#last year of occurence of a masters degree

    anomaster1 = max(rawdata['anoPrimeiroM'])

#plot the histogram and store in x
    dummie = plt.hist(rawdata['anoPrimeiroM'], bins=range(anomaster0,
                      anomaster1), align='left', histtype='bar', rwidth=0.95)

    plt.suptitle('Masters Degrees Obtained per Year', fontsize=20)

#Plot the total of people who finished masters degree in the given position
    plt.text(anomaster0, 0.8*np.argmax(dummie[0]), 'Total = ' +
             str(len(rawdata['anoPrimeiroM'].loc[lambda s: s > 0])), size='20')
    plt.show()

    del dummie

def lattes_grad_level(rawdata):
    """ Plots a histogram of the specialization level of the students.

    Args:
        rawdata: dataframe containing the data for the histogram.
    """
    import pandas as pd
    import matplotlib.pyplot as plt

    pibics = len(rawdata.loc[rawdata.quantasVezesPIBIC >= 1])
    masters = len(rawdata.loc[rawdata.quantosM >= 1])
    phds = len(rawdata.loc[rawdata.quantosD >= 1])
    pphds = len(rawdata.loc[rawdata.quantosPD >= 1])

    graddata = pd.DataFrame([pibics, masters, phds, pphds],
                            index=['Scientific Initiation', 'Masters', 'PhD',
                                   'Postdoctorate'],
                            columns=['Quantity'])


    plt.figure(figsize=(8, 6), dpi=200)
    fig = graddata.plot(y='Quantity', kind='bar', legend=False)
    fig.set_xticklabels(graddata.index, rotation=45)
    plt.title('Academic Level of the Students')
    plt.show()

def get_pub_year_data(rawdata):
    """ Arranges the publication data from calendar year to a generic sequence
        of years, preparing this data to be used for other means.

    Args:
        rawdata: dataframe containing the data for the histogram.
    """
    from datetime import datetime

    import pandas as pd

    firstyear = datetime.now().year - Nworks + 1

    #Normalizes the year of the first publication
    #The first year of the publication dataframe is the current calendar
    #year minus Nworks

    #For means of production indexes, the quantity of papers and works
    #presented in congresses are summed to each other

    pubyeardata = pd.DataFrame(index=rawdata.index)
    for i in range(0, Nworks):
        pubyeardata['pub' + str(firstyear + i)] = rawdata['papers' +
                    str(firstyear + i)] + rawdata['works' + str(firstyear + i)]

        if i == Nworks-1:
            pubdata = pubyeardata.copy()
            strindex = ['year']*pubdata.shape[1]
            for i in range(1, pubdata.shape[1]):
                strindex[i] = strindex[i] + str(i+1)

    pubdata.columns = strindex

    return pubdata

def first_nonzero(frame, frameindex, option=0):
    """Changes the production per year vector based on the variable "option".
    Args:
        frame: the dataframe where the production data is found.
        frameindex: contains the year of the first PIBIC scholarship for each
           student in arg frame. Is only used if arg option=2
        option=0: production is based on calendar year. leave frame unchanged.
        option=1: first production value is first non-zero value of the
           production vector. The last vector indexes are substituted by zeros.
        option=2: first production year is first year of PIBIC scholarship.
           Only make sense to use it in PIBIC-based dataframes.
    """
    import pandas as pd
    from datetime import datetime

    firstyear = datetime.now().year - Nworks + 1

    nrows = frame.shape[0]
    ncols = frame.shape[1]
    count = 0

    if option == 1:
        #for each row
        for i in range(0, nrows):
            while (frame.iloc[i, 0] == 0) & (count < ncols):
                for j in range(0, ncols-1):
                    frame.set_value(i, frame.columns[j], frame.iloc[i, j+1])
                frame.set_value(i, frame.columns[ncols-1], 0)
                count = count + 1

    elif option == 2:

        for i in range(0, nrows):
    #    nshift = frameindex[nrow] - 2004
            nshift = frameindex.iloc[i] - firstyear
            if nshift > 0:
                for j in range(0, ncols-1-nshift):
                    frame.set_value(i, frame.columns[j], frame.iloc[i, j+nshift])
                    frame.set_value(i, frame.columns[ncols-1-j], 0)
                count = count + 1
    else:
        if option != 0: print('Invalid option in function argument.\n Using'+\
                            ' default option = 0.')

def set_fuzzycmeans_clstr(imin, imax, cleandata):
    """Applies the algorithm fuzzy c means to the dataframe in arg cleandata
        to try to find a quantity of mean publication profiles. This quantity
        varies from arg imin to arg imax.
    Args:
        cleandata: the dataframe where the production data is found.
        imin: minimum quantity of fuzzy c means clusters to be evaluated.
        imax: maximum quantity of fuzzy c means clusters to be evaluated.
    """
    import matplotlib.pyplot as plt
    import skfuzzy as fuzz
    import numpy as np
    from sklearn import metrics
    from sklearn.cluster import KMeans
    from sklearn.decomposition import PCA
    from sklearn.preprocessing import scale


    fpcs = []
    centers = []
    clusters = []
    for i in range(imin, imax):
        center, u, u0, d, jm, p, fpc = fuzz.cluster.cmeans(\
            cleandata.transpose(), i, 2, error=0.005, \
            maxiter=1000, init=None)
        cluster_membership = np.argmax(u, axis=0)
#plota o histograma de cada centroide
        plt.figure()

        clusterweight = plt.hist(cluster_membership, bins=range(i+1),
                                 align='left', histtype='bar', rwidth=0.95)
        plt.xticks(range(0, i))
        plt.title('Number of Points in Each Centroid of the ' +
                  str(i)+' Centroid Model')
        plt.show()

#agrupa funcao de desempenho
        fpcs.append(fpc)
#agrupa os centroides
        centers.append(center)
#agrupa o peso dos centroides
        clusters.append(cluster_membership)

        fig, ax = plt.subplots()
        plt.title('Model with ' + str(i) + ' Mean Publication Profiles')
        for j in range(0, i):
            ax.plot(center[j], label=str(clusterweight[0][j]))

        legend = ax.legend(loc='upper right', shadow=True)
        plt.show()

#    plt.figure()
#    plt.plot(center, label=cluster_membership)
#    plt.title(str(i)+ ' Centroides')

    plt.figure()
    plt.plot(range(imin, imax), fpcs, '-x')
    plt.title('Fuzzy C Means Performance related to the Centroid Quantity')
    plt.show()
    return centers, clusters, fpcs


def get_grad_years(x, gradtype):
    """From the arg x, that contains a XML piece of the Lattes CV where a
    graduation course data is found, extract the number of years spent on the
    course, as well as the year in which the course has started.
    Args:
        gradtype: type of graduation course.
    """
    nfirst = nquant = 0
    if (x.attrib["ANO-DE-CONCLUSAO"] != "") | (x.attrib["ANO-DE-INICIO"] != ""):
        nquant = nquant + 1
        if nquant == 1:
            if x.attrib["ANO-DE-CONCLUSAO"] == "":
                x.attrib["ANO-DE-CONCLUSAO"] = \
                    str(int(x.attrib["ANO-DE-INICIO"]) + xpectd_years(gradtype))
            nfirst = int(x.attrib["ANO-DE-CONCLUSAO"])
#Se terminou o curso
        if x.attrib["ANO-DE-CONCLUSAO"] == "":
            x.attrib["ANO-DE-CONCLUSAO"] = \
                str(int(x.attrib["ANO-DE-INICIO"]) + xpectd_years(gradtype))

        if nfirst > int(x.attrib["ANO-DE-CONCLUSAO"]):
            nfirst = int(x.attrib["ANO-DE-CONCLUSAO"])

    return [nfirst, nquant]

def xpectd_years(gradtype):
    """From the arg gradtype, returns an average number of years the
    graduation course found in gradtype takes to be concluded.
    Args:
        gradtype: type of graduation course.
    """
    if gradtype == "GRADUACAO":
        return 4
    elif gradtype == "MESTRADO":
        return 2
    elif gradtype == "DOUTORADO":
        return 4
    elif gradtype == "POS-DOUTORADO":
        return 2
    else:
        print("Invalid input for graduation type in function xpectdyears")
        return 0


def get_graph_from_file(filename, opt='all'):
    """From the file in filename returns a graph where the nodes are the
    researchers and the edges.
    Args:
        filename: contains the name of the file where the graph is extracted.
        opt==all: lists all names found in the Lattes CV as nodes.
        opt==phdboards: lists all names found where the researcher has taken
        part of PhD boards.
        opt==allboards: lists all names found where the researcher has taken
        part of graduation boards.
    """
#From input file filename gets all partnerships occurred between the owner of
#the Lattes CV of the filename file and phd presentations listed on that CV.

    import zipfile
    import xml.etree.ElementTree as ET
    import networkx as nx

#opens zip file downloaded from lattes website
#abre o arquivo zip baixado do site do lattes

    archive = zipfile.ZipFile((filename), 'r')
    cvfile = archive.open('curriculo.xml', 'r')

#inicializa o arquivo xpath
#initializes xpath file

    tree = ET.parse(cvfile)
    root = tree.getroot()

    if opt == 'all':
## get all the authors names cited on lattes cv
        x = root.findall('.//*[@NOME-COMPLETO-DO-AUTOR]')
        nameattb = 'NOME-COMPLETO-DO-AUTOR'
    elif opt == 'phdboards':
## get all the phd commitees found in the lattes cv
        x = root.findall('.//PARTICIPACAO-EM-BANCA-DE-DOUTORADO/*[@NOME-DO-CANDIDATO]')
        nameattb = 'NOME-DO-CANDIDATO'
    elif opt == 'allboards':
## get all commitees found in the lattes cv
        x = root.findall('.//PARTICIPACAO-EM-BANCA-TRABALHOS-CONCLUSAO//*[@NOME-DO-CANDIDATO]')
        nameattb = 'NOME-DO-CANDIDATO'

    y = list(enumerate(x))

#initialize the graph
    cvgraph = nx.Graph()

#get the cv owner name
    cvowner = root[0].attrib['NOME-COMPLETO']

#add the node representing the cv owner
    cvgraph.add_node(cvowner)

#for each name found in the cv
    for elem in x:
        dummie = elem.attrib[nameattb]
        if dummie != cvowner:
            if not(dummie in cvgraph.nodes()):
                cvgraph.add_node(dummie)
                cvgraph.add_edge(cvowner, dummie, weight=1)
            else:
                cvgraph[cvowner][dummie]['weight'] += 1

    return cvgraph

def get_graph_from_folder(cfolder):
    """
    From Lattes CV files in a folder, ret
    """

    import LattesLab as ll
    import networkx as nx
    import matplotlib.pyplot as plt
    from datetime import datetime
    import pandas as pd
    import numpy as np
    import warnings
    import os
    
    folder = os.path.normpath(cfolder)
	
    warnings.filterwarnings("ignore")

    [filelist, errlist] = ll.get_files_list(folder)

    vecgraph = []
    namelist = []

    for file in filelist:
        filename = os.path.join(folder,file)
        dummiegraph = ll.get_graph_from_file(filename)
        vecgraph.append(dummiegraph)
        namelist.append(ll.lattes_owner(filename))

    #join the graphs in the vector vecgraph in a single network

    network = ll.join_graphs(vecgraph)

    network = ll.nodes_class(network, namelist)

    #to avoid plotting big names, convert names to integers, with a dictionary
    network = nx.convert_node_labels_to_integers(network,
                                                 label_attribute='name')

    intlist = []
    extlist = []
    for x in network.nodes(data=True):
        if x[1]['type'] == 'internal': intlist.append(x[0])
        elif x[1]['type'] == 'external': extlist.append(x[0])

    #nx.draw_networkx_nodes(network,pos=nx.spring_layout(network),nodelist=intlist)

    #pos=nx.spring_layout(network, k=1/np.sqrt(len(network)))
    pos = nx.shell_layout(network, [intlist, extlist])
    nx.draw_networkx_nodes(network, pos, nodelist=extlist,
                           node_color='r',  alpha=0.2)   
    nx.draw_networkx_nodes(network, pos, nodelist=intlist, node_color='b')
    #nx.draw_networkx_labels(network,pos)
    nx.draw_networkx_edges(network, pos, width=1.0, alpha=0.2)
    plt.axis('off')
    plt.show()

    figfile = 'graph' + datetime.now().strftime('%Y%m%d%H%M%S') + '.png'

    plt.savefig(os.path.join(folder, figfile))
    
    textfilename = "Labels" + datetime.now().strftime('%Y%m%d%H%M%S') + ".txt",
    

    textfile = open(os.path.join(folder, textfilename), "w")

    for x in network.nodes(data = True):
        dummy1 = str(x[0]).encode(encoding='ISO-8859-1', errors='strict'). \
                        decode(encoding='utf-8', errors='ignore')
        dummy2 = x[1]['name'].encode(encoding='ISO-8859-1', errors='strict'). \
                        decode(encoding='utf-8', errors='ignore')
        textfile.write(dummy1 + '\t'+ dummy2)

    textfile.close()
    del x

    #list of all weights
    netweights = list([x[2]['weight'] for x in network.edges(data=True)])

    abc = ll.top_n_contributions(network, 10)

    network2 = nx.Graph(x for x in network.edges(data=True) \
                        if x[2]['weight'] > 1)

    #measure how many first connections people in internal group have:
    firstconnections = ll.get_node_connections(intlist, network, 1)

    #measure how many second connections people in internal group have:
    secondconnections = ll.get_node_connections(intlist, network, 2)

    connections = pd.DataFrame(
            {'name': namelist,
             'firstconnections': firstconnections,
             'secondconnections': secondconnections,
             'ratio': np.array(firstconnections)/np.array(secondconnections)
             })
    datafilename = "DataFrame" + datetime.now().strftime('%Y%m%d%H%M%S') + ".txt"
    connections.to_csv(os.path.join(folder, datafilename))

    return [network, connections]


def top_n_contributions(xgraph, n):
    """From the graph found in arg xgraph, takes the n largest (with score
    repetition) weights between the edges, which means in the biggest
    contributions between two researchers found in the xgraph nodes.
    Args:
        xgraph: graph where the weight of the edges is measured.
        n: number of highest weights returned by the function.
    """
#from a given graph xgraph, gets the n biggest weights and returns

    import networkx as nx
    import numpy as np
    topcontribs = []

#takes the weights from the graph edges

    netweights = list([x[2]['weight'] for x in xgraph.edges(data=True)])

#creates a list with the sorted weights

    weightlist = list(np.sort(netweights)[::-1])

    for i in range(0, n):
        dummie = [k for k in xgraph.edges(data=True) if
                  k[2]['weight'] == weightlist[i]]
        for z in dummie: topcontribs.append(z)

    for z in topcontribs:
        print(xgraph.node[z[0]]['name'] + ' and ' + xgraph.node[z[1]]['name'] +
              ' have worked together ' + str(z[2]['weight']) + ' times.')
    networklarge = [x for x in xgraph.edges(data=True) if
                    x[2]['weight'] > weightlist[n]]
    nx.draw(nx.Graph(networklarge), with_labels=True)
    return topcontribs


def get_files_list(cfolder):
    """Gets a list of files from the arg folder and check for errors.
    Args:
        folder: the folder where the Lattes CV files are found. The Lattes CV
            files are downloaded as .zip files containing a .xml file.
    """

    import os
    import zipfile
    import xml.etree.ElementTree as ET

    folder = os.path.normpath(cfolder)

    fileslist = os.listdir(folder)
    goodlist = badlist = []
    goodlist = [x for x in fileslist if x.endswith('.zip')]
    badlist = [x for x in fileslist if not x.endswith('.zip')]

#test each xml for parsing capabilities
    for filename in goodlist:
        try:
            rightname = os.path.join(folder, filename)
            archive = zipfile.ZipFile(rightname, 'r')
            if (archive.namelist()[0][-3:] == 'xml')| \
                (archive.namelist()[0][-3:] == 'XML'):
                cvfile = archive.open(archive.namelist()[0], 'r')
                ET.parse(cvfile)
            else:
                print('Error: file ' + archive.namelist()[0] + \
                      'is not a xml file.')
        except:
            print('XML parsing error in file ' + filename)
            goodlist.remove(filename)
            badlist.append(filename)
    return [goodlist, badlist]

def get_colab(filename, columns):
    """From file in arg filename, extract the production of the Lattes CV owner
        and the other researchers that were coauthors in this production.
    Args:
        filename: file containing the Lattes CV subject to analysis.
        columns: list of columns that compose the dataframe.
    """
    import zipfile
    import xml.etree.ElementTree as ET
    import pandas as pd

#abre o arquivo zip baixado do site do lattes
    archive = zipfile.ZipFile((filename), 'r')
#cvdata = archive.read('curriculo.xml')
    cvfile = archive.open('curriculo.xml', 'r')

#inicializa o xpath
    tree = ET.parse(cvfile)
    root = tree.getroot()

    #cv owner id
    cvid = root.attrib['NUMERO-IDENTIFICADOR']

    colabframe = pd.DataFrame(columns=columns)

    #list of all works in events

    colabtype = 'T'

    xworks = root.findall('.//TRABALHO-EM-EVENTOS')

    for x in xworks:
        authors = x.findall('AUTORES')
        for y in authors:
            try:
                dummieid = y.attrib['NRO-ID-CNPQ']
            except:
                dummieid = ''
            if (dummieid != '') & (dummieid != cvid):
                cvid2 = y.attrib['NRO-ID-CNPQ']
                year = x[0].attrib['ANO-DO-TRABALHO']
                title = x[0].attrib['TITULO-DO-TRABALHO']
                dummie = pd.DataFrame(data=[[colabtype, cvid, cvid2, year, title]],
                                      columns=columns)
                colabframe = colabframe.append(dummie)

    #list of all papers
    colabtype = 'A'

    xpapers = root.findall('.//ARTIGO-PUBLICADO')

    for x in xpapers:
        authors = x.findall('AUTORES')
        for y in authors:
            try:
                dummieid = y.attrib['NRO-ID-CNPQ']
            except:
                dummieid = ''
            if (dummieid != '') & (dummieid != cvid):
                cvid2 = y.attrib['NRO-ID-CNPQ']
                year = x[0].attrib['ANO-DO-ARTIGO']
                title = x[0].attrib['TITULO-DO-ARTIGO']
                dummie = pd.DataFrame(data=[[colabtype, cvid, cvid2, year, title]],
                                      columns=columns)
                colabframe = colabframe.append(dummie)

    return colabframe

def join_graphs(vecgraph):
    """Joins two or more graphs found in the arg vecgraph.
    Args:
        vecgraph: list of graphs to be concatenated.
    """
    import networkx as nx
    if len(vecgraph) < 2:
        return vecgraph
    elif len(vecgraph) == 2:
        return nx.compose(vecgraph[0], vecgraph[1])
    else:
        dummie = nx.compose(vecgraph[0], vecgraph[1])
        for i in range(2, len(vecgraph)):
            dummie = nx.compose(dummie, vecgraph[i])
        return dummie

def get_lattes_desc_folder(cfolder):
    """Extracts the description section of each Lattes CV found in arg folder.
    Args:
        folder: the folder where the Lattes CV files are found. The Lattes CV
            files are downloaded as .zip files containing a .xml file.
        savefile: if True, the dataframe is stored in a .csv file for posterior
            use.
    TODO: implement capacity to save file. Maybe use pickle
    """
    import zipfile
    import xml.etree.cElementTree as ET
    import os
    
    folder = os.path.normpath(cfolder)

    [goodlist, badlist] = get_files_list(folder)

    summarylist = []

    del badlist
    for cvzipfile in goodlist:
        filename = os.path.join(folder, cvzipfile)
#abre o arquivo zip baixado do site do lattes
        archive = zipfile.ZipFile((filename), 'r')
#cvdata = archive.read('curriculo.xml')
        cvfile = archive.open('curriculo.xml', 'r')

#get the summary information from lattes cv
        tree = ET.parse(cvfile)
        root = tree.getroot()
        try:
            desc = root[0][0].attrib['TEXTO-RESUMO-CV-RH']
        except:
            desc = ""
        summarylist.append(desc)

    return summarylist

def get_dataframe_from_folder(cfolder, savefile=True):
    """Extracts the Lattes CV dataframe to be used by other functions in
        this library.
    Args:
        folder: the folder where the Lattes CV files are found. The Lattes CV
            files are downloaded as .zip files containing a .xml file.
        savefile: if True, the dataframe is stored in a .csv file for posterior
            use.
    """
    import pandas as pd
    import xml.etree.ElementTree as ET
    import zipfile
    from datetime import datetime
    import os
    
    folder = os.path.normpath(cfolder)

    columns = ['Nome',
               'lattesId',
               'atualizado',
               'quantasVezesPIBIC',
               'anoPrimeiroPIBIC',
               'quantasGrad',
               'anoPrimeiraGrad',
               'quantosM',
               'anoPrimeiroM',
               'quantosD',
               'anoPrimeiroD',
               'quantosPD',
               'anoPrimeiroPosDoc'] + \
               ["works" + str(datetime.now().year - i) for i in range(0, Nworks)] + \
               ["papers" + str(datetime.now().year - i) for i in range(0, Nworks)]

    lattesframe = pd.DataFrame(columns=columns)

#filters the zip files

    ziplist = nonziplist = []

    [ziplist, nonziplist] = get_files_list(folder)

    count = 0

    for filename in ziplist:
        count += 1

        rightname = os.path.join(folder, filename)

        archive = zipfile.ZipFile(rightname, 'r')
        cvfile = archive.open(archive.namelist()[0], 'r')

        tree = ET.parse(cvfile)
        root = tree.getroot()

    #lista todos os atributos do arquivo XML
        elemtree = []

        for elem in tree.iter():
            elemtree.append(elem.tag)

        elemtree = list(set(elemtree))

        root.tag
        root.attrib
        root.getchildren()

    #Dados gerais
        readid = str(root.attrib["NUMERO-IDENTIFICADOR"])
        lastupd = str(root.attrib["DATA-ATUALIZACAO"])
        name = root[0].attrib["NOME-COMPLETO"]

    #Dados de formacao academica

        ngrad = nmaster = nphd = nposdoc = 0
        ano1grad = ano1master = ano1phd = ano1postdoc = 0

        x = root.findall('.//FORMACAO-ACADEMICA-TITULACAO')

    #ESSA PARTE DO CODIGO MERECE UMA FUNCAO, TA BAGUNCADO
        if x != []:
            for i in range(0, len(x[0].getchildren())):
                if x[0][i].tag == "GRADUACAO":
                    [ano1grad, ngrad] = \
                        get_grad_years(x[0][i], x[0][i].tag)
                elif x[0][i].tag == "MESTRADO":
                    [ano1master, nmaster] = \
                        get_grad_years(x[0][i], x[0][i].tag)
                elif x[0][i].tag == "DOUTORADO":
                    [ano1phd, nphd] = \
                        get_grad_years(x[0][i], x[0][i].tag)
                elif x[0][i].tag == "POS-DOUTORADO":
                    [ano1postdoc, nposdoc] = \
                        get_grad_years(x[0][i], x[0][i].tag)

    #producao bibliografica

        root[1].getchildren()

    #quantidade de trabalhos publicados
        x = root.findall('.//TRABALHOS-EM-EVENTOS')

        if not x:
            qtyworks = 0
        else:
            qtyworks = len(x[0].getchildren())

        nprod = []

        for i in range(0, qtyworks):
            nprod.append(x[0][i][0].attrib["ANO-DO-TRABALHO"])

        nprodyear = [0]*Nworks

    #num intervalo de 20 anos, contar a quantidade de publicacoes por ano de 2017
    #i=0 para tras

        for i in range(0, Nworks):
            nprodyear[i] = nprod.count(str(datetime.now().year - i))

    #quantidade de artigos publicados
        x = root.findall('.//ARTIGOS-PUBLICADOS')

        if len(x) > 0:
            npapers = len(x[0].getchildren())
        else:
            npapers = 0

        allpapers = []

        for i in range(0, npapers):
            allpapers.append(x[0][i][0].attrib["ANO-DO-ARTIGO"])

        npaperyear = [0]*Nworks

    #num intervalo de Nworks anos, contar a quantidade de publicacoes por ano
    # de 2017 i=0 para tras

        for i in range(0, Nworks):
            npaperyear[i] = allpapers.count(str(datetime.now().year - i))

    #Procurando pela quantidade de iniciações cientificas
    #    root[0][4][0].tag #estava usando esse, mudei para o debaixo
        x = root.findall('.//*[@OUTRO-VINCULO-INFORMADO="Iniciação Cientifica"]') + \
            root.findall('.//*[@OUTRO-VINCULO-INFORMADO="Iniciação Científica"]') + \
            root.findall('.//*[@OUTRO-ENQUADRAMENTO-FUNCIONAL-INFORMADO=' +  \
                               '"Bolsista de Iniciação Cientifica"]') + \
            root.findall('.//*[@OUTRO-ENQUADRAMENTO-FUNCIONAL-INFORMADO=' +  \
                               '"Bolsista de Iniciação Científica"]') + \
            root.findall('.//*[@OUTRO-ENQUADRAMENTO-FUNCIONAL-INFORMADO=' +  \
                               '"Aluno de Iniciação Cientifica"]') + \
            root.findall('.//*[@OUTRO-ENQUADRAMENTO-FUNCIONAL-INFORMADO=' +  \
                               '"Aluno de Iniciação Científica"]')

        qtdeanos = 0
        if not x:
            ano1PIBIC = 0
        else:
            ano1PIBIC = int(x[0].attrib["ANO-INICIO"])

        for elem in x:
            if elem.attrib["ANO-FIM"] == "": # & \
    #            (elem.attrib["SITUACAO"]=="EM_ANDAMENTO"):

                elem.attrib["ANO-FIM"] = str(datetime.now().year)
            if elem.tag == "VINCULOS":
                if (elem.attrib["MES-INICIO"] != "")&(elem.attrib["MES-FIM"] != ""):
                    qtdeanos += (float(elem.attrib["ANO-FIM"]) -
        				   			  float(elem.attrib["ANO-INICIO"]) +
    					   		     (float(elem.attrib["MES-FIM"]) -
    						   	      float(elem.attrib["MES-INICIO"]))/12)
                else:

    #As vezes o projeto comeca e termina no mesmo ano. Corrigir o delta anos.

                    if elem.attrib["ANO-FIM"] == elem.attrib["ANO-INICIO"]:
                        qtdeanos += 1
                    else:
                        qtdeanos += (float(elem.attrib["ANO-FIM"]) -
                                     float(elem.attrib["ANO-INICIO"]))
            if ano1PIBIC > int(elem.attrib["ANO-INICIO"]):
                ano1PIBIC = int(elem.attrib["ANO-INICIO"])

        qtdePIBIC = round(qtdeanos)

        x = [name, readid, lastupd, qtdePIBIC, ano1PIBIC,
             ngrad, ano1grad, nmaster, ano1master, nphd,
             ano1phd, nposdoc, ano1postdoc] + nprodyear + npaperyear

        dummie = pd.DataFrame(data=[x], columns=columns)

        lattesframe = lattesframe.append(dummie)

#        print(str(100*count/len(ziplist)) + '%%')

#reindex the dataframe
    lattesframe = lattesframe.reset_index()
#drop the old index
    lattesframe = lattesframe.drop('index', axis=1)

    if savefile: lattesframe.to_csv(folder + 'dataframe.csv', index=False)

    return lattesframe


def lattes_classes_from_folder(cfolder, imin=2, imax=10, option=0):
    """
    From the Lattes CV files found in a given folder, extract some exploratory
    data results and perform analysis of the n mean publication profiles,
    where n varies from imin to imax.
    Args:
        folder: the folder where the Lattes CV files are found.
        imin: lowest number of mean publication profiles analyzed.
        imax: highest number of mean publication profiles analyzed.
    """
    import LattesLab as ll
    import os
    
    folder = os.path.normpath(cfolder)

    lattesframe = ll.get_dataframe_from_folder(folder, True)

    cleandata = lattesframe

    ll.lattes_age(lattesframe)

    ll.lattes_pibics(lattesframe)

    ll.masters_rate_year(lattesframe)

    ll.lattes_grad_level(lattesframe)

    pubdata = ll.get_pub_year_data(lattesframe)

    ll.first_nonzero(pubdata, lattesframe['anoPrimeiroPIBIC'], option)

    cleandata = pubdata
    fpcs = []
    centers = []
    clusters = []

    print('Analysis with all data.')

    centers, clusters, fpcs = ll.set_fuzzycmeans_clstr(imin, imax, cleandata)

    #novo dataframe que recebe apenas os estudantes que publicaram
    print('Analysis with all researchers that have published at least once.')
    cleandata2 = cleandata[cleandata.sum(axis=1) != 0]
    fpcs2 = []
    centers2 = []
    clusters2 = []

    centers2, clusters2, fpcs2 = ll.set_fuzzycmeans_clstr(imin, imax, cleandata2)

    return lattesframe

def lattes_classes_from_frame(lattesframe, imin=2, imax=10, option=0):
    """
    From the Lattes CV dataframe previously processed, extract some exploratory
    data results and perform analysis of the n mean publication profiles,
    where n varies from imin to imax.
    Args:
        lattesframe: the Lattes CV dataframe where the Lattes CV data are found.
        imin: lowest number of mean publication profiles analyzed.
        imax: highest number of mean publication profiles analyzed.
    """
    import LattesLab as ll

    cleandata = lattesframe

    ll.lattes_age(lattesframe)

    ll.lattes_pibics(lattesframe)

    ll.masters_rate_year(lattesframe)

    ll.lattes_grad_level(lattesframe)

    pubdata = ll.get_pub_year_data(lattesframe)

    ll.first_nonzero(pubdata, lattesframe['anoPrimeiroPIBIC'], option)

    cleandata = pubdata
    fpcs = []
    centers = []
    clusters = []

    print('Analysis with all data.')

    centers, clusters, fpcs = ll.set_fuzzycmeans_clstr(imin, imax, cleandata)

    #novo dataframe que recebe apenas os estudantes que publicaram
    print('Analysis with all researchers that have published at least once.')
    cleandata2 = cleandata[cleandata.sum(axis=1) != 0]
    fpcs2 = []
    centers2 = []
    clusters2 = []

    centers2, clusters2, fpcs2 = ll.set_fuzzycmeans_clstr(imin, imax, cleandata2)

def filter_PIBICs(lattesframe, npibics=1):
    """Returns the rows of the researchers in arg lattesframe that have
    been part of the PIBIC scholarship at least once.
    Args:
        lattesframe: the pandas dataframe to be filtered.
        npibics: the minimum quantity of PIBICs to be filtered.
    """
    if npibics <= 0:
        print('Invalid arg npibics. Reverting to default npibics == 1.')
        npibics = 1

    return lattesframe.loc[lattesframe['quantasVezesPIBIC'] >= npibics]

def filter_by_phd_year(lattesframe, year0, year1):
    """Returns the rows of the researchers in arg lattesframe that have
    concluded their PhD program between args year0 and year1.
    Args:
        lattesframe: the pandas dataframe to be filtered.
        year0: the first year of the interval.
        year1: the last year of the interval.
    """
    if year0 > year1:
        dummie = year0
        year0 = year1
        year1 = dummie

    return lattesframe[(lattesframe['anoPrimeiroD'] >= year0) &
                       (lattesframe['anoPrimeiroD'] <= year1)]

def filter_by_lattes_age(lattesframe, agedays):
    """Returns the rows of the researchers in arg lattesframe that have
    a lattes age lower than the arg agemonths.
    Args:
        lattesframe: the pandas dataframe to be filtered.
        agedays: the maximum acceptable age of lattes CVs to be filtered
        from lattesframe. Measured in days.
    """
    from datetime import datetime

    mask = [(datetime.today() - datetime.strptime(i, '%d%m%Y')).days < agedays \
            for i in lattesframe['atualizado']]

    return lattesframe[mask]