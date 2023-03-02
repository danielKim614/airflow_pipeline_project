import os
import sys
import shutil

from datetime import datetime, timedelta
from airflow.decorators import dag
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.task_group import TaskGroup
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.models import Variable

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from case_sensor import CaseSensor
from util import *

log_path = os.path.join(r"/[$PATH]/log", "{}-project.log".format(datetime.now().date()))
logger = create_logger("project_log", log_path)

def _move_edge_case(context):
    case_path = context['task_instance'].xcom_pull(key="case_path")
    shutil.move(case_path, r"/[$PATH]/edge")


def _get_case_id(case_path, **context):
    Variable.set("case_id", os.path.basename(case_path))


def _check_A_dir(case_path, **context):
    A_dir_path = os.path.join(case_path, "A")
    if os.path.exists(A_dir_path):
        return A_dir_path
    else:
        logger.error("[111] - {} - No A directory!".format(Variable.get("case_id")))
        raise Exception("No A directory!")


def _get_all_path(case_path, **context):
    all_files = walk_sub_dir(case_path)
    return all_files


def _get_xml_path(case_path, **context):
    xml_files_path_list = search_file(case_path, ".xml")
    meta_data_path_list = exclude_keywords(xml_files_path_list, ["[keyword1]", "[keyword2]", "[keyword3]"])
    if len(meta_data_path_list) != 1:
        logger.warning("[720] - {} - Not a single metadata file!".format(Variable.get("case_id")))
        return None
    xml_path = meta_data_path_list.pop()
    return xml_path


def _get_A_path(A_dir_path, **context):
    A_path_dict = {}
    Aa_path, Ab_path = None, None
    
    Aa_dir_path = os.path.join(A_dir_path, "Aa")
    Ab_dir_path = os.path.join(A_dir_path, "Ab")

    if os.path.exists(Aa_dir_path):
        Aa_candidates_path = search_file(Aa_dir_path, ".stl")
        Aa_path = filter_A_by_priority(Aa_candidates_path)
    if os.path.exists(Ab_dir_path):
        Ab_candidates_path = search_file(Ab_dir_path, ".stl")
        Ab_path = filter_A_by_priority(Ab_candidates_path)

    if Aa_path is None and Ab_path is None:
        logger.error("[111] - {} - No a file!".format(Variable.get("case_id")))
        raise Exception("No A files!")
    elif Aa_path is None:
        A_path_dict["Ab"] = Ab_path
        logger.warning("[111] - {} - No Aa!".format(Variable.get("case_id")))
    elif Ab_path is None:
        A_path_dict["Aa"] = Aa_path
        logger.warning("[111] - {} - No Ab!".format(Variable.get("case_id")))
    else:
        A_path_dict["Aa"], A_path_dict["Ab"] = Aa_path, Ab_path

    return A_path_dict


def _get_B_info(xml_path, **context):
    B_info_dict = {}

    element_ids = get_property_tag_values_list_from_xml(xml_path, "[target_object]", "[target_property]")
    element_ids = list(set(element_ids)) # 중복제거
    
    root = parse_xml(xml_path)
    for element_id in element_ids:
        expr_id = f"[regular expression include {element_id}]"
        object = root.find(expr_id)

        word_with_number = get_property_value_from_xml_object(object, "[property_name]")

        target_path = get_property_value_from_xml_object(object, "[property_name]")
        abs_path = back_slash2slash(target_path)

        if abs_path == None or abs_path == '':
            logger.error("[310] - {} - No B file path! {}".format(Variable.get("case_id"), abs_path))
            continue
        
        B_info_dict[word_with_number] = abs_path
        
    return B_info_dict
    

def _get_B_path(case_path, **context):
    B_path_dict = {}
    B_info_dict = context['task_instance'].xcom_pull(task_ids='get_path.get_B_info')

    for item, sub_dir_path in B_info_dict.items():
        full_path = os.path.join(case_path, sub_dir_path)
        B_path_dict[item] = full_path

    return B_path_dict


def _check_B_path(**context):
    B_path_dict = context['task_instance'].xcom_pull(task_ids='get_path.get_B_path')
    
    tmp_B_path_dict = B_path_dict.copy()
    for item, B_path in tmp_B_path_dict.items():
        if not os.path.exists(B_path):
            del B_path_dict[item]
            logger.warning("[310] - {} - B path does not exist! {}".format(Variable.get("case_id"), B_path))

    return B_path_dict


def _get_C_path(**context):
    C_path_list = []
    all_path = context['task_instance'].xcom_pull(task_ids='get_case_info.get_all_path')

    for file_path in all_path:
        if file_path.endswith(".pts"):
            C_path_list.append(file_path)

    if len(C_path_list) == 0:
        logger.warning("[200] - {} - No C file! Also there will be no D.".format(Variable.get("case_id")))

    return C_path_list


