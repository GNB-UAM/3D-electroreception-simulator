from concurrent.futures import ThreadPoolExecutor
from mpi4py.futures import MPICommExecutor
from simulacion import Simulacion
from mpi4py import MPI
from scipy.optimize import minimize
import multiprocessing
from utils import *
from mako.template import Template
import pandas as pd
import numpy as np
import getpass
import socket
import time
import json
import os
import shutil
import concurrent
import subprocess
from tqdm import tqdm
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--optimize', '-opt', action='store_true', help='optimiza los parametros del submarino usando el algoritmo `L-BFGS-B`')
parser.add_argument('--qsub', '-q', action='store_true', help='ejecuta la simulacion el gestor de tareas del cluster')
args = parser.parse_args()

def run_sim(sim):
    return sim.simular()

def sim_minimize(*params):
    pass
    #cpus = multiprocessing.cpu_count()
    #with ThreadPoolExecutor(max_workers=cpus) as executor:


def optimize(conf_sub, conf_sim, executor):
    pass

def arrancar_simulacion(executor, cluster_env_var='', optimize=False):
    start_time = time.time()
    with open('conf.json') as conf:
        conf = json.load(conf)

        conf_sub = pd.json_normalize(conf['submarino'], sep='.').to_dict(orient='records')[0]
        conf_sim = pd.json_normalize(conf['simulacion'], sep='.').to_dict(orient='records')[0]

        normalizar_conf(conf_sub)
        normalizar_conf(conf_sim)

        if optimize:
            optimize(conf_sub, conf_sim, executor)
        else:
            futures, sims = [], []
            
            sub_comb = list(gen_combinations(conf_sub))
            for i in range(len(su3b_comb)):
                sims.append(Simulacion(sub_comb[i], conf_sim, cluster_env_var=cluster_env_var, uid=i))
                i+=1
                
            for s in sims:
                futures.append(executor.submit(run_sim, s))

            results = []
            with tqdm(total=i) as pbar:
                for future in concurrent.futures.as_completed(futures):
                    res = future.result()
                    shutil.rmtree(f"sim_{res[0]['id']}")
                    results += res
                    pbar.update(1)

            with open('res.json', 'w') as res_file:
                json.dump(results, res_file)
    print("--- %s seconds ---" % (time.time() - start_time))

if __name__ == "__main__":
    hostname = socket.gethostname()

    if args.qsub:
        with MPICommExecutor(MPI.COMM_WORLD, root=0) as executor:
            if executor is not None:
                arrancar_simulacion(executor, cluster_env_var=ENV_VAR, optimize=args.optimize)
        exit()

    if 'labomat' in hostname:
        user = getpass.getuser()

        ENV_VAR = f'LD_LIBRARY_PATH=/home/{user}/lib64:/home/{user}/usr/lib64:$LD_LIBRARY_PATH /home/{user}/lib64/ld-2.17.so /home/{user}/usr/bin/'
        os.environ['ELMER_HOME'] = f'/home/{user}/usr/'

        with open(f'cluster.q', 'w') as text_file:
            cluster_template = Template(filename='cluster_template.q')
            cluster = cluster_template.render(
                workers=8 if args.optimize else 96,
                opt='-opt' if args.optimize else ''
                user=user)
            text_file.write(cluster)

        subprocess.run('qsub cluster.q')
        os.remove('cluster.q')
    else:
        cpus = 1 if args.optimize else multiprocessing.cpu_count()
        with ThreadPoolExecutor(max_workers=cpus) as executor: 
            arrancar_simulacion(executor, optimize=args.optimize)