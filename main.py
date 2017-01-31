import re
import sqlite3
import datetime
from tkinter import *
from tkinter import ttk
from bisect import bisect_left


def main():
    global con, cur
    con = sqlite3.connect('accounts.db')
    cur = con.cursor()

    # Getting all tables from db
    cur.execute("SELECT * FROM sqlite_master WHERE type='table';")
    table_list = cur.fetchall()
    # Checking tables. If db does not contain table with users, we will create it.
    if len(table_list) == 0 or [table[2] for table in table_list].count('users') < 1:
        cur.execute(
            "CREATE TABLE users (id INTEGER PRIMARY KEY, username VARCHAR(100), password VARCHAR(30));")
        con.commit()
    create_window(Login, "Login Page")


def create_window(window_class, title):
    global root, app
    try:
        root.destroy()
    except NameError:
        pass
    root = Tk()
    root.resizable(width=False, height=False)
    root.title(title)
    app = window_class(root)
    center(root)
    root.focus_force()
    root.mainloop()


def center(toplevel):
    # Centering the window
    toplevel.update_idletasks()
    w = toplevel.winfo_screenwidth()
    h = toplevel.winfo_screenheight()
    size = tuple(int(_) for _ in toplevel.geometry().split('+')[0].split('x'))
    x = w / 2 - size[0] / 2
    y = h / 2 - size[1] / 2
    toplevel.geometry("%dx%d+%d+%d" % (size + (x, y)))


def get_id(table):
    # Getting id from table for creating next element in table
    # If table is empty we will catch an exception
    # Else, we will get max id in format [(id,)] and then incriment it
    try:
        cur.execute(
            "SELECT id FROM " + table + " WHERE id=(SELECT max(id) FROM " + table + " );")
        max_id = cur.fetchall()[0][0]
        id = max_id + 1
    except IndexError:
        id = 0
    return str(id)


class Note():
    def __init__(self, id, text, date):
        self.id = id
        self.text = text
        self.date = date

    def __str__(self):
        return self.text

    def __len__(self):
        return len(self.text)


class Login(Frame):
    def __init__(self, master):
        super(Login, self).__init__(master)
        self.grid()
        self.login_window()

    def login_window(self):

        # Title
        self.title = Label(self, text='login')
        self.title.grid(row=0, column=2)

        # Username label
        self.user_entry_label = Label(
            self, text="Username: ")
        self.user_entry_label.grid(row=1, column=1)

        # Username entry box
        self.user_entry = Entry(self, width=30)
        self.user_entry.grid(row=1, column=2)

        # Password label
        self.pass_entry_label = Label(
            self, text="Password: ")
        self.pass_entry_label.grid(row=2, column=1)

        # Password entry box
        self.pass_entry = Entry(self, width=30)
        self.pass_entry.grid(row=2, column=2)

        # Registration button
        self.sing_up_button = Button(
            self, text="Registrate", command=self.sing_up, width=13)
        self.sing_up_button.grid(row=3, column=1, padx=10)

        # Sign in button
        self.sign_in_button = Button(
            self, text="Sign In", command=self.sing_in, width=13)
        self.sign_in_button.grid(row=3, column=2)

        # Binds
        root.bind('<Return>', self.sing_in)

        for child in self.winfo_children():
            child.grid_configure(padx=5, pady=5)

    def get_password(self):
        # Getting password from the table
        cur.execute("SELECT password FROM users WHERE username = \"" +
                    str(self.user_entry.get()) + "\";")

        # Return password in format [("password",)] if user is registerd
        # If not, function will return empty list
        return cur.fetchall()

    def sing_in(self, event=None):
        pass_get = self.pass_entry.get()
        user_get = self.user_entry.get()
        table_password = self.get_password()

        if table_password != [] and pass_get != '' and table_password[0][0] == pass_get:
            self.title.config(text='Logged')
            global user_table
            user_table = user_get
            create_window(UserFrame, "Notes")
        else:
            self.title.config(text='Invalid Login or Password')

    def sing_up(self):
        user_get = self.user_entry.get()
        pass_get = self.pass_entry.get()
        table_password = self.get_password()
        # If first symbol is integer, our table will throw exceptions, so we must check username
        if len(re.findall(r'^\d{1}', user_get)) != 0:
            self.title.config(text='Invalid Login, first letter must be a liter')
            return
        elif len(user_get) == 0 or len(pass_get) == 0:
            self.title.config(text='Invalid Login or Password')
            return

        if len(table_password) == 0:
            id = get_id('users')
            VALUES = id + ", \"" + user_get + "\",\"" + pass_get + "\""

            # Creating account
            cur.execute(
                "INSERT INTO users (id, username, password) VALUES(" + VALUES + ");")
            con.commit()

            # Creating table for user's notes
            sql_request = "CREATE TABLE " + \
                str(user_get) + " (id INTEGER PRIMARY KEY, note VARCHAR(255), date VARCHAR(10));"
            cur.execute(sql_request)
            con.commit()
            self.title.config(text='Sucsessfully registered')
        else:
            self.title.config(text='Sorry, this username is arleady taken')


