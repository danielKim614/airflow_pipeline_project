import re

from vtk_python import *
from common import *

def filter_A_by_priority(A_candidates_list):
    priority_list = []
    for A_candidate in A_candidates_list:
        priority = 0
        if "[word1]" in A_candidate.lower():
            priority += -1
        elif "[word2]" in A_candidate:
            priority += 1
        elif "[word3]" in A_candidate:
            priority += 2
        elif (
            "[word4]" in A_candidate.lower()
            or "[word5]" in A_candidate.lower()
        ):
            priority += 3
        elif "[word6]" in A_candidate.lower():
            priority += 4
        priority_list.append(priority)

    max_priority = max(priority_list)
    if max_priority == -1:
        return None
    else:
        max_priority_index = priority_list.index(max_priority)
        A = A_candidates_list[max_priority_index]

    return A


def get_tag_contents_from_xml(xml_path, tag_name):
    tag_contents = []
    root = parse_xml(xml_path)
    target_tags = root.findall(".//{}".format(tag_name))
    for target_tag in target_tags:
        tag_contents.append(target_tag.text)
    return tag_contents


def get_property_tag_values_list_from_xml(xml_path, target_object, target_property):
    tag_attributes = []
    object_format = ".//Object[@type='{}']".format(target_object)
    attribute_format = ".//Property[@name='{}']".format(target_property)

    root = parse_xml(xml_path)
    for _object in root.findall(object_format):
        value = _object.find(attribute_format).get("value")
        tag_attributes.append(value)

    return tag_attributes


def get_property_value_from_xml_object(xml_object, property_name):
    expr = ".//Property[@name='{}']".format(property_name)
    property_tag = xml_object.find(expr)
    if property_tag is None:
        return None
    else:
        return property_tag.get("value")


def is_in_Aa(**kwargs):
    # Confidentiality Logic
    pass
    return


def is_in_Ab(**kwargs):
    # Confidentiality Logic
    pass
    return
    

def is_something(type):
    something_notation_list = [
        "[notation1]",
        "[notation2]",
    ]
    if type in something_notation_list:
        return True
    
    else:
        return False


def is_corresponding(**kwargs):
    # Confidentiality Logic
    pass
    return


def is_same_num_of_points(poly1, poly2):
    num_of_points1 = poly1.GetNumberOfPoints()
    num_of_points2 = poly2.GetNumberOfPoints()
    if num_of_points1 == num_of_points2:
        return True
    else:
        return False


def extract_number(item_name):
    pattern = re.compile("[0-9]+(-[0-9]+)?")
    number = pattern.search(item_name).group()

    return number


def extract_word(item_name):
    pattern = re.compile("[^0-9]+")
    type = pattern.search(item_name).group()
    # FIXME: 임시방편
    type = type[:-1]

    return type


def construct_convention_dir(output_path, case_id, state="normal"):
    dir_paths = {}
    case_id_dir_path = os.path.join(output_path, case_id)
    dir_paths["case_id_dir_path"] = case_id_dir_path
    dir_paths["A_dir_path"] = os.path.join(case_id_dir_path, "A")

    if state == "no_B":
        pass
    
    elif state == "no_margin":
        dir_paths["B_dir_path"] = os.path.join(case_id_dir_path, "B")

    elif state == "normal":
        dir_paths["B_dir_path"] = os.path.join(case_id_dir_path, "B")
        dir_paths["E_dir_path"] = os.path.join(case_id_dir_path, "E")

    if os.path.exists(case_id_dir_path):
        shutil.rmtree(case_id_dir_path)

    for dir_path in dir_paths.values():
        os.mkdir(dir_path)
    
    return dir_paths

'''
There were some functions for Confidentiality Logic ...
'''