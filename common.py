import os
import xml.etree.ElementTree as ET
import logging
import shutil

def back_slash2slash(path):
    
    return path.replace('\\', '/')

def search_file(dir_path, name):
    full_file_names = []
    file_names = os.listdir(dir_path)
    for file_name in file_names:
        if file_name.endswith(name):
            full_filename = os.path.join(dir_path, file_name)
            full_file_names.append(full_filename)

    return full_file_names

def walk_sub_dir(dir_path):
    all_file_paths = []
    for root, dirs, files in os.walk(dir_path):
      all_file_paths += list(map(lambda x: back_slash2slash(os.path.join(root, x)), files))

    return all_file_paths

def get_sub_dir_files_paths(dir_path):
    all_paths = {}
    all_file_paths, all_dir_paths = [], []
    for root, dirs, files in os.walk(dir_path):
        all_file_paths += list(map(lambda x: os.path.join(root, x), files))
        all_dir_paths += list(map(lambda x: os.path.join(root, x), dirs))

    all_paths["files"] = all_file_paths
    all_paths["dirs"] = all_dir_paths

    return all_paths


def include_keywords(input_list, keywords):
    output_list = []
    for target in input_list:
        for keyword in keywords:
            if keyword in target:
                output_list.append(target)
                break

    return output_list


def exclude_keywords(input_list, keywords):
    output_list = input_list.copy()
    for target in input_list:
        for keyword in keywords:
            if keyword in target:
                output_list.remove(target)
                break

    return output_list


def replace_str_in_list(input_list, old_str, new_str):
    output_list = []
    for target in input_list:
        output_list.append(target.replace(old_str, new_str))

    return output_list


def replace_str_in_dic_value(input_dic, old_str, new_str):
    output_dic = {}
    for key, value in input_dic.items():
        output_dic[key] = value.replace(old_str, new_str)

    return output_dic


def parse_xml(xml_path):
    if xml_path is None:
        raise Exception(".xml does not exist!")

    tree = ET.parse(xml_path)
    root = tree.getroot()

    return root

def create_logger(log_name, log_path):
    logger = logging.getLogger(log_name)
    logger.setLevel(logging.INFO)
    handler = logging.FileHandler(log_path)
    handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger