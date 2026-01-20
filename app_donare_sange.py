import tkinter as tk
from tkinter import ttk, messagebox
import pyodbc
import pandas as pd
from datetime import datetime, date
import calendar
from tkcalendar import DateEntry  # Pentru calendar

# CONEXIUNE AZURE SQL
server = 'sqlsbd.database.windows.net'
database = 'BD_DonareSange'
username = 'adminstudent'  
password = 'Parola123!'  
driver = '{ODBC Driver 18 for SQL Server}'

conn_str = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}'

def get_connection():
    """Creeaza si returneaza o conexiune la baza de date."""
    try:
        server = 'sqlsbd.database.windows.net'
        database = 'BD_DonareSange'
        username = 'adminstudent'
        password = 'Parola123!'  
        driver = '{ODBC Driver 18 for SQL Server}'  
        
        conn_str = f'DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
        
        conn = pyodbc.connect(conn_str)
        return conn
        
    except Exception as e:
        print(f"EROARE CONEXIUNE DETAILS: {str(e)}")
        messagebox.showerror("Eroare conexiune", 
                           f"Nu ma pot conecta la baza de date:\n{str(e)[:200]}\n\nVerifica:\n1. Parola este corecta\n2. Driver ODBC 18 este instalat\n3. IP-ul este permis in Azure Firewall")
        return None

