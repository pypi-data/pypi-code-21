#!usr/bin/python

# Copyright 2016, Rohan Dandage <rraadd_8@hotmail.com,rohan@igib.in>
# This program is distributed under General Public License v. 3.  

"""
================================
``get_protein_features``
================================
"""
from os.path import exists,abspath,dirname,basename,splitext
from os import makedirs,stat
from Bio.PDB import DSSP,PDBParser
# from Bio.PDB.Polypeptide import PPBuilder
import subprocess
# import re
# import pysam

# import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

from Bio import SeqIO,Seq,SeqRecord
# from Bio.Alphabet import IUPAC
# import subprocess

import warnings
warnings.simplefilter(action = "ignore") # , category = PDBConstructionWarning
import logging
logging.basicConfig(format='[%(asctime)s] %(levelname)s\tfrom %(filename)s in %(funcName)s(..): %(message)s',level=logging.DEBUG) # filename=cfg_xls_fh+'.log'
from dms2dfe.lib.global_vars import aas_21,aas_21_3letter,secstruc_lbls
from dms2dfe.lib.io_dfs import set_index
from dms2dfe.lib.io_mut_files import makemutids_fromprtseq
from dms2dfe.lib.io_seq_files import cctmr_fasta2ref_fasta

def getdssp_data(pdb_fh,dssp_fh):
    """
    This uses DSSP to get structural information.

    :param pdb_fh: path to .pdb file
    :param dssp_fh: path to DSSP source.
    """
    dssp_data_fh="%s/../tmp/dssp"% (abspath(dirname(__file__)))
    dssp_com="%s -i %s -o %s" % (dssp_fh,pdb_fh,dssp_data_fh)
    log_fh="%s.log" % dssp_fh
    log_f = open(log_fh,'a')
    subprocess.call(dssp_com,shell=True,stdout=log_f, stderr=subprocess.STDOUT)
    log_f.close()
    start=False
    dssp_f=open(dssp_data_fh, 'r')
    dssp_fwf_f=open(dssp_data_fh+'.fwf', 'w')
    for line in dssp_f:
        if "#" in line:
            start=True
        if start is True:
            dssp_fwf_f.write(line)
    dssp_f.close()
    dssp_fwf_f.close()

    dssp_data=pd.read_fwf(dssp_data_fh+'.fwf',widths=[5,5,2,2,3,4,1,1,2,4,4,1,4,7,1,4,6,1,4,6,1,4,6,1,4,2,6,6,6,6,6,7,7,7])

    dssp_data.columns=["junk","aasi","chain","ref_dssp","Secondary structure","Helix formation in helix types 3 4 and 5","bend","Chirality",\
                       "beta bridge labels","First residue of beta bridge","Second residue of beta bridge","Sheet of beta bridge",\
                       "Solvent Accessible Surface Area",\
                      "Offset from residue to the partner in N-H-->O H-bond (1)","junk","Energy (kcal/mol) of N-H-->O H-bond (1)",\
                      "Offset from residue to the partner in O-->H-N H-bond (1)","junk","Energy (kcal/mol) of O-->H-N H-bond (1)",\
                      "Offset from residue to the partner in N-H-->O H-bond (2)","junk","Energy (kcal/mol) of N-H-->O H-bond (2)",\
                      "Offset from residue to the partner in O-->H-N H-bond (2)","junk","Energy (kcal/mol) of O-->H-N H-bond (2)",\
                       "junk","cosine of the angle between C=O of residue and C=O of previous residue",\
                      "kappa bond/bend angle","alpha torsion/dihedral angle",\
                       "phi torsion angle","psi torsion angle",\
                      "X coordinates of CA atom","Y coordinates of CA atom","Z coordinates of CA atom"]

    dssp_data=dssp_data.loc[dssp_data.loc[:,"chain"]=='A',:] # only chain A
    del dssp_data["junk"]
    del dssp_data["chain"]
    del dssp_data["ref_dssp"]
    dssp_data=dssp_data.set_index("aasi")
    return dssp_data

