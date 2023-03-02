import vtk
import numpy as np
from vtkmodules.util.numpy_support import numpy_to_vtk, vtk_to_numpy, numpy_to_vtkIdTypeArray

def np_array2vtk_points(np_points):
    vtk_points = numpy_to_vtk(np_points)
    points = vtk.vtkPoints()
    points.SetData(vtk_points)

    return points


def vtk_points2vtk_poly_data(vtk_points) -> vtk.vtkPolyData:
    verices = vtk.vtkCellArray()
    for pid in range(vtk_points.GetNumberOfPoints()):
        verices.InsertNextCell(1)
        verices.InsertCellPoint(pid)

    poly_data = vtk.vtkPolyData()
    poly_data.SetPoints(vtk_points)
    poly_data.SetVerts(verices)

    return poly_data


def np_array2vtk_matrix(np_array):
    vtk_matrix = vtk.vtkMatrix4x4()
    for row in range(4):
        for col in range(4):
            vtk_matrix.SetElement(row, col, np_array[row, col])

    return vtk_matrix


def vtk_points2np_array(vtk_poly_data):

    return vtk_to_numpy(vtk_poly_data.GetPoints().GetData())
