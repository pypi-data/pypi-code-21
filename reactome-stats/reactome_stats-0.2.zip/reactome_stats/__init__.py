#Python 2.7
#Neo4J 3.2.3
#
#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np
import time
import os
import re
import urllib
import json
from collections import Counter
import itertools
import matplotlib.pyplot as plt
from neo4j.v1 import GraphDatabase, basic_auth
import csv
from matplotlib_venn import venn2
from matplotlib_venn import venn3
import matplotlib.patches as mpatches



###- FUNCTIONS TO LOAD INFO SOURCES -### 

# 'get_dfUniProt': retrieve uniprot data frame with GO info columns associated to Reactome
def get_dfUniProt ():

  print ("Loading UniProt Human Reviewed Proteins at "+time.strftime("%H:%M:%S"))

  df_UniProt = pd.read_csv("http://www.uniprot.org/uniprot/?query=organism:9606+AND+reviewed:yes&format=tab&columns=id,reviewed,genes(PREFERRED),database(KEGG),database(Reactome),go(biological%20process),go(cellular%20component),go(molecular%20function),go-id,families",sep ="\t")
  #http://www.uniprot.org/uniprot/?query=organism:9606+AND+reviewed:yes&format=tab&columns=id,reviewed,genes(PREFERRED), database(KEGG),database(Reactome), go(biological process), go(cellular component), go(molecular function), go-id, families
  #http://www.uniprot.org/uniprot/?query=organism:9606+AND+reviewed:yes&format=tab&columns=id,reviewed,genes(PREFERRED),database(KEGG),database(Reactome),go(biological%20process),go(cellular%20component),go(molecular%20function),go-id,families
  df_UniProt = df_UniProt.rename(columns = {'Entry':'DB_Object_ID', 'Status':'Status',  'Gene names':'HGNCSymbol',  'Cross-reference (KEGG)':'KeggID',  'Cross-reference (Reactome)':'ReactomeID',  'Gene ontology (biological process)':'GO_BP', 'Gene ontology (cellular component)':'GO_CC', 'Gene ontology (molecular function)':'GO_MF', 'Gene ontology IDs':'GO_ID',  'Protein families':'ProteinFamily'})

  df_UniProt['ProteinFamily'] = df_UniProt.ProteinFamily.replace(np.NaN, 'No Family assigned')
  df_UniProt['ReactomeID'] = df_UniProt.ReactomeID.replace(np.NaN, 'No at Reactome')
  df_UniProt['KeggID'] = df_UniProt.KeggID.replace(np.NaN, 'No at Kegg')

  print ("\nSucessful load at "+time.strftime("%H:%M:%S")+ "!")

  return(df_UniProt)

# 'get_dfUniProtAllh': 
def get_dfUniProtAllh ():

  print ("\nLoading all human proteins (rev or not reviewed) annotated at UniProt " + time.strftime("%H:%M:%S") + "\n")
  df_uniprotAllH = pd.read_csv("http://www.uniprot.org/uniprot/?query=organism:9606&format=tab&columns=id,reviewed,genes(PREFERRED),database(Reactome)",sep ="\t")
  print ("\nSuccessfully load " + time.strftime("%H:%M:%S") + "\n")

  return(df_uniprotAllH)

# 'get_goOntologies': retrieve go ontologies dataframe (processed from original source)
def get_goOntologies (copyNovember2017 = True) : 

  if copyNovember2017 == True:

    print ("Loading GO Ontologies from November 2017 at "+time.strftime("%H:%M:%S"))

    df_GOContologies = pd.read_csv("https://raw.githubusercontent.com/corinabioinformatic/Neo4J_at_Reactome/Analysis_2/output_a2_allGOfromOWLfile.csv",sep ="\t")

    print ("\nFinished succesfully at "+time.strftime("%H:%M:%S")+ "!")

    return(df_GOContologies)

  elif copyNovember2017 == False:

    print ("Loading the up-to-date GO ontologies file at "+time.strftime("%H:%M:%S"))

    target_url = urlopen("http://purl.obolibrary.org/obo/go.owl")
    zipfile  = ZipFile(StringIO(target_url.read()))
    data = zipfile.open('go.owl_2017-10-31.rdf').readlines()
    listClassesGO = []
    listAspectGO = []
    counter = 0

    for line in data: # files are iterable

      matchObj =re.search(r'<owl:Class rdf:about="http://purl.obolibrary.org/obo/GO_(.*)">' ,line)
      matchObj2 =re.search(r'<oboInOwl:hasOBONamespace rdf:datatype="http://www.w3.org/2001/XMLSchema#string">(molecular_function|biological_process|cellular_component)</oboInOwl:hasOBONamespace>' ,line)
      matchObj3 =re.search(r'<owl:deprecated rdf:datatype="http://www.w3.org/2001/XMLSchema#boolean">true</owl:deprecated>' ,line)  

      if (matchObj) and (counter ==0):

        goToAppend = ("GO:"+str(matchObj.group(1)))
        listClassesGO.append(goToAppend)
        counter = counter + 1

      elif (matchObj2) and (counter ==1):

        goToAppend2 = str(matchObj2.group(1))
        listAspectGO.append(goToAppend2)
        counter = counter - 1

      elif (matchObj) and (counter ==1):
        
        listAspectGO.append("")
        goToAppend = ("GO:"+str(matchObj.group(1)))
        listClassesGO.append(goToAppend)

    df_GOContologies = pd.DataFrame({'GO_ID':listClassesGO,'Aspect':listAspectGO})
    print ("\nFinished succesfully at "+time.strftime("%H:%M:%S")+ "!")

    return(df_GOContologies)

