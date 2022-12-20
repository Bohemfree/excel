import numpy as np


class RawFile:
    def __init__(
            self, file_path: str, csv_df: np.array, imu_df: np.array, interval: int):
        """Read & Write rawfile

        :param file_path: raw format file path
        :param csv_df: DataFrame, csv file(only laser data, [5mm])
        :param imu_df: DataFrame, imu file(only Acc_Z, imu data, [individual interval])
        :param interval: Imu data's interval
        """
        # init parameters
        self.file_path = file_path
        self.csv_df = csv_df
        self.imu_df = imu_df
        self.interval = interval

        self.csv_index = 0
        self.imu_index = 0
        self.trigger_info_index = 1

        self.max_csv_df = len(csv_df) * 5
        self.max_imu_df = len(imu_df) * self.interval

        # Writing raw file
        with open(self.file_path, "w") as file:
            file.write('RTSensorRaw\n')
            file.write('File Version,4\n')
            file.write('Interval[mm],50\n')
            file.write('ValueCount,1\n')
            file.write('VarType,US,US,SI,SI,US\n')
            file.write('Laser,Acceleration,TriggerInfo,FlagIndex,Section\n')

    def find_diff(self):
        imu_distance = self.imu_index * self.interval  # [mm]
        csv_distance = self.csv_index * 5  # [mm]
        return csv_distance - imu_distance

    def individual_interval(self, raw_file):
        """Writing rawfile contents in while loop with individual intervals

        :param raw_file: File for writing contents(opened)
        :return: bool, False: continue external while loop
        """
        diff = self.find_diff()
        if diff < -3.5:
            self.csv_index += 1
            return False
        elif -3.5 <= diff < -1.5:
            raw_file.write(
                f'{round(np.mean(self.csv_df.values[self.csv_index - 1:self.csv_index + 1]), 4)},'
                f'{self.imu_df.values[self.imu_index][0]},{self.trigger_info_index},0,0\n')
        elif -1.5 <= diff < 0:
            raw_file.write(
                f'{self.csv_df.values[self.csv_index][0]},'
                f'{self.imu_df.values[self.imu_index][0]},{self.trigger_info_index},0,0\n')
        elif 0 <= diff <= 1.5 and self.csv_index < 20000:
            raw_file.write(
                f'{self.csv_df.values[self.csv_index][0]},'
                f'{self.imu_df.values[self.imu_index][0]},{self.trigger_info_index},0,0\n')
        elif 1.5 < diff <= 3.5:
            raw_file.write(
                f'{round(np.mean(self.csv_df.values[self.csv_index:self.csv_index + 2]), 4)},'
                f'{self.imu_df.values[self.imu_index][0]},{self.trigger_info_index},0,0\n')
        elif 3.5 < diff:
            self.csv_index -= 1
            return False
        self.csv_index += 1
        return True

    def fixed_interval(self, raw_file):
        """Writing rawfile contents in while loop with fixed interval[50mm]
        50mm의 laser data interval 마다 값 저장

        :param raw_file: File for writing contents(opened)
        :return: bool, False: continue external while loop
        """
        while abs(self.find_diff()) > self.interval:
            self.imu_index += 1

        if (self.csv_index * 5 >= self.max_csv_df) or ((self.imu_index * self.interval) >= self.max_imu_df):
            return False

        ex_diff = abs(self.find_diff() - 1)
        if self.imu_index != len(self.imu_df.values):
            self.imu_index += 1
        current_diff = abs(self.find_diff() - 1)

        if ex_diff <= current_diff:
            imu_index = self.imu_index - 1
        else:
            imu_index = self.imu_index

        raw_file.write(
            f'{self.csv_df.values[self.csv_index][0]},'
            f'{self.imu_df.values[imu_index][0]},{self.trigger_info_index},0,0\n')
        # print(fr"index:{imu_index}, distance:{imu_index * self.interval}")
        self.csv_index += 10
        return True

    def write_rawfile(self, use_individual_interval: bool):
        """Writing rawfile mother function

        :param use_individual_interval: bool
        :return:
        """
        raw_file = open(self.file_path, "a")
        while True:  # [mm]
            if (self.csv_index * 5 >= self.max_csv_df) or ((self.imu_index * self.interval) >= self.max_imu_df):
                break

            if self.imu_index == 0:
                raw_file.write(
                    f'{self.csv_df.values[self.csv_index][0]},{self.imu_df.values[self.imu_index][0]},0,0,0\n')
                self.csv_index += 1
                self.imu_index += 1
                continue

            if self.trigger_info_index == 10:
                self.trigger_info_index = 0

            #  Writing raw file
            if use_individual_interval:  # Acc_Z interval 기준
                if not self.individual_interval(raw_file):
                    continue
            else:  # 50mm interval 기준
                if self.csv_index == 1:
                    self.csv_index = 10
                if not self.fixed_interval(raw_file):
                    break

            self.imu_index += 1
            self.trigger_info_index += 1
        raw_file.close()
