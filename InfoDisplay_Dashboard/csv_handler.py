from watchdog.events import FileSystemEventHandler
import csv


class CSVHandler(FileSystemEventHandler):
    def init(self, file):
        self.file = file
        self.data = {}

    def format_file(self):
        data = [
            [
                "timestamp",
                "accel_x",
                "accel_y",
                "accel_z",
                "rt_x",
                "rt_y",
                "rt_z",
                "temperature",
            ]
        ]

        try:
            with open(self.file, "r"):
                tmp = []
                reader = csv.reader(self.file)
                for row in reader:
                    tmp.append(row)

                    if row == [""]:
                        tmp = []

                data.append(tmp)

            with open("formatted_" + self.file, "w+"):
                writer = csv.writer(self.file)

                writer.writerows(data)

        except FileNotFoundError:
            print("Could not find: ", self.file)

        except PermissionError:
            print("Lacking Permissions to read/write", self.file)

    def read_file(self):
        try:
            with open("formatted_" + self.file, "r"):
                reader = csv.DictReader(self.file)

            for row in reader:
                self.data[int(row["timestamp"])] = row

        except FileNotFoundError:
            print("No File ", self.file)

        except PermissionError:
            print("Could not read ", self.file)
