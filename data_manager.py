import os
from datetime import datetime
from models import Club, Student

folder = os.path.dirname(os.path.abspath(__file__))


def clean(text):
    text = text.replace("|", "/")
    text = text.replace("\n", " ")
    text = text.replace(",", ";")
    return text.strip()


def same_text(a, b):
    return " ".join(a.lower().split()) == " ".join(b.lower().split())


class DataManager:
    def __init__(self):
        self.club_file = os.path.join(folder, "data_clubs.txt")
        self.student_file = os.path.join(folder, "data_students.txt")
        self.settings_file = os.path.join(folder, "settings.txt")
        self.log_file = os.path.join(folder, "activity_log.txt")
        self.clubs = {}
        self.students = {}
        self.school_name = "My School"
        self.default_capacity = "20"

    def load_data(self):
        self.clubs = {}
        self.students = {}

        if os.path.exists(self.club_file):
            with open(self.club_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            for line in lines:
                line = line.strip()
                if line == "":
                    continue
                parts = line.split("|")
                if len(parts) < 6:
                    continue
                members = []
                if parts[5] != "":
                    members = parts[5].split(",")
                club = Club(parts[0], parts[1], parts[2], parts[3], parts[4], members)
                self.clubs[club.entity_id] = club

        if os.path.exists(self.student_file):
            with open(self.student_file, "r", encoding="utf-8") as f:
                lines = f.readlines()
            for line in lines:
                line = line.strip()
                if line == "":
                    continue
                parts = line.split("|")
                if len(parts) < 5:
                    continue
                joined = []
                if parts[4] != "":
                    joined = parts[4].split(",")
                student = Student(parts[0], parts[1], parts[2], parts[3], joined)
                self.students[student.entity_id] = student

    def load_settings(self):
        if not os.path.exists(self.settings_file):
            return
        with open(self.settings_file, "r", encoding="utf-8") as f:
            line = f.readline()
            while line != "":
                line = line.strip()
                if "=" in line:
                    parts = line.split("=", 1)
                    key = parts[0].strip()
                    value = parts[1].strip()
                    if key == "school_name" and value != "":
                        self.school_name = value
                    elif key == "default_capacity" and value.isdigit():
                        self.default_capacity = value
                line = f.readline()

    def write_log(self, message):
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        with open(self.log_file, "a", encoding="utf-8") as f:
            f.write(stamp + " | " + message + "\n")

    def read_log(self):
        if not os.path.exists(self.log_file):
            return ""
        with open(self.log_file, "r", encoding="utf-8") as f:
            return f.read()

    def save_data(self):
        lines = []
        for club in self.clubs.values():
            lines.append(str(club) + "\n")
        with open(self.club_file, "w", encoding="utf-8") as f:
            f.writelines(lines)

        lines = []
        for student in self.students.values():
            lines.append(str(student) + "\n")
        with open(self.student_file, "w", encoding="utf-8") as f:
            f.writelines(lines)
        self.write_log("Saved data to files")

    def make_id(self, prefix, existing):
        number = 1
        new_id = prefix + str(number).rjust(3, "0")
        while new_id in existing:
            number += 1
            new_id = prefix + str(number).rjust(3, "0")
        return new_id

    def next_club_id(self):
        return self.make_id("C", self.clubs)

    def next_student_id(self):
        return self.make_id("S", self.students)

    def find_student(self, text):
        text = text.strip().lower()
        if text == "":
            return None
        for student in self.students.values():
            if text in student.name.lower():
                found = student
                break
        else:
            found = None
        return found

    def add_club(self, club_id, name, description, capacity, schedule):
        club_id = clean(club_id).upper()
        name = clean(name)
        schedule = clean(schedule)
        if club_id == "" or name == "":
            return False, "Club ID and name are required."
        if club_id in self.clubs:
            return False, "A club with ID " + club_id + " already exists."
        for club in self.clubs.values():
            if same_text(club.name, name):
                return False, "A club named '" + club.name + "' already exists."
            if schedule != "" and same_text(club.schedule, schedule):
                return False, club.name + " already meets at " + club.schedule + "."
        if not str(capacity).isdigit() or int(capacity) < 1:
            return False, "Capacity must be a whole number of at least 1."
        self.clubs[club_id] = Club(club_id, name, clean(description), capacity, schedule)
        self.write_log("Created club " + name)
        return True, "Club '" + name + "' was created."

    def add_student(self, student_id, name, major, contact):
        student_id = clean(student_id).upper()
        name = clean(name)
        if student_id == "" or name == "":
            return False, "Student ID and name are required."
        if student_id in self.students:
            return False, "A student with ID " + student_id + " already exists."
        self.students[student_id] = Student(student_id, name, clean(major), clean(contact))
        self.write_log("Registered student " + name)
        return True, "Student '" + name + "' was registered."

    def delete_club(self, club_id):
        if club_id not in self.clubs:
            return
        club = self.clubs.pop(club_id)
        for student_id in club.enrolled_students:
            if student_id in self.students:
                joined = self.students[student_id].joined_clubs
                if club_id in joined:
                    joined.remove(club_id)
        self.write_log("Deleted club " + club.name)

    def delete_student(self, student_id):
        if student_id not in self.students:
            return
        student = self.students.pop(student_id)
        for club_id in student.joined_clubs:
            if club_id in self.clubs:
                self.clubs[club_id].remove_student(student_id)
        self.write_log("Deleted student " + student.name)

    def enroll(self, student_id, club_id):
        if student_id not in self.students or club_id not in self.clubs:
            return False, "Please choose both a student and a club."
        club = self.clubs[club_id]
        student = self.students[student_id]
        if student_id in club.enrolled_students:
            return False, student.name + " is already in " + club.name + "."
        if club.is_full():
            return False, club.name + " is full (" + str(club.max_capacity) + " members)."
        club.add_student(student_id)
        student.joined_clubs.append(club_id)
        self.write_log(student.name + " joined " + club.name)
        return True, student.name + " joined " + club.name + "."

    def unenroll(self, student_id, club_id):
        if student_id not in self.students or club_id not in self.clubs:
            return False, "Please choose both a student and a club."
        club = self.clubs[club_id]
        student = self.students[student_id]
        if not club.remove_student(student_id):
            return False, student.name + " is not in " + club.name + "."
        if club_id in student.joined_clubs:
            student.joined_clubs.remove(club_id)
        self.write_log(student.name + " left " + club.name)
        return True, student.name + " left " + club.name + "."

    def total_memberships(self):
        total = 0
        for club in self.clubs.values():
            total += len(club)
        return total

    def fullest_club(self):
        best = None
        for club in self.clubs.values():
            if best is None or len(club) > len(best):
                best = club
        return best

    def major_counts(self):
        counts = {}
        for student in self.students.values():
            if student.major in counts:
                counts[student.major] += 1
            else:
                counts[student.major] = 1
        return counts

    def export_report(self, path):
        text = "SCHOOL CLUB REPORT".center(78) + "\n"
        text += "=" * 78 + "\n"
        text += "Clubs: " + str(len(self.clubs)) + "   Students: " + str(len(self.students))
        text += "   Memberships: " + str(self.total_memberships()) + "\n\n"
        text += "ID".ljust(8) + "Club".ljust(26) + "Members".rjust(8) + "Capacity".rjust(10) + "  Schedule\n"
        text += "-" * 78 + "\n"
        for club in self.clubs.values():
            text += club.entity_id.ljust(8) + club.name[:24].ljust(26)
            text += str(len(club)).rjust(8) + str(club.max_capacity).rjust(10)
            text += "  " + club.schedule + "\n"
        text += "\n" + "STUDENTS PER MAJOR".center(78) + "\n"
        text += "-" * 78 + "\n"
        majors = self.major_counts()
        for major in sorted(majors):
            text += major.ljust(40) + str(majors[major]).rjust(5) + "\n"
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        self.write_log("Exported report")
