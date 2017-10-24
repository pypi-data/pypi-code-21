""" Configuration for calculating Hamming distances on fingervein features extracted using the Maximum Curvature feature extractor, for the VERA database """ 

# Database: 
from bob.bio.vein.configurations.verafinger import database
protocol = 'Full'

# Directory where results will be placed:
temp_directory = './results/vera'  # pre-processed and extracted features will be placed here, along with the enrolled models  
sub_directory = 'mc'
result_directory = temp_directory  # Hamming distances will be placed here  
from bob.io.base import create_directories_safe
create_directories_safe(temp_directory)

# Pre-processing based on locating the finger in the image and horizontally aligning it:
from bob.bio.vein.configurations.maximum_curvature import preprocessor

# Feature extraction based on the Maximum Curvature algorithm:
from bob.bio.vein.configurations.maximum_curvature import extractor

# Hamming distance calculation:
from bob.bio.vein.algorithm import HammingDistance
algorithm = HammingDistance()

# Set up parallel processing using all available processors:
from bob.bio.vein.configurations.parallel import parallel, nice

# Specify the level of detail to be output in the terminal during program execution:
verbose = 2