class UserFrame(Frame):
    def __init__(self, master):
        super(UserFrame, self).__init__(master)
        self.grid()
        self.main_window()

    def main_window(self):

        # Add button
        self.add_button = ttk.Button(self, text="Add", command=self.add_note)
        self.add_button.grid(column=0, row=1, columnspan=1, sticky='w')

        # Save button
        self.update_button = ttk.Button(self, text="Save", command=self.update_note)
        self.update_button.grid(column=0, row=1, columnspan=2, sticky='w')

        # Delete button
        self.delete_button = ttk.Button(self, text="Delete", command=self.delete_note)
        self.delete_button.grid(column=0, row=1, columnspan=2, sticky='w')

        # Text label
        self.note_frame = ttk.LabelFrame(self, text='Click on the note from the right column', height=40)
        self.note_frame.grid(column=0, row=3, sticky='nwes')

        # Text scrollbar
        self.text_scroll = Scrollbar(self.note_frame)
        self.text_scroll.pack(side=RIGHT, fill=Y)

        # Textbox
        self.text_box = Text(self.note_frame, width=30, height=15, wrap=WORD)
        self.text_box.pack()

        # Notes list label
        self.note_list_frame = ttk.LabelFrame(self, text='Notes', height=80)
        self.note_list_frame.grid(column=1, row=3, sticky='n')

        # Note_list Scrollbar
        self.scrollbar = Scrollbar(self.note_list_frame)
        self.scrollbar.pack(side=RIGHT, fill=Y)

        # Listboxs
        self.list_box = Listbox(self.note_list_frame, width=20, height=15)
        self.list_box.pack()

        # Scrollbar config
        self.list_box.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.list_box.yview)

        # Ornamentation
        for child in self.winfo_children():
            child.grid_configure(padx=3, pady=3)

        self.add_button.grid(padx=20)
        self.update_button.grid(padx=105)
        self.delete_button.grid(padx=190)

        # Binds
        self.list_box.bind('<Double-1>', self.show_note)

        # Filling list_box
        cur.execute("SELECT * FROM " + user_table + ";")
        notes = cur.fetchall()
        self.execute_status = 0  # Using for preventing unexpected behavior
        self.notes = []  # Сonvenient storage of notes
        self.notes_id_list = []
        for note in notes:
            # We get notes from table in format [(id, text, date),...]
            note = Note(note[0], note[1], note[2])
            self.notes.append(note)
            self.notes_id_list.append(note.id)
            self.listbox_update(note.text)

    def listbox_update(self, note_text, listbox_id=END):
        if len(note_text) == 0:
            return 0
        elif len(note_text) < 15:
            self.list_box.insert(listbox_id, re.sub(r'\n', ' ', note_text))
        else:
            self.list_box.insert(listbox_id, re.sub(r'\n', ' ', note_text)[:15] + "...")

    def delete_note_from_table(self, note_id):
        cur.execute("DELETE FROM " + str(user_table) + " WHERE id=" + str(note_id) + ";")
        con.commit()

    def insert_note_into_table(self, note_id, note_text, note_date):
        VALUES = str(note_id) + ", \"" + str(note_text) + "\",\"" + str(note_date) + "\""
        cur.execute(
            "INSERT INTO " + user_table + " (id, note, date) VALUES(" + VALUES + ");")
        con.commit()

    def add_note(self, event=None):
        note_text = self.text_box.get("1.0", END)[:-1]
        if len(note_text) == 0:
            return
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        id = get_id(user_table)

        self.text_box.delete("1.0", END)
        self.listbox_update(note_text)

        self.notes_id_list.append(int(id))
        self.notes.append(Note(id, note_text, current_date))
        self.insert_note_into_table(id, note_text, current_date)

    def update_note(self):
        if len(self.notes) == 0:
            return

        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        note_text = self.text_box.get("1.0", END)[:-1]
        selected_note_id = self.notes_id_list[self.list_box.index(ACTIVE)]

        if self.listbox_update(note_text, self.list_box.index(ACTIVE)) == 0:
            self.note_frame.config(text="Use delete method!")
            return

        self.delete_note_from_table(selected_note_id)
        self.insert_note_into_table(selected_note_id, note_text, current_date)

        self.list_box.delete(ANCHOR)
        self.note_frame.config(text="Saved!")

        # note.id has equivalent index in self.notes_id_list and self.notes, so we can use it
        selected_note = self.notes[bisect_left(self.notes_id_list, selected_note_id)]
        # Updating note list
        self.notes[self.notes.index(selected_note)] = Note(selected_note_id, note_text, current_date)

    def delete_note(self):
        # This check is carried out, because after deleting of the active note,
        # its index still remains active, but not shown
        if self.execute_status == 0:
            self.note_frame.config(text="Select a note")
            return
        self.execute_status = 0

        selected_note_id = self.notes_id_list[self.list_box.index(ACTIVE)]

        self.list_box.delete(ANCHOR)
        self.text_box.delete("1.0", END)
        self.delete_note_from_table(selected_note_id)

        selected_note = self.notes[bisect_left(self.notes_id_list, selected_note_id)]
        self.notes.pop(self.notes.index(selected_note))

    def show_note(self, event):
        if len(self.notes) == 0:
            return

        selected_note_id = self.notes_id_list[self.list_box.index(ACTIVE)]
        selected_note = self.notes[bisect_left(self.notes_id_list, selected_note_id)]

        self.text_box.delete("1.0", END)
        self.text_box.insert(END, str(selected_note))

        self.note_frame.config(text=selected_note.date)

        self.execute_status = 1


if __name__ == '__main__':
    main()
