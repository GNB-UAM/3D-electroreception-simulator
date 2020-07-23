import pygmsh
import numpy as np
import subprocess
import os

geom = pygmsh.Geometry()

box = geom.add_box([-0.284, -0.15, -0.125], [0.568, 0.3, 0.25])

cyl1 = geom.add_cylinder([-0.05, 0.0, 0.075], [0, 0, 5/100], 0.25/1000)

cyl2 = geom.add_cylinder([0.05, 0.0, 0.075], [0, 0, 5/100], 0.25/1000)

geom.boolean_fragments([box], [cyl1, cyl2])

with open("pecera.geo", "w") as text_file:
    text_file.write(geom.get_code())

#subprocess.run('gmsh -3 pecera.geo -format unv -bin -o pecera.unv', shell=True)

#os.remove('pecera.geo')