# 'get_dfGOC': Retrieve table GOC annotations (*recommended change the link to GOC -*gaf file)
def get_dfGOC(typeSet = 'all', loadSourcesNov2017 = True):

  if loadSourcesNov2017 == True:

    df_GOC_prot = pd.read_csv("https://github.com/corinabioinformatic/Neo4J_at_Reactome/raw/Analysis_2/input_a2_goa_human_1.gaf.gz", compression='gzip', sep='\t', comment='!', names = ["DB","DB_Object_ID","DB_Object_Symbol","Qualifier","GO_ID","DB:Reference","EvidenceCode","With(or)From","Aspect","DB_Object_Name","DB_Object_Synonym","DB_Object_Type","Taxon","Date","Assigned_By","Annotation_Extension","Gene_Product_Form_ID"])
    #Table 1.B.2
    df_GOC_cplx = pd.read_csv("https://github.com/corinabioinformatic/Neo4J_at_Reactome/raw/Analysis_2/input_a2_goa_human_2complex.gaf.gz", compression='gzip', sep='\t', comment='!', names = ["DB","DB_Object_ID","DB_Object_Symbol","Qualifier","GO_ID","DB:Reference","EvidenceCode","With(or)From","Aspect","DB_Object_Name","DB_Object_Synonym","DB_Object_Type","Taxon","Date","Assigned_By","Annotation_Extension","Gene_Product_Form_ID"])
    #Table 1.B.3
    df_GOC_rna = pd.read_csv("https://github.com/corinabioinformatic/Neo4J_at_Reactome/raw/Analysis_2/input_a2_goa_human_3rna.gaf.gz", compression='gzip', sep='\t', comment='!', names = ["DB","DB_Object_ID","DB_Object_Symbol","Qualifier","GO_ID","DB:Reference","EvidenceCode","With(or)From","Aspect","DB_Object_Name","DB_Object_Synonym","DB_Object_Type","Taxon","Date","Assigned_By","Annotation_Extension","Gene_Product_Form_ID"])
    #Table 1.B.4
    df_GOC_isof = pd.read_csv("https://github.com/corinabioinformatic/Neo4J_at_Reactome/raw/Analysis_2/input_a2_goa_human_4isoform.gaf.gz", compression='gzip', sep='\t', comment='!', names = ["DB","DB_Object_ID","DB_Object_Symbol","Qualifier","GO_ID","DB:Reference","EvidenceCode","With(or)From","Aspect","DB_Object_Name","DB_Object_Synonym","DB_Object_Type","Taxon","Date","Assigned_By","Annotation_Extension","Gene_Product_Form_ID"])

  else:

    df_GOC_prot = pd.read_csv("http://geneontology.org/gene-associations/goa_human.gaf.gz", compression='gzip', sep='\t', comment='!', names = ["DB","DB_Object_ID","DB_Object_Symbol","Qualifier","GO_ID","DB:Reference","EvidenceCode","With(or)From","Aspect","DB_Object_Name","DB_Object_Synonym","DB_Object_Type","Taxon","Date","Assigned_By","Annotation_Extension","Gene_Product_Form_ID"])
    #Table 1.B.2
    df_GOC_cplx = pd.read_csv("http://geneontology.org/gene-associations/goa_human_complex.gaf.gz", compression='gzip', sep='\t', comment='!', names = ["DB","DB_Object_ID","DB_Object_Symbol","Qualifier","GO_ID","DB:Reference","EvidenceCode","With(or)From","Aspect","DB_Object_Name","DB_Object_Synonym","DB_Object_Type","Taxon","Date","Assigned_By","Annotation_Extension","Gene_Product_Form_ID"])
    #Table 1.B.3
    df_GOC_rna = pd.read_csv("http://geneontology.org/gene-associations/goa_human_rna.gaf.gz", compression='gzip', sep='\t', comment='!', names = ["DB","DB_Object_ID","DB_Object_Symbol","Qualifier","GO_ID","DB:Reference","EvidenceCode","With(or)From","Aspect","DB_Object_Name","DB_Object_Synonym","DB_Object_Type","Taxon","Date","Assigned_By","Annotation_Extension","Gene_Product_Form_ID"])
    #Table 1.B.4 from ftp://ftp.ebi.ac.uk/pub/databases/GO/goa/HUMAN/
    df_GOC_isof = pd.read_csv("ftp://ftp.ebi.ac.uk/pub/databases/GO/goa/HUMAN/goa_human_isoform.gaf.gz", compression='gzip', sep='\t', comment='!', names = ["DB","DB_Object_ID","DB_Object_Symbol","Qualifier","GO_ID","DB:Reference","EvidenceCode","With(or)From","Aspect","DB_Object_Name","DB_Object_Synonym","DB_Object_Type","Taxon","Date","Assigned_By","Annotation_Extension","Gene_Product_Form_ID"])


  #Table 1.B
  df_GOC = pd.concat([df_GOC_prot,df_GOC_cplx, df_GOC_rna,df_GOC_isof])

  if typeSet == 'all' :

    return(df_GOC)

  elif typeSet == 'uniprot' :

    df_GOC_Uniprot  = df_GOC[df_GOC['DB'].isin(['UniProtKB'])]
    return(df_GOC_Uniprot)

  elif typeSet == 'curated' :

    df_GOC_Uniprot  = df_GOC[df_GOC['DB'].isin(['UniProtKB'])]  
    df_GOC_UniProt_curated = df_GOC_Uniprot[~df_GOC_Uniprot['EvidenceCode'].isin(['IEA'])]

    return(df_GOC_UniProt_curated)

  elif typeSet == 'iea' :

    df_GOC_Uniprot  = df_GOC[df_GOC['DB'].isin(['UniProtKB'])]
    df_GOC_UniProt_iea = df_GOC_Uniprot[df_GOC_Uniprot['EvidenceCode'].isin(['IEA'])]

    return(df_GOC_UniProt_iea)



########  FUNCTIONS ANALYSIS 5: Gene Ontology ancestors   #######

# 'get_listGOatReactome': Retrieve LIST of unique GO at Reactome (data loaded from table of Uniprot Search engine)
def get_listGOatReactome (tableUniProtReactomeGO):

  print ("Extracting individual GO Id from UniProt "+time.strftime("%H:%M:%S"))

  df_ReactomeGraphDB_GO = tableUniProtReactomeGO[~tableUniProtReactomeGO['ReactomeID'].isin(['No at Reactome'])] #pd.read_csv('https://raw.githubusercontent.com/corinabioinformatic/Neo4J_at_Reactome/Analysis_2/output_a2_AllHumanGOReactomeGraphDB_python.csv')
  listGO = []

  for i in df_ReactomeGraphDB_GO['GO_ID'].tolist():

    valGO = str(i)

    if valGO != "":

      regex = r'GO:([0-9]+)'
      s_ID = re.findall(regex, valGO)
      listGO = (listGO + s_ID)

  #print (time.strftime("%H:%M:%S"))
  listGO_unique = list(set(listGO)) 

  print ("\nFinished succesfully at "+time.strftime("%H:%M:%S"))

  return(listGO_unique)

# 'writeGOtable' : write to table
def writeGOtable (listGOid, nameDf, df_GOConto):


  df_ancestorX = df_GOConto[df_GOConto['GO_ID'].isin(listGOid)]
  folderPath = os.getcwd()
  pathToWrite = (folderPath+nameDf+".csv")  
  df_ancestorX.to_csv(pathToWrite, index = False)
  print ("Table is already available at: "+pathToWrite)

# writeStats
def writeStats (list1, list2, list3, list4 , list5):

  dfResults = pd.DataFrame({'allGOID_uniqueReactome':[len(list1)],'allGOancestors_fromGOReactome':[len(list2)],'n_GOIntersectionChildAndAncestors':[len(list3)],'n_GOonlyChildAtReactome':[len(list4)],'n_GOnotAtReactome':[len(list5)]})
  #Little summary table of the results
  folderPath = os.getcwd()
  pathToWrite = (folderPath+'\\output_a5_resultsAncestors.csv')
  dfResults.to_csv(pathToWrite)

  print ("Table is already available at: "+pathToWrite)

#'get_root_ancestors' : Retrieve list of roots of ontologies
def get_root_ancestors ():

  ###*~*LOADING_ROOT_ANCESTORS*~*###

  url2 = "https://www.ebi.ac.uk/ols/api/ontologies/go/terms/roots"
  response2 = urllib.urlopen(url2)
  data2 = json.loads(response2.read())
  data2_embedded = data2['_embedded']

  list_data2_embedded_terms = data2_embedded['terms']

  list_root_id = []
  #counter2 = 1
  for i in list_data2_embedded_terms:
    if i['obo_id'] != None:
      root_id_n = i['obo_id']
      list_root_id.append(root_id_n)
      #counter2 = counter + 1 

  return(list_root_id)

