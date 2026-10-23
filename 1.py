from tkinter import *
from tkinter import ttk, messagebox, filedialog
import sqlite3
import csv

class UltimateStudentSystem:
    def __init__(self, root):
        self.root = root
        self.root.geometry('1500x820+10+10')
        self.root.title('النظام الشامل لإدارة الطلاب والمدرسة ')
        self.root.configure(background="#f8fafc")
        self.root.resizable(True, True)      

        # --- إنشاء قاعدة البيانات والبيانات الافتراضية ---
        self.create_db()

        # --- شريط العنوان العلوي (Header) ---
        header_frame = Frame(self.root, bg="#0f172a", height=75)
        header_frame.pack(side=TOP, fill=X)
        header_frame.pack_propagate(False)

        title_label = Label(
            header_frame, 
            text=' نظام إدارة وتسجيل الطلاب الذكي - المؤسسة التعليمية', 
            bg="#0f172a", 
            fg="#f8fafc", 
            font=('Cairo', 18, 'bold')
        )
        title_label.pack(side=RIGHT, padx=25, pady=18)

        # --- لوحة الإحصائيات السريعة (Dashboard Widgets) ---
        stats_frame = Frame(self.root, bg="#f8fafc")
        stats_frame.pack(side=TOP, fill=X, padx=20, pady=10)

        self.total_students_lbl = self.create_stat_card(stats_frame, "إجمالي الطلاب المسجلين", "0", "#3b82f6", 0)
        self.male_count_lbl = self.create_stat_card(stats_frame, "الطلاب الذكور", "0", "#0284c7", 1)
        self.female_count_lbl = self.create_stat_card(stats_frame, "الطالبات الإناث", "0", "#8b5cf6", 2)

        # --- الحاوية الرئيسية ---
        main_container = Frame(self.root, bg="#f8fafc")
        main_container.pack(fill=BOTH, expand=True, padx=20, pady=5)

        # --- الإطار الجانبي للتحكم وإدخال البيانات (يمين) ---
        Mange_Frame = Frame(main_container, bg='white', bd=1, relief=SOLID)
        Mange_Frame.pack(side=RIGHT, fill=Y, padx=(12, 0), pady=0)
        Mange_Frame.config(width=410)
        Mange_Frame.pack_propagate(False)

        m_title = Label(
            Mange_Frame, 
            text='📋 لوحة تحكم بيانات الطالب', 
            bg='#1e293b', 
            fg='white', 
            font=('Cairo', 12, 'bold')
        )
        m_title.pack(side=TOP, fill=X, ipady=8)

        fields_container = Frame(Mange_Frame, bg='white')
        fields_container.pack(fill=BOTH, expand=True, padx=15, pady=10)

        self.id_entry = self.create_input_field(fields_container, 'الرقم التسلسلي (ID):')
        self.name_entry = self.create_input_field(fields_container, 'اسم الطالب الرباعي:')
        self.email_entry = self.create_input_field(fields_container, 'البريد الإلكتروني:')
        self.phone_entry = self.create_input_field(fields_container, 'رقم الهاتف المحمول:')
        self.cert_entry = self.create_input_field(fields_container, 'المؤهل / الصف الدراسي:')

        # قائمة الجنس
        lbl_gender = Label(fields_container, text='جنس الطالب:', bg='white', fg='#334155', font=('Cairo', 9, 'bold'))
        lbl_gender.pack(anchor='w', pady=(4, 1))
        
        self.combo_gender = ttk.Combobox(fields_container, font=('Cairo', 10), state='readonly')
        self.combo_gender['values'] = ('ذكر', 'أنثى')
        self.combo_gender.pack(fill=X, pady=(0, 8))

        # --- إطار الأزرار الأساسية ---
        btn_frame = Frame(fields_container, bg='white')
        btn_frame.pack(fill=X, pady=10)

        self.create_button(btn_frame, '➕ إضافة طالب جديد', '#10b981', self.add_student, 0, 0)
        self.create_button(btn_frame, '✏️ تعديل البيانات', '#3b82f6', self.update_student, 1, 0)
        self.create_button(btn_frame, '🗑️ حذف الطالب', '#ef4444', self.delete_student, 2, 0)
        self.create_button(btn_frame, '🧹 تفريغ الحقول', '#64748b', self.clear_fields, 3, 0)
        self.create_button(btn_frame, '📊 تصدير إلى ملف (CSV)', '#f97316', self.export_csv, 4, 0)

        # --- الإطار الأيسر لعرض الجدول والبحث ---
        Details_Frame = Frame(main_container, bg='white', bd=1, relief=SOLID)
        Details_Frame.pack(side=LEFT, fill=BOTH, expand=True, pady=0)

        # شريط البحث والفلترة المتقدم
        search_frame = Frame(Details_Frame, bg='#f1f5f9', bd=1, relief=GROOVE)
        search_frame.pack(fill=X, padx=15, pady=12)

        lbl_search = Label(search_frame, text='🔍 بحث متقدم:', bg='#f1f5f9', font=('Cairo', 10, 'bold'), fg='#334155')
        lbl_search.pack(side=RIGHT, padx=10, pady=8)

        self.combo_search = ttk.Combobox(search_frame, font=('Cairo', 10), state='readonly', width=14)
        self.combo_search['values'] = ('اسم الطالب', 'رقم الهاتف', 'الرقم التسلسلي')
        self.combo_search.pack(side=RIGHT, padx=5, pady=8)
        self.combo_search.current(0)

        self.search_entry = Entry(search_frame, font=('Cairo', 10), bd=1, relief=SOLID, justify='right', width=22)
        self.search_entry.pack(side=RIGHT, padx=5, pady=8)

        search_btn = Button(search_frame, text='بحث', bg='#0d9488', fg='white', font=('Cairo', 9, 'bold'), bd=0, padx=18, pady=2, command=self.search_data)
        search_btn.pack(side=RIGHT, padx=5, pady=8)

        show_all_btn = Button(search_frame, text='عرض الكل', bg='#64748b', fg='white', font=('Cairo', 9, 'bold'), bd=0, padx=15, pady=2, command=self.fetch_data)
        show_all_btn.pack(side=RIGHT, padx=5, pady=8)

        # --- الجدول الاحترافي مع دعم التخطيط والصفوف الملونة ---
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
        scroll_y.pack(side=LEFT, fill=Y)

        scroll_x.config(command=self.student_table.xview)
        scroll_y.config(command=self.student_table.yview)

        # تعريف أعمدة الجدول
        self.student_table.heading('id', text='الرقم التسلسلي')
        self.student_table.heading('name', text='اسم الطالب')
        self.student_table.heading('email', text='البريد الإلكتروني')
        self.student_table.heading('phone', text='رقم الهاتف')
        self.student_table.heading('cert', text='المؤهل / الصف')
        self.student_table.heading('gender', text='الجنس')

        self.student_table['show'] = 'headings'

        self.student_table.column('id', width=100, anchor='center')
        self.student_table.column('name', width=210, anchor='center')
        self.student_table.column('email', width=210, anchor='center')
        self.student_table.column('phone', width=120, anchor='center')
        self.student_table.column('cert', width=140, anchor='center')
        self.student_table.column('gender', width=75, anchor='center')

        self.student_table.pack(fill=BOTH, expand=True)
        self.student_table.bind("<ButtonRelease-1>", self.get_cursor)

        # إعداد أنماط ألوان الصفوف التبادلية (Zebra Striping) - ألوان ناعمة ومتناسقة
        self.student_table.tag_configure('evenrow', background='#f8fafc')
        self.student_table.tag_configure('oddrow', background='#ffffff')

        # --- شريط الحالة السفلي (Status Bar) ---
        self.status_bar = Label(
            self.root, 
            text='🟢 تم تحميل النظام مع الألوان المتناسقة بنجاح', 
            bg='#0f172a', 
            fg='#f8fafc', 
            font=('Cairo', 9), 
            anchor='e', 
            padx=15
        )
        self.status_bar.pack(side=BOTTOM, fill=X)

        # جلب البيانات عند البداية
        self.fetch_data()

    # --- دوال الواجهة والمساعدة ---
    def create_stat_card(self, parent, title, value, color, col):
        card = Frame(parent, bg=color, bd=0, relief=FLAT)
        card.grid(row=0, column=col, padx=8, sticky='nsew')
        parent.grid_columnconfigure(col, weight=1)

        lbl_title = Label(card, text=title, bg=color, fg='white', font=('Cairo', 9, 'bold'))
        lbl_title.pack(pady=(6, 0))

        lbl_val = Label(card, text=value, bg=color, fg='white', font=('Cairo', 16, 'bold'))
        lbl_val.pack(pady=(0, 6))
        return lbl_val

    def create_input_field(self, parent, label_text):
        lbl = Label(parent, text=label_text, bg='white', fg='#334155', font=('Cairo', 9, 'bold'))
        lbl.pack(anchor='w', pady=(3, 1))
        entry = Entry(parent, font=('Cairo', 10), bd=1, relief=SOLID, justify='right')
        entry.pack(fill=X, pady=(0, 5))
        return entry

    def create_button(self, parent, text, bg_color, command, row, col):
        btn = Button(
            parent, 
            text=text, 
            bg=bg_color, 
            fg='white', 
            font=('Cairo', 9, 'bold'), 
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

    # --- قاعدة البيانات والبيانات الافتراضية ---
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
                ('1001', 'أحمد محمد عبد الله', 'ahmad.m@school.jo', '0791234567', 'العاشر الأساسي', 'ذكر'),
                ('1002', 'سارة خالد العمري', 'sara.k@school.jo', '0789876543', 'الأول الثانوي', 'أنثى'),
                ('1003', 'عمر فاروق حسن', 'omar.f@school.jo', '0771122334', 'الثاني الثانوي', 'ذكر'),
                ('1004', 'فاطمة الزهراء علي', 'fatima.a@school.jo', '0798877665', 'التاسع الأساسي', 'أنثى'),
                ('1005', 'زيد إبراهيم الطيطي', 'zaid.i@school.jo', '0785544332', 'الثامن الأساسي', 'ذكر')
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
        self.status_bar.config(text=f'🟢 تم تحديث العرض بنجاح. إجمالي السجلات الحالية: {len(rows)}')

    def update_statistics(self):
        conn = sqlite3.connect('school_ultimate.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM students")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM students WHERE gender='ذكر'")
        males = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM students WHERE gender='أنثى'")
        females = cursor.fetchone()[0]
        
        conn.close()

        self.total_students_lbl.config(text=str(total))
        self.male_count_lbl.config(text=str(males))
        self.female_count_lbl.config(text=str(females))

    def add_student(self):
        if self.id_entry.get() == "" or self.name_entry.get() == "":
            messagebox.showerror("خطأ في البيانات", "الرجاء تعبئة حقل الرقم التسلسلي واسم الطالب إجباريًا!", parent=self.root)
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
            messagebox.showinfo("نجاح العملية", "تمت إضافة الطالب بنجاح وثبيته في قاعدة البيانات", parent=self.root)
        except sqlite3.IntegrityError:
            messagebox.showerror("خطأ تكرار", "الرقم التسلسلي (ID) مدخل مسبقًا لطالب آخر، يرجى اختيار رقم فريد!", parent=self.root)

    def update_student(self):
        selected_item = self.student_table.focus()
        if not selected_item:
            messagebox.showerror("تنبيه", "الرجاء النقر واختيار طالب من الجدول لتعديل بياناته", parent=self.root)
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
        messagebox.showinfo("نجاح", "تم تحديث بيانات الطالب بدقة", parent=self.root)

    def delete_student(self):
        selected_item = self.student_table.focus()
        if not selected_item:
            messagebox.showerror("تنبيه", "الرجاء تحديد طالب من الجدول للحذف", parent=self.root)
            return

        if messagebox.askyesno("تأكيد الحذف النهائي", "هل أنت متأكد تماماً من رغبتك في حذف هذا السجل من النظام؟", parent=self.root):
            conn = sqlite3.connect('school_ultimate.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM students WHERE id=?", (self.id_entry.get(),))
            conn.commit()
            conn.close()

            self.fetch_data()
            self.clear_fields()
            messagebox.showinfo("نجاح", "تم حذف السجل بنجاح", parent=self.root)

    def clear_fields(self):
        self.id_entry.delete(0, END)
        self.name_entry.delete(0, END)
        self.email_entry.delete(0, END)
        self.phone_entry.delete(0, END)
        self.cert_entry.delete(0, END)
        self.combo_gender.set('')
        self.status_bar.config(text='🧹 تم تفريغ الحقول وجاهز لإدخال بيانات جديدة')

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
            self.status_bar.config(text=f'📌 تم تحديد الطالب: {row[1]} (الرقم: {row[0]})')

    def search_data(self):
        search_val = self.search_entry.get().strip()
        if not search_val:
            messagebox.showwarning("تنبيه", "الرجاء إدخال نص للبحث عنه", parent=self.root)
            return

        column_map = {
            'اسم الطالب': 'name',
            'رقم الهاتف': 'phone',
            'الرقم التسلسلي': 'id'
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
        self.status_bar.config(text=f'🔎 نتائج البحث: تم العثور على {len(rows)} تطابق.')

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
                writer.writerow(['الرقم التسلسلي', 'اسم الطالب', 'البريد الإلكتروني', 'رقم الهاتف', 'المؤهل / الصف', 'الجنس'])
                writer.writerows(rows)

            messagebox.showinfo("تم التصدير بنجاح", f"تم حفظ تقرير الطلاب بنجاح في المسار:\n{file_path}", parent=self.root)
            self.status_bar.config(text='📊 تم تصدير بيانات النظام بنجاح إلى ملف خارجي.')
        except Exception as e:
            messagebox.showerror("خطأ في التصدير", f"حدث خطأ أثناء التصدير: {str(e)}", parent=self.root)

root = Tk()
ob = UltimateStudentSystem(root)
root.mainloop()