from datetime import datetime

from pandas import DataFrame
from blaze.utils import example
from blaze import CSV

data = CSV(example('iris.csv'))