#'get_ancestors': retrieve list of ancestor from a list of childs, by mean of OLS Rest API
def get_ancestors (listReactome, listAndStats = True, gocCopyNovember2017 = None):

  if gocCopyNovember2017 == True:

    df_gocOnto = get_goOntologies(copyNovember2017 = True)

  elif gocCopyNovember2017 == None:

    df_gocOnto = get_goOntologies()


  print ("\nLoading main roots from GO "+time.strftime("%H:%M:%S")+"\n")

  ###*~*GET_ROOT_ANCESTORS*~*###

  listRootAncestors = get_root_ancestors()
  print("There are " +str(len(listRootAncestors))+ "root ancestors")
  lenListGOReactome = len(listReactome)

  ###*~*GET_ANCESTORS*~*###
    
  listAncestors = []
  s_goReactome = listReactome
  listDisconnectedGO = []  


  for i in s_goReactome:

    listGOsearch = ["GO", i]
    iSearch = "_".join(listGOsearch)

    url = ("https://www.ebi.ac.uk/ols/api/ontologies/go/terms/http%253A%252F%252Fpurl.obolibrary.org%252Fobo%252F"+iSearch+"/ancestors?size=500")
    #print(url)
    response = urllib.urlopen(url)
    data = json.loads(response.read())
    #1..._embedded
    data_embedded = data['_embedded']

    #"2...terms"
    list_data_embedded_terms = data_embedded['terms']

    #"3...get from list (items) -> obo_id"
    list_obo_id = []

    for ii in list_data_embedded_terms:

      if ii['obo_id'] != None:

        obo_id_n = ii['obo_id']
        #checkList
        list_obo_id.append(obo_id_n)
        #finalList
        listAncestors.append(obo_id_n) #<--- should I use symetric_difference rather than save all in one list?
        #counter = counter + 1 

    if (any(x in listRootAncestors for x in list_obo_id)) == False: #    if any of the ancestors is the root is a connected graph

      #print(len(list_obo_id))
      #print(list_obo_id)
      print ("[!]Something is wrong to arrive to the main ancestors of :"+iSearch)
      listDisconnectedGO.append(iSearch)

    lenListGOReactome = lenListGOReactome-1

    if lenListGOReactome%5000==0:

      print ("Processed "+str(lenListGOReactome)+" GO")

  listAncestorsUnique = set(listAncestors)

  list_reactomeGO_unique = []

  for i in listReactome:

    list_i = ['GO',i]
    list_reactomeGO_unique.append(":".join(list_i)) 

  list_reactomeAncestors_unique = list(set(listAncestorsUnique))

  intersectionAncestorsChild = list(set(list_reactomeGO_unique).intersection(set(list_reactomeAncestors_unique)))
  onlyAtReactome = list(set(list_reactomeGO_unique).difference(set(list_reactomeAncestors_unique))) #should be 0
  notAtReactome = list(set(list_reactomeAncestors_unique).difference(set(list_reactomeGO_unique)))  #this is the interesting list to fill at the DB

  listAncestorsConnectedDisconnected = [intersectionAncestorsChild, onlyAtReactome, notAtReactome, list_reactomeAncestors_unique,listDisconnectedGO]

  if listAndStats == True:

    print ("Writing lists and Statistics about ancestors "+time.strftime("%H:%M:%S"))

    writeGOtable(notAtReactome, 'ancestorNoAnnotatedAtReactome', df_gocOnto)
    writeGOtable(onlyAtReactome, 'GOId_ChilAtReactome', df_gocOnto)
    writeGOtable(intersectionAncestorsChild, 'GOId_ChildAndAncestorAtReactome', df_gocOnto)

    print("Number of unique GO Id annotated at Reactome:")
    print(len(listReactome))

    print("Number of GO ancestor unique in Reactome:")
    print(len(list_reactomeAncestors_unique))

    print("Number of GO Id annotated at Reactome ancestor from other GO Id at Reactome")
    print(len(intersectionAncestorsChild))

    print("Number of GO Id only child annotated at Reactome")
    print(len(onlyAtReactome))

    print("Number of ancestors no at Reactome")
    print(len(notAtReactome))
    #print(notAtReactome)

    writeStats(listReactome,list_reactomeAncestors_unique, intersectionAncestorsChild,onlyAtReactome, notAtReactome)

  return(listAncestorsConnectedDisconnected)



###### FUNCTIONS ANALYSIS 4 : Kegg Pathways Coverage ######

# 'get_hsaList' Retrieve LIST of unique Kegg genome ID from human reviewed proteins (data loaded from table of Uniprot Search engine)
def get_hsaList (tableUniprot):

  listKhsa =[]

  listKeggUnprocessed = tableUniprot['KeggID'].tolist()
  listKeggUnprocessed_1 = filter(None,listKeggUnprocessed)

  #print(len(listKeggUnprocessed_1))
  #aList.remove('xyz')
  listKeggUnprocessed_2 = [ v for v in listKeggUnprocessed_1 if not v.startswith('No at Kegg') ] 
  #print(listKeggUnprocessed_2[:5])

  for i in listKeggUnprocessed_2:

    i_GenomeKegg = filter(None,(i.split(";")))
    listKhsa = listKhsa+i_GenomeKegg

  return(listKhsa)

# 'get_keggPathw' Retrieve a table map of all the kegg pathways associated to the kegg genome identifiers provided. [CAUTION! It takes long time to load]
def get_keggPathw (listKegg_i = None, writeToFolder = True, loadCopyNov2017 = True):

  if loadCopyNov2017 == True:

    print ("\nLoading copy of Kegg map table at 29th November 2017 "+time.strftime("%H:%M:%S")+"\n")

    urlKeggGP = 'https://raw.githubusercontent.com/corinabioinformatic/Neo4J_at_Reactome/Analysis_4/output_a4_keggGenomekeggPathways.csv'
    df_KeggGenomPath = pd.read_table(urlKeggGP, sep = ',')

    return(df_KeggGenomPath)

  elif loadCopyNov2017 == False:

    lenKegg = len(listKegg_i)
    counter = 0
    list_nKeggPath =[]
    list_KeggPath = []
    df_KeggGenomPath = pd.DataFrame({'KeggGenomeId':listKegg_i})

    writeKeggGP = open('output_4a_keggGP.txt','w+')
    writeKeggGP.write("KeggGenome\tn_KeggPathways\tKeggPathways"+"\n")

    for i in listKegg_i:
      #print(i)
      lenKegg = lenKegg-1
      if lenKegg%1000==0:

        print ("Processed "+str(counter)+" proteins")
        print("Working the other..."+str(lenKegg))
        print("listKegg"+str(len(list_KeggPath)))

      url = "http://rest.kegg.jp/link/pathway/"+i
      df_pathwaysKegg = pd.read_csv(url, sep = "\t",names= ["KeggID", "KeggPathID"])
      list_pathwaysKegg = df_pathwaysKegg["KeggPathID"].tolist()
      miniListKegg= []

      if len(list_pathwaysKegg) != 0:

        miniListKegg = miniListKegg + list_pathwaysKegg

      miniListKegg_unique = list(set(miniListKegg)) 
      mini_nListKegg_unique = len(miniListKegg_unique)

      list_KeggPath.append(";".join(miniListKegg_unique)) #list kegg pathways per uniprot ID
      list_nKeggPath.append(mini_nListKegg_unique) #number kegg pathways per uniprot ID
      writeKeggGP.write(str(i)+"\t"+str(mini_nListKegg_unique)+"\t"+(";".join(miniListKegg_unique))+"\n")
      counter = counter + 1

    df_KeggGenomPath['KeggPathwaysID'] = list_KeggPath
    df_KeggGenomPath['n_KeggPathwaysID'] = list_nKeggPath

    if writeToFolder == True:

      folderPath = os.getcwd()
      pathToWrite = folderPath+"output_a4_keggGenomekeggPathways.csv"
      df_KeggGenomPath.to_csv(pathToWrite, index = False)

    return(df_KeggGenomPath)

