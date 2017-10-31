#!usr/bin/python

# Copyright 2016, Rohan Dandage <rraadd_8@hotmail.com,rohan@igib.in>
# This program is distributed under General Public License v. 3.  


import sys
from os.path import exists,splitext,abspath,dirname,basename    
from os import makedirs
from glob import glob
import pandas as pd
import subprocess
import logging
logging.basicConfig(format='[%(asctime)s] %(levelname)s\tfrom %(filename)s in %(funcName)s(..): %(message)s',level=logging.DEBUG) # filename=cfg_dh+'.log'
from dms2dfe.lib.io_data_files import is_cfg_ok,info2src,raw_input2info
    
# GET INPTS    
def main(prj_dh,inputs=None):
    """
    **--step 0**. Configures a project_directory.
    
    Firstly, to create a new project directory (`prj_dh`) in current directory, 

    .. code-block:: text

        from dms2dfe import configure
        configure.main("path/to/project_directory")

    Editing configuration files (`path/to/project_directory/cfg/info`)

    Input parameters can be fed manually in csv file located here `project_directory/cfg/info`.
    
    Optionally input parameters can also be entered using command prompt,

    .. code-block:: text

        from dms2dfe import configure
        configure.main("path/to/project_directory","inputs")

    Optionally to feed default parameters use

    .. code-block:: text

        from dms2dfe import configure
        configure.main("defaults")

    :param prj_dh: path to project directory.

    """
    while prj_dh.endswith('/'):
        prj_dh=prj_dh[:-1]
    if not dirname(prj_dh)==dirname(dirname(prj_dh)):
        logging.error("dms2dfe should be executed from the directory containing project directory. ie. move to '%s' and execute: 'dms2dfe %s'." % (dirname(prj_dh),basename(prj_dh)))
        sys.exit()
    #SET VARS
    cfgs=['lbls', 'fit', 'comparison', 'info', 'repli',
          'feats_mut','feats_sub','feats_pos',
          'barcodes']
    cfg_dh=prj_dh+"/cfg"
    
    if not exists(cfg_dh):
        makedirs(cfg_dh)
        subprocess.call("cp -r %s/cfg %s"% (abspath(dirname(__file__)),prj_dh) ,shell=True)
        logging.info("new project directory created!: %s " % prj_dh)
        logging.info("modify configurations in %s" % cfg_dh)
        is_new_prj_dh=True
    else:
        is_new_prj_dh=False
        # sys.exit()

    if inputs=="inputs":
        raw_input2info(prj_dh,"input")        
        logging.info("configuration inputs modified!")
    elif prj_dh=="defaults":
        raw_input2info((abspath(dirname(__file__))),"default")
        logging.info("configuration defaults modified!")
    elif inputs=="dependencies" or inputs=="deps":
        deps_dh="%s/dms2dfe_dependencies" % abspath(dirname(__file__)) 
        if not exists(deps_dh):
            makedirs(deps_dh)
        log_fh="%s/%s.log" % (deps_dh,basename(deps_dh))
        log_f = open(log_fh,'a')
        #dssp
        dssp_fh=deps_dh+"/dssp-2.0.4-linux-amd64"
        if not exists(dssp_fh):
            logging.info("configuring: dssp")
            dssp_lnk="ftp://ftp.cmbi.ru.nl/pub/software/dssp/dssp-2.0.4-linux-amd64"
            com="wget -q %s --directory-prefix=%s" % (dssp_lnk,deps_dh)
            subprocess.call(com,shell=True,stdout=log_f, stderr=subprocess.STDOUT)
            subprocess.call("chmod +x %s" % dssp_fh,shell=True,stdout=log_f, stderr=subprocess.STDOUT)            
        #bowtie2
        bowtie2_fh=deps_dh+"/bowtie2-2.2.1/bowtie2"   
        if not exists(dirname(bowtie2_fh)):
            logging.info("configuring: bowtie2")
            bowtie2_src=deps_dh+'/v2.2.1.zip'
            if not exists(bowtie2_src):        
                bowtie2_lnk="https://github.com/BenLangmead/bowtie2/archive/v2.2.1.zip"
                com="wget -q %s --directory-prefix=%s" % (bowtie2_lnk,deps_dh)
                subprocess.call(com,shell=True,stdout=log_f, stderr=subprocess.STDOUT)
            subprocess.call("unzip %s -d %s" % (bowtie2_src,deps_dh),
                            shell=True,stdout=log_f, stderr=subprocess.STDOUT)
            #subprocess.call("chmod +x %s" % bowtie2_fh,shell=True,stdout=log_f, stderr=subprocess.STDOUT) 
            subprocess.call("cd %s;make all; cd -;" % dirname(bowtie2_fh),shell=True,stdout=log_f, stderr=subprocess.STDOUT)

        #samtools
	depn='samtools'
        samtools_fh=deps_dh+"/samtools-0.1.20/samtools"        
        if not exists(samtools_fh):
            logging.info("configuring: samtools")
            samtools_src=deps_dh+'/0.1.20.zip'
            if not exists(samtools_src):
                samtools_lnk="https://github.com/samtools/samtools/archive/0.1.20.zip"
                com="wget -q %s --directory-prefix=%s" % (samtools_lnk,deps_dh)
                subprocess.call(com,shell=True,stdout=log_f, stderr=subprocess.STDOUT)
                subprocess.call("unzip -f %s -d %s;" % (samtools_src,deps_dh),\
                                shell=True,stdout=log_f, stderr=subprocess.STDOUT)
            else:
                subprocess.call("unzip -f %s -d %s;" % (samtools_src,deps_dh),\
                                shell=True,stdout=log_f, stderr=subprocess.STDOUT)
            com='cd %s/samtools-0.1.20;make' % deps_dh
            sub_call_return=subprocess.call(com,shell=True,stdout=log_f, stderr=subprocess.STDOUT)
            while int(sub_call_return)!=0:
                inpt=raw_input("On a debian system, missing packages requred for installation of '%s' by running this command:\n\n$ sudo apt-get install zlib1g-dev libncurses5-dev;sudo apt-get update\n\nand THEN input 'y' (otherwise 'n').:" % (depn))
                if 'y' in inpt:
                    sub_call_return=subprocess.call(com,shell=True,stdout=log_f, stderr=subprocess.STDOUT)
                    subprocess.call("chmod +x %s" % samtools_fh,shell=True,stdout=log_f, stderr=subprocess.STDOUT)
                else:
                    logging.error("%s could not be installed. Error code=%s. More details in %s/dms2dfe_dependencies.log ." % (depn,sub_call_return,deps_dh))
                    sub_call_return=0
        #trimmomatic
        trimmomatic_fh=deps_dh+"/Trimmomatic-0.33/trimmomatic-0.33.jar"
        if not exists(trimmomatic_fh):
            logging.info("configuring: trimmomatic")
            trimmomatic_lnk="http://www.usadellab.org/cms/uploads/supplementary/Trimmomatic/Trimmomatic-0.33.zip"
            com="wget -q %s --directory-prefix=%s" % (trimmomatic_lnk,deps_dh)
            subprocess.call(com,shell=True,stdout=log_f, stderr=subprocess.STDOUT)
            subprocess.call("unzip %s/Trimmomatic-0.33.zip -d %s/" % (deps_dh,deps_dh),\
                            shell=True,stdout=log_f, stderr=subprocess.STDOUT)

        #clustalo
        clustalo_fh=deps_dh+"/clustalo-1.2.2-Ubuntu-x86_64"
        if not exists(clustalo_fh):
            logging.info("configuring: clustalo")
            soft_lnk="http://www.clustal.org/omega/clustalo-1.2.2-Ubuntu-x86_64"
            com="wget -q %s --directory-prefix=%s" % (soft_lnk,deps_dh)
            subprocess.call(com,shell=True,stdout=log_f, stderr=subprocess.STDOUT)
            subprocess.call("chmod +x %s" % clustalo_fh,shell=True,stdout=log_f, stderr=subprocess.STDOUT)

        #msms
        msms_fh=deps_dh+"/msms/msms.x86_64Linux2.2.6.1"
        if not exists(msms_fh):
            logging.info("configuring: msms")
            soft_lnk="http://mgltools.scripps.edu/downloads/tars/releases/MSMSRELEASE/REL2.6.1/msms_i86_64Linux2_2.6.1.tar.gz"
            com="wget -q %s --directory-prefix=%s/msms; tar -xvzf %s/msms/msms_i86_64Linux2_2.6.1.tar.gz -C %s/msms" % (soft_lnk,deps_dh,deps_dh,deps_dh)
            subprocess.call(com,shell=True,stdout=log_f, stderr=subprocess.STDOUT)
            pdb_to_xyzr_fh="%s/pdb_to_xyzr" % dirname(msms_fh)
            # pdb_to_xyzr_fh=deps_dh+"/msms/pdb_to_xyzr"
            with open(pdb_to_xyzr_fh, 'r') as f:
                line = f.read()
                line=line.replace("./atmtypenumbers","%s/msms/atmtypenumbers" % deps_dh)
            with open(pdb_to_xyzr_fh, 'w') as f:
                f.write(line)    
            # with open(pdb_to_xyzr_fh,"w") as f:
            #     if 
            
        #rate4site
        rate4site_fh=deps_dh+"/rate4site/rate4site-3.0.0/src/rate4site/rate4site"
        if not exists(rate4site_fh):
            logging.info("configuring: rate4site")
            soft_lnk="https://launchpadlibrarian.net/155121258/rate4site_3.0.0.orig.tar.gz"
	    #soft_lnk="ftp://rostlab.org/rate4site/rate4site-3.0.0.tar.gz"
            com="wget -q %s --directory-prefix=%s/rate4site;\
                tar -xvzf %s/rate4site/rate4site*.tar.gz -C %s/rate4site;\
                cd %s/rate4site/rate4site-3.0.0;\
                ./configure;make" % (soft_lnk,deps_dh,deps_dh,deps_dh,deps_dh)
            sub_call_return=subprocess.call(com,shell=True,stdout=log_f, stderr=subprocess.STDOUT)
            #print sub_call_return
            if int(sub_call_return)!=0:
            	logging.error("rate4site could not be installed. Error code=%s. More details in %s/dms2dfe_dependencies.log ." % (sub_call_return,deps_dh))
                inpt=raw_input("On a debian system, install 'rate4site' by this command:\n\n$ sudo apt-get install rate4site; sudo apt-get update\n\nand THEN input 'y' (otherwise 'n').:")
                if 'y' in inpt:
                    com='ln -s /usr/bin/rate4site %s/rate4site/rate4site-3.0.0/src/rate4site/rate4site' % (deps_dh)
                    #print com
                    subprocess.call(com,shell=True)
                else:
                    logging.error('rate4site could not be installed. aborting..')
                    sys.exit() 

        std=subprocess.Popen("which java",shell=True,stdout=log_f, stderr=subprocess.STDOUT)
        log_f.close();log_f=open(log_fh,'r');log_lines=log_f.readlines();log_f.close();log_f = open(log_fh,'a')
        if len([l for l in log_lines if "/usr/bin" in l])==0:
            print "\n###   TROUBLESHOOT   ###\njava environment isn't installed on the system.\nIt would be required for running Trimmomatic through fast2qcd module. Please install it by following command,\n\nsudo apt-get install openjdk-7-jre-headless;sudo apt-get update\n\nAfter the successfull installation, please configure dms2dfe by following command.\n\nfrom dms2dfe import configure\nconfigure.main(prj_dh)\n\n"
            # sys.exit()
        std=subprocess.Popen("which glxinfo",shell=True,stdout=subprocess.PIPE)
        if not std.stdout.read():
            print "\n###   TROUBLESHOOT   ###\nTo generate images from PDB structures using UCSF-Chimera, essential graphics drivers are required.\nIn case of the hardware already present on system please install following drivers.\n\nsudo apt-get install mesa-utils;sudo apt-get update\n\n"
         
        log_f.close()
        #add to defaults
        info=pd.read_csv("%s/cfg/info" % (prj_dh))
        info=info.set_index("varname",drop=True)
        info.loc["trimmomatic_fh","input"]=trimmomatic_fh
        info.loc["dssp_fh","input"]=dssp_fh
        info.loc["bowtie2_fh","input"]=bowtie2_fh
        info.loc["samtools_fh","input"]=samtools_fh
        info.loc["clustalo_fh","input"]=clustalo_fh
        info.loc["msms_fh","input"]=msms_fh
        info.loc["rate4site_fh","input"]=rate4site_fh
        info.reset_index().to_csv("%s/cfg/info" % (prj_dh), index=False)
        logging.info("dependencies installed!")

    if exists(cfg_dh) and not is_new_prj_dh:
        if is_cfg_ok(cfg_dh,cfgs):
            info2src(prj_dh)
        else:
            logging.info("check the configuration again.")
            # sys.exit()
    logging.shutdown()
                        
if __name__ == '__main__':
    
    if len(sys.argv)==2:
        main(sys.argv[1])
    elif len(sys.argv)==3:
        main(sys.argv[1],sys.argv[2])
