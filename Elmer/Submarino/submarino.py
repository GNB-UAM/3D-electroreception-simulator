import pygmsh,subprocess,os,json,argparse
import numpy as np
import pandas as pd

parser = argparse.ArgumentParser()
parser.add_argument('--mesh', '-m', action='store_true', help='genera el mesh con nombre `0.unv`')
parser.add_argument('--render', '-r', action='store_true', help='quita la pecera para poder ver el submarino mejor')
args = parser.parse_args()

class Submarino():
  def __init__(self, conf, uid=0, open_gmsh=False):
    self.conf = conf
    self.open_gmsh = open_gmsh
    self.file_name = uid
    self.sim_folder = f'sim_{uid}'

    self.parts = []
    self.geom = pygmsh.opencascade.Geometry(
      characteristic_length_min=conf['mesh.min'],
      characteristic_length_max=conf['mesh.max'],
    )

    self._create_geo()

    if open_gmsh:
      self._open_gmsh()
      os.remove(f'{self.file_name}.geo')

  def _get_vector(self, key):
    return np.array([self.conf[f'{key}.x'], self.conf[f'{key}.y'], self.conf[f'{key}.z']])

  def _open_gmsh(self):
    subprocess.run(f'gmsh {self.file_name}.geo', shell=True)

  def _construir_submarino(self):
    self.parts.append(self.geom.add_ball([0,0,0], self.conf['radio'], x0=0))

    self.parts.append(self.geom.add_cylinder([0,0,0], [0,0,-self.conf['altura_cuerpo']], self.conf['radio']))

    def construir_bateria(mirror=False):
      return self.geom.add_cylinder([-self.conf['baterias.longitud']/2, (self.conf['radio'] if not mirror else -self.conf['radio'])*0.6,-(self.conf['altura_cuerpo'] + self.conf['baterias.radio'])], [self.conf['baterias.longitud'],0,0], self.conf['baterias.radio'])

    # camara
    #self.parts.append(self.geom.add_cylinder([self.conf['radio'],-self.conf['camara.longitud']/2,-self.conf['camara.longitud']/2], [0,self.conf['camara.longitud'],0], self.conf['camara.radio']))

    def rotate_geom(parts, ang):
      for part in parts:
        self.geom.rotate(part, self._get_vector('posicion'), np.radians(ang), [0,0,1])

    def move_geom(parts, pos):
      for part in parts:
        self.geom.translate(part, pos)
      
    def construir_sensor(angulo, mirror=False):
      if mirror:
        angulo = -angulo

      pos_x = np.cos(np.radians(angulo)) * self.conf['radio']
      pos_y = np.sin(np.radians(angulo)) * self.conf['radio']
      pos_z = self.conf['sensor.altura']

      sensor_pos = [pos_x, pos_y, pos_z]

      sensor = self.geom.add_ball(sensor_pos, self.conf['sensor.radio'])
      self.geom.rotate(sensor, sensor_pos, np.radians(angulo), [0,0,1])
      self.geom.rotate(sensor, [0,0,0], np.radians(self.conf['sensor.rotacion']), [0,0,1])
      return sensor

    ang_sep = self.conf['sensor.angulo_separacion'] / 2
    self.parts.append(construir_sensor(ang_sep))
    self.parts.append(construir_sensor(ang_sep, mirror=True))

    move_geom(self.parts, self._get_vector('posicion'))

    rotate_geom(self.parts, self.conf['rotacion'])

  def _create_geo(self):
    self._construir_submarino()

    piscina = self.geom.add_box(-self._get_vector('piscina_dim')/2, self._get_vector('piscina_dim'))
    if args.render:
      self.geom.boolean_intersection([piscina, *self.parts])
      self.geom.add_raw_code('Transfinite Line {21, 9, 8, 10, 6, 16, 5, 7} = %d Using Progression 1;' % self.conf['mesh.refinamiento_mesh_esferas'])
    else:
      self.geom.boolean_difference([piscina], self.parts)
      self.geom.add_raw_code('Transfinite Line {50, 58, 49, 51, 46, 53, 47, 48} = %d Using Progression 1;' % self.conf['mesh.refinamiento_mesh_esferas'])


    with open(f'{self.file_name}.geo', 'w') as text_file:
      text_file.write(self.geom.get_code())

    return self

  def meshear(self):
    subprocess.run(f'gmsh -v 0 -3 {self.file_name}.geo -format msh -o {self.file_name}.msh', shell=True)
    os.remove(f'{self.file_name}.geo')

if __name__ == "__main__":
  with open('conf.json') as conf:
    conf = json.load(conf)
    conf = pd.json_normalize(conf, sep='.').to_dict(orient='records')[0]
    conf = {'.'.join(k.split('.')[1:]): v for k, v in conf.items() if k.startswith('submarino')}
    
    if args.mesh:
      Submarino(conf).meshear()
    else:
      Submarino(conf, open_gmsh=True)