# 'get_reactomeKeggPathwaysTable' 
def get_reactomeKeggPathwaysTable (df_UniProt, df_KeggMapAll, writeTableStats = True):

  print ("\nCreate merged table with Reactome and Kegg Pathways per UniProtID at "+time.strftime("%H:%M:%S")+"\n")

  #removing all the Kegg genome ids with no pathway associated
  df_KeggMap = df_KeggMapAll[~df_KeggMapAll['KeggPathwaysID'].isin([0])] 

  listUniProt_ID = []
  listKegg_ID = []
  listReactome_ID = []
  listProteinFamily = []

  lenUniprot = len(df_UniProt['DB_Object_ID'].tolist())
  print(lenUniprot)

  #loop to create a dataframe with the mapp genome-proteins

  for i in range(0,len(df_UniProt['DB_Object_ID'].tolist())):

    keggId = df_UniProt.iloc[i]['KeggID']
    listKeggId = keggId.split(';')

    for j in listKeggId:

      listUniProt_ID.append(df_UniProt.iloc[i]['DB_Object_ID'])
      listKegg_ID.append(j)
      listReactome_ID.append(df_UniProt.iloc[i]['ReactomeID'])
      listProteinFamily.append(df_UniProt.iloc[i]['ProteinFamily'])

    lenUniprot = lenUniprot-1
    if lenUniprot%5000==0:
      print ("Processed "+str(lenUniprot)+" proteins")

  print (time.strftime("%H:%M:%S"))

  df_UniProtUnfolded = pd.DataFrame({'DB_Object_ID':listUniProt_ID,'ReactomeID':listReactome_ID,'KeggGenomeId':listKegg_ID, 'ProteinFamily':listProteinFamily})

  #print(len(df_KeggMap['DB_Object_ID'].unique()))
  df_UniProtKeggPathways = pd.merge(df_UniProtUnfolded, df_KeggMap, how='inner', on = 'KeggGenomeId')


  print('len table  unique')
  print(len(df_UniProtKeggPathways.drop_duplicates()))
  print('len Uniprot unique')
  print(len(df_UniProtKeggPathways['DB_Object_ID'].unique()))
  df_KeggPathways =  df_UniProtKeggPathways[~df_UniProtKeggPathways['KeggPathwaysID'].isnull()].drop_duplicates()
  print('len df kegg without duplicated rows')
  print(len(df_KeggPathways.drop_duplicates()))
  print("unique proteins with kegg pathway")
  print(len(df_KeggPathways['DB_Object_ID'].unique()))
  #print(df_KeggPathways.iloc[0])
  df_KeggPathways2 = df_KeggPathways.loc[:,['DB_Object_ID','KeggPathwaysID', 'nKeggPathwaysID']].drop_duplicates()
  print('len df kegg without duplicated rows excluding keggG')
  print(len(df_KeggPathways2.drop_duplicates()))

  mylist = df_KeggPathways2['DB_Object_ID'].tolist()
  print("duplicated values")
  print([k for k,v in Counter(mylist).items() if v>1])

  if writeTableStats == True:

    folderPath = os.getcwd()
    pathToWrite = (folderPath+'\\output_a4_keggGPReactome.csv')    
    df_UniProtKeggPathways.to_csv(pathToWrite, index = False)

    print("Data available at : "+pathToWrite)
    df_NoReactome = df_UniProtKeggPathways[df_UniProtKeggPathways['ReactomeID'].isin(['No at Reactome'])]
    df_NoReactomeYesKegg =  df_NoReactome[~df_NoReactome['KeggPathwaysID'].isnull()]
    pathToWrite2 = (folderPath+'\\output_a4_ProteinsNoAtReactomeYesKeggPath.csv')    
    print(len(df_NoReactomeYesKegg['KeggGenomeId'].unique()))
    #number of proteins no at reactome, but with kegg pathway.
    print(len(df_NoReactomeYesKegg['DB_Object_ID'].unique()))

    df_NoReactomeYesKegg.to_csv(pathToWrite2, index = False)

  return(df_UniProtKeggPathways)



###### FUNCTIONS ANALYSIS 3 : MultiTable Counts different sources ######

#'get_worktable' Retrieve a merged table between Uniprot, GOC and Kegg table 
def get_worktable(dfGOC= None, dfUniprot = None, df_KeggGP_0 = None, writeTable = 'no',loadCopyNov2017 = True):

  if loadCopyNov2017 == False:

    print ("\nCreating merged table from multiple sources  STEP 1 at "+time.strftime("%H:%M:%S")+"\n")

    df_KeggGP_00 = df_KeggGP_0[~df_KeggGP_0['n_KeggPathwaysID'].isin([0])].drop_duplicates()
    df_KeggGP = df_KeggGP_00.loc[:,['DB_Object_ID']].drop_duplicates()
    df_KeggGP["WithKeggPathway"] = "yes"

    n_goBp = []
    n_goCc = []
    n_goMf = []
    n_goAll = []
    list_goBp = []
    list_goCc = []
    list_goMf = []
    list_goAll = []

    #2.- Subset df_UniProt curated to get only columns DBobject, prot family and ReactomeID and KEgg Id
    #>>> table to filter by human reviewed proteins  & to merge because it has PRotein family, KEggGenome, etc
    df_UniProt_subset = dfUniprot.loc[:,['DB_Object_ID', 'ProteinFamily', 'ReactomeID', 'KeggID']]
    #>>>table of GOC filtered by reviewed human proteins
    df_UniqueProtGOC = dfGOC[dfGOC['DB_Object_ID'].isin(df_UniProt_subset['DB_Object_ID'])]
    #>>> table of GOC which provides the main counts og GOIDs.
    #df_proteinsGOCAnnotation_n = df_UniqueProtGOC.groupby(['DB_Object_ID'])['GO_ID'].nunique().to_frame().reset_index().rename(columns= {'DB_Object_ID':'DB_Object_ID','GO_ID':'n_GO_ID'})

    listUniqueProtGOC = df_UniqueProtGOC['DB_Object_ID'].unique()
    counterProt = len(listUniqueProtGOC)

    for i in listUniqueProtGOC:

      counterProt = counterProt -1
      dfGOC_i = df_UniqueProtGOC[df_UniqueProtGOC['DB_Object_ID'].isin([i])]

      dfGOC_i_bp = len(dfGOC_i[dfGOC_i['Aspect'].isin(['P'])])
      dfGOC_i_cc = len(dfGOC_i[dfGOC_i['Aspect'].isin(['C'])])    
      dfGOC_i_mf = len(dfGOC_i[dfGOC_i['Aspect'].isin(['F'])])
      dfGOC_i_all= len(dfGOC_i)
      n_goBp.append(dfGOC_i_bp)
      n_goCc.append(dfGOC_i_cc)
      n_goMf.append(dfGOC_i_mf)
      n_goAll.append(dfGOC_i_all)

      dfGOC_i_bp_toList = (dfGOC_i[dfGOC_i['Aspect'].isin(['P'])])['GO_ID'].unique().tolist()
      dfGOC_i_cc_toList = (dfGOC_i[dfGOC_i['Aspect'].isin(['C'])])['GO_ID'].unique().tolist()   
      dfGOC_i_mf_toList = (dfGOC_i[dfGOC_i['Aspect'].isin(['F'])])['GO_ID'].unique().tolist()
      dfGOC_i_all_toList = (dfGOC_i['GO_ID'].unique().tolist())
      list_goBp.append(dfGOC_i_bp_toList)
      list_goCc.append(dfGOC_i_cc_toList)
      list_goMf.append(dfGOC_i_mf_toList)
      list_goAll.append(dfGOC_i_all_toList)

      if counterProt%5000==0:

        print ("\nProcessed "+str(counterProt)+" proteins")

    df_GOaspect = pd.DataFrame({"DB_Object_ID":df_UniqueProtGOC['DB_Object_ID'].unique().tolist()})
    print("****CONTROL CHECK")
    print(len(df_GOaspect))
    df_GOaspect['n_GOBP'] = n_goBp
    df_GOaspect['n_GOCC'] = n_goCc
    df_GOaspect['n_GOMF'] = n_goMf
    df_GOaspect['n_GOall'] = n_goAll
    df_GOaspect['list_GOBP'] = list_goBp
    df_GOaspect['list_GOCC'] = list_goCc
    df_GOaspect['list_GOMF'] = list_goMf
    df_GOaspect['list_GOAll'] = list_goAll

    #3.-Merge by column
    df_proteinsGOCAnnotation_nuu_fam_kegg_reactome = (df_UniProt_subset.merge(df_GOaspect, how='left', on= 'DB_Object_ID'))
    print(len(df_proteinsGOCAnnotation_nuu_fam_kegg_reactome))

    df_proteinsGOCAnnotation_nu_fam_kegg_reactome = (df_proteinsGOCAnnotation_nuu_fam_kegg_reactome.merge(df_KeggGP, how='left', on= ['DB_Object_ID']))

    df_proteinsGOCAnnotation_nu_fam_kegg_reactome['list_GOAll'].fillna('-', inplace=True)
    df_proteinsGOCAnnotation_nu_fam_kegg_reactome['list_GOBP'].fillna('-', inplace=True)
    df_proteinsGOCAnnotation_nu_fam_kegg_reactome['list_GOCC'].fillna('-', inplace=True)
    df_proteinsGOCAnnotation_nu_fam_kegg_reactome['list_GOMF'].fillna('-', inplace=True)

    print(len(df_proteinsGOCAnnotation_nu_fam_kegg_reactome))

    folderPath = os.getcwd()
    pathToWrite3 = folderPath+"output_a3_uniprotGOCcount.csv"

    print("Table write at "+pathToWrite3)
    df_proteinsGOCAnnotation_nu_fam_kegg_reactome.to_csv(pathToWrite3,index = False, sep = "\t")

    print ("\nSuccesfully finished at  "+time.strftime("%H:%M:%S")+ " !")

  elif loadCopyNov2017 == True:

    df_proteinsGOCAnnotation_nu_fam_kegg_reactome = pd.read_csv('https://raw.githubusercontent.com/corinabioinformatic/Neo4J_at_Reactome/ReactomeStats/Examples/Analysis_3_4_5/output_a3_uniprotGOCcount.csv', sep = "\t")

  return(df_proteinsGOCAnnotation_nu_fam_kegg_reactome)

