import numpy as np
import vtk
from vtk.util.numpy_support import vtk_to_numpy

# The source file
file_name = "case_t0001.vtu"

# Read the source file.
reader = vtk.vtkXMLUnstructuredGridReader()
reader.SetFileName(file_name)
reader.Update()  # Needed because of GetScalarRange
output = reader.GetOutput()
potential = output.GetPointData().GetArray("potential")

volts_array = vtk_to_numpy(potential)

print(volts_array.shape)

print(f'Max Voltage: {volts_array.max()}V     Min Voltage: {volts_array.min()}V')