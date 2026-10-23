from tkinter import *
from tkinter import ttk, messagebox, filedialog
import sqlite3
import csv

class UltimateStudentSystem:
    def __init__(self, root):
        self.root = root
        self.root.geometry('1500x820+10+10')
        self.root.title('Enterprise Student Management System ')
        self.root.configure(background="#f8fafc")
        self.root.resizable(True, True)      

        # --- Initialize Database & Default Data ---
        self.create_db()

        # --- Top Header Frame ---
        header_frame = Frame(self.root, bg="#0f172a", height=75)
        header_frame.pack(side=TOP, fill=X)
        header_frame.pack_propagate(False)

        title_label = Label(
            header_frame, 
            text=' Student Management Information System', 
            bg="#0f172a", 
            fg="#f8fafc", 
            font=('Segoe UI', 16, 'bold')
        )
        title_label.pack(side=LEFT, padx=25, pady=18)

        # --- Dashboard Statistics Cards ---
        stats_frame = Frame(self.root, bg="#f8fafc")
        stats_frame.pack(side=TOP, fill=X, padx=20, pady=10)

        self.total_students_lbl = self.create_stat_card(stats_frame, "Total Registered Students", "0", "#3b82f6", 0)
        self.male_count_lbl = self.create_stat_card(stats_frame, "Male Students", "0", "#0284c7", 1)
        self.female_count_lbl = self.create_stat_card(stats_frame, "Female Students", "0", "#8b5cf6", 2)

        # --- Main Container Frame ---
        main_container = Frame(self.root, bg="#f8fafc")
        main_container.pack(fill=BOTH, expand=True, padx=20, pady=5)

        # --- Left Control & Input Panel (تم نقله إلى اليسار) ---
        Mange_Frame = Frame(main_container, bg='white', bd=1, relief=SOLID)
        Mange_Frame.pack(side=LEFT, fill=Y, padx=(0, 12), pady=0)
        Mange_Frame.config(width=410)
        Mange_Frame.pack_propagate(False)

        m_title = Label(
            Mange_Frame, 
            text='📋 Student Control Panel', 
            bg='#1e293b', 
            fg='white', 
            font=('Segoe UI', 12, 'bold')
        )
        m_title.pack(side=TOP, fill=X, ipady=8)

        fields_container = Frame(Mange_Frame, bg='white')
        fields_container.pack(fill=BOTH, expand=True, padx=15, pady=10)

        self.id_entry = self.create_input_field(fields_container, 'Student ID / Serial Number:')
        self.name_entry = self.create_input_field(fields_container, 'Full Student Name:')
        self.email_entry = self.create_input_field(fields_container, 'Email Address:')
        self.phone_entry = self.create_input_field(fields_container, 'Mobile Phone Number:')
        self.cert_entry = self.create_input_field(fields_container, 'Grade / Qualification:')

        # Gender Combobox
        lbl_gender = Label(fields_container, text='Gender:', bg='white', fg='#334155', font=('Segoe UI', 9, 'bold'))
        lbl_gender.pack(anchor='w', pady=(4, 1))
        
        self.combo_gender = ttk.Combobox(fields_container, font=('Segoe UI', 10), state='readonly')
        self.combo_gender['values'] = ('Male', 'Female')
        self.combo_gender.pack(fill=X, pady=(0, 8))

        # --- Action Buttons Frame ---
        btn_frame = Frame(fields_container, bg='white')
        btn_frame.pack(fill=X, pady=10)

        self.create_button(btn_frame, '➕ Add New Student', '#10b981', self.add_student, 0, 0)
        self.create_button(btn_frame, '✏️ Update Details', '#3b82f6', self.update_student, 1, 0)
        self.create_button(btn_frame, '🗑️ Delete Record', '#ef4444', self.delete_student, 2, 0)
        self.create_button(btn_frame, '🧹 Clear Fields', '#64748b', self.clear_fields, 3, 0)
        self.create_button(btn_frame, '📊 Export to CSV', '#f97316', self.export_csv, 4, 0)

        # --- Right Table & Search Display Frame (تم نقله إلى اليمين) ---
        Details_Frame = Frame(main_container, bg='white', bd=1, relief=SOLID)
        Details_Frame.pack(side=RIGHT, fill=BOTH, expand=True, pady=0)

        # Advanced Search Bar (معكوسة لتسيب جهة اليسار)
        search_frame = Frame(Details_Frame, bg='#f1f5f9', bd=1, relief=GROOVE)
        search_frame.pack(fill=X, padx=15, pady=12)

        lbl_search = Label(search_frame, text='🔍 Advanced Search:', bg='#f1f5f9', font=('Segoe UI', 10, 'bold'), fg='#334155')
        lbl_search.pack(side=LEFT, padx=10, pady=8)

        self.combo_search = ttk.Combobox(search_frame, font=('Segoe UI', 10), state='readonly', width=15)
        self.combo_search['values'] = ('Student Name', 'Phone Number', 'Student ID')
        self.combo_search.pack(side=LEFT, padx=5, pady=8)
        self.combo_search.current(0)

        self.search_entry = Entry(search_frame, font=('Segoe UI', 10), bd=1, relief=SOLID, justify='left', width=22)
        self.search_entry.pack(side=LEFT, padx=5, pady=8)

        search_btn = Button(search_frame, text='Search', bg='#0d9488', fg='white', font=('Segoe UI', 9, 'bold'), bd=0, padx=18, pady=2, command=self.search_data)
        search_btn.pack(side=LEFT, padx=5, pady=8)

        show_all_btn = Button(search_frame, text='Show All', bg='#64748b', fg='white', font=('Segoe UI', 9, 'bold'), bd=0, padx=15, pady=2, command=self.fetch_data)
        show_all_btn.pack(side=LEFT, padx=5, pady=8)

        # --- Professional Treeview Table with Scrollbars ---
        table_frame = Frame(Details_Frame, bg='white')
        table_frame.pack(fill=BOTH, expand=True, padx=15, pady=(0, 15))

        scroll_x = Scrollbar(table_frame, orient=HORIZONTAL)
        scroll_y = Scrollbar(table_frame, orient=VERTICAL)

        self.student_table = ttk.Treeview(
            table_frame, 
            columns=('id', 'name', 'email', 'phone', 'cert', 'gender'),
            xscrollcommand=scroll_x.set,
            yscrollcommand=scroll_y.set,
            height=20
        )

        scroll_x.pack(side=BOTTOM, fill=X)
        scroll_y.pack(side=RIGHT, fill=Y) # شريط التمرير أصبح على اليمين بالترتيب الإنجليزي

        scroll_x.config(command=self.student_table.xview)
        scroll_y.config(command=self.student_table.yview)

        # Table Column Headings
        self.student_table.heading('id', text='Student ID')
        self.student_table.heading('name', text='Full Name')
        self.student_table.heading('email', text='Email Address')
        self.student_table.heading('phone', text='Phone Number')
        self.student_table.heading('cert', text='Grade / Class')
        self.student_table.heading('gender', text='Gender')

        self.student_table['show'] = 'headings'

        self.student_table.column('id', width=100, anchor='center')
        self.student_table.column('name', width=210, anchor='center')
        self.student_table.column('email', width=210, anchor='center')
        self.student_table.column('phone', width=120, anchor='center')
        self.student_table.column('cert', width=140, anchor='center')
        self.student_table.column('gender', width=75, anchor='center')

        self.student_table.pack(fill=BOTH, expand=True)
        self.student_table.bind("<ButtonRelease-1>", self.get_cursor)

        # Zebra Striping Styles
        self.student_table.tag_configure('evenrow', background='#f8fafc')
        self.student_table.tag_configure('oddrow', background='#ffffff')

        # --- Bottom Status Bar ---
        self.status_bar = Label(
            self.root, 
            text='🟢 System loaded successfully with default records', 
            bg='#0f172a', 
            fg='#f8fafc', 
            font=('Segoe UI', 9), 
            anchor='w',  # محاذاة لليسار
            padx=15
        )
        self.status_bar.pack(side=BOTTOM, fill=X)

        # Load initial data
        self.fetch_data()

    # --- UI Helper Functions ---
    def create_stat_card(self, parent, title, value, color, col):
        card = Frame(parent, bg=color, bd=0, relief=FLAT)
        card.grid(row=0, column=col, padx=8, sticky='nsew')
        parent.grid_columnconfigure(col, weight=1)

        lbl_title = Label(card, text=title, bg=color, fg='white', font=('Segoe UI', 9, 'bold'))
        lbl_title.pack(pady=(6, 0))

        lbl_val = Label(card, text=value, bg=color, fg='white', font=('Segoe UI', 16, 'bold'))
        lbl_val.pack(pady=(0, 6))
        return lbl_val

    def create_input_field(self, parent, label_text):
        lbl = Label(parent, text=label_text, bg='white', fg='#334155', font=('Segoe UI', 9, 'bold'))
        lbl.pack(anchor='w', pady=(3, 1))
        entry = Entry(parent, font=('Segoe UI', 10), bd=1, relief=SOLID, justify='left')
        entry.pack(fill=X, pady=(0, 5))
        return entry

    def create_button(self, parent, text, bg_color, command, row, col):
        btn = Button(
            parent, 
            text=text, 
            bg=bg_color, 
            fg='white', 
            font=('Segoe UI', 9, 'bold'), 
            bd=0, 
            activebackground='#1e293b',
            activeforeground='white',
            command=command,
            padx=8,
            pady=5
        )
        btn.grid(row=row, column=col, padx=2, pady=3, sticky='nsew')
        parent.grid_rowconfigure(row, weight=1)
        parent.grid_columnconfigure(col, weight=1)

    # --- Database Operations & Sample Data ---
    def create_db(self):
        conn = sqlite3.connect('school_ultimate.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                cert TEXT,
                gender TEXT
            )
        ''')
        
        cursor.execute("SELECT COUNT(*) FROM students")
        count = cursor.fetchone()[0]
        if count == 0:
            sample_data = [
                ('1001', 'Ahmad Mohammad Abdullah', 'ahmad.m@school.jo', '0791234567', '10th Grade', 'Male'),
                ('1002', 'Sara Khaled Al-Omari', 'sara.k@school.jo', '0789876543', '11th Grade', 'Female'),
                ('1003', 'Omar Farouq Hassan', 'omar.f@school.jo', '0771122334', '12th Grade', 'Male'),
                ('1004', 'Fatima Al-Zahraa Ali', 'fatima.a@school.jo', '0798877665', '9th Grade', 'Female'),
                ('1005', 'Zaid Ibrahim Al-Titi', 'zaid.i@school.jo', '0785544332', '8th Grade', 'Male')
            ]
            cursor.executemany("INSERT INTO students VALUES (?, ?, ?, ?, ?, ?)", sample_data)
            conn.commit()
            
        conn.close()

    def fetch_data(self):
        conn = sqlite3.connect('school_ultimate.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM students")
        rows = cursor.fetchall()
        
        self.student_table.delete(*self.student_table.get_children())
        
        for index, row in enumerate(rows):
            row_tag = 'evenrow' if index % 2 == 0 else 'oddrow'
            self.student_table.insert('', END, values=row, tags=(row_tag,))
        
        conn.close()
        self.update_statistics()
        self.search_entry.delete(0, END)
        self.status_bar.config(text=f'🟢 View updated successfully. Total records: {len(rows)}')

    def update_statistics(self):
        conn = sqlite3.connect('school_ultimate.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM students")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM students WHERE gender='Male'")
        males = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM students WHERE gender='Female'")
        females = cursor.fetchone()[0]
        
        conn.close()

        self.total_students_lbl.config(text=str(total))
        self.male_count_lbl.config(text=str(males))
        self.female_count_lbl.config(text=str(females))

    def add_student(self):
        if self.id_entry.get() == "" or self.name_entry.get() == "":
            messagebox.showerror("Validation Error", "Student ID and Full Name fields are mandatory!", parent=self.root)
            return

        try:
            conn = sqlite3.connect('school_ultimate.db')
            cursor = conn.cursor()
            cursor.execute("INSERT INTO students VALUES (?, ?, ?, ?, ?, ?)", (
                self.id_entry.get(),
                self.name_entry.get(),
                self.email_entry.get(),
                self.phone_entry.get(),
                self.cert_entry.get(),
                self.combo_gender.get()
            ))
            conn.commit()
            conn.close()
            
            self.fetch_data()
            self.clear_fields()
            messagebox.showinfo("Success", "Student added successfully to the database.", parent=self.root)
        except sqlite3.IntegrityError:
            messagebox.showerror("Duplicate Error", "Student ID already exists. Please enter a unique ID!", parent=self.root)

    def update_student(self):
        selected_item = self.student_table.focus()
        if not selected_item:
            messagebox.showerror("Selection Error", "Please select a student record from the table to update.", parent=self.root)
            return

        conn = sqlite3.connect('school_ultimate.db')
        cursor = conn.cursor()
        cursor.execute("UPDATE students SET name=?, email=?, phone=?, cert=?, gender=? WHERE id=?", (
            self.name_entry.get(),
            self.email_entry.get(),
            self.phone_entry.get(),
            self.cert_entry.get(),
            self.combo_gender.get(),
            self.id_entry.get()
        ))
        conn.commit()
        conn.close()

        self.fetch_data()
        self.clear_fields()
        messagebox.showinfo("Success", "Student record updated successfully.", parent=self.root)

    def delete_student(self):
        selected_item = self.student_table.focus()
        if not selected_item:
            messagebox.showerror("Selection Error", "Please select a student record to delete.", parent=self.root)
            return

        if messagebox.askyesno("Confirm Deletion", "Are you sure you want to permanently delete this student record?", parent=self.root):
            conn = sqlite3.connect('school_ultimate.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM students WHERE id=?", (self.id_entry.get(),))
            conn.commit()
            conn.close()

            self.fetch_data()
            self.clear_fields()
            messagebox.showinfo("Success", "Student record deleted successfully.", parent=self.root)

    def clear_fields(self):
        self.id_entry.delete(0, END)
        self.name_entry.delete(0, END)
        self.email_entry.delete(0, END)
        self.phone_entry.delete(0, END)
        self.cert_entry.delete(0, END)
        self.combo_gender.set('')
        self.status_bar.config(text='🧹 Fields cleared. Ready for new input.')

    def get_cursor(self, event):
        cursor_row = self.student_table.focus()
        contents = self.student_table.item(cursor_row)
        row = contents['values']
        if row:
            self.clear_fields()
            self.id_entry.insert(0, row[0])
            self.name_entry.insert(0, row[1])
            self.email_entry.insert(0, row[2])
            self.phone_entry.insert(0, row[3])
            self.cert_entry.insert(0, row[4])
            self.combo_gender.set(row[5])
            self.status_bar.config(text=f'📌 Selected Student: {row[1]} (ID: {row[0]})')

    def search_data(self):
        search_val = self.search_entry.get().strip()
        if not search_val:
            messagebox.showwarning("Warning", "Please enter a search keyword.", parent=self.root)
            return

        column_map = {
            'Student Name': 'name',
            'Phone Number': 'phone',
            'Student ID': 'id'
        }
        selected_col = column_map.get(self.combo_search.get(), 'name')

        conn = sqlite3.connect('school_ultimate.db')
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM students WHERE {selected_col} LIKE ?", ('%' + search_val + '%',))
        rows = cursor.fetchall()

        self.student_table.delete(*self.student_table.get_children())
        for index, row in enumerate(rows):
            row_tag = 'evenrow' if index % 2 == 0 else 'oddrow'
            self.student_table.insert('', END, values=row, tags=(row_tag,))
        conn.close()
        self.status_bar.config(text=f'🔎 Search Results: Found {len(rows)} matching record(s).')

    def export_csv(self):
        try:
            file_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")])
            if not file_path:
                return
            
            conn = sqlite3.connect('school_ultimate.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM students")
            rows = cursor.fetchall()
            conn.close()

            with open(file_path, mode='w', newline='', encoding='utf-8-sig') as f:
                writer = csv.writer(f)
                writer.writerow(['Student ID', 'Full Name', 'Email Address', 'Phone Number', 'Grade / Class', 'Gender'])
                writer.writerows(rows)

            messagebox.showinfo("Export Successful", f"Student records exported successfully to:\n{file_path}", parent=self.root)
            self.status_bar.config(text='📊 Database records successfully exported to an external file.')
        except Exception as e:
            messagebox.showerror("Export Error", f"An error occurred during export: {str(e)}", parent=self.root)

root = Tk()
ob = UltimateStudentSystem(root)
root.mainloop()