#'get_clusteredFamily_counts' Retrive a data with counts based on protein family and the table retrieved with the getWorkTable function
def get_clusteredFamily_counts(df_fam_kegg_reactome, writeT = False):

  print ("\nCreating counts table from multiple sources  STEP 2 at "+time.strftime("%H:%M:%S")+"\n")

  listReactomeStatus = []
  listKeggStatus = []
  listProteinsOneGOStatus = []
  list_nProteinsFamily = []
  list_nProteinsFamilyAtReactom = []
  list_nProteinsFamilyNoAtReactome = []
  list_nProteinsFamilyAtKegg = []
  list_nProteinsFamilyNoAtKegg = [] 
  list_nGOperFamily = []
  list_nGOBPperFamily = []
  list_nGOCCperFamily = []
  list_nGOMFperFamily = []
  list_nProteinsOneGO = []
  listProteinsOneGO = []
  list_GOperFamily = []
  list_GOBPperFamily = []
  list_GOCCperFamily = []
  list_GOMFperFamily = []

  proteinFamilies = df_fam_kegg_reactome['ProteinFamily'].unique()
  print("***CONTROL CHECK")
  print(len(proteinFamilies))
  print(len(df_fam_kegg_reactome['DB_Object_ID']))

  print(len(df_fam_kegg_reactome['DB_Object_ID'].unique()))

  for family in proteinFamilies:
    #subset of all the proteins in a family:
    df_familyX = df_fam_kegg_reactome[df_fam_kegg_reactome['ProteinFamily'].isin([family])]

    #proteins at Reactome
    df_familyX_atReactome = df_familyX[~df_familyX["ReactomeID"].isin(['No at Reactome'])]
    df_familyX_NotAtReactome = df_familyX[df_familyX["ReactomeID"].isin(['No at Reactome'])]
    
    #proteins with just one GO annotated
    df_familyX_oneGOstatus = df_familyX.loc[df_familyX["n_GOall"].isin([1])]
    df_familyX_noOneGOstatus = df_familyX[~df_familyX["n_GOall"].isin(df_familyX_oneGOstatus['n_GOall'])]
    #print(df_familyX["list_GOAll"].tolist()) #df[1].fillna(0, inplace=True) ## df_UniProt['ProteinFamily'] = df_UniProt.ProteinFamily.replace(np.NaN, 'No Family assigned')
            
    s_goID = list(set(itertools.chain.from_iterable(df_familyX["list_GOAll"].tolist())))
    s_goIDBP = list(set(itertools.chain.from_iterable(df_familyX["list_GOBP"].tolist())))
    s_goIDCC = list(set(itertools.chain.from_iterable(df_familyX["list_GOCC"].tolist())))
    s_goIDMF = list(set(itertools.chain.from_iterable(df_familyX["list_GOMF"].tolist())))

    #proteins only withKegg Pathways
    df_familyX_withKeggPathways = df_familyX[df_familyX["WithKeggPathway"].isin(['yes'])]
    df_familyX_noKeggPathways = df_familyX[~df_familyX["WithKeggPathway"].isin(['yes'])]

    #1st CONDITIONAL 
    if ((len(df_familyX_atReactome) > 0) and (len(df_familyX_NotAtReactome) >0)):

      listReactomeStatus.append("Some")

    elif ((len(df_familyX_atReactome) == 0) and (len(df_familyX_NotAtReactome) >0)) :

      listReactomeStatus.append("None")

    elif ((len(df_familyX_atReactome) > 0) and (len(df_familyX_NotAtReactome) ==0)) :

      listReactomeStatus.append("All")

    else:

      break

    #2nd CONDITIONAL 
    if ((len(df_familyX_withKeggPathways) > 0) and (len(df_familyX_noKeggPathways) >0)) :

      listKeggStatus.append("Some")

    elif ((len(df_familyX_withKeggPathways) == 0) and (len(df_familyX_noKeggPathways) >0)) :

      listKeggStatus.append("None")

    elif ((len(df_familyX_withKeggPathways) > 0) and (len(df_familyX_noKeggPathways) ==0)) :

      listKeggStatus.append("All")

    else:

      break

    #3rd CONDITIONAL
    if ((len(df_familyX_oneGOstatus) > 0) and (len(df_familyX_noOneGOstatus) > 0)):

      listProteinsOneGOStatus.append("All")
      listProteinsOneGO.append(str(df_familyX_oneGOstatus['DB_Object_ID'].tolist()))
      list_nProteinsOneGO.append(len(df_familyX_oneGOstatus['DB_Object_ID'].tolist()))

    elif ((len(df_familyX_oneGOstatus) == 0) and (len(df_familyX_noOneGOstatus) > 0)):

      listProteinsOneGOStatus.append("None")
      listProteinsOneGO.append("-")
      list_nProteinsOneGO.append(0)

    elif ((len(df_familyX_oneGOstatus) > 0) and (len(df_familyX_noOneGOstatus) == 0)):

      listProteinsOneGOStatus.append("Some")
      listProteinsOneGO.append(str(df_familyX_oneGOstatus['DB_Object_ID'].tolist()))
      list_nProteinsOneGO.append(len(df_familyX_oneGOstatus['DB_Object_ID'].tolist()))

    else:

      break

    list_nProteinsFamily.append(len(df_familyX['DB_Object_ID']))
    list_nProteinsFamilyAtReactom.append(len(df_familyX_atReactome['DB_Object_ID']))
    list_nProteinsFamilyNoAtReactome.append(len(df_familyX_NotAtReactome['DB_Object_ID']))

    list_nProteinsFamilyAtKegg.append(len(df_familyX_withKeggPathways['DB_Object_ID']))
    list_nProteinsFamilyNoAtKegg.append(len(df_familyX_noKeggPathways['DB_Object_ID']))
    
    list_nGOperFamily.append(len(s_goID))
    list_nGOBPperFamily.append(len(s_goIDBP))
    list_nGOCCperFamily.append(len(s_goIDCC))
    list_nGOMFperFamily.append(len(s_goIDMF))

    list_GOperFamily.append(str(list(set(s_goID))))
    list_GOBPperFamily.append(str(list(set(s_goIDBP))))
    list_GOCCperFamily.append(str(list(set(s_goIDCC))))
    list_GOMFperFamily.append(str(list(set(s_goIDMF))))

  finalDf_h = pd.DataFrame(proteinFamilies, columns = ['ProteinFamily'])
  finalDf_h['atReactome'] = listReactomeStatus
  finalDf_h['atKegg'] = listKeggStatus  
  finalDf_h['oneGOIDperProtein'] = listProteinsOneGOStatus
  finalDf_h['n_proteinsPerFamily'] = list_nProteinsFamily
  finalDf_h['n_proteinsPerFamily_atReactome'] = list_nProteinsFamilyAtReactom
  finalDf_h['n_proteinsPerFamily_noReactome'] = list_nProteinsFamilyNoAtReactome
  finalDf_h['n_proteinsPerFamily_atKegg'] = list_nProteinsFamilyAtKegg
  finalDf_h['n_proteinsPerFamily_noKegg'] = list_nProteinsFamilyNoAtKegg  
  finalDf_h['n_GOIDperFamily'] = list_nGOperFamily
  finalDf_h['n_GOBPperFamily'] = list_nGOBPperFamily
  finalDf_h['n_GOCCperFamily'] = list_nGOCCperFamily
  finalDf_h['n_GOMFperFamily'] = list_nGOMFperFamily
  finalDf_h['n_proteinsWithOneGOId'] = list_nProteinsOneGO 
  finalDf_h['proteinsWithOneGOId'] = listProteinsOneGO #list_nProteinsOneGO
  finalDf_h['GOIDperfamily'] = list_GOperFamily
  finalDf_h['GOBPperfamily'] = list_GOBPperFamily
  finalDf_h['GOCCperfamily'] = list_GOCCperFamily
  finalDf_h['GOMFperfamily'] = list_GOMFperFamily

  if writeT == True:

    folderPath = os.getcwd()
    pathToWrite4 = folderPath+"output_a3_family_GO_reactome_nprotCount.csv"

    finalDf_h.to_csv(folderPath, index = False)
    print("Table write at "+pathToWrite4)
    print ("\nSuccesfully finished at  "+time.strftime("%H:%M:%S")+ " !")


  return(finalDf_h)

