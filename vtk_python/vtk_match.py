import vtk
import numpy as np
from .vtk_io import *
from .vtk_numpy import *
from vtk_python.vtk_pure import *
from vtkmodules.vtkFiltersModeling import vtkOutlineFilter

def get_threedatapoints_numpy_array(mesh):
    numpy_array = vtk_to_numpy(mesh.GetPoints().GetData())
    numpy_array_length = numpy_array.shape[0]
    numpy_array_chunk_length = numpy_array_length//3
    threedatapoints_numpy_array = np.array([numpy_array[i*numpy_array_chunk_length ] for i in range(0,3)])
    return threedatapoints_numpy_array


def distance_3_polys_matching(poly_data, true_margin_poly) : 
    true_margin_numpy_array = get_threedatapoints_numpy_array(true_margin_poly)
    distance_list = [] 
    for data_point in true_margin_numpy_array:
        # true_margin_vtk_point = np_array2vtk_points(data_point)
        closest_points = get_closest_n_points(poly_data, data_point, N=1)
        distance = vtk.vtkMath.Distance2BetweenPoints(data_point, closest_points[0])
        distance_list.append(distance)
    return distance_list


def check_3_polys_matching_by_distance(poly_data, true_margin_poly) : 
    distance_list = distance_3_polys_matching(poly_data, true_margin_poly)
    for distance in distance_list:
        if distance > 0.15 :
            return False
    return True


def apply_transform_matrix(polydata, tf):
    transformFilter = vtk.vtkTransformPolyDataFilter()
    transformFilter.SetInputData(polydata)
    transformFilter.SetTransform(tf)
    transformFilter.Update()
    return transformFilter.GetOutput()
