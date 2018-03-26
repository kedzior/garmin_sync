import os.path


class DeviceInfo:
    def __init__(self, device):
        self.__device = device
        self.__vendor = None
        self.__model = None
        path = '/sys/block/' + os.path.basename(self.__device) + '/device'

        self.__vendor = self.__get_file_content(path + '/vendor')
        self.__model = self.__get_file_content(path + '/model')

    def get_mount_path(self):
        with open('/proc/mounts') as file:
            for line in file:
                columns = line.split(' ')
                if columns[0] == self.__device:
                    return columns[1]
        return None

    @property
    def model(self):
        return self.__model

    @property
    def vendor(self):
        return self.__vendor

    def __get_file_content(self, path):
        if os.path.exists(path):
            with open(path, 'r') as f:
                return f.read().strip()
        return None
