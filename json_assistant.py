# coding=utf-8
from json import load, dump
from csv import reader
import os
from os import path
import sys

BASE_DIR = os.path.dirname(sys.argv[0])


class StudentList:
    STUDENT_LIST_DIR = path.join(BASE_DIR, 'student_list')
    EMPTY_DATA = {"students": []}

    def __init__(self, class_no: int):
        self.class_no: int = class_no
        self.file_path: str = path.join(self.STUDENT_LIST_DIR, f'class_{class_no}.json')
        if not path.exists(self.file_path):
            raise FileNotFoundError(f'{self.file_path} not found')
        self.student_list: list = []

        with open(self.file_path, mode="r", encoding="utf-8") as f:
            self.student_list = load(f).get("students", [])

    def write_data(self, data: dict):
        with open(self.file_path, mode="w", encoding="utf-8") as f:
            dump(data, f, indent=4, ensure_ascii=False)

    def get_student_list(self):
        return self.student_list

    @staticmethod
    def get_all_student_lists():
        all_student_lists = {}
        for f in os.listdir(StudentList.STUDENT_LIST_DIR):
            if not f.startswith('class_'):
                continue
            class_no = f.replace('class_', '').replace('.json', '')
            all_student_lists[class_no] = StudentList(class_no=int(class_no)).get_student_list()
        return all_student_lists

    @staticmethod
    def read_student_lists_from_csv(class_no: int):
        try:
            student_list_obj = StudentList(class_no=class_no)
        except FileNotFoundError:
            with open(path.join(StudentList.STUDENT_LIST_DIR, f"class_{class_no}.json"), mode="w",
                      encoding="utf-8") as f:
                dump(StudentList.EMPTY_DATA, f, indent=4)
            student_list_obj = StudentList(class_no=class_no)
        student_list_data = student_list_obj.EMPTY_DATA
        with open(path.join(StudentList.STUDENT_LIST_DIR, f"{class_no}.csv"), mode="r", newline="",
                  encoding="utf-8-sig") as f:
            csv_reader = reader(f)
            i = 0
            for row in csv_reader:
                i += 1
                if i == 1:
                    continue
                student_list_data["students"].append(
                    {
                        "classNo": int(row[0]),
                        "seatNo": int(row[1]),
                        "name": row[2]
                    }
                )
                print(row)
        student_list_obj.write_data(student_list_data)


if __name__ == '__main__':
    StudentList.read_student_lists_from_csv(class_no=int(input("輸入班級編號：")))
