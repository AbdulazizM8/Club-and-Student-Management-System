class SystemEntity:
    total_created = 0

    def __init__(self, entity_id):
        self.entity_id = entity_id
        SystemEntity.total_created += 1

    def __del__(self):
        SystemEntity.total_created -= 1

    def __eq__(self, other):
        return self.entity_id == other.entity_id

    def __str__(self):
        return self.entity_id


class Club(SystemEntity):
    def __init__(self, entity_id, name, description, max_capacity, schedule, enrolled_students=None):
        super().__init__(entity_id)
        self.name = name
        self.description = description
        self.max_capacity = int(max_capacity)
        self.schedule = schedule
        if enrolled_students is None:
            enrolled_students = []
        self.enrolled_students = enrolled_students

    def __len__(self):
        return len(self.enrolled_students)

    def is_full(self):
        return len(self.enrolled_students) >= self.max_capacity

    def add_student(self, student_id):
        if student_id in self.enrolled_students or self.is_full():
            return False
        self.enrolled_students.append(student_id)
        return True

    def remove_student(self, student_id):
        if student_id in self.enrolled_students:
            self.enrolled_students.remove(student_id)
            return True
        return False

    def __str__(self):
        members = ",".join(self.enrolled_students)
        return "|".join([self.entity_id, self.name, self.description,
                         str(self.max_capacity), self.schedule, members])


class Student(SystemEntity):
    def __init__(self, entity_id, name, major, contact, joined_clubs=None):
        super().__init__(entity_id)
        self.name = name
        self.major = major
        self.contact = contact
        if joined_clubs is None:
            joined_clubs = []
        self.joined_clubs = joined_clubs

    def __lt__(self, other):
        return self.name.lower() < other.name.lower()

    def __str__(self):
        clubs = ",".join(self.joined_clubs)
        return "|".join([self.entity_id, self.name, self.major, self.contact, clubs])