def _get_D_path(**context):
    C_path_list = context['task_instance'].xcom_pull(task_ids='get_path.get_C_path')

    D_path_list = replace_str_in_list(C_path_list, ".[ext]", ".stl")

    return D_path_list


def _check_D_path(**context):
    D_path_list = context['task_instance'].xcom_pull(task_ids='get_path.get_D_path')

    tmp_D_path_list = D_path_list.copy()
    for D_path in tmp_D_path_list:
        if not os.path.exists(D_path):
            D_path_list.remove(D_path)
            logger.warning("[300] - {} - D path does not exist! {}".format(Variable.get("case_id"), D_path))

    return D_path_list


def _get_E_and_export(output_path, **context):
    case_id = Variable.get("case_id")
    A_path_dict = context['task_instance'].xcom_pull(task_ids='get_path.get_A_path')
    B_path_dict = context['task_instance'].xcom_pull(task_ids='get_path.get_B_path')
    C_path_list = context['task_instance'].xcom_pull(task_ids='get_path.get_C_path')
    D_path_list = context['task_instance'].xcom_pull(task_ids='get_path.get_D_path')

    A = {}
    B = {}
    C = {}
    D = {}
    E = {}

    # 1. Read B
    for item, B_path in B_path_dict.items():
        try:
            B[item] = read_mesh(B_path)
        except:
            logger.warning("[320] - {} - #{} B file is not readable!".format(case_id, item))

    # 2. Read A
    for A_type, A_path in A_path_dict.items():
        if A_path is not None:
            try:
                A[A_type] = read_mesh(A_path)
            except:
                logger.warning("[111] - {} - {} A file is not readable!".format(case_id, A_type))

    # 3. Combine A with B
    tmp_B = B.copy()
    for item, B_poly in tmp_B.items():
        num = extract_number(item)
        word = extract_word(item)
        if is_something(word):
            if is_in_Aa("num", num):
                try:
                    A["Aa"] = append_mesh(B_poly, A["Aa"])
                except:
                    logger.warning("[511] - {} - Failed to append something to A!".format(case_id))
                del B[item]

            elif is_in_Ab("num", num):
                try:
                    A["Ab"] = append_mesh(B_poly, A["Ab"])
                except:
                    logger.warning("[511] - {} - Failed to append something to A!".format(case_id))
                del B[item]
        else:
            B[num] = B[item]
            del B[item]
            
    # 4. Read C
    for C_path in C_path_list:
        try:
            C_dict = read_pts(C_path)
        except:
            logger.warning("[201] - {} - C file is not readable! {}".format(case_id, C_path))
        
        if C_dict != None:
            C_file_name = os.path.basename(C_path).replace(".pts", "")
            C[C_file_name] = C_dict
        else:
            logger.warning("[201] - {} - pts file is empty! {}".format(case_id, C_path))

    # 5. Read D
    for D_path in D_path_list:
        try:
            D_poly = read_mesh(D_path)
        except:
            logger.warning("[301] - {} - D file is not readable! {}".format(case_id, D_path))
        C_file_name = os.path.basename(D_path).replace(".stl", "")
        D[C_file_name] = D_poly

    # 6. Get Transform Landmarks
    for file_name, C_dict in C.items():
        tmp_false_num = list(C_dict.keys()).pop()
        for true_num, B_poly in B.items():
            if is_corresponding(true_num, tmp_false_num):
                D_poly = D[file_name]
                if is_same_num_of_points(D_poly, B_poly):
                    transform_matrix = get_landmark_transform_matrix(D_poly, B_poly)
                    for C_num, C_poly in C_dict.items():
                        E_poly = apply_transform_matrix(C_poly, transform_matrix)

                        # 7. Check E's Alignment with B
                        try:
                            if check_3_polys_matching_by_distance(B_poly, E_poly) == False:
                                raise Exception("B and E are not matching!")
                        except:
                            logger.warning("[621] - {} - #{} B and E are not matching!".format(case_id, num))
                        E[C_num] = E_poly
                    break

    # 8. Check E's Alignment with A
    for num, E_poly in E.items():
        try:
            if is_in_Aa("num", num):
                if check_3_polys_matching_by_distance(A["Aa"], E_poly) == False:
                    raise Exception("A and E are not matching!")
            elif is_in_Ab("num", num):
                if check_3_polys_matching_by_distance(A["Ab"], E_poly) == False:
                    raise Exception("A and E are not matching!")
        except:
            logger.warning("[411] - {} - A and #{} E are not matching!".format(case_id, num))

    # 9. Make Directory
    state = "normal"
    if len(B) == 0:
        output_path = os.path.join(output_path, "no_B")
        state = "no_B"
    elif len(E) == 0:
        output_path = os.path.join(output_path, "no_E")
        state = "no_E"
    else:
        output_path = os.path.join(output_path, "normal")

    dir_path_dict = construct_convention_dir(output_path, case_id, state)

    # 10. Export A
    for A_type, A in A.items():
        try:
            write_mesh(A, dir_path_dict["base_dir_path"], f"{A_type}.ply")
        except:
            logger.warning("[111] - {} - Failed to write {} A mesh!".format(case_id, A_type))

    # 11. Export B
    for num, B_poly in B.items():
        B_name = num + ".ply"
        try:
            write_mesh(B_poly, dir_path_dict["B_dir_path"], B_name)
        except:
            logger.warning("[311] - {} - Failed to write #{} B mesh!".format(case_id, num))

    # 12. Export E
    for num, E_poly in E.items():
        try:
            E_name = num + ".vtp"
            write_mesh(E_poly, dir_path_dict["E_dir_path"], E_name)
        except:
            logger.warning("[211] - {} - Failed to write #{} E mesh!".format(case_id, num))

    logger.info("[***] - {} - Convert Success.".format(case_id))


