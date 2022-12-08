# -*- coding: utf-8 -*-
import pandas as pd
import os
import glob
import natsort
import sys
import numpy as np

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from file import rawfile

if __name__ == "__main__":
    """IMU 파일의 interval 을 기준으로 csv 중간 column의 데이터 값과 Z_Acc 값 정리 
        저장파일 포멧 : .raw
        [Laser,Acceleration,TriggerInfo,FlagIndex,Section]
        Laser: csv 파일은 5mm 간격
        Acceleration: EBIMU_9DOFV5 파일의 Accelero_Z(g) 데이터
        TriggerInfo: 0
        FlagIndex: 0
        Section: 0
    """

    # 10km/h, 20km/h, 30km/h, 40km/h, 50km/h (mm)
    intervals = [2.7, 5.5, 8.3, 11.1, 13.8]
    anal_path = r'D:\data\20221206_gocator교정데이터'
    result_path = os.path.join(anal_path, 'rawfile_results')
    os.makedirs(result_path, exist_ok=True)

    gocator_paths = glob.glob(anal_path + r'\*\*_Gocator_v7\*')
    imu_paths = glob.glob(anal_path + r'\*\*IMU')

    if not imu_paths:
        sys.exit('IMU 폴더가 존재하지 않습니다.')
    if not gocator_paths:
        sys.exit('Gocator_v7 폴더가 존재하지 않습니다.')

    for interval, gocator_path, imu_path in zip(intervals, gocator_paths, imu_paths):
        csv_files = glob.glob(gocator_path + r'\*Profile\*.csv')
        imu_file = glob.glob(imu_path + fr'\*{os.path.basename(gocator_path)}.txt')
        csv_files = natsort.natsorted(csv_files)[:10]

        # Read imu file's "Accelero_Z(g)" column
        imu_df = pd.read_csv(imu_file[0], usecols=[6])
        csv_df = pd.DataFrame()
        for csv_file in csv_files:
            csv_df = csv_df.append(pd.read_csv(csv_files[0], header=None, usecols=[2999]))

        # Rawfile path 지정
        anal_name = os.path.basename(os.path.dirname(gocator_path))
        sensor_location = os.path.basename(gocator_path)
        rawfile_path = os.path.join(result_path, (anal_name + '_' + sensor_location + '.raw'))
        rawfile.RawFile(rawfile_path)

        raw_file = open(rawfile_path, "a")
        csv_index = 0
        imu_index = 0
        TriggerInfo_index = 1

        while True:  # [mm], 100m 초과 시 종료
            if imu_index == 0:
                raw_file.write(f'{csv_df.values[csv_index][0]},{imu_df.values[imu_index][0]},0,0,0\n')
                csv_index += 1
                imu_index += 1
                continue

            imu_distance = imu_index * interval  # [mm]
            csv_distance = csv_index * 5  # [mm]
            diff = csv_distance - imu_distance

            if imu_distance > 100000:
                break

            if TriggerInfo_index == 9:
                TriggerInfo_index = 0

            if diff < -3.5:
                csv_index += 1
                continue
            elif -3.5 <= diff < -1.5:
                raw_file.write(f'{round(np.mean(csv_df.values[csv_index-1:csv_index+1]), 4)},{imu_df.values[imu_index][0]},{TriggerInfo_index},0,0\n')
            elif -1.5 <= diff < 0:
                raw_file.write(f'{csv_df.values[csv_index][0]},{imu_df.values[imu_index][0]},{TriggerInfo_index},0,0\n')
            elif 0 <= diff <= 1.5 and csv_index < 20000:
                raw_file.write(f'{csv_df.values[csv_index][0]},{imu_df.values[imu_index][0]},{TriggerInfo_index},0,0\n')
            elif 1.5 < diff <= 3.5:
                raw_file.write(f'{round(np.mean(csv_df.values[csv_index:csv_index+2]), 4)},{imu_df.values[imu_index][0]},{TriggerInfo_index},0,0\n')
            elif 3.5 < diff:
                csv_index -= 1
                continue

            imu_index += 1
            csv_index += 1
            TriggerInfo_index += 1

        raw_file.close()
