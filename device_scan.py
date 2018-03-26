import os.path


class DeviceScan:
    def scan(self):
        devices = []
        with open("/proc/partitions", "r") as f:
            for line in f.readlines()[2:]:
                columns = [column.strip() for column in line.split()]
                minor_number = int(columns[1])
                name = columns[3]

                if (minor_number % 16) == 0:
                    path = "/sys/class/block/" + name

                    if os.path.islink(path):
                        if os.path.realpath(path).find("/usb") > 0:
                            devices.append("/dev/" + name)

        return devices
