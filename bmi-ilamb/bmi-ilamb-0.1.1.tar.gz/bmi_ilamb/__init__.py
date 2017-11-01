"""Basic Model Interface (BMI) for the ILAMB benchmarking system."""

import os
from .bmi_ilamb import BmiIlamb
from .config import Configuration


__all__ = ['BmiIlamb', 'Configuration']

package_dir = os.path.dirname(__file__)
data_dir = os.path.join(package_dir, 'data')
