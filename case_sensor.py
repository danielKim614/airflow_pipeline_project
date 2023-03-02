import datetime
import os
from glob import glob
from typing import Sequence

from airflow.hooks.filesystem import FSHook
from airflow.sensors.base import BaseSensorOperator
from airflow.utils.context import Context


class CaseSensor(BaseSensorOperator):
    template_fields: Sequence[str] = ("filepath",)
    ui_color = "#91818a"

    def __init__(self, *, filepath, fs_conn_id="fs_default", recursive=False, **kwargs):
        super().__init__(**kwargs)
        self.filepath = filepath
        self.fs_conn_id = fs_conn_id
        self.recursive = recursive

    def poke(self, context: Context):
        hook = FSHook(self.fs_conn_id)
        basepath = hook.get_path()
        full_path = os.path.join(basepath, self.filepath)
        self.log.info("Poking for file %s", full_path)

        for path in glob(full_path, recursive=self.recursive):
            new_case_list = os.listdir(path)
            if new_case_list != []:
                case_id = new_case_list[0]
                path = os.path.join(path, case_id)
                if os.path.isdir(path):
                    mod_time = datetime.datetime.fromtimestamp(os.path.getmtime(path)).strftime("%Y%m%d%H%M%S")
                    self.log.info("Found File %s last modified: %s", str(path), mod_time)
                    self.xcom_push(context, key="case_path", value=path)
                    return True
                return False
            for _, _, files in os.walk(path):
                if len(files) > 0:
                    return True
                
        return False