def pdb2dfromactivesite(pdb_fh,active_sites=[]):
    """
    This calculates distances between each ligand atom or optionally provided amino acids (sources) and each residue in the protein.
    
    :param pdb_fh: path to .pdb file.
    :param active_sites: optional list of residue numbers as sources. 
    """
    junk_residues = ["HOH"," MG","CA"," NA","SO4","IOD","NA","CL","GOL","PO4"]
    pdb_parser=PDBParser()
    pdb_data=pdb_parser.get_structure("pdb_name",pdb_fh)
    model = pdb_data[0]
    chainA = model["A"] #only a chain
    residues   = list(chainA.get_residues())
    ligands_residue_objs=[]
    for residue in chainA:
        if not residue.get_resname() in junk_residues:
            if not residue.get_resname() in aas_21_3letter: #only aas 
                ligands_residue_objs.append(residue)
            elif residue.id[1] in active_sites:
                ligands_residue_objs.append(residue)
            
    dfromligands=pd.DataFrame()
    for ligandi in range(len(ligands_residue_objs)):
        ligand_residue_obj=ligands_residue_objs[ligandi]
        for ligand_atom_obj in ligand_residue_obj:
            for residue in chainA:
                if residue.get_resname() in aas_21_3letter: #only aas 
                    dfromligands.loc[residue.id[1],"ref_pdb"]=residue.get_resname()
                    if not ligand_residue_obj.get_resname() in aas_21_3letter:
                        dfromligands.loc[residue.id[1],"Distance from Ligand: %s (ATOM: %s)" % \
                                         (ligand_residue_obj.get_resname(),ligand_atom_obj.get_name())]\
                        =ligand_residue_obj[ligand_atom_obj.get_name()]-residue["CA"]
                    else:
                        dfromligands.loc[residue.id[1],"Distance from active site residue: %s %d (ATOM: %s)" % \
                                         (ligand_residue_obj.get_resname(),ligand_residue_obj.get_id()[1],\
                                          ligand_atom_obj.get_name())]\
                        =ligand_residue_obj[ligand_atom_obj.get_name()]-residue["CA"]

    dfromligands.index.name="aasi"
    if "ref_pdb" in dfromligands:
        del dfromligands["ref_pdb"]
    #average and minimum distances
    cols_all=dfromligands.columns.tolist()
    for moltype in ['Distance from Ligand:','Distance from active site residue:']:
        cols_moltype=[c for c in cols_all if moltype in c]
        if len(cols_all)>0:
            dfromligands.loc[:,'%s average' % moltype]=dfromligands.loc[:,cols_moltype].T.mean()
            dfromligands.loc[:,'%s minimum' % moltype]=dfromligands.loc[:,cols_moltype].T.min()
            mols=np.unique([c[c.find(moltype):c.find(' (ATOM')] for c in cols_moltype])
            if len(mols)>1:
                for mol in mols:
                    cols_mol=[c for c in cols_moltype if mol in c]
                    dfromligands.loc[:,'%s: average' % mol]=dfromligands.loc[:,cols_mol].T.mean()
                    dfromligands.loc[:,'%s: minimum' % mol]=dfromligands.loc[:,cols_mol].T.min()    

    return dfromligands



