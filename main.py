import sqlite3
import datetime
from tkinter import *
from tkinter import ttk
import re


def main():
    global con, cur, root, app
    con = sqlite3.connect('accounts.db')
    cur = con.cursor()

    # Check the existence of a user table
    #
    # Getting all tables from db
    cur.execute("SELECT * FROM sqlite_master WHERE type='table';")
    table_list = cur.fetchall()
    # Checking tables. If db does not contain table with users, we will create it.
    if len(table_list) == 0:
        cur.execute(
            "CREATE TABLE users (id INTEGER PRIMARY KEY, username VARCHAR(100), password VARCHAR(30));")
        con.commit()
    else:
        if [table[2] for table in table_list].count('users') < 1:
            cur.execute(
                "CREATE TABLE users (id INTEGER PRIMARY KEY, username VARCHAR(100), password VARCHAR(30));")
            con.commit()

    root = Tk()
    root.title("Login Page")
    app = Login(root)
    center(root)
    root.mainloop()


def center(toplevel):
    # Centering window
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

    def get_password(self):
        # Getting password from the table
        cur.execute("SELECT password FROM users WHERE username = \"" +
                    str(self.user_entry.get()) + "\";")

        # Return password in format [("password",)] if user is registerd
        # If not, it will return empty list
        return cur.fetchall()

    def sing_in(self):
        pass_get = self.pass_entry.get()
        table_password = self.get_password()

        if table_password != [] and pass_get != '' and table_password[0][0] == pass_get:
            self.title.config(text='Logged')
            self.main_window()
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

    def main_window(self):
        global root, app, user_table
        user_table = self.user_entry.get()
        root.destroy()
        root = Tk()
        root.title("Notes")
        app = UserFrame(root)
        center(root)
        root.mainloop()


class UserFrame(Frame):
    def __init__(self, master):
        super(UserFrame, self).__init__(master)
        self.grid()
        self.notes = []
        self.main_window()

    def main_window(self):

        # Add button
        self.add_button = ttk.Button(self, text="Add", command=self.add_note)
        self.add_button.grid(column=0, row=1, columnspan=1, sticky='w')

        # Delete button
        self.delete_button = ttk.Button(self, text="Delete", command=self.delete_note)
        self.delete_button.grid(column=0, row=1, columnspan=1, ipadx=10)

        # Note entry box
        self.note_entry = Entry(self, width=50)
        self.note_entry.grid(column=0, row=2, sticky='w')

        # Result label
        self.result_frame = ttk.LabelFrame(self, text='Notes', height=70)
        self.result_frame.grid(column=0, row=4, sticky='nwes')

        # Scrollbar
        self.scrollbar = Scrollbar(self.result_frame)
        self.scrollbar.pack(side=RIGHT, fill=Y)

        # Listboxs
        self.list_box = Listbox(self.result_frame, width=50)
        self.list_box.pack()

        # Scrollbar config
        self.list_box.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.config(command=self.list_box.yview)

        # Note box
        self.note_box = Message(self, text="Double-click on the message to the full view")
        self.note_box.config(aspect=500, justify=CENTER, width=90)
        self.note_box.grid(column=2, row=4)

        for child in self.winfo_children():
            child.grid_configure(padx=5, pady=5)

        # Binds
        self.list_box.bind('<Double-1>', self.show_note)

        # Filling list_box
        cur.execute("SELECT * FROM " + user_table + ";")
        notes = cur.fetchall()
        for note in notes:
            # We get notes from table in format [(id, text, date),...]
            note = Note(note[0], note[1], note[2])
            self.notes.append(note)
            if len(note) < 15:
                self.list_box.insert(END, note.text)
            else:
                self.list_box.insert(END, str(note.text)[:15] + "...")

    def add_note(self):
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        note = self.note_entry.get()
        self.note_entry.delete(0, 'end')
        if len(note) < 15:
            self.list_box.insert(END, note)
        else:
            self.list_box.insert(END, str(note)[:15] + "...")
        id = get_id(user_table)
        self.notes.append(Note(id, note, current_date))
        VALUES = id + ", \"" + note + "\",\"" + current_date + "\""
        cur.execute(
            "INSERT INTO " + user_table + " (id, note, date) VALUES(" + VALUES + ");")
        con.commit()

    def delete_note(self):
        selected_note = self.list_box.get(ACTIVE)
        for note in self.notes:
            if note.text[:15] == str(selected_note)[:15]:
                self.list_box.delete(ANCHOR)
                cur.execute("DELETE FROM " + user_table + " WHERE id=" + str(note.id) + ";")
                con.commit()
                self.notes.pop(self.notes.index(note))
                break

    def show_note(self, event):
        selected_note = self.list_box.get(ACTIVE)
        for note in self.notes:
            if note.text[:15] == str(selected_note)[:15]:
                self.note_box.config(text=note.date + "\n" + note.text)


if __name__ == '__main__':
    main()
