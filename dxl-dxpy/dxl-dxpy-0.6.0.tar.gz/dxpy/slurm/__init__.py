"""
A Python interface 
"""
from .slurm import TaskInfo, apply_command, sbatch, sid_from_submit, squeue, is_complete