def get_consrv_score(fsta_fh,host,clustalo_fh,rate4site_fh):
    from Bio.Blast import NCBIWWW
    from Bio.Blast import NCBIXML
    from skbio import TabularMSA, Protein
    from Bio.Alphabet import IUPAC
    from dms2dfe.lib.io_seq_files import fasta_nts2prt
    blast_method='blastp'
    blast_db="swissprot"
    
    # make prt fasta
    fsta_prt_fh="%s_prt%s" % (splitext(fsta_fh)[0],splitext(fsta_fh)[1])
    if not exists(fsta_prt_fh):
        prt_seq=fasta_nts2prt(fsta_fh,host=host)

    for fsta_data in SeqIO.parse(fsta_prt_fh,'fasta'):
        ref_id=fsta_data.id
        prt_seq=str(fsta_data.seq)
        break

    blast_fh="%s_blastp.xml" % (splitext(fsta_fh)[0])
    blast_fasta_fh="%s.fasta" % (splitext(blast_fh)[0])
    msa_fh=blast_fasta_fh.replace("blastp","blastp_msa")
    if not exists(msa_fh):
        if not exists(blast_fasta_fh):
            if not exists(blast_fh):
                # get blast
                blast_handle = NCBIWWW.qblast(blast_method, 
                               blast_db, sequence=prt_seq)
                blast_results = blast_handle.read()
                blast_f=open(blast_fh, 'w')
                blast_f.write(blast_results)
                blast_f.close()
            blast_f = open(blast_fh, 'r')
            blast_records=NCBIXML.parse(blast_f)

            # blast to fasta
            blast_fasta_f=open(blast_fasta_fh, 'w')
            fsta_data=[]
            fsta_data.append(SeqRecord.SeqRecord(Seq.Seq(prt_seq,IUPAC.protein),
                                 id = ref_id,description=''))
            for rec in blast_records:
                for aln in rec.alignments:
                    for hsp in aln.hsps:
                        fsta_data.append(SeqRecord.SeqRecord(Seq.Seq(hsp.sbjct,IUPAC.protein),
                                 id = aln.hit_id,description=''))
            SeqIO.write(fsta_data, blast_fasta_f, "fasta")
            blast_fasta_f.close()
    # blast fasta to msa : clustaw
        clustalo_com="%s -i %s -o %s --outfmt=fasta --log=%s.log" % (clustalo_fh,blast_fasta_fh,msa_fh,msa_fh)
        log_fh="%s.log" % clustalo_fh
        log_f = open(log_fh,'a')
        subprocess.call(clustalo_com,shell=True,stdout=log_f, stderr=subprocess.STDOUT)
        log_f.close()
    # msa to consrv skbio==0.4.1
    msa = TabularMSA.read(msa_fh, constructor=Protein)
    msa.reassign_index(minter='id')
    metric='inverse_shannon_uncertainty'
    gap_modes=['ignore','include']
    gap_modes_labels=['gaps ignored','gaps included'] #'no gaps',
    data_feats_conserv=pd.DataFrame(columns=["aasi"])

    for fsta_data in SeqIO.parse(msa_fh,'fasta'):
        if ref_id in fsta_data.id:
            ref_seq=fsta_data.seq
            break

    for gap_mode in gap_modes:
        positional_conservation = msa.conservation(metric=metric, degenerate_mode='nan', gap_mode=gap_mode)
        aai=1
        for i in range(len(ref_seq)):
            if ref_seq[i]!="-":
                data_feats_conserv.loc[i,"aasi"]=aai
                data_feats_conserv.loc[i,"Conservation score (inverse shannon uncertainty): %s" % (gap_modes_labels[gap_modes.index(gap_mode)])]=positional_conservation[i]
                aai+=1
    data_feats_conserv=data_feats_conserv.set_index("aasi")

    # rate4site_rates=["-Im","-Ib"]
    # rate4site_rates_labels=["maximum likelihood rates","empirical Bayes rates"]
    rate4site_rates=["-Ib"]
    # rate4site_rates_labels=["maximum likelihood rates","empirical Bayes rates"]
    rate4site_trees=["-zj","-zn"]
    rate4site_trees_labels=["Jukes-Cantor distances","maximum likelihood distances"]
    data_feats_conserv_rate4site=pd.DataFrame()
    data_feats_conserv_rate4site.index.name="aasi"
    rate4site_out_fh="%s.rate4site" % (splitext(rate4site_fh)[0])
    for rate4site_rate in rate4site_rates:
        for rate4site_tree in rate4site_trees:
            rate4site_out_csv_fh="%s/%s.csv%s%s" % (dirname(rate4site_out_fh),ref_id,rate4site_rate,rate4site_tree)
            if not exists(rate4site_out_csv_fh):
                rate4site_com="%s -s %s -o %s -x %s_x -y %s_y -a %s %s %s;rm r4s.res" % \
                (rate4site_fh,msa_fh,rate4site_out_fh,rate4site_out_fh,rate4site_out_fh,ref_id,rate4site_rate,rate4site_tree)
                # print rate4site_com
                log_fh="%s.log" % rate4site_out_csv_fh
                log_f = open(log_fh,'a')
                subprocess.call(rate4site_com,shell=True,stdout=log_f, stderr=subprocess.STDOUT)
                log_f.close()
                with open(rate4site_out_fh,"r") as rate4site_out_f:
                    lines = rate4site_out_f.readlines()
                with open(rate4site_out_csv_fh,'w') as rate4site_out_csv_f:
                    for line in lines:
                        if (12<lines.index(line)<len(lines)-2):
                            rate4site_out_csv_f.write(line[:19]+"\n")
            col_name="Conservation score (%s)" % (\
    #             rate4site_rates_labels[rate4site_rates.index(rate4site_rate)],\
                rate4site_trees_labels[rate4site_trees.index(rate4site_tree)])
            data=pd.read_csv(rate4site_out_csv_fh,delim_whitespace=True, header=None,names=["aasi","ref",col_name])
            data=data.drop("ref",axis=1).set_index("aasi")
    #         if not "aasi" in data_feats_conserv_rate4site.columns:
    #             data_feats_conserv_rate4site.loc[:,"aasi"]=data.loc[:,"aasi"]
    #         data_feats_conserv_rate4site.loc[:,col_name]=data.loc[:,col_name]
            data_feats_conserv_rate4site=pd.concat([data,data_feats_conserv_rate4site],axis=1)
    data_feats_conserv_rate4site=data_feats_conserv_rate4site
    
    data_feats_conserv=pd.concat([data_feats_conserv,data_feats_conserv_rate4site],axis=1)
    return data_feats_conserv

