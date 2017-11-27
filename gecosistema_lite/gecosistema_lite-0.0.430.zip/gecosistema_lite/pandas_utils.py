# -------------------------------------------------------------------------------
# Licence:
# Copyright (c) 2012-2017 Luzzi Valerio 
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
#
# Name:        pandas_utils.py
# Purpose:
#
# Author:      Luzzi Valerio
#
# Created:     27/11/2017
# -------------------------------------------------------------------------------
import pandas as pd
from filesystem import *

def read_csv(filename):
    """
    read_csv - read_csv using pandas and c-engine
    """
    df = pd.read_csv(filename, sep=detectSeparator(filename), engine="c")
    data = df.as_matrix()
    columns = df.columns.values.tolist()
    return columns,data

if __name__ == "__main__":
    filename= "./tests/xls/file.csv"
    print read_csv(filename)