def showBarPlot(table1, filterN = 50, writeTable = 'no'):

  print ("\nBarplot from Families Table output of analysis 3 "+time.strftime("%H:%M:%S")+"\n")

  #Q1: barplot of all the family of proteins with proteins with at least one GO
  table1go = table1[~table1['n_proteinsWithOneGOId'].isin([0])]
  table1_groupedBy = table1go.sort_values(['n_proteinsWithOneGOId'], ascending = [False])

  height50 = (table1_groupedBy['n_proteinsWithOneGOId'].tolist())[0:filterN] #n_proteinsPerFamily
  
  bars50_unmodified = (table1_groupedBy['ProteinFamily'].tolist())[0:filterN] #ProteinFamily
  bars50 = []

  for i in bars50_unmodified:

    newString = i.replace('family', '')
    newString2 = newString.replace(',', '\n')
    bars50.append(newString2)

  y_pos = np.arange(len(bars50))

  # Create bars
  plt.bar(y_pos, height50)
  plt.title('Top 50 families with some proteins with just one GO')

  # Create names on the x-axis
  plt.xticks(y_pos, bars50, rotation=90, size = 9)

  # Create labels
  position = range(1,len(bars50))

  # Text on the top of each barplot
  for i in range(len(position)):

    plt.text(x = position[i]-0.5 , y = height50[i], s = height50[i], size = 5)

  plt.show()



###### FUNCTIONS ANALYSIS 2 : GO ontologies, GO annotations and GO Ids annotated at Reactome coverage.

def vennCoverage_3d (table1, table2, table3, vs1="A", vs2="B", vs3="C"):

  go_Term = (str(vs1)+" vs "+str(vs2)+" vs "+str(vs3))

  s1 = table1['DB_Object_ID'].unique()
  s2 = table2['DB_Object_ID'].unique()
  s3 = table3['DB_Object_ID'].unique()

  out = venn3([set(s1),set(s2),set(s3)])#venn3(subsets = sets, set_labels = ('GOC experimental', 'Reactome', 'GOC no experimental'), alpha =1)

  if out.get_patch_by_id('100'):
    out.get_patch_by_id('100').set_color('lightskyblue')
  if out.get_patch_by_id('010'):    
    out.get_patch_by_id('010').set_color('blue')  
  if out.get_patch_by_id('001'):
    out.get_patch_by_id('001').set_color('cyan')  

  blue_patch = mpatches.Patch(color='lightskyblue', label=(vs1)) # ('+str(sets[0])+')'))
  lblue_patch = mpatches.Patch(color='blue', label=(vs2)) # ('+str(sets[1])+')'))
  cyan_patch = mpatches.Patch(color='cyan', label=(vs3)) #sss ('+str(sets[2])+')'))

  for text in out.set_labels:
      text.set_fontsize(0)

  plt.legend(handles=[blue_patch, lblue_patch, cyan_patch]) 

  plt.title(go_Term)
  plt.show()

  #np.setdiff1d(a, b)
  #np.intersect1d([1, 3, 4, 3], [3, 1, 2, 1])
  #numpy.concatenate((a1, a2, ...), axis=0)
  only_a = np.setdiff1d(s1,np.concatenate((s2,s3), axis = 0))
  only_b = np.setdiff1d(s2,np.concatenate((s1,s3), axis = 0))
  only_c = np.setdiff1d(s3,np.concatenate((s1,s2), axis = 0)) 
  ab = np.setdiff1d(np.intersect1d(s1,s2),s3)
  ac = np.setdiff1d(np.intersect1d(s1,s3),s2)
  bc = np.setdiff1d(np.intersect1d(s2,s3),s1)
  abc = np.intersect1d(s1,np.intersect1d(s2,s3))

  listVennSets= [only_a,only_b,only_c, ab, ac, bc, abc]

  return(listVennSets)

def vennDiagramGOReactomeCoverageAll_2d (tableGOC, tableReactome, vs1 = 'A', vs2 = 'B'):

  go_Term = (str(vs1)+" vs "+str(vs2))

  s1=tableGOC['ProteinFamily'].unique()
  s2=tableReactome['ProteinFamily'].unique()

  out = venn2([set(s1),set(s2)]) 
  
  if out.get_patch_by_id('10'):
    out.get_patch_by_id('10').set_color('lightskyblue') 
  if out.get_patch_by_id('01'):
    out.get_patch_by_id('01').set_color('blue') 
  if out.get_patch_by_id('11'):
    out.get_patch_by_id('11').set_color('cyan')

  for text in out.set_labels:
      text.set_fontsize(0)

  #create legend from handles and labels: 

  blue_patch = mpatches.Patch(color='lightskyblue', label=(vs1))# ('+str(sets[0])+')'))
  lblue_patch = mpatches.Patch(color='blue', label=(vs2))# ('+str(sets[1])+')'))
  cyan_patch = mpatches.Patch(color='cyan', label=(str(vs1)+' & '+str(vs2)))#sss ('+str(sets[2])+')'))

  plt.legend(handles=[blue_patch, lblue_patch, cyan_patch])

  plt.title(go_Term)
  plt.show()

  #np.setdiff1d(a, b)
  #np.intersect1d([1, 3, 4, 3], [3, 1, 2, 1])
  #numpy.concatenate((a1, a2, ...), axis=0)
  only_a = np.setdiff1d(s1, s2)
  only_b = np.setdiff1d(s2, s1)
  ab = np.intersect1d(s1, s2)

  dfIntersec = [only_a, only_b, ab]

  return(dfIntersec)

def countGO (serieGO):

  listGO = []
  listOflist = serieGO.get_values()
  #print(listOflist[0])

  for i in listOflist:
    try:
      nGOs = len(i)
    except:
      ##print("no GO:  "+str(i))
      nGOs = 0
    listGO.append(nGOs)
  #print(listGO[0])
  #print("done!")

  return(listGO)

def getSerieGOs (tableFam):

  s_BP = tableFam.GO_BP.str.findall(r'\[GO:([0-9]+)\]')
  s_CC = tableFam.GO_CC.str.findall(r'\[GO:([0-9]+)\]')
  s_MF = tableFam.GO_MF.str.findall(r'\[GO:([0-9]+)\]')
  s_allgo = tableFam.GO_ID.str.findall(r'GO:([0-9]+)')
  listSeries = [s_BP, s_CC, s_MF, s_allgo]

  return(listSeries)

def addCountsToTable (tableFam, s_BPr, s_CCo, s_MFu, s_allg):

  tableFam['numberGO_BP_ID'] = pd.Series(countGO(s_BPr),index=tableFam.index)
  tableFam['numberGO_CC_ID'] = pd.Series(countGO(s_CCo),index=tableFam.index)
  tableFam['numberGO_MF_ID'] = pd.Series(countGO(s_MFu),index=tableFam.index)
  tableFam['total_GO_ID'] = pd.Series(countGO(s_allg),index=tableFam.index)

  tableFamSorted = tableFam.sort_values(by = ['total_GO_ID'], ascending = False)


  return(tableFamSorted)