def get_residue_depth(pdb_fh,msms_fh):
    from Bio.PDB import Selection,PDBParser
    from Bio.PDB.Polypeptide import is_aa
    from Bio.PDB.ResidueDepth import get_surface,_read_vertex_array,residue_depth,ca_depth,min_dist
    surface_fh="%s/%s.msms.vert" % (dirname(msms_fh),basename(pdb_fh))
    if not exists(surface_fh):
        pdb_to_xyzr_fh="%s/pdb_to_xyzr" % dirname(msms_fh)
        xyzr_fh="%s/%s.xyzr" % (dirname(msms_fh),basename(pdb_fh))
        pdb_to_xyzr_com="%s %s > %s" % (pdb_to_xyzr_fh,pdb_fh,xyzr_fh)
        msms_com="%s -probe_radius 1.5 -if %s -of %s > %s.log" % (msms_fh,xyzr_fh,splitext(surface_fh)[0],splitext(surface_fh)[0])
        log_fh="%s.log" % msms_fh
        log_f = open(log_fh,'a')
        log_f.write("%s;\n%s\n" % (pdb_to_xyzr_com,msms_com))
        subprocess.call("%s;%s" % (pdb_to_xyzr_com,msms_com) , shell=True,stdout=log_f, stderr=subprocess.STDOUT)
        log_f.close()

    surface =_read_vertex_array(surface_fh)
    
    pdb_parser=PDBParser()
    pdb_data=pdb_parser.get_structure("pdb_name",pdb_fh)
    model = pdb_data[0]
    residue_list = Selection.unfold_entities(model, 'R') 
    
    depth_dict = {}
    depth_list = []
    depth_keys = []
    for residue in residue_list:
        if not is_aa(residue):
            continue
        rd = residue_depth(residue, surface)
        ca_rd = ca_depth(residue, surface)
        # Get the key
        res_id = residue.get_id()
        chain_id = residue.get_parent().get_id()
        if chain_id=="A":
            depth_dict[(chain_id, res_id)] = (rd, ca_rd)
            depth_list.append((residue, (rd, ca_rd)))
            depth_keys.append((chain_id, res_id))
            # Update xtra information
            residue.xtra['EXP_RD'] = rd
            residue.xtra['EXP_RD_CA'] = ca_rd
        else:
            break
    depth_df=pd.DataFrame(depth_dict).T.reset_index()
    depth_df=depth_df.drop("level_0",axis=1)
    aasi_prev=0
    for i in range(len(depth_df)):
        if depth_df.loc[i,"level_1"][1]!=aasi_prev:
            depth_df.loc[i,"aasi"]=depth_df.loc[i,"level_1"][1]
            aasi_prev=depth_df.loc[i,"level_1"][1]

    depth_df=depth_df.drop("level_1",axis=1)
    depth_df=depth_df.loc[~pd.isnull(depth_df.loc[:,"aasi"]),:]
    depth_df=depth_df.set_index("aasi",drop=True)
    depth_df.columns=["Residue depth","Residue (C-alpha) depth"]
    return depth_df

def get_bfactor(pdb_fh,ref_out=False):
    pdb_parser=PDBParser()
    pdb_data=pdb_parser.get_structure("pdb_name",pdb_fh)
    data_bfactor=pd.DataFrame(columns=['ref_3letter','Temperature factor (flexibility)'])
    data_bfactor.index.name='refi'
    for model in pdb_data:
        for chain in model:
            for residue in chain:
                if residue.get_resname() in aas_21_3letter: #only aas 
                    for atom in residue:
                        data_bfactor.loc[residue.id[1],'ref_3letter']=residue.get_resname()
                        data_bfactor.loc[residue.id[1],'Temperature factor (flexibility)']=atom.get_bfactor()
                        break
    if ref_out:
        return data_bfactor
    else:
        return data_bfactor.loc[:,'Temperature factor (flexibility)']

