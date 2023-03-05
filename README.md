# Airflow Pipeline Project
## Introduction
- 이 프로젝트는 airflow를 사용하여 3D 데이터의 변환부터 적재까지를 다룬 파이프라인입니다.<br/>
- 서로 같은 두 mesh 데이터의 landmark를 구하여 다른 mesh 데이터에 이를 적용하여, 필요한 데이터를 export하는 것이 최종 목표입니다.
- 자세한 로직은 대외비이기 때문에 익명화하였습니다. (A-E 알파벳으로 표현 및 [ ]로 표현)
## Environments
- Ubuntu 20.04.5 LTS
- CPU : 12th Gen Intel(R) Core(TM) i7-12700
- RAM : 16GB

## Get started
1. Install miniconda on Linux System.
```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
&& sh Miniconda3-latest-Linux-x86_64.sh
```

2. Install Airflow on Linux System.
```bash
pip install apache-airflow
```

3. Install vtk package on miniconda.
```bash
pip install vtk
```
## Build and Test
1. Set airflow.cfg file.
    - $PATH = /airflow/airflow.cfg
    - dags_folder -> {_directory path for airflow dags_}
    - executor -> localexecutor

2.	Fix path about input, output, log, and edge case.
3.	Run airflow
    - Webserver
    - Scheduler
4. Input data in airflow's input directory which user set

## Contribute
- vtk_python을 제외하고는 직접 구현한 모듈입니다.
- 기존에 제공된 vtk_python 디렉토리의 모듈에서도 추가로 몇 가지 함수를 추가하였습니다.
- TODO
    - Refactoring Code