# FEREASTRA PRINCIPALA
class BloodDonationApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Platforma de Donare Sange")
        self.root.geometry("1200x700")
        self.root.configure(bg='#ffe6f2')
        
        # Stiluri pentru widget-uri
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Culori
        self.color_bg = '#ffe6f2'
        self.color_fg = '#99004d'
        self.color_button = '#ff66b3'
        self.color_button_text = 'white'
        self.color_listbox = '#fff0f7'
        
        # Configurare stiluri
        self.style.configure('TLabel', background=self.color_bg, foreground=self.color_fg, font=('Arial', 10))
        self.style.configure('TButton', background=self.color_button, foreground=self.color_button_text, font=('Arial', 10, 'bold'))
        self.style.map('TButton', background=[('active', '#ff3385')])
        
        # Frame pentru titlu
        title_frame = tk.Frame(root, bg='#ff66b3', height=80)
        title_frame.pack(fill=tk.X)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, text="🏥 PLATFORMA DE DONARE SANGE", 
                               font=('Arial', 24, 'bold'), 
                               bg='#ff66b3', fg='white')
        title_label.pack(expand=True)
        
        # Frame principal (meniu + continut)
        main_frame = tk.Frame(root, bg=self.color_bg)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Meniu lateral
        menu_frame = tk.Frame(main_frame, bg='#ffb3d9', width=200, relief=tk.RAISED, borderwidth=2)
        menu_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 20))
        menu_frame.pack_propagate(False)
        
        menu_title = tk.Label(menu_frame, text="MENIU", font=('Arial', 14, 'bold'), 
                             bg='#ff66b3', fg='white', width=20)
        menu_title.pack(pady=10, padx=5)
        
        # Butoane meniu
        menu_buttons = [
            ("👥 Donatori", self.show_donors),
            ("🏥 Boli Restrictive", self.show_diseases),
            ("🩸 Analize Medicale", self.show_analyses),
            ("📅 Programari", self.show_appointments),
            ("💉 Donatii", self.show_donations),
            ("📊 Stoc Sange", self.show_stock),
            ("📈 Rapoarte", self.show_reports),
            ("🚪 Iesire", self.root.quit)
        ]
        
        for text, command in menu_buttons:
            btn = ttk.Button(menu_frame, text=text, command=command, width=20)
            btn.pack(pady=5, padx=10)
        
        # Frame pentru continut
        self.content_frame = tk.Frame(main_frame, bg=self.color_bg)
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Afiseaza donatorii la start
        self.show_donors()
    
    def clear_content(self):
        """sterge tot continutul din frame-ul de continut."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    # ==================== DONATORI ====================
    def show_donors(self):
        """Afiseaza interfata pentru gestionarea donatorilor."""
        self.clear_content()
        
        # Titlu
        title = tk.Label(self.content_frame, text="GESTIONARE DONATORI", 
                        font=('Arial', 18, 'bold'), bg=self.color_bg, fg=self.color_fg)
        title.pack(pady=(0, 20))
        
        # Frame pentru butoane
        button_frame = tk.Frame(self.content_frame, bg=self.color_bg)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Adauga Donator", command=self.add_donor_window).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Actualizeaza", command=self.load_donors).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Exporta CSV", command=self.export_donors_csv).pack(side=tk.LEFT, padx=5)
        
        # Frame pentru cautare
        search_frame = tk.Frame(self.content_frame, bg=self.color_bg)
        search_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(search_frame, text="Cauta dupa nume:", bg=self.color_bg, fg=self.color_fg).pack(side=tk.LEFT, padx=5)
        self.search_entry = ttk.Entry(search_frame, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Cauta", command=self.search_donors).pack(side=tk.LEFT, padx=5)
        ttk.Button(search_frame, text="Reseteaza", command=self.load_donors).pack(side=tk.LEFT, padx=5)
        
        # Tabel pentru afisare
        columns = ('ID', 'Nume', 'Prenume', 'CNP', 'Gen', 'Grupa', 'Eligibil', 'Telefon', 'Email')
        self.donor_tree = ttk.Treeview(self.content_frame, columns=columns, show='headings', height=15)
        
        # Setare antete
        col_widths = [50, 100, 100, 120, 50, 70, 70, 100, 150]
        for col, width in zip(columns, col_widths):
            self.donor_tree.heading(col, text=col)
            self.donor_tree.column(col, width=width, anchor=tk.CENTER)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(self.content_frame, orient=tk.VERTICAL, command=self.donor_tree.yview)
        self.donor_tree.configure(yscrollcommand=scrollbar.set)
        self.donor_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Butoane pentru selectie
        action_frame = tk.Frame(self.content_frame, bg=self.color_bg)
        action_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(action_frame, text="Editeaza", command=self.edit_donor).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="sterge", command=self.delete_donor).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Vezi Analize", command=self.view_donor_analyses).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Vezi Boli", command=self.view_donor_diseases).pack(side=tk.LEFT, padx=5)
        
        # incarca datele
        self.load_donors()
    
    def load_donors(self, search_term=None):
        """incarca donatorii in tabel."""
        for item in self.donor_tree.get_children():
            self.donor_tree.delete(item)
    
        conn = get_connection()
        if conn is None:
            return
    
        cursor = conn.cursor()
        try:
            if search_term:
                cursor.execute("""
                    SELECT IDDonator, Nume, Prenume, CNP, Gen, GrupaSanguina, 
                           CASE WHEN EsteEligibil = 1 THEN 'DA' ELSE 'NU' END, 
                           Telefon, Email 
                    FROM Donatori 
                    WHERE Nume LIKE ? OR Prenume LIKE ?
                    ORDER BY Nume, Prenume
                """, f'%{search_term}%', f'%{search_term}%')
            else:
                cursor.execute("""
                    SELECT IDDonator, Nume, Prenume, CNP, Gen, GrupaSanguina, 
                           CASE WHEN EsteEligibil = 1 THEN 'DA' ELSE 'NU' END, 
                           Telefon, Email 
                    FROM Donatori 
                    ORDER BY Nume, Prenume
                """)
        
            rows = cursor.fetchall()
        
            for row in rows:
                row_values = []
                for value in row:
                    if value is None:
                        row_values.append('')
                    else:
                        row_values.append(str(value))
                self.donor_tree.insert('', tk.END, values=row_values)
        
            status = f"Afisati {len(rows)} donatori" + (" (filtrat)" if search_term else "")
            self.show_status(status)
        
        except Exception as e:
            messagebox.showerror("Eroare", f"Eroare la incarcarea donatorilor:\n{str(e)}")
        finally:
            cursor.close()
            conn.close()
    
    def search_donors(self):
        """Cauta donatori dupa nume."""
        search_term = self.search_entry.get().strip()
        if search_term:
            self.load_donors(search_term)
        else:
            self.load_donors()
    
    def add_donor_window(self):
        """Deschide fereastra pentru adaugare donator."""
        window = tk.Toplevel(self.root)
        window.title("Adauga Donator Nou")
        window.geometry("500x600")
        window.configure(bg=self.color_bg)
        window.grab_set()
        
        tk.Label(window, text="DATE DONATOR NOU", font=('Arial', 16, 'bold'), 
                bg=self.color_bg, fg=self.color_fg).pack(pady=20)
        
        form_frame = tk.Frame(window, bg=self.color_bg)
        form_frame.pack(padx=40, pady=10)
        
        fields = [
            ("Nume*", "nume"),
            ("Prenume*", "prenume"),
            ("CNP* (13 cifre)", "cnp"),
            ("Data Nasterii* (YYYY-MM-DD)", "data_nasterii"),
            ("Telefon", "telefon"),
            ("Email", "email"),
            ("Adresa", "adresa")
        ]
        
        self.donor_entries = {}
        for i, (label, key) in enumerate(fields):
            tk.Label(form_frame, text=label, bg=self.color_bg, fg=self.color_fg, 
                    font=('Arial', 10)).grid(row=i, column=0, sticky=tk.W, pady=8)
            entry = ttk.Entry(form_frame, width=40)
            entry.grid(row=i, column=1, pady=8, padx=10)
            self.donor_entries[key] = entry
        
        tk.Label(form_frame, text="Gen*", bg=self.color_bg, fg=self.color_fg, 
                font=('Arial', 10)).grid(row=len(fields), column=0, sticky=tk.W, pady=8)
        gender_frame = tk.Frame(form_frame, bg=self.color_bg)
        gender_frame.grid(row=len(fields), column=1, pady=8, sticky=tk.W)
        
        self.gender_var = tk.StringVar(value="M")
        tk.Radiobutton(gender_frame, text="Masculin", variable=self.gender_var, 
                      value="M", bg=self.color_bg).pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(gender_frame, text="Feminin", variable=self.gender_var, 
                      value="F", bg=self.color_bg).pack(side=tk.LEFT, padx=10)
        
        tk.Label(form_frame, text="Grupa Sanguina*", bg=self.color_bg, fg=self.color_fg, 
                font=('Arial', 10)).grid(row=len(fields)+1, column=0, sticky=tk.W, pady=8)
        self.blood_group_var = tk.StringVar()
        blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', '0+', '0-']
        blood_combo = ttk.Combobox(form_frame, textvariable=self.blood_group_var, 
                                  values=blood_groups, width=37)
        blood_combo.grid(row=len(fields)+1, column=1, pady=8, padx=10)
        blood_combo.current(0)
        
        button_frame = tk.Frame(window, bg=self.color_bg)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Salveaza", command=lambda: self.save_donor(window)).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Anuleaza", command=window.destroy).pack(side=tk.LEFT, padx=10)
    
    def save_donor(self, window):
        """Salveaza donatorul nou in baza de date."""
        required = ['nume', 'prenume', 'cnp', 'data_nasterii']
        for field in required:
            if not self.donor_entries[field].get().strip():
                messagebox.showwarning("Validare", f"Campul '{field}' este obligatoriu!")
                return
        
        cnp = self.donor_entries['cnp'].get().strip()
        if not (len(cnp) == 13 and cnp.isdigit()):
            messagebox.showwarning("Validare", "CNP-ul trebuie sa aiba 13 cifre!")
            return
        
        conn = get_connection()
        if conn is None:
            return
        
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO Donatori (Nume, Prenume, CNP, DataNasterii, Gen, GrupaSanguina, 
                                    Telefon, Email, Adresa, DataInregistrarii)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, GETDATE())
            """, (
                self.donor_entries['nume'].get().strip(),
                self.donor_entries['prenume'].get().strip(),
                cnp,
                self.donor_entries['data_nasterii'].get().strip(),
                self.gender_var.get(),
                self.blood_group_var.get(),
                self.donor_entries['telefon'].get().strip() or None,
                self.donor_entries['email'].get().strip() or None,
                self.donor_entries['adresa'].get().strip() or None
            ))
            
            conn.commit()
            messagebox.showinfo("Succes", "Donator adaugat cu succes!")
            window.destroy()
            self.load_donors()
            
        except pyodbc.IntegrityError:
            messagebox.showerror("Eroare", "CNP-ul exista deja in sistem!")
        except Exception as e:
            messagebox.showerror("Eroare", f"Eroare la salvare:\n{str(e)}")
        finally:
            cursor.close()
            conn.close()
    
    def edit_donor(self):
        """Editeaza donatorul selectat."""
        selection = self.donor_tree.selection()
        if not selection:
            messagebox.showwarning("Selectie", "Selecteaza un donator din lista!")
            return
    
        item = self.donor_tree.item(selection[0])
        values = item['values']
    
        if not values:
            messagebox.showerror("Eroare", "Nu s-au gasit date pentru donatorul selectat!")
            return
    
        donor_id = values[0]
        if donor_id is None:
            messagebox.showerror("Eroare", "ID-ul donatorului este NULL!")
            return
    
        try:
            donor_id_int = int(donor_id)
        except (ValueError, TypeError) as e:
            messagebox.showerror("Eroare", f"ID invalid pentru donator: {donor_id}")
            return
        
        self.edit_donor_window(donor_id_int)
    
    def edit_donor_window(self, donor_id):
        """Fereastra pentru editare donator."""
        conn = get_connection()
        if conn is None:
            return
        
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT Nume, Prenume, CNP, DataNasterii, Gen, GrupaSanguina, 
                       Telefon, Email, Adresa, EsteEligibil
                FROM Donatori 
                WHERE IDDonator = ?
            """, donor_id)
            row = cursor.fetchone()
            
            if not row:
                messagebox.showerror("Eroare", "Donatorul nu a fost gasit!")
                return
                
        except Exception as e:
            messagebox.showerror("Eroare", f"Eroare la incarcare:\n{str(e)}")
            return
        finally:
            cursor.close()
            conn.close()
        
        window = tk.Toplevel(self.root)
        window.title(f"Editare Donator ID: {donor_id}")
        window.geometry("500x650")
        window.configure(bg=self.color_bg)
        window.grab_set()
        
        tk.Label(window, text="EDITARE DONATOR", font=('Arial', 16, 'bold'), 
                bg=self.color_bg, fg=self.color_fg).pack(pady=20)
        
        form_frame = tk.Frame(window, bg=self.color_bg)
        form_frame.pack(padx=40, pady=10)
        
        fields = [
            ("Nume*", "nume", row[0]),
            ("Prenume*", "prenume", row[1]),
            ("CNP* (13 cifre)", "cnp", row[2]),
            ("Data Nasterii* (YYYY-MM-DD)", "data_nasterii", str(row[3])),
            ("Telefon", "telefon", row[6] or ""),
            ("Email", "email", row[7] or ""),
            ("Adresa", "adresa", row[8] or "")
        ]
        
        self.edit_entries = {}
        for i, (label, key, value) in enumerate(fields):
            tk.Label(form_frame, text=label, bg=self.color_bg, fg=self.color_fg).grid(row=i, column=0, sticky=tk.W, pady=8)
            entry = ttk.Entry(form_frame, width=40)
            entry.insert(0, value)
            entry.grid(row=i, column=1, pady=8, padx=10)
            self.edit_entries[key] = entry
        
        tk.Label(form_frame, text="Gen*", bg=self.color_bg, fg=self.color_fg).grid(row=len(fields), column=0, sticky=tk.W, pady=8)
        gender_frame = tk.Frame(form_frame, bg=self.color_bg)
        gender_frame.grid(row=len(fields), column=1, pady=8, sticky=tk.W)
        
        self.edit_gender_var = tk.StringVar(value=row[4])
        tk.Radiobutton(gender_frame, text="Masculin", variable=self.edit_gender_var, 
                      value="M", bg=self.color_bg).pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(gender_frame, text="Feminin", variable=self.edit_gender_var, 
                      value="F", bg=self.color_bg).pack(side=tk.LEFT, padx=10)
        
        tk.Label(form_frame, text="Grupa Sanguina*", bg=self.color_bg, fg=self.color_fg).grid(row=len(fields)+1, column=0, sticky=tk.W, pady=8)
        self.edit_blood_var = tk.StringVar(value=row[5])
        blood_combo = ttk.Combobox(form_frame, textvariable=self.edit_blood_var, 
                                  values=['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', '0+', '0-'], width=37)
        blood_combo.grid(row=len(fields)+1, column=1, pady=8, padx=10)
        
        tk.Label(form_frame, text="Eligibil", bg=self.color_bg, fg=self.color_fg).grid(row=len(fields)+2, column=0, sticky=tk.W, pady=8)
        self.eligible_var = tk.BooleanVar(value=row[9] == 1)
        tk.Checkbutton(form_frame, variable=self.eligible_var, bg=self.color_bg).grid(row=len(fields)+2, column=1, sticky=tk.W, pady=8)
        
        button_frame = tk.Frame(window, bg=self.color_bg)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Salveaza Modificari", 
                  command=lambda: self.update_donor(donor_id, window)).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Anuleaza", command=window.destroy).pack(side=tk.LEFT, padx=10)
    
    def update_donor(self, donor_id, window):
        """Actualizeaza donatorul in baza de date."""
        conn = get_connection()
        if conn is None:
            return
        
        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE Donatori 
                SET Nume = ?, Prenume = ?, CNP = ?, DataNasterii = ?, 
                    Gen = ?, GrupaSanguina = ?, Telefon = ?, Email = ?, 
                    Adresa = ?, EsteEligibil = ?
                WHERE IDDonator = ?
            """, (
                self.edit_entries['nume'].get().strip(),
                self.edit_entries['prenume'].get().strip(),
                self.edit_entries['cnp'].get().strip(),
                self.edit_entries['data_nasterii'].get().strip(),
                self.edit_gender_var.get(),
                self.edit_blood_var.get(),
                self.edit_entries['telefon'].get().strip() or None,
                self.edit_entries['email'].get().strip() or None,
                self.edit_entries['adresa'].get().strip() or None,
                1 if self.eligible_var.get() else 0,
                donor_id
            ))
            
            conn.commit()
            messagebox.showinfo("Succes", "Donator actualizat cu succes!")
            window.destroy()
            self.load_donors()
            
        except Exception as e:
            messagebox.showerror("Eroare", f"Eroare la actualizare:\n{str(e)}")
        finally:
            cursor.close()
            conn.close()
    
    def delete_donor(self):
        """sterge donatorul selectat."""
        selection = self.donor_tree.selection()
        if not selection:
            messagebox.showwarning("Selectie", "Selecteaza un donator din lista!")
            return
        
        item = self.donor_tree.item(selection[0])
        donor_id, nume, prenume = item['values'][0], item['values'][1], item['values'][2]
        
        confirm = messagebox.askyesno("Confirmare", 
                                     f"Esti sigur ca vrei sa stergi donatorul:\n{nume} {prenume}?\n\nAceasta actiune va sterge si toate datele asociate!")
        
        if not confirm:
            return
        
        conn = get_connection()
        if conn is None:
            return
        
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM Donatori WHERE IDDonator = ?", donor_id)
            conn.commit()
            messagebox.showinfo("Succes", "Donator sters cu succes!")
            self.load_donors()
            
        except Exception as e:
            messagebox.showerror("Eroare", f"Eroare la stergere:\n{str(e)}")
        finally:
            cursor.close()
            conn.close()
    
    def view_donor_analyses(self):
        """Afiseaza analizele donatorului selectat."""
        selection = self.donor_tree.selection()
        if not selection:
            messagebox.showwarning("Selectie", "Selecteaza un donator din lista!")
            return
        
        item = self.donor_tree.item(selection[0])
        donor_id, nume, prenume = item['values'][0], item['values'][1], item['values'][2]
        
        # Deschide fereastra cu analizele donatorului
        self.show_donor_analyses_window(donor_id, f"{nume} {prenume}")
    
    def view_donor_diseases(self):
        """Afiseaza bolile donatorului selectat."""
        selection = self.donor_tree.selection()
        if not selection:
            return
        
        item = self.donor_tree.item(selection[0])
        donor_id, nume, prenume = item['values'][0], item['values'][1], item['values'][2]
        
        # Deschide fereastra cu bolile donatorului
        self.show_donor_diseases_window(donor_id, f"{nume} {prenume}")
    
    def export_donors_csv(self):
        """Exporta donatorii in fisier CSV."""
        conn = get_connection()
        if conn is None:
            return
        
        try:
            df = pd.read_sql("SELECT * FROM Donatori", conn)
            df.to_csv('donatori_export.csv', index=False, encoding='utf-8')
            messagebox.showinfo("Export", "Datele au fost exportate in 'donatori_export.csv'")
        except Exception as e:
            messagebox.showerror("Eroare", f"Eroare la export:\n{str(e)}")
        finally:
            conn.close()
    
    # ==================== BOLI RESTRICTIVE ====================
    def show_diseases(self):
        """Afiseaza interfata pentru gestionarea bolilor restrictive."""
        self.clear_content()
        
        title = tk.Label(self.content_frame, text="GESTIONARE BOLI RESTRICTIVE", 
                        font=('Arial', 18, 'bold'), bg=self.color_bg, fg=self.color_fg)
        title.pack(pady=(0, 20))
        
        button_frame = tk.Frame(self.content_frame, bg=self.color_bg)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Adauga Boala", command=self.add_disease_window).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Actualizeaza", command=self.load_diseases).pack(side=tk.LEFT, padx=5)
        
        columns = ('ID', 'Denumire', 'Descriere')
        self.disease_tree = ttk.Treeview(self.content_frame, columns=columns, show='headings', height=15)
        
        col_widths = [50, 200, 300]
        for col, width in zip(columns, col_widths):
            self.disease_tree.heading(col, text=col)
            self.disease_tree.column(col, width=width, anchor=tk.W)
        
        scrollbar = ttk.Scrollbar(self.content_frame, orient=tk.VERTICAL, command=self.disease_tree.yview)
        self.disease_tree.configure(yscrollcommand=scrollbar.set)
        self.disease_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        action_frame = tk.Frame(self.content_frame, bg=self.color_bg)
        action_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(action_frame, text="Editeaza", command=self.edit_disease).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="sterge", command=self.delete_disease).pack(side=tk.LEFT, padx=5)
        
        self.load_diseases()
    
    def load_diseases(self):
        """incarca bolile in tabel."""
        for item in self.disease_tree.get_children():
            self.disease_tree.delete(item)
    
        conn = get_connection()
        if conn is None:
            return
    
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT IDBoala, Denumire, Descriere FROM BoliRestrictive ORDER BY Denumire")
            rows = cursor.fetchall()
        
            for row in rows:
                row_values = []
                for value in row:
                    if value is None:
                        row_values.append('')
                    else:
                        row_values.append(str(value))
                self.disease_tree.insert('', tk.END, values=row_values)
        
            self.show_status(f"Afisate {len(rows)} boli restrictive")
        
        except Exception as e:
            messagebox.showerror("Eroare", f"Eroare la incarcarea bolilor:\n{str(e)}")
        finally:
            cursor.close()
            conn.close()
    
    def add_disease_window(self):
        """Fereastra pentru adaugare boala."""
        window = tk.Toplevel(self.root)
        window.title("Adauga Boala Restrictiva")
        window.geometry("500x300")
        window.configure(bg=self.color_bg)
        window.grab_set()
        
        tk.Label(window, text="ADAUGARE BOALA RESTRICTIVA", font=('Arial', 16, 'bold'), 
                bg=self.color_bg, fg=self.color_fg).pack(pady=20)
        
        form_frame = tk.Frame(window, bg=self.color_bg)
        form_frame.pack(padx=40, pady=10)
        
        tk.Label(form_frame, text="Denumire*:", bg=self.color_bg, fg=self.color_fg).grid(row=0, column=0, sticky=tk.W, pady=8)
        disease_name_entry = ttk.Entry(form_frame, width=40)
        disease_name_entry.grid(row=0, column=1, pady=8, padx=10)
        
        tk.Label(form_frame, text="Descriere:", bg=self.color_bg, fg=self.color_fg).grid(row=1, column=0, sticky=tk.W, pady=8)
        disease_desc_text = tk.Text(form_frame, width=40, height=5)
        disease_desc_text.grid(row=1, column=1, pady=8, padx=10)
        
        def save_disease():
            denumire = disease_name_entry.get().strip()
            if not denumire:
                messagebox.showwarning("Validare", "Denumirea este obligatorie!")
                return
            
            descriere = disease_desc_text.get("1.0", tk.END).strip()
            
            conn = get_connection()
            if conn is None:
                return
            
            cursor = conn.cursor()
            try:
                cursor.execute("INSERT INTO BoliRestrictive (Denumire, Descriere) VALUES (?, ?)", 
                             (denumire, descriere if descriere else None))
                conn.commit()
                messagebox.showinfo("Succes", "Boala adaugata cu succes!")
                window.destroy()
                self.load_diseases()
            except Exception as e:
                messagebox.showerror("Eroare", f"Eroare la salvare:\n{str(e)}")
            finally:
                cursor.close()
                conn.close()
        
        button_frame = tk.Frame(window, bg=self.color_bg)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Salveaza", command=save_disease).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Anuleaza", command=window.destroy).pack(side=tk.LEFT, padx=10)
    
    def edit_disease(self):
        """Editeaza boala selectata."""
        selection = self.disease_tree.selection()
        if not selection:
            messagebox.showwarning("Selectie", "Selecteaza o boala din lista!")
            return
    
        item = self.disease_tree.item(selection[0])
        values = item['values']
    
        if not values or len(values) < 1:
            return
    
        try:
            disease_id = int(values[0])
        except:
            messagebox.showerror("Eroare", "ID invalid!")
            return
        
        self.edit_disease_window(disease_id, values[1], values[2] if len(values) > 2 else "")
    
    def edit_disease_window(self, disease_id, denumire, descriere):
        """Fereastra pentru editare boala."""
        window = tk.Toplevel(self.root)
        window.title(f"Editare Boala ID: {disease_id}")
        window.geometry("500x300")
        window.configure(bg=self.color_bg)
        window.grab_set()
        
        tk.Label(window, text="EDITARE BOALA RESTRICTIVA", font=('Arial', 16, 'bold'), 
                bg=self.color_bg, fg=self.color_fg).pack(pady=20)
        
        form_frame = tk.Frame(window, bg=self.color_bg)
        form_frame.pack(padx=40, pady=10)
        
        tk.Label(form_frame, text="Denumire*:", bg=self.color_bg, fg=self.color_fg).grid(row=0, column=0, sticky=tk.W, pady=8)
        disease_name_entry = ttk.Entry(form_frame, width=40)
        disease_name_entry.insert(0, denumire)
        disease_name_entry.grid(row=0, column=1, pady=8, padx=10)
        
        tk.Label(form_frame, text="Descriere:", bg=self.color_bg, fg=self.color_fg).grid(row=1, column=0, sticky=tk.W, pady=8)
        disease_desc_text = tk.Text(form_frame, width=40, height=5)
        disease_desc_text.insert("1.0", descriere)
        disease_desc_text.grid(row=1, column=1, pady=8, padx=10)
        
        def update_disease():
            new_denumire = disease_name_entry.get().strip()
            if not new_denumire:
                messagebox.showwarning("Validare", "Denumirea este obligatorie!")
                return
            
            new_descriere = disease_desc_text.get("1.0", tk.END).strip()
            
            conn = get_connection()
            if conn is None:
                return
            
            cursor = conn.cursor()
            try:
                cursor.execute("UPDATE BoliRestrictive SET Denumire = ?, Descriere = ? WHERE IDBoala = ?", 
                             (new_denumire, new_descriere if new_descriere else None, disease_id))
                conn.commit()
                messagebox.showinfo("Succes", "Boala actualizata cu succes!")
                window.destroy()
                self.load_diseases()
            except Exception as e:
                messagebox.showerror("Eroare", f"Eroare la actualizare:\n{str(e)}")
            finally:
                cursor.close()
                conn.close()
        
        button_frame = tk.Frame(window, bg=self.color_bg)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Salveaza Modificari", command=update_disease).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Anuleaza", command=window.destroy).pack(side=tk.LEFT, padx=10)
    
    def delete_disease(self):
        """sterge boala selectata."""
        selection = self.disease_tree.selection()
        if not selection:
            messagebox.showwarning("Selectie", "Selecteaza o boala din lista!")
            return
        
        item = self.disease_tree.item(selection[0])
        disease_id, denumire = item['values'][0], item['values'][1]
        
        confirm = messagebox.askyesno("Confirmare", 
                                     f"Esti sigur ca vrei sa stergi boala:\n{denumire}?\n\nAceasta actiune va sterge si asocierea cu donatorii!")
        
        if not confirm:
            return
        
        conn = get_connection()
        if conn is None:
            return
        
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM BoliRestrictive WHERE IDBoala = ?", disease_id)
            conn.commit()
            messagebox.showinfo("Succes", "Boala stearsa cu succes!")
            self.load_diseases()
        except Exception as e:
            messagebox.showerror("Eroare", f"Eroare la stergere:\n{str(e)}")
        finally:
            cursor.close()
            conn.close()
    
    def show_donor_diseases_window(self, donor_id, donor_name):
        """Afiseaza bolile unui donator."""
        window = tk.Toplevel(self.root)
        window.title(f"Boli Restrictive - {donor_name}")
        window.geometry("600x400")
        window.configure(bg=self.color_bg)
        window.grab_set()
        
        tk.Label(window, text=f"BOLI RESTRICTIVE - {donor_name}", font=('Arial', 16, 'bold'), 
                bg=self.color_bg, fg=self.color_fg).pack(pady=20)
        
        # Frame pentru adaugare boala
        add_frame = tk.Frame(window, bg=self.color_bg)
        add_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(add_frame, text="Adauga boala:", bg=self.color_bg, fg=self.color_fg).pack(side=tk.LEFT, padx=5)
        
        # Combobox cu toate bolile
        conn = get_connection()
        if conn is None:
            window.destroy()
            return
        
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT IDBoala, Denumire FROM BoliRestrictive ORDER BY Denumire")
            diseases = cursor.fetchall()
            disease_dict = {f"{d[1]} (ID:{d[0]})": d[0] for d in diseases}
            
            disease_var = tk.StringVar()
            disease_combo = ttk.Combobox(add_frame, textvariable=disease_var, 
                                        values=list(disease_dict.keys()), width=30)
            disease_combo.pack(side=tk.LEFT, padx=5)
            
            tk.Label(add_frame, text="Data diagnostic (YYYY-MM-DD):", bg=self.color_bg, fg=self.color_fg).pack(side=tk.LEFT, padx=5)
            date_entry = ttk.Entry(add_frame, width=15)
            date_entry.insert(0, date.today().strftime("%Y-%m-%d"))
            date_entry.pack(side=tk.LEFT, padx=5)
            
            def add_disease_to_donor():
                selected = disease_var.get()
                if not selected:
                    messagebox.showwarning("Validare", "Selecteaza o boala!")
                    return
                
                diag_date = date_entry.get().strip()
                if not diag_date:
                    messagebox.showwarning("Validare", "Data diagnostic este obligatorie!")
                    return
                
                disease_id = disease_dict[selected]
                
                try:
                    cursor.execute("""
                        INSERT INTO DonatoriBoli (IDDonator, IDBoala, DataDiagnostic)
                        VALUES (?, ?, ?)
                    """, (donor_id, disease_id, diag_date))
                    conn.commit()
                    messagebox.showinfo("Succes", "Boala asociata cu succes!")
                    load_donor_diseases()
                    disease_var.set('')
                except pyodbc.IntegrityError:
                    messagebox.showerror("Eroare", "Aceasta boala este deja asociata donatorului!")
                except Exception as e:
                    messagebox.showerror("Eroare", f"Eroare la asociere:\n{str(e)}")
            
            ttk.Button(add_frame, text="Adauga", command=add_disease_to_donor).pack(side=tk.LEFT, padx=10)
            
        except Exception as e:
            messagebox.showerror("Eroare", f"Eroare la incarcarea bolilor:\n{str(e)}")
            cursor.close()
            conn.close()
            window.destroy()
            return
        
        # Tabel cu bolile donatorului
        columns = ('ID Boala', 'Denumire', 'Data Diagnostic', 'Actiuni')
        disease_tree = ttk.Treeview(window, columns=columns, show='headings', height=10)
        
        for col in columns:
            disease_tree.heading(col, text=col)
            disease_tree.column(col, width=150 if col != 'Denumire' else 200)
        
        scrollbar = ttk.Scrollbar(window, orient=tk.VERTICAL, command=disease_tree.yview)
        disease_tree.configure(yscrollcommand=scrollbar.set)
        disease_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 20), pady=10)
        
        def load_donor_diseases():
            for item in disease_tree.get_children():
                disease_tree.delete(item)
            
            try:
                cursor.execute("""
                    SELECT b.IDBoala, b.Denumire, db.DataDiagnostic
                    FROM DonatoriBoli db
                    JOIN BoliRestrictive b ON db.IDBoala = b.IDBoala
                    WHERE db.IDDonator = ?
                    ORDER BY db.DataDiagnostic DESC
                """, donor_id)
                
                rows = cursor.fetchall()
                for row in rows:
                    disease_tree.insert('', tk.END, values=(row[0], row[1], row[2], "Sterge"))
            
            except Exception as e:
                messagebox.showerror("Eroare", f"Eroare la incarcare:\n{str(e)}")
        
        def remove_disease(event):
            selection = disease_tree.selection()
            if not selection:
                return
            
            item = disease_tree.item(selection[0])
            values = item['values']
            
            if len(values) < 1:
                return
            
            disease_id = values[0]
            disease_name = values[1]
            
            confirm = messagebox.askyesno("Confirmare", 
                                         f"Esti sigur ca vrei sa stergi asocierea cu boala:\n{disease_name}?")
            
            if not confirm:
                return
            
            try:
                cursor.execute("DELETE FROM DonatoriBoli WHERE IDDonator = ? AND IDBoala = ?", 
                             (donor_id, disease_id))
                conn.commit()
                messagebox.showinfo("Succes", "Asociere stearsa cu succes!")
                load_donor_diseases()
            except Exception as e:
                messagebox.showerror("Eroare", f"Eroare la stergere:\n{str(e)}")
        
        disease_tree.bind('<Double-1>', remove_disease)
        
        load_donor_diseases()
        
        def on_close():
            cursor.close()
            conn.close()
            window.destroy()
        
        window.protocol("WM_DELETE_WINDOW", on_close)
    
    # ==================== ANALIZE MEDICALE ====================
    def show_analyses(self):
        """Afiseaza interfata pentru gestionarea analizelor medicale."""
        self.clear_content()
        
        title = tk.Label(self.content_frame, text="GESTIONARE ANALIZE MEDICALE", 
                        font=('Arial', 18, 'bold'), bg=self.color_bg, fg=self.color_fg)
        title.pack(pady=(0, 20))
        
        button_frame = tk.Frame(self.content_frame, bg=self.color_bg)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Adauga Analiza", command=self.add_analysis_window).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Actualizeaza", command=self.load_analyses).pack(side=tk.LEFT, padx=5)
        
        columns = ('ID', 'Denumire', 'Val. Min', 'Val. Max', 'Urmareste')
        self.analysis_tree = ttk.Treeview(self.content_frame, columns=columns, show='headings', height=15)
        
        col_widths = [50, 200, 80, 80, 80]
        for col, width in zip(columns, col_widths):
            self.analysis_tree.heading(col, text=col)
            self.analysis_tree.column(col, width=width, anchor=tk.CENTER)
        
        scrollbar = ttk.Scrollbar(self.content_frame, orient=tk.VERTICAL, command=self.analysis_tree.yview)
        self.analysis_tree.configure(yscrollcommand=scrollbar.set)
        self.analysis_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        action_frame = tk.Frame(self.content_frame, bg=self.color_bg)
        action_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(action_frame, text="Editeaza", command=self.edit_analysis).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="sterge", command=self.delete_analysis).pack(side=tk.LEFT, padx=5)
        
        self.load_analyses()
    
    def load_analyses(self):
        """incarca analizele in tabel."""
        for item in self.analysis_tree.get_children():
            self.analysis_tree.delete(item)
    
        conn = get_connection()
        if conn is None:
            return
    
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT IDAnaliza, Denumire, ValoareMinima, ValoareMaxima, Urmareste FROM AnalizeMedicale ORDER BY Denumire")
            rows = cursor.fetchall()
        
            for row in rows:
                row_values = []
                for i, value in enumerate(row):
                    if value is None:
                        row_values.append('')
                    elif i == 4:  # Urmareste column
                        row_values.append('DA' if value == 1 else 'NU')
                    else:
                        row_values.append(str(value))
                self.analysis_tree.insert('', tk.END, values=row_values)
        
            self.show_status(f"Afisate {len(rows)} analize medicale")
        
        except Exception as e:
            messagebox.showerror("Eroare", f"Eroare la incarcarea analizelor:\n{str(e)}")
        finally:
            cursor.close()
            conn.close()
    
    def add_analysis_window(self):
        """Fereastra pentru adaugare analiza."""
        window = tk.Toplevel(self.root)
        window.title("Adauga Analiza Medicala")
        window.geometry("500x350")
        window.configure(bg=self.color_bg)
        window.grab_set()
        
        tk.Label(window, text="ADAUGARE ANALIZA MEDICALA", font=('Arial', 16, 'bold'), 
                bg=self.color_bg, fg=self.color_fg).pack(pady=20)
        
        form_frame = tk.Frame(window, bg=self.color_bg)
        form_frame.pack(padx=40, pady=10)
        
        tk.Label(form_frame, text="Denumire*:", bg=self.color_bg, fg=self.color_fg).grid(row=0, column=0, sticky=tk.W, pady=8)
        analysis_name_entry = ttk.Entry(form_frame, width=40)
        analysis_name_entry.grid(row=0, column=1, pady=8, padx=10)
        
        tk.Label(form_frame, text="Valoare Minima:", bg=self.color_bg, fg=self.color_fg).grid(row=1, column=0, sticky=tk.W, pady=8)
        min_val_entry = ttk.Entry(form_frame, width=40)
        min_val_entry.grid(row=1, column=1, pady=8, padx=10)
        
        tk.Label(form_frame, text="Valoare Maxima:", bg=self.color_bg, fg=self.color_fg).grid(row=2, column=0, sticky=tk.W, pady=8)
        max_val_entry = ttk.Entry(form_frame, width=40)
        max_val_entry.grid(row=2, column=1, pady=8, padx=10)
        
        tk.Label(form_frame, text="Urmareste:", bg=self.color_bg, fg=self.color_fg).grid(row=3, column=0, sticky=tk.W, pady=8)
        follow_var = tk.BooleanVar(value=True)
        tk.Checkbutton(form_frame, variable=follow_var, bg=self.color_bg).grid(row=3, column=1, sticky=tk.W, pady=8)
        
        def save_analysis():
            denumire = analysis_name_entry.get().strip()
            if not denumire:
                messagebox.showwarning("Validare", "Denumirea este obligatorie!")
                return
            
            min_val = min_val_entry.get().strip()
            max_val = max_val_entry.get().strip()
            
            conn = get_connection()
            if conn is None:
                return
            
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO AnalizeMedicale (Denumire, ValoareMinima, ValoareMaxima, Urmareste)
                    VALUES (?, ?, ?, ?)
                """, (
                    denumire,
                    float(min_val) if min_val else None,
                    float(max_val) if max_val else None,
                    1 if follow_var.get() else 0
                ))
                conn.commit()
                messagebox.showinfo("Succes", "Analiza adaugata cu succes!")
                window.destroy()
                self.load_analyses()
            except ValueError:
                messagebox.showerror("Eroare", "Valorile minime/maxime trebuie sa fie numere!")
            except Exception as e:
                messagebox.showerror("Eroare", f"Eroare la salvare:\n{str(e)}")
            finally:
                cursor.close()
                conn.close()
        
        button_frame = tk.Frame(window, bg=self.color_bg)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Salveaza", command=save_analysis).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Anuleaza", command=window.destroy).pack(side=tk.LEFT, padx=10)
    
    def edit_analysis(self):
        """Editeaza analiza selectata."""
        selection = self.analysis_tree.selection()
        if not selection:
            messagebox.showwarning("Selectie", "Selecteaza o analiza din lista!")
            return
    
        item = self.analysis_tree.item(selection[0])
        values = item['values']
    
        if not values or len(values) < 1:
            return
    
        try:
            analysis_id = int(values[0])
        except:
            messagebox.showerror("Eroare", "ID invalid!")
            return
        
        self.edit_analysis_window(analysis_id, values[1], values[2], values[3], values[4] == 'DA')
    
    def edit_analysis_window(self, analysis_id, denumire, min_val, max_val, urmareste):
        """Fereastra pentru editare analiza."""
        window = tk.Toplevel(self.root)
        window.title(f"Editare Analiza ID: {analysis_id}")
        window.geometry("500x350")
        window.configure(bg=self.color_bg)
        window.grab_set()
        
        tk.Label(window, text="EDITARE ANALIZA MEDICALA", font=('Arial', 16, 'bold'), 
                bg=self.color_bg, fg=self.color_fg).pack(pady=20)
        
        form_frame = tk.Frame(window, bg=self.color_bg)
        form_frame.pack(padx=40, pady=10)
        
        tk.Label(form_frame, text="Denumire*:", bg=self.color_bg, fg=self.color_fg).grid(row=0, column=0, sticky=tk.W, pady=8)
        analysis_name_entry = ttk.Entry(form_frame, width=40)
        analysis_name_entry.insert(0, denumire)
        analysis_name_entry.grid(row=0, column=1, pady=8, padx=10)
        
        tk.Label(form_frame, text="Valoare Minima:", bg=self.color_bg, fg=self.color_fg).grid(row=1, column=0, sticky=tk.W, pady=8)
        min_val_entry = ttk.Entry(form_frame, width=40)
        min_val_entry.insert(0, min_val if min_val else '')
        min_val_entry.grid(row=1, column=1, pady=8, padx=10)
        
        tk.Label(form_frame, text="Valoare Maxima:", bg=self.color_bg, fg=self.color_fg).grid(row=2, column=0, sticky=tk.W, pady=8)
        max_val_entry = ttk.Entry(form_frame, width=40)
        max_val_entry.insert(0, max_val if max_val else '')
        max_val_entry.grid(row=2, column=1, pady=8, padx=10)
        
        tk.Label(form_frame, text="Urmareste:", bg=self.color_bg, fg=self.color_fg).grid(row=3, column=0, sticky=tk.W, pady=8)
        follow_var = tk.BooleanVar(value=urmareste)
        tk.Checkbutton(form_frame, variable=follow_var, bg=self.color_bg).grid(row=3, column=1, sticky=tk.W, pady=8)
        
        def update_analysis():
            new_denumire = analysis_name_entry.get().strip()
            if not new_denumire:
                messagebox.showwarning("Validare", "Denumirea este obligatorie!")
                return
            
            new_min_val = min_val_entry.get().strip()
            new_max_val = max_val_entry.get().strip()
            
            conn = get_connection()
            if conn is None:
                return
            
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    UPDATE AnalizeMedicale 
                    SET Denumire = ?, ValoareMinima = ?, ValoareMaxima = ?, Urmareste = ?
                    WHERE IDAnaliza = ?
                """, (
                    new_denumire,
                    float(new_min_val) if new_min_val else None,
                    float(new_max_val) if new_max_val else None,
                    1 if follow_var.get() else 0,
                    analysis_id
                ))
                conn.commit()
                messagebox.showinfo("Succes", "Analiza actualizata cu succes!")
                window.destroy()
                self.load_analyses()
            except ValueError:
                messagebox.showerror("Eroare", "Valorile minime/maxime trebuie sa fie numere!")
            except Exception as e:
                messagebox.showerror("Eroare", f"Eroare la actualizare:\n{str(e)}")
            finally:
                cursor.close()
                conn.close()
        
        button_frame = tk.Frame(window, bg=self.color_bg)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Salveaza Modificari", command=update_analysis).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Anuleaza", command=window.destroy).pack(side=tk.LEFT, padx=10)
    
    def delete_analysis(self):
        """sterge analiza selectata."""
        selection = self.analysis_tree.selection()
        if not selection:
            messagebox.showwarning("Selectie", "Selecteaza o analiza din lista!")
            return
        
        item = self.analysis_tree.item(selection[0])
        analysis_id, denumire = item['values'][0], item['values'][1]
        
        confirm = messagebox.askyesno("Confirmare", 
                                     f"Esti sigur ca vrei sa stergi analiza:\n{denumire}?\n\nAceasta actiune va sterge si toate rezultatele asociate!")
        
        if not confirm:
            return
        
        conn = get_connection()
        if conn is None:
            return
        
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM AnalizeMedicale WHERE IDAnaliza = ?", analysis_id)
            conn.commit()
            messagebox.showinfo("Succes", "Analiza stearsa cu succes!")
            self.load_analyses()
        except Exception as e:
            messagebox.showerror("Eroare", f"Eroare la stergere:\n{str(e)}")
        finally:
            cursor.close()
            conn.close()
    
    def show_donor_analyses_window(self, donor_id, donor_name):
        """Afiseaza analizele unui donator."""
        window = tk.Toplevel(self.root)
        window.title(f"Analize Medicale - {donor_name}")
        window.geometry("800x500")
        window.configure(bg=self.color_bg)
        window.grab_set()
        
        tk.Label(window, text=f"ANALIZE MEDICALE - {donor_name}", font=('Arial', 16, 'bold'), 
                bg=self.color_bg, fg=self.color_fg).pack(pady=20)
        
        # Frame pentru adaugare rezultat
        add_frame = tk.Frame(window, bg=self.color_bg)
        add_frame.pack(fill=tk.X, padx=20, pady=10)
        
        tk.Label(add_frame, text="Adauga rezultat:", bg=self.color_bg, fg=self.color_fg).pack(side=tk.LEFT, padx=5)
        
        conn = get_connection()
        if conn is None:
            window.destroy()
            return
        
        cursor = conn.cursor()
        try:
            # Combobox cu analizele disponibile
            cursor.execute("SELECT IDAnaliza, Denumire FROM AnalizeMedicale ORDER BY Denumire")
            analyses = cursor.fetchall()
            analysis_dict = {f"{a[1]} (ID:{a[0]})": a[0] for a in analyses}
            
            analysis_var = tk.StringVar()
            analysis_combo = ttk.Combobox(add_frame, textvariable=analysis_var, 
                                         values=list(analysis_dict.keys()), width=30)
            analysis_combo.pack(side=tk.LEFT, padx=5)
            
            tk.Label(add_frame, text="Valoare:", bg=self.color_bg, fg=self.color_fg).pack(side=tk.LEFT, padx=5)
            value_entry = ttk.Entry(add_frame, width=15)
            value_entry.pack(side=tk.LEFT, padx=5)
            
            tk.Label(add_frame, text="Data (YYYY-MM-DD):", bg=self.color_bg, fg=self.color_fg).pack(side=tk.LEFT, padx=5)
            date_entry = ttk.Entry(add_frame, width=15)
            date_entry.insert(0, date.today().strftime("%Y-%m-%d"))
            date_entry.pack(side=tk.LEFT, padx=5)
            
            def add_analysis_result():
                selected = analysis_var.get()
                if not selected:
                    messagebox.showwarning("Validare", "Selecteaza o analiza!")
                    return
                
                value_str = value_entry.get().strip()
                if not value_str:
                    messagebox.showwarning("Validare", "Valoarea este obligatorie!")
                    return
                
                try:
                    value = float(value_str)
                except ValueError:
                    messagebox.showerror("Eroare", "Valoarea trebuie sa fie un numar!")
                    return
                
                analysis_date = date_entry.get().strip()
                if not analysis_date:
                    messagebox.showwarning("Validare", "Data este obligatorie!")
                    return
                
                analysis_id = analysis_dict[selected]
                
                # Determină dacă este în limite normale
                cursor.execute("SELECT ValoareMinima, ValoareMaxima FROM AnalizeMedicale WHERE IDAnaliza = ?", analysis_id)
                limits = cursor.fetchone()
                in_limits = None
                
                if limits and limits[0] is not None and limits[1] is not None:
                    in_limits = 1 if limits[0] <= value <= limits[1] else 0
                
                try:
                    cursor.execute("""
                        INSERT INTO RezultateAnalize (IDDonator, IDAnaliza, DataAnaliza, Valoare, EsteInLimitaNormala)
                        VALUES (?, ?, ?, ?, ?)
                    """, (donor_id, analysis_id, analysis_date, value, in_limits))
                    conn.commit()
                    messagebox.showinfo("Succes", "Rezultat adaugat cu succes!")
                    load_donor_analyses()
                    analysis_var.set('')
                    value_entry.delete(0, tk.END)
                except pyodbc.IntegrityError as e:
                    if "Violation of PRIMARY KEY" in str(e):
                        messagebox.showerror("Eroare", "Acest donator are deja un rezultat pentru aceasta analiza la aceasta data!")
                    else:
                        messagebox.showerror("Eroare", f"Eroare la adaugare:\n{str(e)}")
                except Exception as e:
                    messagebox.showerror("Eroare", f"Eroare la adaugare:\n{str(e)}")
            
            ttk.Button(add_frame, text="Adauga", command=add_analysis_result).pack(side=tk.LEFT, padx=10)
            
        except Exception as e:
            messagebox.showerror("Eroare", f"Eroare la incarcarea analizelor:\n{str(e)}")
            cursor.close()
            conn.close()
            window.destroy()
            return
        
        # Tabel cu rezultatele analizelor
        columns = ('ID Analiza', 'Analiza', 'Valoare', 'Limita Normala', 'Data', 'Actiuni')
        analysis_tree = ttk.Treeview(window, columns=columns, show='headings', height=15)
        
        col_widths = [80, 150, 80, 120, 100, 80]
        for col, width in zip(columns, col_widths):
            analysis_tree.heading(col, text=col)
            analysis_tree.column(col, width=width, anchor=tk.CENTER)
        
        scrollbar = ttk.Scrollbar(window, orient=tk.VERTICAL, command=analysis_tree.yview)
        analysis_tree.configure(yscrollcommand=scrollbar.set)
        analysis_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=20, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 20), pady=10)
        
        def load_donor_analyses():
            for item in analysis_tree.get_children():
                analysis_tree.delete(item)
            
            try:
                cursor.execute("""
                    SELECT ra.IDAnaliza, am.Denumire, ra.Valoare, 
                           CASE WHEN ra.EsteInLimitaNormala = 1 THEN 'DA' 
                                WHEN ra.EsteInLimitaNormala = 0 THEN 'NU' 
                                ELSE 'N/A' END,
                           ra.DataAnaliza
                    FROM RezultateAnalize ra
                    JOIN AnalizeMedicale am ON ra.IDAnaliza = am.IDAnaliza
                    WHERE ra.IDDonator = ?
                    ORDER BY ra.DataAnaliza DESC
                """, donor_id)
                
                rows = cursor.fetchall()
                for row in rows:
                    analysis_tree.insert('', tk.END, values=(row[0], row[1], f"{row[2]:.2f}", row[3], row[4], "Sterge"))
            
            except Exception as e:
                messagebox.showerror("Eroare", f"Eroare la incarcare:\n{str(e)}")
        
        def remove_analysis_result(event):
            selection = analysis_tree.selection()
            if not selection:
                return
            
            item = analysis_tree.item(selection[0])
            values = item['values']
            
            if len(values) < 1:
                return
            
            analysis_id = values[0]
            analysis_name = values[1]
            analysis_date = values[4]
            
            confirm = messagebox.askyesno("Confirmare", 
                                         f"Esti sigur ca vrei sa stergi rezultatul pentru:\n{analysis_name} din data {analysis_date}?")
            
            if not confirm:
                return
            
            try:
                cursor.execute("""
                    DELETE FROM RezultateAnalize 
                    WHERE IDDonator = ? AND IDAnaliza = ? AND DataAnaliza = ?
                """, (donor_id, analysis_id, analysis_date))
                conn.commit()
                messagebox.showinfo("Succes", "Rezultat sters cu succes!")
                load_donor_analyses()
            except Exception as e:
                messagebox.showerror("Eroare", f"Eroare la stergere:\n{str(e)}")
        
        analysis_tree.bind('<Double-1>', remove_analysis_result)
        
        load_donor_analyses()
        
        def on_close():
            cursor.close()
            conn.close()
            window.destroy()
        
        window.protocol("WM_DELETE_WINDOW", on_close)
    
    # ==================== PROGRAMARI ====================
    def show_appointments(self):
        """Afiseaza interfata pentru gestionarea programarilor."""
        self.clear_content()
        
        title = tk.Label(self.content_frame, text="GESTIONARE PROGRAMARI", 
                        font=('Arial', 18, 'bold'), bg=self.color_bg, fg=self.color_fg)
        title.pack(pady=(0, 20))
        
        button_frame = tk.Frame(self.content_frame, bg=self.color_bg)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Adauga Programare", command=self.add_appointment_window).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Programari Astazi", command=lambda: self.load_appointments("today")).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Toate Programarile", command=lambda: self.load_appointments()).pack(side=tk.LEFT, padx=5)
        
        columns = ('ID', 'Donator', 'Data Programare', 'Stare')
        self.appointment_tree = ttk.Treeview(self.content_frame, columns=columns, show='headings', height=15)
        
        col_widths = [50, 150, 150, 100]
        for col, width in zip(columns, col_widths):
            self.appointment_tree.heading(col, text=col)
            self.appointment_tree.column(col, width=width, anchor=tk.CENTER)
        
        scrollbar = ttk.Scrollbar(self.content_frame, orient=tk.VERTICAL, command=self.appointment_tree.yview)
        self.appointment_tree.configure(yscrollcommand=scrollbar.set)
        self.appointment_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        action_frame = tk.Frame(self.content_frame, bg=self.color_bg)
        action_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(action_frame, text="Confirma", command=lambda: self.update_appointment_status('Confirmata')).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Anuleaza", command=lambda: self.update_appointment_status('Anulata')).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Finalizeaza", command=lambda: self.update_appointment_status('Finalizata')).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="sterge", command=self.delete_appointment).pack(side=tk.LEFT, padx=5)
        
        self.load_appointments()
    
    def load_appointments(self, filter_type=None):
        """incarca programarile in tabel."""
        for item in self.appointment_tree.get_children():
            self.appointment_tree.delete(item)
    
        conn = get_connection()
        if conn is None:
            return
    
        cursor = conn.cursor()
        try:
            if filter_type == "today":
                cursor.execute("""
                    SELECT p.IDProgramare, d.Nume + ' ' + d.Prenume, p.DataProgramare, p.Stare
                    FROM Programari p
                    JOIN Donatori d ON p.IDDonator = d.IDDonator
                    WHERE CAST(p.DataProgramare AS DATE) = CAST(GETDATE() AS DATE)
                    ORDER BY p.DataProgramare
                """)
            else:
                cursor.execute("""
                    SELECT p.IDProgramare, d.Nume + ' ' + d.Prenume, p.DataProgramare, p.Stare
                    FROM Programari p
                    JOIN Donatori d ON p.IDDonator = d.IDDonator
                    ORDER BY p.DataProgramare DESC
                """)
            
            rows = cursor.fetchall()
        
            for row in rows:
                row_values = []
                for value in row:
                    if value is None:
                        row_values.append('')
                    else:
                        row_values.append(str(value))
                self.appointment_tree.insert('', tk.END, values=row_values)
        
            self.show_status(f"Afisate {len(rows)} programari")
        
        except Exception as e:
            messagebox.showerror("Eroare", f"Eroare la incarcarea programarilor:\n{str(e)}")
        finally:
            cursor.close()
            conn.close()
    
    def add_appointment_window(self):
        """Fereastra pentru adaugare programare."""
        window = tk.Toplevel(self.root)
        window.title("Adauga Programare")
        window.geometry("500x300")
        window.configure(bg=self.color_bg)
        window.grab_set()
        
        tk.Label(window, text="ADAUGARE PROGRAMARE", font=('Arial', 16, 'bold'), 
                bg=self.color_bg, fg=self.color_fg).pack(pady=20)
        
        form_frame = tk.Frame(window, bg=self.color_bg)
        form_frame.pack(padx=40, pady=10)
        
        # Combobox cu donatorii
        conn = get_connection()
        if conn is None:
            window.destroy()
            return
        
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT IDDonator, Nume + ' ' + Prenume FROM Donatori ORDER BY Nume, Prenume")
            donors = cursor.fetchall()
            donor_dict = {f"{d[1]} (ID:{d[0]})": d[0] for d in donors}
            
            tk.Label(form_frame, text="Donator*:", bg=self.color_bg, fg=self.color_fg).grid(row=0, column=0, sticky=tk.W, pady=8)
            donor_var = tk.StringVar()
            donor_combo = ttk.Combobox(form_frame, textvariable=donor_var, 
                                      values=list(donor_dict.keys()), width=37)
            donor_combo.grid(row=0, column=1, pady=8, padx=10)
            
            tk.Label(form_frame, text="Data si Ora* (YYYY-MM-DD HH:MM):", bg=self.color_bg, fg=self.color_fg).grid(row=1, column=0, sticky=tk.W, pady=8)
            datetime_entry = ttk.Entry(form_frame, width=37)
            datetime_entry.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M"))
            datetime_entry.grid(row=1, column=1, pady=8, padx=10)
            
            tk.Label(form_frame, text="Stare:", bg=self.color_bg, fg=self.color_fg).grid(row=2, column=0, sticky=tk.W, pady=8)
            status_var = tk.StringVar(value="Confirmata")
            status_combo = ttk.Combobox(form_frame, textvariable=status_var, 
                                       values=['Confirmata', 'Anulata', 'Finalizata'], width=37)
            status_combo.grid(row=2, column=1, pady=8, padx=10)
            
            def save_appointment():
                selected = donor_var.get()
                if not selected:
                    messagebox.showwarning("Validare", "Selecteaza un donator!")
                    return
                
                datetime_str = datetime_entry.get().strip()
                if not datetime_str:
                    messagebox.showwarning("Validare", "Data si ora sunt obligatorii!")
                    return
                
                donor_id = donor_dict[selected]
                status = status_var.get()
                
                try:
                    cursor.execute("""
                        INSERT INTO Programari (IDDonator, DataProgramare, Stare)
                        VALUES (?, ?, ?)
                    """, (donor_id, datetime_str, status))
                    conn.commit()
                    messagebox.showinfo("Succes", "Programare adaugata cu succes!")
                    window.destroy()
                    self.load_appointments()
                except Exception as e:
                    messagebox.showerror("Eroare", f"Eroare la salvare:\n{str(e)}")
            
            button_frame = tk.Frame(window, bg=self.color_bg)
            button_frame.pack(pady=20)
            
            ttk.Button(button_frame, text="Salveaza", command=save_appointment).pack(side=tk.LEFT, padx=10)
            ttk.Button(button_frame, text="Anuleaza", command=window.destroy).pack(side=tk.LEFT, padx=10)
            
        except Exception as e:
            messagebox.showerror("Eroare", f"Eroare la incarcarea donatorilor:\n{str(e)}")
            cursor.close()
            conn.close()
            window.destroy()
    
    def update_appointment_status(self, new_status):
        """Actualizeaza starea programarii selectate."""
        selection = self.appointment_tree.selection()
        if not selection:
            messagebox.showwarning("Selectie", "Selecteaza o programare din lista!")
            return
        
        item = self.appointment_tree.item(selection[0])
        appointment_id = item['values'][0]
        
        conn = get_connection()
        if conn is None:
            return
        
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE Programari SET Stare = ? WHERE IDProgramare = ?", (new_status, appointment_id))
            conn.commit()
            messagebox.showinfo("Succes", f"Programare {new_status.lower()} cu succes!")
            self.load_appointments()
        except Exception as e:
            messagebox.showerror("Eroare", f"Eroare la actualizare:\n{str(e)}")
        finally:
            cursor.close()
            conn.close()
    
    def delete_appointment(self):
        """sterge programarea selectata."""
        selection = self.appointment_tree.selection()
        if not selection:
            messagebox.showwarning("Selectie", "Selecteaza o programare din lista!")
            return
        
        item = self.appointment_tree.item(selection[0])
        appointment_id, donor_name, datetime_str = item['values'][0], item['values'][1], item['values'][2]
        
        confirm = messagebox.askyesno("Confirmare", 
                                     f"Esti sigur ca vrei sa stergi programarea:\n{donor_name} - {datetime_str}?")
        
        if not confirm:
            return
        
        conn = get_connection()
        if conn is None:
            return
        
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM Programari WHERE IDProgramare = ?", appointment_id)
            conn.commit()
            messagebox.showinfo("Succes", "Programare stearsa cu succes!")
            self.load_appointments()
        except Exception as e:
            messagebox.showerror("Eroare", f"Eroare la stergere:\n{str(e)}")
        finally:
            cursor.close()
            conn.close()
    
    # ==================== DONATII ====================
    def show_donations(self):
        """Afiseaza interfata pentru gestionarea donatiilor."""
        self.clear_content()
        
        title = tk.Label(self.content_frame, text="GESTIONARE DONATII", 
                        font=('Arial', 18, 'bold'), bg=self.color_bg, fg=self.color_fg)
        title.pack(pady=(0, 20))
        
        button_frame = tk.Frame(self.content_frame, bg=self.color_bg)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Adauga Donatie", command=self.add_donation_window).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Actualizeaza", command=self.load_donations).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Exporta Raport", command=self.export_donations_report).pack(side=tk.LEFT, padx=5)
        
        columns = ('ID', 'Donator', 'Data Donatie', 'Cantitate (ml)', 'Locatie')
        self.donation_tree = ttk.Treeview(self.content_frame, columns=columns, show='headings', height=15)
        
        col_widths = [50, 150, 120, 100, 150]
        for col, width in zip(columns, col_widths):
            self.donation_tree.heading(col, text=col)
            self.donation_tree.column(col, width=width, anchor=tk.CENTER)
        
        scrollbar = ttk.Scrollbar(self.content_frame, orient=tk.VERTICAL, command=self.donation_tree.yview)
        self.donation_tree.configure(yscrollcommand=scrollbar.set)
        self.donation_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        action_frame = tk.Frame(self.content_frame, bg=self.color_bg)
        action_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(action_frame, text="sterge", command=self.delete_donation).pack(side=tk.LEFT, padx=5)
        
        self.load_donations()
    
    def load_donations(self):
        """incarca donatiile in tabel."""
        for item in self.donation_tree.get_children():
            self.donation_tree.delete(item)
    
        conn = get_connection()
        if conn is None:
            return
    
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT d.IDDonatie, dn.Nume + ' ' + dn.Prenume, d.DataDonatie, d.Cantitate, d.Locatie
                FROM Donatii d
                JOIN Donatori dn ON d.IDDonator = dn.IDDonator
                ORDER BY d.DataDonatie DESC
            """)
            rows = cursor.fetchall()
        
            for row in rows:
                row_values = []
                for value in row:
                    if value is None:
                        row_values.append('')
                    else:
                        row_values.append(str(value))
                self.donation_tree.insert('', tk.END, values=row_values)
        
            self.show_status(f"Afisate {len(rows)} donatii")
        
        except Exception as e:
            messagebox.showerror("Eroare", f"Eroare la incarcarea donatiilor:\n{str(e)}")
        finally:
            cursor.close()
            conn.close()
    
    def add_donation_window(self):
        """Fereastra pentru adaugare donatie."""
        window = tk.Toplevel(self.root)
        window.title("Adauga Donatie")
        window.geometry("500x350")
        window.configure(bg=self.color_bg)
        window.grab_set()
        
        tk.Label(window, text="ADAUGARE DONATIE", font=('Arial', 16, 'bold'), 
                bg=self.color_bg, fg=self.color_fg).pack(pady=20)
        
        form_frame = tk.Frame(window, bg=self.color_bg)
        form_frame.pack(padx=40, pady=10)
        
        conn = get_connection()
        if conn is None:
            window.destroy()
            return
        
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT IDDonator, Nume + ' ' + Prenume FROM Donatori WHERE EsteEligibil = 1 ORDER BY Nume, Prenume")
            donors = cursor.fetchall()
            donor_dict = {f"{d[1]} (ID:{d[0]})": d[0] for d in donors}
            
            tk.Label(form_frame, text="Donator* (doar eligibili):", bg=self.color_bg, fg=self.color_fg).grid(row=0, column=0, sticky=tk.W, pady=8)
            donor_var = tk.StringVar()
            donor_combo = ttk.Combobox(form_frame, textvariable=donor_var, 
                                      values=list(donor_dict.keys()), width=37)
            donor_combo.grid(row=0, column=1, pady=8, padx=10)
            
            tk.Label(form_frame, text="Data Donatie* (YYYY-MM-DD):", bg=self.color_bg, fg=self.color_fg).grid(row=1, column=0, sticky=tk.W, pady=8)
            date_entry = ttk.Entry(form_frame, width=37)
            date_entry.insert(0, date.today().strftime("%Y-%m-%d"))
            date_entry.grid(row=1, column=1, pady=8, padx=10)
            
            tk.Label(form_frame, text="Cantitate* (400-500 ml):", bg=self.color_bg, fg=self.color_fg).grid(row=2, column=0, sticky=tk.W, pady=8)
            quantity_var = tk.StringVar(value="450")
            quantity_spin = ttk.Spinbox(form_frame, from_=400, to=500, textvariable=quantity_var, width=34)
            quantity_spin.grid(row=2, column=1, pady=8, padx=10)
            
            tk.Label(form_frame, text="Locatie*:", bg=self.color_bg, fg=self.color_fg).grid(row=3, column=0, sticky=tk.W, pady=8)
            location_entry = ttk.Entry(form_frame, width=37)
            location_entry.insert(0, "Centrul de transfuzii Bucuresti")
            location_entry.grid(row=3, column=1, pady=8, padx=10)
            
            def save_donation():
                selected = donor_var.get()
                if not selected:
                    messagebox.showwarning("Validare", "Selecteaza un donator!")
                    return
                
                date_str = date_entry.get().strip()
                if not date_str:
                    messagebox.showwarning("Validare", "Data este obligatorie!")
                    return
                
                try:
                    quantity = int(quantity_var.get())
                    if not (400 <= quantity <= 500):
                        messagebox.showerror("Eroare", "Cantitatea trebuie sa fie intre 400 si 500 ml!")
                        return
                except ValueError:
                    messagebox.showerror("Eroare", "Cantitatea trebuie sa fie un numar!")
                    return
                
                location = location_entry.get().strip()
                if not location:
                    messagebox.showwarning("Validare", "Locatia este obligatorie!")
                    return
                
                donor_id = donor_dict[selected]
                
                try:
                    # Adauga donatia
                    cursor.execute("""
                        INSERT INTO Donatii (IDDonator, DataDonatie, Cantitate, Locatie)
                        VALUES (?, ?, ?, ?)
                    """, (donor_id, date_str, quantity, location))
                    
                    # Actualizeaza data ultimei donatii pentru donator
                    cursor.execute("""
                        UPDATE Donatori 
                        SET UltimaDonatie = ? 
                        WHERE IDDonator = ?
                    """, (date_str, donor_id))
                    
                    # Adauga la stoc
                    cursor.execute("""
                        SELECT GrupaSanguina FROM Donatori WHERE IDDonator = ?
                    """, donor_id)
                    blood_group = cursor.fetchone()[0]
                    
                    cursor.execute("""
                        INSERT INTO StocSange (GrupaSanguina, Cantitate, DataActualizarii)
                        VALUES (?, ?, GETDATE())
                    """, (blood_group, quantity))
                    
                    conn.commit()
                    messagebox.showinfo("Succes", "Donatie inregistrata cu succes si stoc actualizat!")
                    window.destroy()
                    self.load_donations()
                except Exception as e:
                    conn.rollback()
                    messagebox.showerror("Eroare", f"Eroare la salvare:\n{str(e)}")
            
            button_frame = tk.Frame(window, bg=self.color_bg)
            button_frame.pack(pady=20)
            
            ttk.Button(button_frame, text="Salveaza", command=save_donation).pack(side=tk.LEFT, padx=10)
            ttk.Button(button_frame, text="Anuleaza", command=window.destroy).pack(side=tk.LEFT, padx=10)
            
        except Exception as e:
            messagebox.showerror("Eroare", f"Eroare la incarcarea donatorilor:\n{str(e)}")
            cursor.close()
            conn.close()
            window.destroy()
    
    def delete_donation(self):
        """sterge donatia selectata."""
        selection = self.donation_tree.selection()
        if not selection:
            messagebox.showwarning("Selectie", "Selecteaza o donatie din lista!")
            return
        
        item = self.donation_tree.item(selection[0])
        donation_id, donor_name, date_str = item['values'][0], item['values'][1], item['values'][2]
        
        confirm = messagebox.askyesno("Confirmare", 
                                     f"Esti sigur ca vrei sa stergi donatia:\n{donor_name} - {date_str}?\n\nAceasta actiune va elimina si cantitatea din stoc!")
        
        if not confirm:
            return
        
        conn = get_connection()
        if conn is None:
            return
        
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM Donatii WHERE IDDonatie = ?", donation_id)
            conn.commit()
            messagebox.showinfo("Succes", "Donatie stearsa cu succes!")
            self.load_donations()
        except Exception as e:
            messagebox.showerror("Eroare", f"Eroare la stergere:\n{str(e)}")
        finally:
            cursor.close()
            conn.close()
    
    def export_donations_report(self):
        """Exporta raport donatii."""
        conn = get_connection()
        if conn is None:
            return
        
        try:
            df = pd.read_sql("""
                SELECT d.DataDonatie, dn.Nume + ' ' + dn.Prenume as Donator, 
                       dn.GrupaSanguina, d.Cantitate, d.Locatie
                FROM Donatii d
                JOIN Donatori dn ON d.IDDonator = dn.IDDonator
                ORDER BY d.DataDonatie DESC
            """, conn)
            df.to_csv('raport_donatii.csv', index=False, encoding='utf-8')
            messagebox.showinfo("Export", "Raportul a fost exportat in 'raport_donatii.csv'")
        except Exception as e:
            messagebox.showerror("Eroare", f"Eroare la export:\n{str(e)}")
        finally:
            conn.close()
    
    # ==================== STOC SANGE ====================
    def show_stock(self):
        """Afiseaza interfata pentru gestionarea stocului de sange."""
        self.clear_content()
        
        title = tk.Label(self.content_frame, text="GESTIONARE STOC SANGE", 
                        font=('Arial', 18, 'bold'), bg=self.color_bg, fg=self.color_fg)
        title.pack(pady=(0, 20))
        
        button_frame = tk.Frame(self.content_frame, bg=self.color_bg)
        button_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(button_frame, text="Actualizeaza Stoc", command=self.load_stock).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Adauga in Stoc", command=self.add_to_stock_window).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Exporta Stoc", command=self.export_stock_csv).pack(side=tk.LEFT, padx=5)
        
        columns = ('Grupa Sanguina', 'Cantitate Totala (ml)', 'Stare')
        self.stock_tree = ttk.Treeview(self.content_frame, columns=columns, show='headings', height=15)
        
        col_widths = [150, 150, 150]
        for col, width in zip(columns, col_widths):
            self.stock_tree.heading(col, text=col)
            self.stock_tree.column(col, width=width, anchor=tk.CENTER)
        
        scrollbar = ttk.Scrollbar(self.content_frame, orient=tk.VERTICAL, command=self.stock_tree.yview)
        self.stock_tree.configure(yscrollcommand=scrollbar.set)
        self.stock_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Statistici
        stats_frame = tk.Frame(self.content_frame, bg=self.color_bg)
        stats_frame.pack(fill=tk.X, pady=10)
        
        self.total_label = tk.Label(stats_frame, text="Total stoc: 0 ml", font=('Arial', 12, 'bold'), 
                                   bg=self.color_bg, fg=self.color_fg)
        self.total_label.pack(side=tk.LEFT, padx=20)
        
        self.critical_label = tk.Label(stats_frame, text="Grupe critice: 0", font=('Arial', 12), 
                                      bg=self.color_bg, fg='red')
        self.critical_label.pack(side=tk.LEFT, padx=20)
        
        self.load_stock()
    
    def load_stock(self):
        """incarca stocul in tabel."""
        for item in self.stock_tree.get_children():
            self.stock_tree.delete(item)
    
        conn = get_connection()
        if conn is None:
            return
    
        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT GrupaSanguina, SUM(Cantitate) as TotalCantitate
                FROM StocSange
                WHERE DataExpirare IS NULL OR DataExpirare > GETDATE()
                GROUP BY GrupaSanguina
                ORDER BY GrupaSanguina
            """)
            rows = cursor.fetchall()
        
            total_ml = 0
            critical_groups = 0
            
            blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', '0+', '0-']
            stock_dict = {bg: 0 for bg in blood_groups}
            
            for row in rows:
                stock_dict[row[0]] = row[1]
            
            for bg in blood_groups:
                quantity = stock_dict[bg]
                total_ml += quantity
                
                if quantity < 500:  # Sub 500 ml consideram critic
                    status = "CRITIC" if quantity < 200 else "BAJ" if quantity < 500 else "OK"
                    if quantity < 200:
                        critical_groups += 1
                else:
                    status = "OK"
                
                self.stock_tree.insert('', tk.END, values=(bg, f"{quantity} ml", status))
        
            self.total_label.config(text=f"Total stoc: {total_ml} ml")
            self.critical_label.config(text=f"Grupe sub 200ml: {critical_groups}", 
                                      fg='red' if critical_groups > 0 else 'black')
        
            self.show_status(f"Stoc afisat: {total_ml} ml total")
        
        except Exception as e:
            messagebox.showerror("Eroare", f"Eroare la incarcarea stocului:\n{str(e)}")
        finally:
            cursor.close()
            conn.close()
    
    def add_to_stock_window(self):
        """Fereastra pentru adaugare in stoc."""
        window = tk.Toplevel(self.root)
        window.title("Adauga in Stoc")
        window.geometry("400x250")
        window.configure(bg=self.color_bg)
        window.grab_set()
        
        tk.Label(window, text="ADAUGARE IN STOC", font=('Arial', 16, 'bold'), 
                bg=self.color_bg, fg=self.color_fg).pack(pady=20)
        
        form_frame = tk.Frame(window, bg=self.color_bg)
        form_frame.pack(padx=40, pady=10)
        
        tk.Label(form_frame, text="Grupa Sanguina*:", bg=self.color_bg, fg=self.color_fg).grid(row=0, column=0, sticky=tk.W, pady=8)
        blood_var = tk.StringVar()
        blood_combo = ttk.Combobox(form_frame, textvariable=blood_var, 
                                  values=['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', '0+', '0-'], width=20)
        blood_combo.grid(row=0, column=1, pady=8, padx=10)
        blood_combo.current(0)
        
        tk.Label(form_frame, text="Cantitate (ml)*:", bg=self.color_bg, fg=self.color_fg).grid(row=1, column=0, sticky=tk.W, pady=8)
        quantity_entry = ttk.Entry(form_frame, width=23)
        quantity_entry.insert(0, "450")
        quantity_entry.grid(row=1, column=1, pady=8, padx=10)
        
        tk.Label(form_frame, text="Data Expirare (YYYY-MM-DD):", bg=self.color_bg, fg=self.color_fg).grid(row=2, column=0, sticky=tk.W, pady=8)
        expiry_entry = ttk.Entry(form_frame, width=23)
        expiry_entry.grid(row=2, column=1, pady=8, padx=10)
        
        def save_to_stock():
            blood_group = blood_var.get()
            if not blood_group:
                messagebox.showwarning("Validare", "Selecteaza o grupa sanguina!")
                return
            
            quantity_str = quantity_entry.get().strip()
            if not quantity_str:
                messagebox.showwarning("Validare", "Cantitatea este obligatorie!")
                return
            
            try:
                quantity = int(quantity_str)
                if quantity <= 0:
                    messagebox.showerror("Eroare", "Cantitatea trebuie sa fie pozitiva!")
                    return
            except ValueError:
                messagebox.showerror("Eroare", "Cantitatea trebuie sa fie un numar!")
                return
            
            expiry_date = expiry_entry.get().strip()
            
            conn = get_connection()
            if conn is None:
                return
            
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO StocSange (GrupaSanguina, Cantitate, DataExpirare, DataActualizarii)
                    VALUES (?, ?, ?, GETDATE())
                """, (blood_group, quantity, expiry_date if expiry_date else None))
                conn.commit()
                messagebox.showinfo("Succes", "Stoc actualizat cu succes!")
                window.destroy()
                self.load_stock()
            except Exception as e:
                messagebox.showerror("Eroare", f"Eroare la salvare:\n{str(e)}")
            finally:
                cursor.close()
                conn.close()
        
        button_frame = tk.Frame(window, bg=self.color_bg)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Salveaza", command=save_to_stock).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Anuleaza", command=window.destroy).pack(side=tk.LEFT, padx=10)
    
    def export_stock_csv(self):
        """Exporta stocul in CSV."""
        conn = get_connection()
        if conn is None:
            return
        
        try:
            df = pd.read_sql("""
                SELECT GrupaSanguina, Cantitate, DataExpirare, DataActualizarii
                FROM StocSange
                ORDER BY GrupaSanguina, DataActualizarii DESC
            """, conn)
            df.to_csv('stoc_sange_export.csv', index=False, encoding='utf-8')
            messagebox.showinfo("Export", "Stocul a fost exportat in 'stoc_sange_export.csv'")
        except Exception as e:
            messagebox.showerror("Eroare", f"Eroare la export:\n{str(e)}")
        finally:
            conn.close()
    
    #RAPOARTE
    def show_reports(self):
        """Afiseaza interfata pentru rapoarte."""
        self.clear_content()
    
        title = tk.Label(self.content_frame, text="RAPOARTE SI STATISTICI", 
                        font=('Arial', 18, 'bold'), bg=self.color_bg, fg=self.color_fg)
        title.pack(pady=(0, 20))
    
        # Frame pentru butoane de rapoarte
        reports_frame = tk.Frame(self.content_frame, bg=self.color_bg)
        reports_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=20)
    
        # Grid 3x3 cu butoane pentru rapoarte
        reports = [
            #INTEROGARI SIMPLE (6)
            ("📊 Donatori pe Grupe", self.report_blood_groups),           # SIMPLU
            ("🏥 Donatori cu Boli", self.report_donors_with_diseases),    # SIMPLU
            ("🩸 Analize Anormale", self.report_abnormal_analyses),       # SIMPLU
            ("📅 Programari Viitoare", self.report_upcoming_appointments), # SIMPLU
            ("💉 Top Donatori", self.report_top_donors),                  # SIMPLU
            ("✅ Donatori Eligibili", self.report_eligible_donors),       # SIMPLU
        
            #INTEROGARI COMPLEXE (4)
            ("📈 Donatii pe Luna", self.report_donations_monthly),        # COMPLEX
            ("⚠️ Stoc Critic", self.report_critical_stock),               # COMPLEX
            ("📊 Stat. Eligibilitate", self.report_eligibility_stats),    # COMPLEX
            ("🚨 Donatori Risc Ridicat", self.report_high_risk_donors)    # COMPLEX
        ]
    
        for i, (text, command) in enumerate(reports):
            row, col = divmod(i, 3)
            btn = ttk.Button(reports_frame, text=text, command=command, width=25)
            btn.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
            reports_frame.grid_rowconfigure(row, weight=1)
            reports_frame.grid_columnconfigure(col, weight=1)
    
        # Adauga un label explicativ
        info_frame = tk.Frame(self.content_frame, bg=self.color_bg)
        info_frame.pack(pady=10)
    
        tk.Label(info_frame, text="", 
                 font=('Arial', 9), bg=self.color_bg, fg='#cc0000').pack()
    
    def report_blood_groups(self):
        """Raport: Donatori pe grupe sanguine."""
        conn = get_connection()
        if conn is None:
            return
        
        try:
            df = pd.read_sql("""
                SELECT GrupaSanguina, COUNT(*) as NrDonatori,
                       SUM(CASE WHEN EsteEligibil = 1 THEN 1 ELSE 0 END) as Eligibili,
                       SUM(CASE WHEN EsteEligibil = 0 THEN 1 ELSE 0 END) as Neeligibili
                FROM Donatori
                GROUP BY GrupaSanguina
                ORDER BY GrupaSanguina
            """, conn)
            
            self.show_report_window("Donatori pe Grupe Sanguine", df)
        except Exception as e:
            messagebox.showerror("Eroare", f"Eroare la generare raport:\n{str(e)}")
        finally:
            conn.close()
    
    def report_donations_monthly(self):
        """Raport: Donatii pe luna."""
        conn = get_connection()
        if conn is None:
            return
        
        try:
            df = pd.read_sql("""
                SELECT FORMAT(DataDonatie, 'yyyy-MM') as Luna,
                       COUNT(*) as NrDonatii,
                       SUM(Cantitate) as CantitateTotala,
                       AVG(Cantitate) as CantitateMedie
                FROM Donatii
                GROUP BY FORMAT(DataDonatie, 'yyyy-MM')
                ORDER BY Luna DESC
            """, conn)
            
            self.show_report_window("Donatii pe Luna", df)
        except Exception as e:
            messagebox.showerror("Eroare", f"Eroare la generare raport:\n{str(e)}")
        finally:
            conn.close()
    
    def report_donors_with_diseases(self):
        """Raport: Donatori cu boli restrictive."""
        conn = get_connection()
        if conn is None:
            return
        
        try:
            df = pd.read_sql("""
                SELECT d.Nume + ' ' + d.Prenume as Donator,
                       d.GrupaSanguina,
                       b.Denumire as Boala,
                       db.DataDiagnostic
                FROM DonatoriBoli db
                JOIN Donatori d ON db.IDDonator = d.IDDonator
                JOIN BoliRestrictive b ON db.IDBoala = b.IDBoala
                ORDER BY d.Nume, d.Prenume, db.DataDiagnostic DESC
            """, conn)
            
            self.show_report_window("Donatori cu Boli Restrictive", df)
        except Exception as e:
            messagebox.showerror("Eroare", f"Eroare la generare raport:\n{str(e)}")
        finally:
            conn.close()
    
    def report_abnormal_analyses(self):
        """Raport: Analize anormale."""
        conn = get_connection()
        if conn is None:
            return
        
        try:
            df = pd.read_sql("""
                SELECT d.Nume + ' ' + d.Prenume as Donator,
                       am.Denumire as Analiza,
                       ra.Valoare,
                       am.ValoareMinima,
                       am.ValoareMaxima,
                       ra.DataAnaliza
                FROM RezultateAnalize ra
                JOIN Donatori d ON ra.IDDonator = d.IDDonator
                JOIN AnalizeMedicale am ON ra.IDAnaliza = am.IDAnaliza
                WHERE ra.EsteInLimitaNormala = 0
                ORDER BY ra.DataAnaliza DESC
            """, conn)
            
            self.show_report_window("Analize Anormale", df)
        except Exception as e:
            messagebox.showerror("Eroare", f"Eroare la generare raport:\n{str(e)}")
        finally:
            conn.close()
    
    def report_upcoming_appointments(self):
        """Raport: Programari viitoare."""
        conn = get_connection()
        if conn is None:
            return
        
        try:
            df = pd.read_sql("""
                SELECT d.Nume + ' ' + d.Prenume as Donator,
                       p.DataProgramare,
                       p.Stare,
                       d.Telefon,
                       d.Email
                FROM Programari p
                JOIN Donatori d ON p.IDDonator = d.IDDonator
                WHERE p.DataProgramare >= GETDATE()
                AND p.Stare = 'Confirmata'
                ORDER BY p.DataProgramare
            """, conn)
            
            self.show_report_window("Programari Viitoare", df)
        except Exception as e:
            messagebox.showerror("Eroare", f"Eroare la generare raport:\n{str(e)}")
        finally:
            conn.close()
    
    def report_top_donors(self):
        """Raport: Top donatori."""
        conn = get_connection()
        if conn is None:
            return
        
        try:
            df = pd.read_sql("""
                SELECT TOP 10 d.Nume + ' ' + d.Prenume as Donator,
                       d.GrupaSanguina,
                       COUNT(dn.IDDonatie) as NrDonatii,
                       SUM(dn.Cantitate) as CantitateTotala,
                       MAX(dn.DataDonatie) as UltimaDonatie
                FROM Donatori d
                LEFT JOIN Donatii dn ON d.IDDonator = dn.IDDonator
                GROUP BY d.IDDonator, d.Nume, d.Prenume, d.GrupaSanguina
                ORDER BY NrDonatii DESC, CantitateTotala DESC
            """, conn)
            
            self.show_report_window("Top 10 Donatori", df)
        except Exception as e:
            messagebox.showerror("Eroare", f"Eroare la generare raport:\n{str(e)}")
        finally:
            conn.close()
    
    def report_critical_stock(self):
        """Raport: Stoc critic."""
        conn = get_connection()
        if conn is None:
            return
    
        try:
            df = pd.read_sql("""
                WITH GrupeSanguine AS (
                    SELECT 'A+' as Grupa UNION SELECT 'A-' UNION SELECT 'B+' 
                    UNION SELECT 'B-' UNION SELECT 'AB+' UNION SELECT 'AB-' 
                    UNION SELECT '0+' UNION SELECT '0-'
                ),
                StocValabil AS (
                    SELECT GrupaSanguina, SUM(Cantitate) as CantitateTotala
                    FROM StocSange
                    WHERE DataExpirare IS NULL OR DataExpirare > GETDATE()
                    GROUP BY GrupaSanguina
                )
                SELECT gs.Grupa as GrupaSanguina, 
                       COALESCE(sv.CantitateTotala, 0) as CantitateTotala,
                       CASE 
                         WHEN COALESCE(sv.CantitateTotala, 0) < 200 THEN 'CRITIC'
                         WHEN COALESCE(sv.CantitateTotala, 0) < 500 THEN 'BAJ'
                         ELSE 'OK'
                       END as Stare
                FROM GrupeSanguine gs
                LEFT JOIN StocValabil sv ON gs.Grupa = sv.GrupaSanguina
                WHERE COALESCE(sv.CantitateTotala, 0) < 500
                ORDER BY CantitateTotala
            """, conn)
        
            self.show_report_window("Stoc Critic (sub 500ml)", df)
        except Exception as e:
            messagebox.showerror("Eroare", f"Eroare la generare raport:\n{str(e)}")
        finally:
            conn.close()
    
    def report_eligible_donors(self):
        """Raport: Donatori eligibili."""
        conn = get_connection()
        if conn is None:
            return
        
        try:
            df = pd.read_sql("""
                SELECT Nume + ' ' + Prenume as Donator,
                       GrupaSanguina,
                       Telefon,
                       Email,
                       DataInregistrarii
                FROM Donatori
                WHERE EsteEligibil = 1
                ORDER BY Nume, Prenume
            """, conn)
            
            self.show_report_window("Donatori Eligibili", df)
        except Exception as e:
            messagebox.showerror("Eroare", f"Eroare la generare raport:\n{str(e)}")
        finally:
            conn.close()

    def report_eligibility_stats(self):
        """Raport: Statistici eligibilitate cu CASE."""
        conn = get_connection()
        if conn is None:
            return
    
        try:
            df = pd.read_sql("""
                SELECT 
                    GrupaSanguina,
                    COUNT(*) as TotalDonatori,
                    SUM(CASE WHEN EsteEligibil = 1 THEN 1 ELSE 0 END) as Eligibili,
                    SUM(CASE WHEN EsteEligibil = 0 THEN 1 ELSE 0 END) as Neeligibili,
                    CONCAT(
                        FORMAT(
                            CAST(SUM(CASE WHEN EsteEligibil = 1 THEN 1.0 ELSE 0 END) / 
                            NULLIF(COUNT(*), 0) * 100 as DECIMAL(5,2)), 
                        'N2'), '%') as ProcentEligibili
                FROM Donatori
                GROUP BY GrupaSanguina
                ORDER BY GrupaSanguina
            """, conn)
        
            self.show_report_window("Statistici Eligibilitate pe Grupe", df)
        except Exception as e:
            messagebox.showerror("Eroare", f"Eroare la generare raport:\n{str(e)}")
        finally:
            conn.close()
    
    def report_high_risk_donors(self):
        """Raport complex: Donatori cu risc ridicat (mai multe probleme combinate)."""
        conn = get_connection()
        if conn is None:
            return
    
        try:
            df = pd.read_sql("""
                -- Interogare complexa cu multiple subcereri si conditii
                SELECT 
                    d.Nume + ' ' + d.Prenume as Donator,
                    d.GrupaSanguina,
                    d.DataNasterii,
                
                    -- Subcerere pentru numarul de boli
                    (SELECT COUNT(*) 
                     FROM DonatoriBoli db 
                     WHERE db.IDDonator = d.IDDonator) as NrBoli,
                
                    -- Subcerere pentru analize anormale
                    (SELECT COUNT(*) 
                     FROM RezultateAnalize ra 
                     WHERE ra.IDDonator = d.IDDonator 
                       AND ra.EsteInLimitaNormala = 0) as NrAnalizeAnormale,
                
                    -- Subcerere pentru data ultimei donatii
                    (SELECT MAX(DataDonatie) 
                     FROM Donatii dn 
                     WHERE dn.IDDonator = d.IDDonator) as UltimaDonatie,
                
                    -- Calcul varsta
                    DATEDIFF(YEAR, d.DataNasterii, GETDATE()) as Varsta,
                
                    -- Calcul luni de la ultima donatie
                    CASE 
                        WHEN (SELECT MAX(DataDonatie) FROM Donatii dn WHERE dn.IDDonator = d.IDDonator) IS NULL 
                        THEN 999
                        ELSE DATEDIFF(MONTH, 
                             (SELECT MAX(DataDonatie) FROM Donatii dn WHERE dn.IDDonator = d.IDDonator), 
                             GETDATE())
                    END as LuniDeLaUltimaDonatie,
                
                    -- Scor de risc (calculat)
                    CASE 
                        WHEN d.EsteEligibil = 0 THEN 3
                        ELSE 0
                    END +
                    (SELECT COUNT(*) FROM DonatoriBoli db WHERE db.IDDonator = d.IDDonator) * 2 +
                    (SELECT COUNT(*) FROM RezultateAnalize ra WHERE ra.IDDonator = d.IDDonator AND ra.EsteInLimitaNormala = 0) +
                    CASE 
                        WHEN (SELECT MAX(DataDonatie) FROM Donatii dn WHERE dn.IDDonator = d.IDDonator) IS NULL 
                        THEN 1
                        WHEN DATEDIFF(MONTH, (SELECT MAX(DataDonatie) FROM Donatii dn WHERE dn.IDDonator = d.IDDonator), GETDATE()) > 12 
                        THEN 2
                        ELSE 0
                    END as ScorRisc
                
                FROM Donatori d
            
                WHERE 
                    -- Conditii pentru risc ridicat
                    (
                        d.EsteEligibil = 0 
                        OR EXISTS (SELECT 1 FROM DonatoriBoli db WHERE db.IDDonator = d.IDDonator)
                        OR EXISTS (SELECT 1 FROM RezultateAnalize ra WHERE ra.IDDonator = d.IDDonator AND ra.EsteInLimitaNormala = 0)
                        OR DATEDIFF(MONTH, 
                             ISNULL((SELECT MAX(DataDonatie) FROM Donatii dn WHERE dn.IDDonator = d.IDDonator), '1900-01-01'), 
                             GETDATE()) > 12
                    )
                
                ORDER BY ScorRisc DESC, NrBoli DESC, NrAnalizeAnormale DESC
            
            """, conn)
        
            self.show_report_window("Donatori cu Risc Ridicat", df)
        except Exception as e:
            messagebox.showerror("Eroare", f"Eroare la generare raport:\n{str(e)}")
        finally:
            conn.close()
    
    def show_report_window(self, title, dataframe):
        """Afiseaza un raport intr-o fereastra separata."""
        window = tk.Toplevel(self.root)
        window.title(title)
        window.geometry("900x500")
        window.configure(bg=self.color_bg)
        
        tk.Label(window, text=title, font=('Arial', 16, 'bold'), 
                bg=self.color_bg, fg=self.color_fg).pack(pady=10)
        
        # Frame pentru tabel
        table_frame = tk.Frame(window)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Creare tabel
        columns = list(dataframe.columns)
        tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=20)
        
        # Setare antete
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=100, anchor=tk.CENTER)
        
        # Scrollbar
        scrollbar_y = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
        scrollbar_x = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=tree.xview)
        tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        tree.grid(row=0, column=0, sticky='nsew')
        scrollbar_y.grid(row=0, column=1, sticky='ns')
        scrollbar_x.grid(row=1, column=0, sticky='ew')
        
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
        # Inserare date
        for _, row in dataframe.iterrows():
            tree.insert('', tk.END, values=list(row))
        
        # Butoane
        button_frame = tk.Frame(window, bg=self.color_bg)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="Exporta CSV", 
                  command=lambda: self.export_dataframe_csv(dataframe, title)).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Inchide", command=window.destroy).pack(side=tk.LEFT, padx=5)
    
    def export_dataframe_csv(self, dataframe, report_name):
        """Exporta un DataFrame in CSV."""
        filename = f"raport_{report_name.lower().replace(' ', '_')}.csv"
        dataframe.to_csv(filename, index=False, encoding='utf-8')
        messagebox.showinfo("Export", f"Raport exportat in '{filename}'")
    
    def show_status(self, message):
        """Afiseaza un mesaj de status."""
        # Poți adauga o bara de status in viitor
        print(f"Status: {message}")

# RULARE APLICATIE
if __name__ == "__main__":
    try:
        import pyodbc
        import pandas as pd
    except ImportError:
        print("EROARE: PyODBC sau Pandas nu sunt instalate!")
        print("Instaleaza cu: pip install pyodbc pandas")
        input("Apasa Enter pentru a iesi...")
        exit()
    
    root = tk.Tk()
    app = BloodDonationApp(root)
    root.mainloop()