def get_dfrominterface(pdb_fh):
    """
    This calculates distances between each ligand atom or optionally provided amino acids (sources) and each residue in the protein.
    
    :param pdb_fh: path to .pdb file.
    """
    junk_residues = ["HOH"," MG","CA"," NA","SO4","IOD","NA","CL","GOL","PO4"]
    pdb_parser=PDBParser()
    pdb_data=pdb_parser.get_structure("pdb_name",pdb_fh)
    model = pdb_data[0]


    if len(model.child_dict)==2:
        chainA = model["A"] #only a chain
        chainB = model["B"] #only a chain
        def get_resobjs(chainA):
            ligands_residue_objs=[]
            for residue in chainA:
                if not residue.get_resname() in junk_residues:
                    if residue.get_resname() in aas_21_3letter: #only aas
                        ligands_residue_objs.append(residue)
            return ligands_residue_objs

        chainA_resobjs=get_resobjs(chainA)
        chainB_resobjs=get_resobjs(chainB)

        resobjs_tups=zip(chainA_resobjs,chainB_resobjs)

        dfrominter=pd.DataFrame(columns=['Distance from dimer interface'])
        for tup in resobjs_tups:
            resA=tup[0]
            resB=tup[1]
            if resA.get_id()[1]==resB.get_id()[1]:
                dfrominter.loc[resA.get_id()[1],'Distance from dimer interface']=\
                (resA['CA']-resB['CA'])/2    
        dfrominter.index.name='refi'
        return dfrominter
    
def get_pdb_feats(pdb_fh):
    pdb_parser=PDBParser()
    pdb_data=pdb_parser.get_structure("pdb_name",pdb_fh)
    model = pdb_data[0]
    if len(model.child_dict)==2:
        pdb_feats=pd.concat([get_bfactor(pdb_fh), get_dfrominterface(pdb_fh)],axis=1)
    else:
        pdb_feats=get_bfactor(pdb_fh)
    return pdb_feats

