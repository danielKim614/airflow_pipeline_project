import vtk
import numpy as np
from .vtk_io import *
from .vtk_numpy import *
from vtkmodules.vtkFiltersModeling import vtkOutlineFilter

def append_mesh(src, dst) -> vtk.vtkPolyData:
    vtk_append = vtk.vtkAppendPolyData()
    vtk_append.AddInputData(src)
    vtk_append.AddInputData(dst)
    vtk_append.Update()
    
    return vtk_append.GetOutput()


def get_landmark_transform_matrix(src, dst):
    landmarkTransform = vtk.vtkLandmarkTransform()
    landmarkTransform.SetModeToRigidBody()
    landmarkTransform.SetSourceLandmarks(src.GetPoints())
    landmarkTransform.SetTargetLandmarks(dst.GetPoints())
    landmarkTransform.Modified()
    landmarkTransform.Update()

    return landmarkTransform


def get_closest_point_index_within_radius(mesh, point, radius=0.15) :
    """
    Default `radius` is contact distance. 0.15 is approximate
    If return value is -1, point does not exist within radius

    `vtkPointLocator()` can be replaced `vtkKdTree()`. (Same result)
    """
    locator = vtk.vtkPointLocator()
    locator.SetDataSet(mesh)
    locator.BuildLocator()

    distance = vtk.mutable(0.0)
    pid = locator.FindClosestPointWithinRadius(radius, point, distance)

    return pid


def get_closest_n_points(src, point, N=1):
    point_tree = vtk.vtkKdTree()
    point_tree.BuildLocatorFromPoints(src.GetPoints())

    closest_point_index_vtk = vtk.vtkIdList()
    point_tree.FindClosestNPoints(N, point, closest_point_index_vtk)

    closest_points = []
    for i in range(closest_point_index_vtk.GetNumberOfIds()):
        point_id = closest_point_index_vtk.GetId(i)
        closest_point = src.GetPoint(point_id)
        closest_points.append(closest_point)
        
    return closest_points


def numpy_matrix2vtk_matrix(numpyMatrix):
    vtkMatrix = vtk.vtkMatrix4x4()
    for i in range(4):
        for j in range(4):
            vtkMatrix.SetElement(i, j, numpyMatrix[i, j])

    return vtkMatrix


def set_transform_matrix(vtkMatrix : list):
    transform = vtk.vtkTransform()   
    for matrix in vtkMatrix:
        if matrix == None:
            matrix = vtk.vtkMatrix4x4()
        matrix.Invert()
        transform.Concatenate(matrix)
    transform.Update()

    return transform


def vtk_poly_data2xml_string(poly_data) : 
    writer = vtk.vtkXMLPolyDataWriter()
    writer.SetInputData(poly_data) 
    writer.WriteToOutputStringOn()
    writer.Update()

    return writer.GetOutputString()


def xml_string2vtk_poly_data(xml_string_obj):
    reader = vtk.vtkXMLPolyDataReader()
    reader.ReadFromInputStringOn()
    reader.SetInputString(xml_string_obj)
    reader.Update()

    return reader.GetOutput()