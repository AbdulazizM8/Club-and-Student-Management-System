import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from data_manager import DataManager
from models import SystemEntity
import visualizations

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
COLORS = ["#ffb3b3", "#ffe08a", "#a8e6f7", "#9ee8cf", "#cfc9ff", "#ffc7f2"]


class MainWindow:
    def __init__(self, root):
        self.root = root
        self.dm = DataManager()
        self.dm.load_data()
        self.dm.load_settings()
        self.sort_reverse = {}
        self.chart = None

        root.title(self.dm.school_name + " - Club & Student Management System")
        root.geometry("1024x768")

        style = ttk.Style()
        style.configure("Treeview", rowheight=32, font=("Arial", 11))
        style.configure("Treeview.Heading", font=("Arial", 11, "bold"))

        self.digits_check = (root.register(self.only_digits), "%P")
        self.id_check = (root.register(self.valid_id), "%P")

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)

        self.tab_dash = ttk.Frame(self.notebook)
        self.tab_clubs = ttk.Frame(self.notebook)
        self.tab_calendar = ttk.Frame(self.notebook)
        self.tab_roster = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_dash, text="Dashboard")
        self.notebook.add(self.tab_clubs, text="Club Dir")
        self.notebook.add(self.tab_calendar, text="Calendar")
        self.notebook.add(self.tab_roster, text="Admin Page")

        self.build_dashboard()
        self.build_directory()
        self.build_calendar()
        self.build_roster()

        self.notebook.bind("<<NotebookTabChanged>>", lambda event: self.refresh_all())
        root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.refresh_all()

    def only_digits(self, text):
        return text == "" or text.isdigit()

    def valid_id(self, text):
        return text == "" or (text.isalnum() and len(text) <= 8)

    def build_dashboard(self):
        top = ttk.Frame(self.tab_dash)
        top.pack(fill="x", padx=10, pady=10)

        logo_frame = ttk.Frame(top)
        logo_frame.pack(side="left")
        visualizations.draw_school_logo(logo_frame)

        info = ttk.Frame(top)
        info.pack(side="left", padx=25)
        self.stats_label = ttk.Label(info, text="", font=("Arial", 13), justify="left")
        self.stats_label.pack(anchor="w")
        ttk.Button(info, text="Save Data", command=self.save_clicked).pack(anchor="w", pady=10)
        ttk.Button(info, text="Export Report...", command=self.export_clicked).pack(anchor="w")

        log_frame = ttk.Frame(top)
        log_frame.pack(side="left", padx=10)
        ttk.Label(log_frame, text="Recent activity").pack(anchor="w")
        self.log_box = tk.Text(log_frame, width=44, height=9, font=("Arial", 9),
                               spacing1=3, spacing3=3, state="disabled")
        self.log_box.pack()

        chart_frame = ttk.Frame(self.tab_dash)
        chart_frame.pack(fill="both", expand=True, padx=10, pady=5)
        if visualizations.HAS_MATPLOTLIB:
            self.chart = visualizations.EnrollmentChart(chart_frame)
        else:
            ttk.Label(chart_frame, text="Install matplotlib to see the chart:\npip install matplotlib",
                      font=("Arial", 12)).pack(pady=40)

    def make_table(self, parent, columns, widths, height):
        frame = ttk.Frame(parent)
        tree = ttk.Treeview(frame, columns=columns, show="headings", height=height)
        tree.tag_configure("even", background="#ffffff", foreground="#111111")
        tree.tag_configure("odd", background="#eef2fa", foreground="#111111")
        for i in range(len(columns)):
            tree.heading(columns[i], text=columns[i],
                         command=lambda c=columns[i]: self.sort_tree(tree, c))
            tree.column(columns[i], width=widths[i], anchor="w")
        scroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        return frame, tree

    def stripe(self, tree):
        number = 0
        for item in tree.get_children(""):
            if number % 2 == 0:
                tree.item(item, tags=("even",))
            else:
                tree.item(item, tags=("odd",))
            number += 1

    def sort_tree(self, tree, column):
        key = str(tree) + column
        reverse = self.sort_reverse.get(key, False)
        items = []
        for item in tree.get_children(""):
            items.append((tree.set(item, column), item))
        if column == "Enrolled" or column == "Capacity":
            items.sort(key=lambda pair: int(pair[0]), reverse=reverse)
        else:
            items.sort(key=lambda pair: pair[0].lower(), reverse=reverse)
        position = 0
        for value, item in items:
            tree.move(item, "", position)
            position += 1
        self.stripe(tree)
        self.sort_reverse[key] = not reverse

    def build_directory(self):
        top = ttk.Frame(self.tab_clubs)
        top.pack(fill="both", expand=True, padx=10, pady=10)

        columns = ("ID", "Name", "Enrolled", "Capacity", "Schedule")
        frame, self.club_tree = self.make_table(top, columns, (60, 210, 70, 70, 170), 14)
        frame.pack(side="left", fill="both", expand=True)
        self.club_tree.bind("<<TreeviewSelect>>", self.show_club_details)

        badge_frame = ttk.Frame(top)
        badge_frame.pack(side="left", anchor="n", padx=10)
        ttk.Label(badge_frame, text="Club badge").pack()
        self.badge = visualizations.ClubBadge(badge_frame, 220)

        self.detail_label = ttk.Label(self.tab_clubs, text="Select a club to see its details.",
                                      wraplength=950, justify="left")
        self.detail_label.pack(fill="x", padx=10, pady=5)
        ttk.Button(self.tab_clubs, text="Delete Selected Club",
                   command=self.delete_club_clicked).pack(pady=5)

    def show_club_details(self, event=None):
        selected = self.club_tree.selection()
        if len(selected) == 0:
            return
        club = self.dm.clubs.get(selected[0])   
        if club is None:
            return
        names = []
        for student_id in club.enrolled_students:
            if student_id in self.dm.students:
                names.append(self.dm.students[student_id].name)
        members = ", ".join(names)
        if members == "":
            members = "nobody yet"
        places = str(len(club)) + " of " + str(club.max_capacity) + " places taken"
        self.detail_label.config(text=club.name + " (" + places + "): " + club.description
                                 + "\nMembers: " + members)
        self.badge.draw(club)

    def delete_club_clicked(self):
        selected = self.club_tree.selection()
        if len(selected) == 0:
            messagebox.showerror("Error", "Select a club first.")
            return
        if messagebox.askyesno("Confirm", "Delete club " + selected[0] + "?"):
            self.dm.delete_club(selected[0])
            self.badge.draw(None)
            self.refresh_all()

    def build_calendar(self):
        self.cal_frame = tk.Frame(self.tab_calendar)
        self.cal_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.cal_note = ttk.Label(self.tab_calendar, text="", wraplength=950, justify="left")
        self.cal_note.pack(fill="x", padx=10, pady=5)

    def parse_schedule(self, text):
        for symbol in [";", "/", "&", "-", ","]:
            text = text.replace(symbol, " ")
        days = []
        hour = -1
        minute = 0
        for word in text.split():
            day = word[:3].capitalize()
            if day in DAYS:
                if DAYS.index(day) not in days:
                    days.append(DAYS.index(day))
            elif ":" in word and hour == -1:
                parts = word.split(":")
                if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                    hour = int(parts[0])
                    minute = int(parts[1])
        if "PM" in text.upper() and 0 < hour < 12:
            hour += 12
        if len(days) == 0 or hour < 0 or hour > 23 or minute > 59:
            return None
        return days, hour, minute

    def two(self, number):
        return str(number).rjust(2, "0")

    def refresh_calendar(self):
        for widget in self.cal_frame.winfo_children():
            widget.destroy()

        cells = {}
        skipped = []
        first_hour = 8
        last_hour = 18
        count = 0
        for club in self.dm.clubs.values():
            color = COLORS[count % len(COLORS)]
            count += 1
            result = self.parse_schedule(club.schedule)
            if result is None:
                skipped.append(club.name + " (" + club.schedule + ")")
                continue
            days, hour, minute = result
            first_hour = min(first_hour, hour)
            last_hour = max(last_hour, hour)
            for day in days:
                if (day, hour) not in cells:
                    cells[(day, hour)] = []
                cells[(day, hour)].append((club.name, minute, color))

        tk.Label(self.cal_frame, text="Time", bg="#101a33", fg="white",
                 font=("Arial", 10, "bold")).grid(row=0, column=0, sticky="nsew")
        for day in range(7):
            tk.Label(self.cal_frame, text=DAY_NAMES[day], bg="#101a33", fg="white",
                     font=("Arial", 10, "bold")).grid(row=0, column=day + 1, sticky="nsew")

        row = 1
        for hour in range(first_hour, last_hour + 1):
            tk.Label(self.cal_frame, text=self.two(hour) + ":00", bg="#e8ecf4", fg="black",
                     font=("Arial", 9), width=6, relief="solid", borderwidth=1).grid(
                row=row, column=0, sticky="nsew")
            for day in range(7):
                if (day, hour) in cells:
                    cell = tk.Frame(self.cal_frame, bg="white", relief="solid", borderwidth=1)
                    cell.grid(row=row, column=day + 1, sticky="nsew")
                    for name, minute, color in cells[(day, hour)]:
                        text = name + "\n" + self.two(hour) + ":" + self.two(minute)
                        tk.Label(cell, text=text, bg=color, fg="black",
                                 font=("Arial", 9)).pack(fill="x", padx=2, pady=1)
                else:
                    tk.Label(self.cal_frame, text="", bg="white", height=2, relief="solid",
                             borderwidth=1).grid(row=row, column=day + 1, sticky="nsew")
            row += 1

        for column in range(1, 8):
            self.cal_frame.grid_columnconfigure(column, weight=1, uniform="day")

        if len(skipped) > 0:
            self.cal_note.config(text="Not shown (use a format like Mon 16:00): " + ", ".join(skipped))
        else:
            self.cal_note.config(text="Each block shows a club and its meeting time. "
                                      "Clubs you add in the Administrative Roster tab appear here too.")

    def build_roster(self):
        forms = ttk.Frame(self.tab_roster)
        forms.pack(fill="x", padx=10, pady=8)

        student_form = tk.LabelFrame(forms, text="Register Student", padx=8, pady=8)
        student_form.pack(side="left", fill="both", expand=True, padx=5)
        self.s_id = self.add_field(student_form, "ID (letters/digits):", 0, self.id_check)
        tk.Button(student_form, text="Suggest", command=self.suggest_student_id).grid(row=0, column=2)
        self.s_name = self.add_field(student_form, "Full name:", 1)
        self.s_major = self.add_field(student_form, "Major:", 2)
        self.s_contact = self.add_field(student_form, "Contact:", 3)
        tk.Button(student_form, text="Register Student", command=self.add_student_clicked).grid(
            row=4, column=0, columnspan=2, pady=6)

        club_form = tk.LabelFrame(forms, text="Create Club", padx=8, pady=8)
        club_form.pack(side="left", fill="both", expand=True, padx=5)
        self.c_id = self.add_field(club_form, "ID (letters/digits):", 0, self.id_check)
        tk.Button(club_form, text="Suggest", command=self.suggest_club_id).grid(row=0, column=2)
        self.c_name = self.add_field(club_form, "Club name:", 1)
        self.c_desc = self.add_field(club_form, "Description:", 2)
        self.c_cap = self.add_field(club_form, "Max capacity:", 3, self.digits_check)
        self.c_cap.insert(0, self.dm.default_capacity)
        self.c_sched = self.add_field(club_form, "Schedule (Mon 16:00):", 4)
        tk.Button(club_form, text="Create Club", command=self.add_club_clicked).grid(
            row=5, column=0, columnspan=2, pady=6)

        enroll_form = tk.LabelFrame(self.tab_roster, text="Enrollment and Search", padx=8, pady=8)
        enroll_form.pack(fill="x", padx=15, pady=5)
        tk.Label(enroll_form, text="Student:").grid(row=0, column=0)
        self.enroll_student = ttk.Combobox(enroll_form, state="readonly", width=30)
        self.enroll_student.grid(row=0, column=1, padx=5)
        tk.Label(enroll_form, text="Club:").grid(row=0, column=2)
        self.enroll_club = ttk.Combobox(enroll_form, state="readonly", width=30)
        self.enroll_club.grid(row=0, column=3, padx=5)
        tk.Button(enroll_form, text="Enroll", command=self.enroll_clicked).grid(row=0, column=4, padx=5)
        tk.Button(enroll_form, text="Remove", command=self.unenroll_clicked).grid(row=0, column=5, padx=5)
        tk.Label(enroll_form, text="Find student:").grid(row=1, column=0, pady=(8, 0))
        self.search_entry = tk.Entry(enroll_form, width=33)
        self.search_entry.grid(row=1, column=1, padx=5, pady=(8, 0))
        tk.Button(enroll_form, text="Find", command=self.find_clicked).grid(row=1, column=2, pady=(8, 0))

        columns = ("ID", "Name", "Major", "Contact", "Clubs")
        frame, self.student_tree = self.make_table(self.tab_roster, columns, (70, 170, 170, 200, 200), 6)
        frame.pack(fill="both", expand=True, padx=15, pady=5)
        tk.Button(self.tab_roster, text="Delete Selected Student",
                  command=self.delete_student_clicked).pack(pady=4)

    def add_field(self, parent, label, row, check=None):
        tk.Label(parent, text=label).grid(row=row, column=0, sticky="e", pady=2)
        if check is None:
            entry = tk.Entry(parent, width=28)
        else:
            entry = tk.Entry(parent, width=28, validate="key", validatecommand=check)
        entry.grid(row=row, column=1, padx=5, pady=2)
        return entry

    def clear(self, *entries):
        for entry in entries:
            entry.delete(0, "end")

    def show_result(self, result):
        ok, message = result
        if ok:
            messagebox.showinfo("Success", message)
        else:
            messagebox.showerror("Error", message)
        self.refresh_all()
        return ok

    def add_student_clicked(self):
        result = self.dm.add_student(self.s_id.get(), self.s_name.get(),
                                     self.s_major.get(), self.s_contact.get())
        if self.show_result(result):
            self.clear(self.s_id, self.s_name, self.s_major, self.s_contact)

    def add_club_clicked(self):
        result = self.dm.add_club(self.c_id.get(), self.c_name.get(), self.c_desc.get(),
                                  self.c_cap.get(), self.c_sched.get())
        if self.show_result(result):
            self.clear(self.c_id, self.c_name, self.c_desc, self.c_cap, self.c_sched)
            self.c_cap.insert(0, self.dm.default_capacity)

    def suggest_student_id(self):
        self.clear(self.s_id)
        self.s_id.insert(0, self.dm.next_student_id())

    def suggest_club_id(self):
        self.clear(self.c_id)
        self.c_id.insert(0, self.dm.next_club_id())

    def find_clicked(self):
        student = self.dm.find_student(self.search_entry.get())
        if student is None:
            messagebox.showerror("Not found", "No student matches that name.")
            return
        self.student_tree.selection_set(student.entity_id)
        self.student_tree.see(student.entity_id)
        clubs = ", ".join(student.joined_clubs)
        if clubs == "":
            clubs = "none"
        messagebox.showinfo("Student found", student.name + " (" + student.entity_id + ")\n"
                            + "Major: " + student.major + "\nClubs: " + clubs)

    def picked_ids(self):
        student_id = self.enroll_student.get().split(" - ")[0]
        club_id = self.enroll_club.get().split(" - ")[0]
        return student_id, club_id

    def enroll_clicked(self):
        student_id, club_id = self.picked_ids()
        self.show_result(self.dm.enroll(student_id, club_id))

    def unenroll_clicked(self):
        student_id, club_id = self.picked_ids()
        self.show_result(self.dm.unenroll(student_id, club_id))

    def delete_student_clicked(self):
        selected = self.student_tree.selection()
        if len(selected) == 0:
            messagebox.showerror("Error", "Select a student first.")
            return
        if messagebox.askyesno("Confirm", "Delete student " + selected[0] + "?"):
            self.dm.delete_student(selected[0])
            self.refresh_all()

    def refresh_all(self):
        self.refresh_clubs()
        self.refresh_students()
        self.refresh_stats()
        self.refresh_calendar()
        self.refresh_log()
        if self.chart is not None:
            self.chart.update(self.dm)

    def refresh_clubs(self):
        self.club_tree.delete(*self.club_tree.get_children())
        for club in self.dm.clubs.values():
            self.club_tree.insert("", "end", iid=club.entity_id,
                                  values=(club.entity_id, club.name, len(club),
                                          club.max_capacity, club.schedule))
        self.stripe(self.club_tree)
        choices = []
        for club in self.dm.clubs.values():
            choices.append(club.entity_id + " - " + club.name)
        self.enroll_club["values"] = choices

    def refresh_students(self):
        self.student_tree.delete(*self.student_tree.get_children())
        choices = []
        for student in sorted(self.dm.students.values()):
            self.student_tree.insert("", "end", iid=student.entity_id,
                                     values=(student.entity_id, student.name, student.major,
                                             student.contact, ", ".join(student.joined_clubs)))
            choices.append(student.entity_id + " - " + student.name)
        self.stripe(self.student_tree)
        self.enroll_student["values"] = choices

    def refresh_stats(self):
        fullest = self.dm.fullest_club()
        popular = "-"
        if fullest is not None:
            popular = fullest.name
        text = self.dm.school_name + "\n"
        text += "Clubs: " + str(len(self.dm.clubs)) + "\n"
        text += "Students: " + str(len(self.dm.students)) + "\n"
        text += "Total memberships: " + str(self.dm.total_memberships()) + "\n"
        text += "Most popular club: " + popular + "\n"
        text += "Records in memory: " + str(SystemEntity.total_created)
        self.stats_label.config(text=text)

    def refresh_log(self):
        text = self.dm.read_log().strip()
        if text == "":
            shown = "No activity yet."
        else:
            lines = text.split("\n")
            shown = "\n".join(lines[-8:])
        self.log_box.config(state="normal")
        self.log_box.delete("1.0", "end")
        self.log_box.insert("end", shown)
        self.log_box.config(state="disabled")
        self.log_box.see("end")

    def save_clicked(self):
        self.dm.save_data()
        messagebox.showinfo("Saved", "Data saved to text files.")

    def export_clicked(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt",
                                            filetypes=[("Text files", "*.txt")],
                                            initialfile="club_report.txt")
        if path:
            self.dm.export_report(path)
            messagebox.showinfo("Exported", "Report saved to:\n" + path)

    def on_closing(self):
        answer = messagebox.askyesnocancel("Quit", "Save changes before exiting?")
        if answer is None:
            pass
        elif answer:
            self.dm.save_data()
            self.root.destroy()
        else:
            self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    MainWindow(root)
    root.mainloop()