def get_data_feats_pos(prj_dh,info,data_out_fh):
    if not exists(data_out_fh):
        cctmr=info.cctmr
        fsta_fh=info.fsta_fh
        pdb_fh=info.pdb_fh
        dssp_fh=info.dssp_fh
        active_sites=info.active_sites
        host=info.host
        clustalo_fh=info.clustalo_fh
        msms_fh=info.msms_fh
        rate4site_fh=info.rate4site_fh

        if active_sites!='nan':
            active_sites=[int(i) for i in active_sites.split(" ")]
        else:
            active_sites=[]

        if cctmr != 'nan':
            cctmr=[int("%s" % i) for i in cctmr.split(" ")]
            aas_len=cctmr[1]-1
            fsta_fh=cctmr_fasta2ref_fasta(fsta_fh,cctmr)
        else :
            fsta_data = SeqIO.read(open(fsta_fh), "fasta")
            aas_len=len(fsta_data)/3

        if not exists(prj_dh+"/data_feats/aas"):
            makedirs(prj_dh+"/data_feats/aas")

        if(exists("%s/cfg/feats_pos" % prj_dh) and \
            stat("%s/cfg/feats_pos" % prj_dh).st_size !=0):
            data_feats=pd.read_csv('%s/cfg/feats_pos' % prj_dh)
            if 'aasi' in data_feats:
                if not 'refi' in data_feats:
                    data_feats.loc[:,'refi']=data_feats.loc[:,'aasi']
                del data_feats['aasi']
        elif  (exists("%s/cfg/feats" % prj_dh) and \
            stat("%s/cfg/feats" % prj_dh).st_size !=0):
            data_feats=pd.read_csv('%s/cfg/feats' % prj_dh)
        if isinstance(data_feats,pd.DataFrame) and len(data_feats)!=0:
                data_feats=data_feats.set_index("refi",drop=True)
                data_feats.index = [int(i) for i in data_feats.index]
                tmp=pd.DataFrame(index=range(1,aas_len+1,1))
                tmp.index.name="refi"
                data_feats=pd.concat([tmp,data_feats],axis=1,join_axes=[tmp.index])
                logging.info("custom features taken from: cfg/feats")
        else:
            data_feats=pd.DataFrame(index=range(1,aas_len+1,1))
            data_feats.index.name="refi"
        if not 'ref' in data_feats:
            data_feats.loc[:,'ref']=list(info.prt_seq)
        if "Unnamed: 0" in data_feats.columns:
            data_feats=data_feats.drop("Unnamed: 0", axis=1)

        if not pd.isnull(pdb_fh):
            feats_types=["dssp","dfromact","depth","consrv_score",'pdb']
            for feats_type in feats_types:
                data_feats_fh="%s/data_feats/aas/feats_%s" % (prj_dh,feats_type)
                if feats_type=="dssp":
                    if not exists(data_feats_fh):
                        dssp_df=getdssp_data(pdb_fh,dssp_fh)
                        dssp_df.reset_index().to_csv(data_feats_fh,index=False)
                    else:
                        dssp_df=pd.read_csv(data_feats_fh)
                        dssp_df=dssp_df.set_index("aasi",drop=True)
                elif feats_type=="dfromact":
                    if not exists(data_feats_fh):
                        dfromact_df=pdb2dfromactivesite(pdb_fh,active_sites)
                        dfromact_df.reset_index().to_csv(data_feats_fh,index=False)
                    else:
                        dfromact_df=pd.read_csv(data_feats_fh)
                        dfromact_df=dfromact_df.set_index("aasi",drop=True)                        
                elif feats_type=="depth":
                    logging.info("getting structural features")
                    if not exists(data_feats_fh):
                        # try:
                        depth_df=get_residue_depth(pdb_fh,msms_fh)
                        depth_df.reset_index().to_csv(data_feats_fh,index=False)
                        # except:
                        #     depth_df=pd.DataFrame(index=data_feats.index)
                        #     logging.error("nawk not installed")
                    else:
                        depth_df=pd.read_csv(data_feats_fh)
                        depth_df=depth_df.set_index("aasi",drop=True)                        
                elif feats_type=="consrv_score":
                    logging.info("getting conservation scores")
                    if not exists(data_feats_fh):
                        consrv_score_df=get_consrv_score(fsta_fh,host,clustalo_fh,rate4site_fh)
                        consrv_score_df.reset_index().to_csv(data_feats_fh,index=False)            
                    else:
                        consrv_score_df=pd.read_csv(data_feats_fh)
                        consrv_score_df=consrv_score_df.set_index("aasi",drop=True)                        
                elif feats_type=="pdb":
                    logging.info("getting features from pdb")
                    if not exists(data_feats_fh):
                        pdb_df=get_pdb_feats(pdb_fh)
                        pdb_df.reset_index().to_csv(data_feats_fh,index=False)            
                    else:
                        pdb_df=pd.read_csv(data_feats_fh)
                        pdb_df=pdb_df.set_index("refi",drop=True)
            if len(data_feats)!=0:
                data_feats=pd.concat([data_feats,
                                      dssp_df,
                                      dfromact_df,
                                      consrv_score_df,
                                      depth_df,
                                     pdb_df], axis=1) #combine dssp_df and dfromact
            else:
                data_feats=pd.concat([dssp_df,
                                      dfromact_df,
                                      consrv_score_df,
                                      depth_df,
                                     pdb_df], axis=1) #combine dssp_df and dfromact
            # data_feats.reset_index().to_csv("%s/data_feats/aas/feats_all" % prj_dh,index=False)
            # data_feats.loc[:,'refi']=data_feats.loc[:,'aasi']
            # del data_feats['aasi']
            data_feats.index.name='refi'
            data_feats=data_feats.reset_index()
            refrefis=[]
            # print data_feats.index.name
            # print data_feats.index.tolist()[:5]
            for i in data_feats.index.tolist():
                # print data_feats.loc[i,'ref']
                if data_feats.loc[i,'ref']!='*':
                    refrefis.append("%s%03d" % (data_feats.loc[i,'ref'],data_feats.loc[i,'refi']))
                elif data_feats.loc[i,'ref']=='*':
                    refrefis.append("X%03d" % (data_feats.loc[i,'refi']))
            data_feats.loc[:,'refrefi']=refrefis
            del data_feats['ref']
            del data_feats['refi']            

            # data_feats.to_csv(data_out_fh+'_test',index=False)
            
            # feats_sub_pos_tups=[[
            #                     'Solvent Accessible Surface Area',
            #                      'Solvent Accessible Surface Area']]
            # data_feats_mut_diffs_fh="%s/data_feats_mut_diffs" % dirname(data_out_fh)            
            # data_feats=get_data_feats_mut_diffs(data_feats,
            #                                     feats_sub_pos_tups,
            #                                     data_out_fh=data_feats_mut_diffs_fh)

            data_feats.to_csv(data_out_fh)
            logging.info("output: data_feats/aas/data_feats_pos")
            return data_feats
        else:
            logging.warning("pdb_fh not given in cfg")
    else:
        logging.info("already processed") 

