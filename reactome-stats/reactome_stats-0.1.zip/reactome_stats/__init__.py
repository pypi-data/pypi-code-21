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

#'get_ancestors': retrieve lst of ancestor from a list of childs, by mean of OLS Rest API
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
def get_worktable(dfGOC, dfUniprot, df_KeggGP_0, writeTable = 'yes'):

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
  return(df_proteinsGOCAnnotation_nu_fam_kegg_reactome)

#'get_clusteredFamily_counts' Retrive a data with counts based on protein family and the table retrieved with the getWorkTable function
def get_clusteredFamily_counts(df_fam_kegg_reactome):

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

  folderPath = os.getcwd()
  pathToWrite4 = folderPath+"output_a3_family_GO_reactome_nprotCount.csv"

  finalDf_h.to_csv(folderPath, index = False)
  print("Table write at "+pathToWrite4)
  print ("\nSuccesfully finished at  "+time.strftime("%H:%M:%S")+ " !")


  return(finalDf_h)