def _delete_input_case(case_path, **context):
    shutil.rmtree(case_path)


default_args = {
    "owner": "SeungkiKim",
    "description": "Transform A, B, E meshes which is aligned and log errors",
    "start_date": datetime(2023, 1, 1),
    "on_failure_callback": _move_edge_case,
}

with DAG(
    "three_shape_dag",
    default_args=default_args,
    catchup=False,
) as dag:
    
    case_sensor = CaseSensor(
        task_id='case_sensor',
        filepath=r'/[$PATH]/input',
        fs_conn_id='fs_default',
        poke_interval=5,
        timeout=10,
        dag=dag,
    )

    get_case_id = PythonOperator(
            task_id="get_case_id",
            python_callable=_get_case_id,
            op_kwargs={"case_path" : "{{ ti.xcom_pull(key='case_path') }}"},
            provide_context=True,
        )

    with TaskGroup("get_case_info") as get_case_info:
        check_A_dir = PythonOperator(
            task_id="check_scans_dir",
            python_callable=_check_A_dir,
            op_kwargs={"case_path" : "{{ ti.xcom_pull(key='case_path') }}"},
            provide_context=True,
        )


        get_all_path = PythonOperator(
            task_id="get_all_path",
            python_callable=_get_all_path,
            op_kwargs={"case_path" : "{{ ti.xcom_pull(key='case_path') }}"},
            provide_context=True,
        )

        get_xml_path = PythonOperator(
            task_id="get_xml_path",
            python_callable=_get_xml_path,
            op_kwargs={"case_path" : "{{ ti.xcom_pull(key='case_path') }}"},
            provide_context=True,
        )

    with TaskGroup("get_path") as get_path:
        get_B_info = PythonOperator(
            task_id="get_B_info",
            python_callable=_get_B_info,
            op_kwargs={"xml_path" : "{{ ti.xcom_pull(task_ids='get_case_info.get_xml_path') }}"},
            provide_context=True,
        )
        
        get_B_path = PythonOperator(
            task_id="get_B_path",
            python_callable=_get_B_path,
            op_kwargs={"case_path" : "{{ ti.xcom_pull(key='case_path') }}"},
            provide_context=True,
        )

        check_B_path = PythonOperator(
            task_id="check_B_path",
            python_callable=_check_B_path,
            provide_context=True,
        )

        get_A_path = PythonOperator(
            task_id="get_A_path",
            python_callable=_get_A_path,
            op_kwargs={"scan_dir_path" : "{{ ti.xcom_pull(task_ids='get_case_info.check_scans_dir') }}"},
            provide_context=True,
        )

        get_C_path = PythonOperator(
            task_id="get_C_path",
            python_callable=_get_C_path,
            provide_context=True,
        )

        get_D_path = PythonOperator(
            task_id="get_D_path",
            python_callable=_get_D_path,
            op_kwargs={"case_path" : "{{ ti.xcom_pull(key='case_path') }}"},
            provide_context=True,
        )

        check_D_path = PythonOperator(
            task_id="check_D_path",
            python_callable=_check_D_path,
            provide_context=True,
        )

        
    get_E_and_export = PythonOperator(
        task_id="get_E_and_export",
        python_callable=_get_E_and_export,
        op_kwargs= {"output_path" : r"//[$PATH]/output"},
        provide_context=True,
    )

    delete_input_case = PythonOperator(
        task_id="delete_input_case",
        python_callable=_delete_input_case,
        op_kwargs={"case_path" : "{{ ti.xcom_pull(key='case_path') }}"},
        provide_context=True,
    )
    
    call_trigger = TriggerDagRunOperator(
        task_id="call_trigger",
        trigger_dag_id="three_shape_dag",
        trigger_rule='all_done',
        dag=dag,
    )

    check_A_dir >> [get_all_path, get_xml_path]
    get_A_path >> [get_B_info, get_C_path]
    get_C_path >> get_D_path >> check_D_path
    get_B_info >> get_B_path >> check_B_path
    case_sensor >> get_case_id >> get_case_info >> get_path >> get_E_and_export >> delete_input_case >> call_trigger