def get_data_feats_mut_diffs(data_feats_pos,feats_sub_pos_tups,
                             data_out_fh):
    data_feats_aas_fh='%s/data_feats_aas' % abspath(dirname(__file__))
    data_feats_aas=pd.read_csv(data_feats_aas_fh)
    data_feats_aas=data_feats_aas.set_index("aas",drop=True)

    if 'refrefi' in data_feats_pos.columns:
        data_feats_pos=data_feats_pos.set_index('refrefi')

    data_feats_mut_diffs=pd.DataFrame()
    for feats_sub_pos_tup in feats_sub_pos_tups:
        feat_sub=feats_sub_pos_tup[0]
        feat_pos=feats_sub_pos_tup[1]
        feat_pos_label="$\Delta$(%s) per position" % feat_pos
        feat_mut="$\Delta$(%s) per mutation" % feat_pos
        if (feat_sub in data_feats_aas.columns) and \
            (feat_pos in data_feats_pos.columns):
            for refrefi in data_feats_pos.index:
                for mut in data_feats_aas.index:
                    mutid="%s%s" % (refrefi,mut)
                    data_feats_mut_diffs.loc[mutid,'refrefi']=refrefi
                    data_feats_mut_diffs.loc[mutid,'mut']=mut                
                    data_feats_mut_diffs.loc[mutid,feat_mut]=\
                        data_feats_aas.loc[mut,feat_sub]\
                        -data_feats_pos.loc[refrefi,feat_pos]            
        #     mean
        data_feats_pos_diffs=data_feats_mut_diffs.pivot_table(values=feat_mut,
                            index='mut',columns='refrefi').mean()
        data_feats_pos_diffs.index.name='refrefi'
        data_feats_pos_diffs.name=feat_pos_label
        data_feats_pos=pd.concat([data_feats_pos,data_feats_pos_diffs],axis=1)
        data_feats_pos.index.name='refrefi'
    data_feats_mut_diffs.index.name='mutids'
    data_feats_mut_diffs.to_csv(data_out_fh)
    return data_feats_pos

def get_data_feats_sub(data_out_fh,data_feats_aas_fh='%s/data_feats_aas' % abspath(dirname(__file__))):
#     data_feats_aas_fh='%s/data_feats_aas' % abspath(dirname(__file__))
    if not exists(data_out_fh):
        data_feats_aas=pd.read_csv(data_feats_aas_fh)
        data_feats_aas=data_feats_aas.set_index("aas",drop=True)

        subids=[]
        for refaa in aas_21:
            for mutaa in aas_21:
                subids.append("%s%s" % (refaa,mutaa))  
        data_feats_sub=pd.DataFrame(index=subids)
        data_feats_sub.index.name='subids'

        for subid in data_feats_sub.index:
            refaa=subid[0]
            mutaa=subid[1]
            # data_feats_sub.loc[subid,'Reference amino acid']=refaa
            # data_feats_sub.loc[subid,'Mutant amino acid']=mutaa
            if (refaa in data_feats_aas.index) and (mutaa in data_feats_aas.index):
                for feat in data_feats_aas:        
                    data_feats_sub.loc[subid,"Reference amino acid's %s" % feat]=\
                    data_feats_aas.loc[refaa,feat]
                    data_feats_sub.loc[subid,"Mutant amino acid's %s" % feat]=\
                    data_feats_aas.loc[mutaa,feat]
                    data_feats_sub.loc[subid,
                                       "$\Delta$(%s) per substitution" \
                                       % feat]\
                    =data_feats_aas.loc[mutaa,feat]-data_feats_aas.loc[refaa,feat]
        # data_feats_sub.loc[:,'Substitution type']=data_feats_sub.index            
        data_feats_sub.to_csv(data_out_fh)
        logging.info("output: data_feats/aas/data_feats_sub")
        return data_feats_sub
    else:
        logging.info("already processed") 

