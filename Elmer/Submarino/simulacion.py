import subprocess,os,vtk,glob,time,json,shutil,itertools,concurrent
import numpy as np
import pandas as pd
from tqdm import tqdm
from pprint import pprint
from itertools import product
from mako.template import Template
from concurrent.futures import ThreadPoolExecutor
from vtk.util.numpy_support import vtk_to_numpy
from submarino import Submarino
from collections import defaultdict
from utils import *

class Simulacion():
    def __init__(self, sub_combs, sim_dict, uid=0, cluster_env_var=''):
        self.cluster_env_var = cluster_env_var
        self.submarin_conf, self.sim_conf = sub_combs, sim_dict

        self.file_name = str(uid)
        self.sim_folder = f'sim_{uid}'

        self.sim_combs = list(gen_combinations(self.sim_conf))
        self.sim_params_join = defaultdict(list)
        for comb in self.sim_combs:
            [self.sim_params_join[k].append(v) for k, v in comb.items()]
                

    def simular(self):
        mesh_start_time = time.time()
        submarino = Submarino(self.submarin_conf, self.file_name)
        submarino.meshear()
        time_mesh = time.time() - mesh_start_time

        vcc = 'Variable time; Real MATC "corriente(tx-1)"'
        corriente_vals = [c / ((4*np.pi*(self.submarin_conf['sensor.radio']**2)) / 2) for c in self.sim_params_join['corriente_sensor']]

        if not os.path.exists(self.sim_folder):
            os.mkdir(self.sim_folder)

        cond_agua = 'Variable time; Real MATC "conductividad(tx-1)"'
        cond_vals = self.sim_params_join['conductividad_agua']

        with open(f'{self.sim_folder}/case.sif', 'w') as text_file:
            case_template = Template(filename='case_template.sif')
            case = case_template.render(
                folder_sim=self.sim_folder,
                num_params=len(self.sim_combs),
                conductividad_vals= ' '.join(map(str, cond_vals)),
                conductividad_agua=cond_agua,
                corriente_vals= ' '.join(map(str, corriente_vals)),
                vcc=vcc)
            text_file.write(case)

        grid_start_time = time.time()
        subprocess.run(f'{self.cluster_env_var}ElmerGrid 14 2 {self.file_name}.msh -out {self.sim_folder} -unite -removeintbcs -removelowdim -removeunused -3d', shell=True, stdout=subprocess.DEVNULL)
        time_grid = time.time() - grid_start_time
        
        os.remove(f'{self.file_name}.msh')

        solver_start_time = time.time()
        subprocess.run(f'{self.cluster_env_var}ElmerSolver {self.sim_folder}/case.sif', shell=True, stdout=subprocess.DEVNULL)
        time_solver = time.time() - solver_start_time

        voltages = []
        for vtu in glob.glob(f'{self.sim_folder}/case_*.vtu'):
            reader = vtk.vtkXMLUnstructuredGridReader()
            reader.SetFileName(vtu)
            reader.Update()
            output = reader.GetOutput()
            potential = output.GetPointData().GetArray('potential')

            voltages.append(vtk_to_numpy(potential).max())

        times = {
            'time.mesh': time_mesh,
            'time.grid': time_grid,
            'time.solver': time_solver
        }

        res_dicts = []
        for i in range(len(self.sim_combs)):
            d = {
                'v': voltages[i],
                'id': self.file_name,
                **self.sim_combs[i],
                **self.submarin_conf,
                **times
            }
            res_dicts.append(d)

        return res_dicts