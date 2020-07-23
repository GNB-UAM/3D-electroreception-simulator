import pygmsh
import numpy as np
import subprocess
import os
import shutil

geom = pygmsh.opencascade.Geometry(
  characteristic_length_min=0.1,
  characteristic_length_max=0.1,
  )

cyl1 = geom.add_cylinder([0.0, 0.0, 0.0], [0, 0, 1], 1.0)

cyl2 = geom.add_cylinder([0.0, 0.0, -1.0], [0, 0, 1], 1.0)

geom.boolean_fragments([cyl1], [cyl2])

with open('val.geo', 'w') as text_file:
    text_file.write(geom.get_code())

subprocess.run('gmsh -3 val.geo -format unv -bin -o val.unv', shell=True)

os.remove('val.geo')

if os.path.exists('val/') and os.path.isdir('val/'):
    shutil.rmtree('val/')

subprocess.run('ElmerGrid 8 2 val.unv -unite -removeintbcs -removelowdim -removeunused -3d', shell=True)

shutil.move('val.unv', 'val/val.unv')

shutil.copy('case.sif', 'val/case.sif')

os.chdir('val/')

subprocess.run('ElmerSolver case.sif', shell=True)