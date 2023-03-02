import os
import sys
import vtk
import json
import numpy as np
import re
from .vtk_numpy import np_array2vtk_points, vtk_points2vtk_poly_data

def read_pts(pts_path):
    with open(pts_path, 'r') as f:
        pts_file = f.readlines()

    if len(pts_file) == 0:
        return None

    np_margin_points = np.empty([0, 3])
    pattern = re.compile('\d[-\d]*')
    pts_margin_points = {}
    for line in pts_file:
        if len(line.split(' ')) == 3:
            np_margin_point = np.fromstring(line, sep=' ')
            np_margin_points = np.vstack([np_margin_points, np_margin_point])
        else:
            # Universal Numbering System
            num = pattern.search(line).group() # str
            pts_margin_points[num] = np_margin_points
            np_margin_points = np.empty([0, 3])
            continue

    pts_poly_data_dict = {}
    for num, np_points in pts_margin_points.items():
        vtk_points = np_array2vtk_points(np_points)
        vtk_polydata = vtk_points2vtk_poly_data(vtk_points)
        pts_poly_data_dict[num] = vtk_polydata
    
    return pts_poly_data_dict


def read_mesh(path):
    if not os.path.exists(path):
        raise Exception("File does not exists")

    ext = os.path.splitext(path)[1]
    if ext==".vtp":
        reader = vtk.vtkXMLPolyDataReader()
    elif ext==".stl":
        reader = vtk.vtkSTLReader()
    elif ext==".ply":
        reader = vtk.vtkPLYReader()
    elif ext==".obj":
        reader = vtk.vtkOBJReader()
    else:
        return None

    reader.SetFileName(path)
    reader.Update()
    
    return reader.GetOutput()


def write_mesh(poly_data, path, save_name, exist_ok=True):
    ext = os.path.splitext(save_name)[1]
    
    if ext==".vtp":
        writer = vtk.vtkXMLPolyDataWriter()
    elif ext==".stl":
        writer = vtk.vtkSTLWriter()
    elif ext==".ply":
        writer = vtk.vtkPLYWriter()
    elif ext==".obj":
        writer = vtk.vtkOBJWriter()
    else:
        raise Exception("{} is not supported".foramt(ext))

    save_path = os.path.join(path, save_name)
    if os.path.exists(save_path) and not exist_ok:
        raise Exception("{save_name} exist on {}".foramt(save_path, path))

    else:
        os.makedirs(path, exist_ok=True)

    writer.SetInputData(poly_data)
    writer.SetFileName(save_path)
    writer.Update()
