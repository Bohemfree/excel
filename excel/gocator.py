# -*- coding: utf-8 -*-

"""IMU 파일의 interval 을 기준으로 csv 중간 column의 데이터 값과 Z_Acc 값 정리
        저장파일 포멧 : .raw
        [Laser,Acceleration,TriggerInfo,FlagIndex,Section]
        Laser: csv 파일은 5mm 간격
        Acceleration: EBIMU_9DOFV5 파일의 Accelero_Z(g) 데이터
        TriggerInfo: 0
        FlagIndex: 0
        Section: 0
"""

import pandas as pd
import os
import glob
import natsort
import sys
import numpy as np

from file import rawfile
sys.path.append(os.path.dirname(os.path.dirname(__file__)))


def acc_interval(anal_path: str, acc_intervals: list, use_indiviual_interval: bool = False):
    """Acceleration_Z(g)의 interval을 기준으로 laser 데이터 값 정리하여 raw 파일로 저장하는 함수
    Args:
        anal_path: 조사경로(e.g: D:/dataset/조사1), .krs 파일 경로의 상위 경로
        acc_intervals: raw 파일에 저장할 acc_interval 간격, 지정안하면, 50mm 기준

    :return: None
    """

    result_path = os.path.join(anal_path, 'rawfile_results')
    os.makedirs(result_path, exist_ok=True)

    gocator_paths = glob.glob(anal_path + r'\*\*_Gocator_v7\*')
    imu_paths = glob.glob(anal_path + r'\*\*IMU')

    if not imu_paths:
        sys.exit('IMU 폴더가 존재하지 않습니다.')
    if not gocator_paths:
        sys.exit('Gocator_v7 폴더가 존재하지 않습니다.')

    for gocator_index, gocator_path in enumerate(gocator_paths):
        # Rawfile path 지정
        anal_name = os.path.basename(os.path.dirname(gocator_path))
        sensor_location = os.path.basename(gocator_path)
        rawfile_path = os.path.join(result_path, (anal_name + '_' + sensor_location + '.raw'))
        print(fr"{anal_name + '_' + sensor_location} 진행중.... {gocator_index + 1}/{len(gocator_paths)}")

        csv_files = glob.glob(gocator_path + r'\*Profile\*.csv')
        imu_file = glob.glob(imu_paths[gocator_index] + fr'\*{os.path.basename(gocator_path)}.txt')
        if not csv_files:
            sys.exit('csv 파일이 존재하지 않습니다.')
        if not imu_file:
            sys.exit('IMU 파일이 존재하지 않습니다.')

        csv_files = natsort.natsorted(csv_files)

        # Read imu file's "Accelero_Z(g)" column
        imu_df = pd.read_csv(imu_file[0], usecols=[6])
        csv_df = pd.DataFrame()
        for csv_file in csv_files:
            csv_df = csv_df.append(pd.read_csv(csv_file, header=None, usecols=[2999]))

        rawfile_class = rawfile.RawFile(
            file_path=rawfile_path, csv_df=csv_df, imu_df=imu_df, interval=acc_intervals[gocator_index])
        rawfile_class.write_rawfile(use_indiviual_interval)


if __name__ == "__main__":
    # 10km/h, 20km/h, 30km/h, 40km/h, 50km/h (mm)
    intervals = [2.778, 5.5, 8.3, 11.1, 13.8]
    input_path = r'D:\data\20221206_gocator교정데이터'

    # km/h 별 interval 적용
    acc_interval(anal_path=input_path, acc_intervals=intervals, use_individual_interval=False)
    # interval 50mm 고정
    # acc_interval(anal_path=input_path, acc_intervals=intervals, use_indiviual_interval=False)