def getProtFamTable (tableToCount):
  #col1
  listLabelsFamilyBarPlot = tableToCount['ProteinFamily'].unique()

  listGoBPFamiliesBarPlot = []
  listGoCCFamiliesBarPlot = []
  listGoMFFamiliesBarPlot = []
  listAllGoFamiliesBarPlot = []

  numberProtPerFamily = []
  listNormGoBPFamiliesBarPlot = []
  listNormGoCCFamiliesBarPlot = []
  listNormGoMFFamiliesBarPlot = []  
  listNormAllGoFamiliesBarPlot = []


  for i in listLabelsFamilyBarPlot:

    df_family_i = tableToCount[tableToCount['ProteinFamily'].isin([i])]
    nProt = len(df_family_i['ProteinFamily'])
    #col2,3,4,5

    sumBP = df_family_i['numberGO_BP_ID'].sum()
    sumCC = df_family_i['numberGO_CC_ID'].sum()
    sumMF = df_family_i['numberGO_MF_ID'].sum()
    sumAll = df_family_i['total_GO_ID'].sum()

    normalizedValue_BP = round(float(sumBP)/float(nProt),1)
    normalizedValue_CC = round(float(sumCC)/float(nProt),1)
    normalizedValue_MF = round(float(sumMF)/float(nProt),1)
    normalizedValue_all = round(float(sumAll)/float(nProt),1)

    listGoBPFamiliesBarPlot.append(int(sumBP))
    listGoCCFamiliesBarPlot.append(int(sumCC))
    listGoMFFamiliesBarPlot .append(int(sumMF))
    listAllGoFamiliesBarPlot.append(int(sumAll))
    numberProtPerFamily.append(nProt)
    listNormGoBPFamiliesBarPlot.append(normalizedValue_BP)
    listNormGoCCFamiliesBarPlot.append(normalizedValue_CC)
    listNormGoMFFamiliesBarPlot.append(normalizedValue_MF)
    listNormAllGoFamiliesBarPlot.append(normalizedValue_all)


  dfFamilies = pd.DataFrame(listLabelsFamilyBarPlot, columns=['ProteinFamily'])

  dfFamilies['sumGO_BP_ID'] = listGoBPFamiliesBarPlot
  dfFamilies['sumGO_CC_ID'] = listGoCCFamiliesBarPlot
  dfFamilies['sumGO_MF_ID'] = listGoMFFamiliesBarPlot
  dfFamilies['sumAllGO_ID'] = listAllGoFamiliesBarPlot
  dfFamilies['numberProtPerFamily'] = numberProtPerFamily
  dfFamilies['normGOBP_ID'] = listNormGoBPFamiliesBarPlot
  dfFamilies['normGOCC_ID'] = listNormGoCCFamiliesBarPlot
  dfFamilies['normGOMF_ID'] = listNormGoMFFamiliesBarPlot
  dfFamilies['normAllGO_ID'] = listNormAllGoFamiliesBarPlot

  return (dfFamilies)

def get_elemTuples (tableCounts, normaliz):

  labelsCounts = []
  listGoFamiliesBarPlot = []

  if normaliz == "no":

    dfFamilies_sorted = tableCounts.sort_values(by = ['sumAllGO_ID'], ascending = False).reset_index(drop=True)
    ##print(dfFamilies_sorted['sumAllGO_ID'][0:5])

    for j in range(0,len(dfFamilies_sorted['ProteinFamily'])):

      listGoFamiliesBarPlot.append((dfFamilies_sorted['sumGO_BP_ID'][j], dfFamilies_sorted['sumGO_CC_ID'][j] ,dfFamilies_sorted['sumGO_MF_ID'][j]))

    labelsCounts = [dfFamilies_sorted['ProteinFamily'], listGoFamiliesBarPlot, dfFamilies_sorted['sumAllGO_ID']]

  elif normaliz == "yes":

    dfFamilies_sorted = tableCounts.sort_values(by = ['normAllGO_ID'], ascending = False).reset_index(drop=True)
    ##print(dfFamilies_sorted['sumAllGO_ID'][0:5])

    for j in range(0,len(dfFamilies_sorted['ProteinFamily'])):

      listGoFamiliesBarPlot.append((dfFamilies_sorted['normGOBP_ID'][j], dfFamilies_sorted['normGOCC_ID'][j] ,dfFamilies_sorted['normGOMF_ID'][j]))

    labelsCounts = [dfFamilies_sorted['ProteinFamily'], listGoFamiliesBarPlot, dfFamilies_sorted['normAllGO_ID']]

  elif normaliz == "no-special":
    #df.sort(['c1','c2'], ascending=[False,True])
    #dfFamilies_sorted = tableCounts.sort_values(by = ['n_protAtReactome']).reset_index(drop=True)
    dfFamilies_sorted = tableCounts.sort(['n_protAtReactome','sumAllGO_ID'], ascending=[True, False]).reset_index(drop=True)
    ##print(dfFamilies_sorted['sumAllGO_ID'][0:5])

    for j in range(0,len(dfFamilies_sorted['ProteinFamily'])):

      listGoFamiliesBarPlot.append((dfFamilies_sorted['sumGO_BP_ID'][j], dfFamilies_sorted['sumGO_CC_ID'][j] ,dfFamilies_sorted['sumGO_MF_ID'][j]))

    labelsCounts = [dfFamilies_sorted['ProteinFamily'], listGoFamiliesBarPlot, dfFamilies_sorted['n_protAtReactome']]

  return(labelsCounts)

def chooseBarplotReactomeGO (tableCountsTo, filter = 25, normalized = "no"):

  listBarPlot = get_elemTuples(tableCountsTo, normaliz = normalized)
  #listBarPlot_1[0],listBarPlot_1[1], listBarPlot_1[2]
  #print("!!!!!!")
  #print(len(listBarPlot))
  labels_all = listBarPlot[0] #legend
  elements_all = listBarPlot[1]
  tot_all = listBarPlot[2]
  
  #FILTERING TO PLOT SOME
  elements = elements_all[0:filter] #limit25
  ##print("========****")
  ##print(elements[0:10])
  label_full_0 = labels_all[0:filter] #limit25
  label_full =  [a.replace("family", "") for a in label_full_0] #limit25
  labels =[b.replace(" ", "\n") for b in label_full]  

  tot_filter = tot_all[0:filter]

  ##print(tot[0:10])
  df2 = pd.DataFrame.from_records(elements, columns=["GO Ids (BP)","GO Ids (CC)","GO Ids (MF)"]) #x axis, y axis colors
  

  #plt.xticks(ind, ('BBE', 'CandidateSet', 'Complex', 'DefinedSet', 'Depolymeristio', 'EWAS','FailedReaction','GenomeEncodedEntity','OpenSet','Pathway','Polymer','Polymerisation','Reaction', 'TopLevelPathway'), rotation =90)

  ax =df2.plot(kind='bar', stacked=True)  #df2!
  ax.set_xticklabels(labels,fontsize=6)

  if normalized == "no":
    ax.set_title('Number of GO IDs \n  per Protein Families')
  elif normalized == "yes":
    ax.set_title('Normalized number of GO IDs \n  per Protein Families')


  #for p in ax.patches:
  # ax.annotate(str(p.get_height()), (p.get_x() * 1.005, p.get_height() * 1.005))
  #sumList = []
  #counter = 0

  #list number of GO per bar.

  listNgo = tot_filter
  counter = 0

  if normalized != "no-special":

    for p in ax.patches:

      if counter < len(listNgo): #list!

        #print("Axis=========")
        #print(p.get_x())
        #print(listNgo[counter]) 
        #print("=============")
        ax.annotate(listNgo[counter], 
          (p.get_x(),
          listNgo[counter]+(listNgo[counter]*0.05)), #put the number
          ha='left', 
          va='top').set_fontsize(8)#,
          #xytext=(0, 100),
          #textcoords='offset points').set_fontsize(10)

        counter = counter+1

  #plt.xticks(rotation=45)
  plt.show()
  #print("going...")

