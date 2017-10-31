#!usr/bin/python

# source file for dms2dfe's configuration 

host='coli' #Host name for assigning codon table
Ni_cutoff='8' #Lower cut off for frequency per mutant
Q_cutoff='30' #Lower cut off for Phred score quality
transform_type='log' #Type of transformation of frequecies of mutants
norm_type='none' #Type of normalization of fold changes
alignment_type='loc' #Alignment type
cores='8' #Number of cores to be used
clips='nan' #Optional: Clip upstream UPTO and downstream FROM codons (space delimited) rg. 10<SPACE>167
mut_subset='N' #Optional: Subset of mutations to be used for down-stream analysis
ml_input='Fi' #nan
fsta_fh='Firnberg_et_al_2014/btem.fasta' #Optional: Path to reference fasta file
pdb_fh='Firnberg_et_al_2014/btem.pdb' #Optional: Path to pdb file
active_sites='68 166' #Optional: residue numbers of active sites (space delimited) eg. 68<SPACE>192
cctmr='nan' #Optional: if reference sequence is concatamer (space delimited) eg. 1<SPACE>265<SPACE>268<SPACE>532
trimmomatic_com='nan' #Optional: additional commands to pass to trmmomatic
bowtie2_com='nan' #Optional: additional commands to pass to bowtie2
dssp_fh='/home/debian/Documents/dms2dfe/dms2dfe/dms2dfe/dms2dfe_dependencies/dssp-2.0.4-linux-amd64' #Optional: path to dssp module (dependencies)
trimmomatic_fh='/home/debian/Documents/dms2dfe/dms2dfe/dms2dfe/dms2dfe_dependencies/Trimmomatic-0.33/trimmomatic-0.33.jar' #Optional: path to trimmomatic source (.jar) file (dependencies)
bowtie2_fh='/home/debian/Documents/dms2dfe/dms2dfe/dms2dfe/dms2dfe_dependencies/bowtie2-2.2.1/bowtie2' #Optional: path to bowtie2 source file
samtools_fh='/home/debian/Documents/dms2dfe/dms2dfe/dms2dfe/dms2dfe_dependencies/samtools-0.1.20/samtools' #Optional: path to samtools source file
clustalo_fh='/home/debian/Documents/dms2dfe/dms2dfe/dms2dfe/dms2dfe_dependencies/clustalo-1.2.2-Ubuntu-x86_64' #Optional: path to clustal omega source file
msms_fh='/home/debian/Documents/dms2dfe/dms2dfe/dms2dfe/dms2dfe_dependencies/msms/msms.x86_64Linux2.2.6.1' #Optional: path to MSMS source file (for calculation of residue depths)
rate4site_fh='/home/debian/Documents/dms2dfe/dms2dfe/dms2dfe/dms2dfe_dependencies/rate4site/rate4site-3.0.0/src/rate4site/rate4site' #Optional: path to rate4site source file (for calculation of conservation scores)
rscript_fh='/home/debian/miniconda/envs/dms2dfe/bin/Rscript' #Optional: path to Rscript (for use of Deseq2)
prj_dh='/home/debian/Documents/dms2dfe/ms_datasets/analysis/Firnberg_et_al_2014' #nan
fsta_id='btem' #nan
fsta_seq='TAATAAATGAGTATTCAACATTTCCGTGTCGCCCTTATTCCCTTTTTTGCGGCATTTTGCCTTCCTGTTTTTGCTCACCCAGAAACGCTGGTGAAAGTAAAAGATGCTGAAGATCAGTTGGGTGCACGAGTGGGTTACATCGAACTGGATCTCAACAGCGGTAAGATCCTTGAGAGTTTTCGCCCCGAAGAACGTTTTCCAATGATGAGCACTTTTAAAGTTCTGCTATGTGGCGCGGTATTATCCCGTGTTGACGCCGGGCAAGAGCAACTCGGTCGCCGCATACACTATTCTCAGAATGACTTGGTTGAGTACTCACCAGTCACAGAAAAGCATCTTACGGATGGCATGACAGTAAGAGAATTATGCAGTGCTGCCATAACCATGAGTGATAACACTGCGGCCAACTTACTTCTGACAACGATCGGAGGACCGAAGGAGCTAACCGCTTTTTTGCACAACATGGGGGATCATGTAACTCGCCTTGATCGTTGGGAACCGGAGCTGAATGAAGCCATACCAAACGACGAGCGTGACACCACGATGCCTGCAGCAATGGCAACAACGTTGCGCAAACTATTAACTGGCGAACTACTTACTCTAGCTTCCCGGCAACAATTAATAGACTGGATGGAGGCGGATAAAGTTGCAGGACCACTTCTGCGCTCGGCCCTTCCGGCTGGCTGGTTTATTGCTGATAAATCTGGAGCCGGTGAGCGTGGGTCTCGCGGTATCATTGCAGCACTGGGGCCAGATGGTAAGCCCTCCCGTATCGTAGTTATCTACACGACGGGGAGTCAGGCAACTATGGATGAACGAAATAGACAGATCGCTGAGATAGGTGCCTCACTGATTAAGCATTGGTAA' #nan
fsta_len='867' #nan
prt_seq='XXMSIQHFRVALIPFFAAFCLPVFAHPETLVKVKDAEDQLGARVGYIELDLNSGKILESFRPEERFPMMSTFKVLLCGAVLSRVDAGQEQLGRRIHYSQNDLVEYSPVTEKHLTDGMTVRELCSAAITMSDNTAANLLLTTIGGPKELTAFLHNMGDHVTRLDRWEPELNEAIPNDERDTTMPAAMATTLRKLLTGELLTLASRQQLIDWMEADKVAGPLLRSALPAGWFIADKSGAGERGSRGIIAALGPDGKPSRIVVIYTTGSQATMDERNRQIAEIGASLIKHWX' #nan
