#!/shared/apps/sage/sage-5.12/spkg/bin/sage -python
'''
local testing command:
mpirun -np 2 python mpi_linearregression.py --cmip5_dir /Users/tj/data/cmip5/access1-3/ --cpc_dir /Users/tj/data/usa_cpc_nc/merged/
'''
import sys
sys.path.insert(0, "/home/vandal.t/anaconda/lib/python2.7/site-packages")

from mpi4py import MPI
from scipy.stats import pearsonr, spearmanr, kendalltau
import os
import time
import numpy
from sklearn.linear_model import LinearRegression, LassoCV
from pydownscale.data import DownscaleData, read_nc_files
from pydownscale.downscale import DownscaleModel
import argparse
import pandas

parser = argparse.ArgumentParser(description='Datafiles.')
parser.add_argument('--cmip5_dir', dest='cmip5_dir')
parser.add_argument('--cpc_dir', dest='cpc_dir')
args = parser.parse_args()

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

# initialize downscale data
cmip5_dir = args.cmip5_dir   #/Users/tj/data/cmip5/access1-0/
cpc_dir = args.cpc_dir      # /Users/tj/data/usa_cpc_nc/merged/

# climate model data, monthly
cmip5 = read_nc_files(cmip5_dir)
#cmip5.time = pandas.to_datetime(cmip5.time.values)
cmip5 = cmip5.resample('MS', 'time', how='mean')   ## try to not resample

# daily data to monthly
cpc = read_nc_files(cpc_dir)
#cpc.time = pandas.to_datetime(cpc.time.values)
monthlycpc = cpc.resample('MS', dim='time', how='mean')  ## try to not resample

data = DownscaleData(cmip5, monthlycpc)
data.normalize_monthly()
if rank == 0:
   ## lets split up our y's
   pairs = data.location_pairs('lat', 'lon')[:size]   ## lets chunk this data up into size parts
else:
   pairs = None

pairs = comm.scatter(pairs, root=0)
results = []
models = [LinearRegression(), LassoCV(alphas=[1, 10, 100])]
seasons = ['DJF', 'MAM', 'JJA', 'SON']
for model in models:
    for season in seasons:
        t0 = time.time()
        dmodel = DownscaleModel(data, model, season=season)
        dmodel.train(location={'lat': pairs[0], 'lon': pairs[1]})
        res = dmodel.get_results()
        res['time_to_execute'] = time.time() - t0
        results.append(res)

newData = comm.gather(results, root=0)

if rank == 0:
   newData = [item for l in newData for item in l]   ## condense lists of lists
   data = pandas.DataFrame(newData)
   data.to_csv("results.csv", index=False)