def getProtFamInOutReactomeTable (tableToCount2):
  #col1
  listLabelsFamilyBarPlot = tableToCount2['ProteinFamily'].unique()

  listGoBPFamiliesBarPlot = []
  listGoCCFamiliesBarPlot = []
  listGoMFFamiliesBarPlot = []
  listAllGoFamiliesBarPlot = []

  numberProtPerFamily = []
  numberProtPerFamily_atR = []
  numberProtPerFamily_noR = []

  for i in listLabelsFamilyBarPlot:

    df_family_i = tableToCount2[tableToCount2['ProteinFamily'].isin([i])]
    df_R = df_family_i[~df_family_i['ReactomeID'].isnull()]
    df_nR = df_family_i[df_family_i['ReactomeID'].isnull()]

    nProt = len(df_family_i['ProteinFamily'])
    nProt_R = len(df_R['ReactomeID'])
    nProt_noR = len(df_nR['ReactomeID'])
    #col2,3,4,5

    sumBP = df_family_i['numberGO_BP_ID'].sum()
    sumCC = df_family_i['numberGO_CC_ID'].sum()
    sumMF = df_family_i['numberGO_MF_ID'].sum()
    sumAll = df_family_i['total_GO_ID'].sum()

    listGoBPFamiliesBarPlot.append(int(sumBP))
    listGoCCFamiliesBarPlot.append(int(sumCC))
    listGoMFFamiliesBarPlot .append(int(sumMF))
    listAllGoFamiliesBarPlot.append(int(sumAll))
    numberProtPerFamily.append(nProt)
    numberProtPerFamily_atR.append(nProt_R)
    numberProtPerFamily_noR.append(nProt_noR)

  dfFamilies = pd.DataFrame(listLabelsFamilyBarPlot, columns=['ProteinFamily'])

  dfFamilies['sumGO_BP_ID'] = listGoBPFamiliesBarPlot
  dfFamilies['sumGO_CC_ID'] = listGoCCFamiliesBarPlot
  dfFamilies['sumGO_MF_ID'] = listGoMFFamiliesBarPlot
  dfFamilies['sumAllGO_ID'] = listAllGoFamiliesBarPlot
  dfFamilies['numberProtPerFamily'] = numberProtPerFamily
  dfFamilies['n_protAtReactome'] = numberProtPerFamily_atR
  dfFamilies['n_protNoReactome'] = numberProtPerFamily_noR

  return (dfFamilies)



#______________________________________________________________________________________________________


####FUNCTIONS ANALYSIS 1 : 
#Get Reactome uniprot ID from human at from reactome graphd DB available
def neo4JCypher (usernm = None, passwd = None, writeTable= True, defaulTable = True):

  if defaulTable == False:

    driver = GraphDatabase.driver("bolt://localhost:7687", auth = basic_auth(str(usernm), str(passwd)))
    session = driver.session()
    print ("\nStarting Neo4J session "+time.strftime("%H:%M:%S")+"\n")

    #1.-Sending query CYPHER
    result = session.run("""MATCH (p:Pathway {speciesName:{speciesName}})-[:hasEvent*]->(rle:ReactionLikeEvent),
          (rle)-[:input|output|catalystActivity|physicalEntity|regulatedBy|regulator|hasComponent|hasMember|hasCandidate|repeatedUnit*]->(pe:PhysicalEntity),
          (pe)-[:referenceEntity]->(re:ReferenceEntity)-[:referenceDatabase]->(rd:ReferenceDatabase)
    RETURN DISTINCT re.identifier AS Identifier, rd.displayName AS Database, rle.stId AS ReactionID""", {"speciesName":"Homo sapiens"})

    #2.-Receiving answer in a new file:
    df_proteinUniProtPerReaction_raw = pd.DataFrame([dict(record) for record in result])
    df_proteinUniProtPerReaction = df_proteinUniProtPerReaction_raw.rename(columns={"re.identifier":"Identifier", "rd.displayName":"Database", "rle.stId":"ReactionID"})
    print ("\nEnding Neo4J session "+time.strftime("%H:%M:%S")+"\n")
    session.close()

  elif defaulTable == True:

    print ("\nLoading Neo4J table from Reactome Graph Database v62 "+time.strftime("%H:%M:%S")+"\n")
    df_proteinUniProtPerReaction = pd.read_csv("https://raw.githubusercontent.com/corinabioinformatic/Neo4J_at_Reactome/Analysis_1/output_a1_table_outputCypher_UnipStatusOrganism(10850).tab", sep='\t')

  if writeTable == True:

    folderPath = os.getcwd()
    pathToWrite = (folderPath+"\\output_a1_pythonCypher_proteinID.csv") 
    df_proteinUniProtPerReaction.to_csv(pathToWrite, index = False) # path and file where you are going to save your results
    print("File available at "+ pathToWrite)

  return(df_proteinUniProtPerReaction)

#compare resources Reactome and UniProt
def compareSources(tableReactome, tableUniProtAllh, drawVenn = True):

  print ("\nComparing sources at  "+time.strftime("%H:%M:%S")+"\n")

  df_cypher_uniprotHomoStatusReactions = tableReactome[tableReactome['Organism'] == 'Homo sapiens (Human)']

  #print(df_cypher_uniprotHomoStatusReactions.iloc[0])
  #print(len(df_cypher_uniprotHomoStatusReactions['Entry']))
  set_cypher_uniprotHomoStatusReactions = df_cypher_uniprotHomoStatusReactions['Entry']


  df_uniprotSearchEngine_allHuman = tableUniProtAllh
  df_uniprotSearchEngine_reviewedHuman = df_uniprotSearchEngine_allHuman[df_uniprotSearchEngine_allHuman['Status']=='reviewed']

  #print(df_uniprotSearchEngine_reviewedHuman.iloc[0])
  #print(len(df_uniprotSearchEngine_reviewedHuman['Entry']))
  set_entryUniprotSearchEngine_reviewedHuman = df_uniprotSearchEngine_reviewedHuman['Entry']

  #print(df_uniprotSearchEngine_reviewedHuman['Cross-reference (Reactome)'].unique())
  df_uniprotSearchEngine_reviewedHumanNoReactomeTag = df_uniprotSearchEngine_reviewedHuman[df_uniprotSearchEngine_reviewedHuman['Cross-reference (Reactome)'].isnull()]
  df_uniprotSearchEngine_reviewedHumanReactomeTag = df_uniprotSearchEngine_reviewedHuman[~df_uniprotSearchEngine_reviewedHuman['Cross-reference (Reactome)'].isnull()]

  set_entryUniprotSearchEngine_reviewedHumanNoReactomeTag = df_uniprotSearchEngine_reviewedHumanNoReactomeTag['Entry']

  #print(len(set_entryUniprotSearchEngine_reviewedHumanNoReactomeTag))
  #print(len(df_uniprotSearchEngine_reviewedHumanReactomeTag['Entry']))
  listVenn = [list(set(set_cypher_uniprotHomoStatusReactions)), list(set(set_entryUniprotSearchEngine_reviewedHuman)), list(set(set_entryUniprotSearchEngine_reviewedHumanNoReactomeTag))]

  if drawVenn == True :

    print (len(set_cypher_uniprotHomoStatusReactions))
    print (len(set_entryUniprotSearchEngine_reviewedHuman))
    print (len(set_entryUniprotSearchEngine_reviewedHumanNoReactomeTag))
    print (set_cypher_uniprotHomoStatusReactions[0])
    print (set_entryUniprotSearchEngine_reviewedHuman[0])
    print (set_entryUniprotSearchEngine_reviewedHumanNoReactomeTag[0])


    out = venn3(subsets = [set(set_cypher_uniprotHomoStatusReactions), set(set_entryUniprotSearchEngine_reviewedHuman), set(set_entryUniprotSearchEngine_reviewedHumanNoReactomeTag)], set_labels = ('Reactome', 'UniProt/\nSwissProt', 'Cross-reference\nReactome-UniProt'))

    out.get_patch_by_id('100').set_color('cyan')  
    out.get_patch_by_id('010').set_color('blue')     
    out.get_patch_by_id('011').set_color('grey')      

    plt.title("Annotated proteins at Reactome and UniProt databases")

    plt.show()
  print("List of proteins annotated or no in different sources. Ready.")

  return(listVenn)
