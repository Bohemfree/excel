class RawFile:
    """Read & Write rawfile
    Args:
        filename: Saving raw filename of file (e.g: test.raw)

    """
    def __init__(self, filename: str):
        # Writing raw file
        with open(filename, "w") as raw_file:
            raw_file.write('RTSensorRaw\n')
            raw_file.write('File Version,4\n')
            raw_file.write('Interval[mm],5\n')
            raw_file.write('ValueCount,1\n')
            raw_file.write('VarType,US,US,SI,SI,US\n')
            raw_file.write('Laser,Acceleration,TriggerInfo,FlagIndex,Section\n')