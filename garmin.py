import glob
import os.path
import time

from connection import Connection
from datetime import datetime
from device_info import DeviceInfo
from device_scan import DeviceScan


class GarminSync:
    supported_devices = [
        # (Vendor, Model, Path),
        ('Garmin', 'FR35 Flash', '/GARMIN/ACTIVITY/'),
        ('Garmin', 'Vivo Smart HR GP', '/'),
    ]
    config_file = '.garmin_sync'
    time_format = '%Y-%m-%d %H:%M:%S'

    def update(self):
        last_date = self.__read_sync_file()
        current_time = int(time.time())
        device_scanner = DeviceScan()
        devices = device_scanner.scan()
        for device in devices:
            device_info = DeviceInfo(device)
            mount_path = device_info.get_mount_path()
            if device_info.vendor == GarminSync.supported_devices[0][0] and\
               device_info.model == GarminSync.supported_devices[0][1]:
                if mount_path is not None:
                    files_to_upload = self.__scan_files(mount_path, last_date)
                    if files_to_upload == []:
                        print('Up to date!')
                    else:
                        try:
                            self.__upload_files(files_to_upload)
                        except Exception:
                            return
                    self.__save_sync_file(current_time)
                else:
                    print('Please mount your Garmin device!')
                return
        print('Garmin device not found!')

    def __read_sync_file(self):
        if not os.path.isfile(GarminSync.config_file):
            self.__save_sync_file(0)
        with open(GarminSync.config_file, 'r') as f:
            last_sync = int(f.read())
            print('Last sync: ' + datetime.fromtimestamp(last_sync).
                  strftime(GarminSync.time_format))
        return last_sync

    def __save_sync_file(self, sync_time):
        with open(GarminSync.config_file, 'w') as f:
            print('Successfully synced: ' +
                  datetime.fromtimestamp(sync_time).
                  strftime(GarminSync.time_format))
            f.write(str(sync_time))

    def __scan_files(self, mount_path, last_date):
        path = mount_path + GarminSync.supported_devices[0][2]
        files_to_upload = []
        for file in glob.glob(path + '*'):
            file_data = os.stat(file)
            if int(file_data.st_mtime) > last_date:
                files_to_upload.append(file)
        return files_to_upload

    def __upload_files(self, files):
        conn = Connection()
        if conn.authenticate():
            for file in files:
                try:
                    conn.upload_activity(file)
                except Exception:
                    print('Error while processing file: \'' + file + '\'')
                    print('Probably FIT file broke.')
                    print('Please fix the FIT file and upload it manually.')
                    print('https://forums.garmin.com/forum/into-sports/\
                          garmin-connect/31157-how-to-repair-a-fit-file')
                    print('File omited.')
            print(str(len(files)) + ' files were sent!')
        else:
            print('Could not authenticate!')
            raise Exception('Could not authenticate')


if __name__ == '__main__':
    gs = GarminSync()
    gs.update()
