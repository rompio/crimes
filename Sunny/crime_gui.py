import customtkinter as ctk
from tkinter import ttk
from tkinter import messagebox
import importlib.util
import sys

# Dynamically import the _postgres_main module
spec = importlib.util.spec_from_file_location("postgres_main", "./_postgres_main.py")
postgres_main = importlib.util.module_from_spec(spec)
sys.modules["postgres_main"] = postgres_main
spec.loader.exec_module(postgres_main)

# Import only the functions that exist in _postgres_main.py
connect_to_db = postgres_main.connect_to_db
execute_query = postgres_main.execute_query
create_db = postgres_main.create_db

# Add the fetch_data function here since it's not in _postgres_main.py
def fetch_data(query, param=()):
    conn = connect_to_db()
    cursor = conn.cursor()
    cursor.execute(query, param)
    result = cursor.fetchall()
    conn.close()
    return result

def populate_treeview():
    crime_tree.delete(*crime_tree.get_children())
    for row in fetch_data('SELECT * FROM Crimes'):
        crime_tree.insert('', 'end', values=row)

def add_crime():
    type = type_entry.get()
    date = date_entry.get()
    location = location_entry.get()

    if type and date and location:
        execute_query('INSERT INTO Crimes (Type, Date, Location) VALUES (%s, %s, %s)', (type, date, location))
        populate_treeview()
    else:
        messagebox.showerror("Input Error", "All fields must be filled out.")

def update_crime():
    selected = crime_tree.selection()
    if not selected:
        messagebox.showerror("Selection Error", "Please select a record to update.")
        return

    crime_id = crime_tree.item(selected[0], 'values')[0]
    type = type_entry.get()
    date = date_entry.get()
    location = location_entry.get()

    if type and date and location:
        execute_query('UPDATE Crimes SET Type = %s, Date = %s, Location = %s WHERE CrimeID = %s', 
                      (type, date, location, crime_id))
        populate_treeview()
    else:
        messagebox.showerror("Input Error", "All fields must be filled out.")

def delete_crime():
    selected = crime_tree.selection()
    if not selected:
        messagebox.showerror("Selection Error", "Please select a record to delete.")
        return

    crime_id = crime_tree.item(selected[0], 'values')[0]
    execute_query('DELETE FROM Crimes WHERE CrimeID = %s', (crime_id,))
    populate_treeview()

def on_crime_select(event):
    selected = crime_tree.selection()
    if selected:
        selected_record = crime_tree.item(selected[0], 'values')
        type_entry.delete(0, ctk.END)
        type_entry.insert(0, selected_record[1])
        date_entry.delete(0, ctk.END)
        date_entry.insert(0, selected_record[2])
        location_entry.delete(0, ctk.END)
        location_entry.insert(0, selected_record[3])

def main():
    create_db()

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")

    global root, crime_tree, type_entry, date_entry, location_entry

    root = ctk.CTk()
    root.title("Crime Investigation Database")
    root.geometry("800x600")

    # Treeview Styles
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview", background="#2e2e2e", foreground="white", rowheight=25, fieldbackground="#2e2e2e")
    style.map('Treeview', background=[('selected', '#1f538d')])

    # Treeview
    crime_tree = ttk.Treeview(root, columns=("CrimeID", "Type", "Date", "Location"), show="headings")
    crime_tree.heading("CrimeID", text="Crime ID")
    crime_tree.heading("Type", text="Type")
    crime_tree.heading("Date", text="Date")
    crime_tree.heading("Location", text="Location")
    crime_tree.bind('<<TreeviewSelect>>', on_crime_select)
    crime_tree.pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)

    # Input Fields
    input_frame = ctk.CTkFrame(root)
    input_frame.pack(pady=10)

    ctk.CTkLabel(input_frame, text="Type:").grid(row=0, column=0, padx=5, pady=5)
    type_entry = ctk.CTkEntry(input_frame)
    type_entry.grid(row=0, column=1, padx=5, pady=5)

    ctk.CTkLabel(input_frame, text="Date (YYYY-MM-DD):").grid(row=1, column=0, padx=5, pady=5)
    date_entry = ctk.CTkEntry(input_frame)
    date_entry.grid(row=1, column=1, padx=5, pady=5)

    ctk.CTkLabel(input_frame, text="Location:").grid(row=2, column=0, padx=5, pady=5)
    location_entry = ctk.CTkEntry(input_frame)
    location_entry.grid(row=2, column=1, padx=5, pady=5)

    # Buttons
    button_frame = ctk.CTkFrame(root)
    button_frame.pack(pady=10)

    add_button = ctk.CTkButton(button_frame, text="Add Crime", command=add_crime)
    add_button.grid(row=0, column=0, padx=5, pady=5)

    update_button = ctk.CTkButton(button_frame, text="Update Crime", command=update_crime)
    update_button.grid(row=0, column=1, padx=5, pady=5)

    delete_button = ctk.CTkButton(button_frame, text="Delete Crime", command=delete_crime)
    delete_button.grid(row=0, column=2, padx=5, pady=5)

    populate_treeview()
    root.mainloop()

if __name__ == '__main__':
    main()