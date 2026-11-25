''' '''

A desktop app for keeping track of school clubs, students and who belongs to which club.

This project was built as the Final project for the Software Programming Course, so it only uses the standard library plus Matplotlib (for the chart).

What it can do:

The window has four tabs.

Dashboard: 

1. Shows the school name, the number of clubs and students, total memberships and the most popular club.
2. A small school picture drawn with Tkinter shapes (rectangles, ovals, a polygon roof and a few lines).
3. A "Recent activity" box that shows the last few things that happened (clubs created, students enrolled, saves and so on).
4. A bar chart of members against capacity for every club, with each club's meeting time next to its bar.
5. Buttons to save the data and to export a text report.

Club Dir

1. A table with the club ID, name, how many students are enrolled, capacity and schedule.
2. Click a column header to sort by it. Click again to reverse the order.
3. Click a club to see its description and the names of its members.
4. Every club also gets its own badge, drawn with Turtle graphics. The shape depends on how many members the club has and the colours depend on its name.
5. A button to delete the selected club.

Calendar

1. A Monday to Sunday timetable. Each club is shown as a coloured block at its day and time.
2. A club that meets on more than one day (for example `Mon/Wed 17:00`) appears on every one of those days.
3. If two clubs meet in the same hour, their blocks are stacked in the same cell.
4. Clubs whose schedule can't be read are listed under the calendar instead of silently disappearing.
5. New clubs show up here as soon as you create them.

Admin Page
1. Register a new student (ID, full name, major, contact).
2. Create a new club (ID, name, description, capacity, schedule).
3. The Suggest button next to each ID field fills in the next free ID, like `C013` or `S041`.
4. Enroll a student in a club or remove them from it.
5. Find a student by typing part of their name. The student is selected in the table and a box shows their major and clubs.
6. A table of all students (sorted by name) and a button to delete the selected one.

RULES FOR USING:

1. A club can't use an ID, a name or a meeting time that another club already has. Upper and lower case and extra spaces are ignored, so `chess  CLUB` counts as `Chess Club`.
2. A club can't have more members than its capacity, and a student can't join the same club twice.
3. Capacity only accepts digits. IDs only accept letters and digits (up to 8 characters).
4. If a required field is empty, you get an error message instead of a half-finished record.
5. Any `|` or `,` typed into a field is replaced, so it can't break the text files.
6. When you close the window it asks whether to save first (Yes, No or Cancel).


FOR RUNNING:

You need Python 3.8 or newer. Tkinter comes with the normal Python installers for Windows and macOS. 

Files

main.py             the window, tabs, buttons and forms
models.py           SystemEntity, Club and Student classes
data_manager.py     loading, saving and all the rules
visualizations.py   school picture, bar chart and Turtle club badge
data_clubs.txt      the clubs
data_students.txt   the students
settings.txt        school name and default capacity
activity_log.txt    created by the app the first time something happens


Data files:

One record per line, fields separated by `|`, and lists of ID s separated by commas.


C004|Photography Club|Photo walks and editing workshops|10|Thu 16:00|S003,S012,S015,S019,S037
S009|Jin Choi|Economics|jin.c@school.edu|C001,C009


A club line is: ID, name, description, capacity, schedule, member IDs.
A student line is: ID, name, major, contact, club IDs.


Schedule format

The calendar should be inputted data like this:

Mon 16:00
Tue 15:30
Mon/Wed 4:30 PM
Monday, Friday 09:15
Sat 10:00-11:30

Only the start time is used. The first three letters of each day determines the day.


Sample data

The project comes with 12 clubs and 40 students so there is something to look at straight away. 