def get_data_feats_mut(prj_dh,data_out_fh,info):
    if not exists(data_out_fh):
        data_feats_mut_fh="%s/cfg/feats_mut" % (prj_dh)
        data_feats_mut_diffs_fh="%s/data_feats/aas/data_feats_mut_diffs" % (prj_dh)
        data_feats_mut=pd.DataFrame()
        for data_fh in [data_feats_mut_fh,data_feats_mut_diffs_fh]:
            if exists(data_fh):
                data=pd.read_csv(data_fh)
                if len(data)!=0:
                    if 'mutids' in data.columns:
                        data=data.set_index('mutids',drop=True)
                    elif set(['mut','ref','refi']).issuperset(set(data.columns.tolist())): 
                        data.loc[:,'mutids']=makemutids(data,data.loc[:,'refi'])
                        data=data.set_index('mutids',drop=True)
                    if len(data_feats_mut)==0:
                        data_feats_mut=data
                    else:
                        data_feats_mut=pd.concat([data_feats_mut,data],axis=1)
                        data_feats_mut.index.name='mutids'
            else:
                logging.info('not exists: %s' % basename(data_fh))
        for col in ['mut','ref','refi','refrefi']:
            if col in data_feats_mut:
                del data_feats_mut[col]        
        if len(data_feats_mut)==0:
            data_feats_mut=pd.DataFrame(index=makemutids_fromprtseq(info.prt_seq))
            data_feats_mut.index.name='mutids'
        data_feats_mut.to_csv(data_out_fh)
        logging.info("output: data_feats/aas/data_feats_mut")
        return data_feats_mut    
    else:
        logging.info("already processed") 

def concat_feats(data_feats_all,data_feats,col_index):
    data_feats_all=set_index(data_feats_all,col_index)
    data_feats    =set_index(data_feats    ,col_index)
    data_feats_all=data_feats_all.join(data_feats)
    return data_feats_all


def get_data_feats_all(data_feats_mut_fh,data_feats_pos_fh,data_feats_sub_fh,
                      data_out_fh,info):
    if not exists(data_out_fh):
        from os.path import splitext
        from dms2dfe.lib.io_seq_files import fasta_nts2prt
        from dms2dfe.lib.global_vars import aas_21

        data_feats_mut=pd.read_csv(data_feats_mut_fh)
        data_feats_pos=pd.read_csv(data_feats_pos_fh)
        data_feats_sub=pd.read_csv(data_feats_sub_fh)

        #fsta_fh='/gmr_wt.fasta'
        # if info.cctmr != 'nan':
        #     cctmr=[int("%s" % i) for i in cctmr.split(" ")]
        #     aas_len=cctmr[1]-1
        #     fsta_fh=cctmr_fasta2ref_fasta(fsta_fh,cctmr)

        # prt_seq=fasta_nts2prt(fsta_fh,host=host).replace('*','X')
        prt_seq=info.prt_seq
        data_feats_all=pd.DataFrame()
        for refi in range(1,len(prt_seq)+1):
            ref=prt_seq[refi-1]
            for mut in aas_21:
                mutid="%s%03d%s" % (ref,refi,mut)
                refrefi=mutid[:4] 
                subid=mutid[0]+mutid[-1]
                data_feats_all.loc[mutid,'refrefi']=refrefi
                data_feats_all.loc[mutid,'subids']=subid
        #     break
        data_feats_all.index.name='mutids'

        # FEATS PER POS
        data_feats_all=concat_feats(data_feats_all,
                                    data_feats_pos,
                     'refrefi')
        # FEATS PER SUB
        data_feats_all=concat_feats(data_feats_all,
                                    data_feats_sub,
                     'subids')
        # FEATS PER MUT
        data_feats_all=concat_feats(data_feats_all,
                                    data_feats_mut,
                     'mutids')
        
        for col in ['subids','refrefi']:
            if col in data_feats_all:
                del data_feats_all[col] 
        cols_del=[col for col in data_feats_all if 'Unnamed' in col]
        for col in cols_del:
            del data_feats_all[col] 

        data_feats_all.to_csv(data_out_fh)                
        logging.info("output: data_feats/aas/data_feats_all")                
        return data_feats_all
    else:
        logging.info("already processed") 