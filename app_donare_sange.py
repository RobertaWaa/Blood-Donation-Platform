import tkinter as tk
from tkinter import ttk, messagebox
import pyodbc
import pandas as pd

#CONEXIUNE AZURE SQL
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
        
        title_label = tk.Label(title_frame, text="🏥 PLATFORMa DE DONARE SaNGE", 
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
        ttk.Button(action_frame, text="Vezi Analize", command=self.view_analyses).pack(side=tk.LEFT, padx=5)
        ttk.Button(action_frame, text="Vezi Boli", command=self.view_diseases).pack(side=tk.LEFT, padx=5)
        
        # incarca datele
        self.load_donors()
    
    def load_donors(self, search_term=None):
        """Încarcă donatorii în tabel."""
        # Șterge datele existente
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
        
            # DEBUG: Afișează câte rânduri și primul rând
            print(f"DEBUG - Rânduri returnate din SQL: {len(rows)}")
            if rows:
                print(f"DEBUG - Primul rând RAW: {rows[0]}")
                print(f"DEBUG - Tip prim rând: {type(rows[0])}")
                print(f"DEBUG - Lungime prim rând: {len(rows[0])}")
                for i, val in enumerate(rows[0]):
                    print(f"  Col {i}: {repr(val)} (tip: {type(val)})")
        
            # INSERARE CORECTĂ ÎN TREEVIEW
            for row in rows:
                # Convertim fiecare rând într-o listă simplă
                # row este un tuple de la cursor.fetchall()
                row_values = []
                for value in row:
                    # Convertim None la string gol
                    if value is None:
                        row_values.append('')
                    else:
                        row_values.append(str(value))
            
                # DEBUG pentru primul rând
                if len(row_values) > 0 and row_values[0] == '5':
                    print(f"DEBUG - Inserare rând Dumitrescu: {row_values}")
            
                # Inserăm în Treeview
                self.donor_tree.insert('', tk.END, values=row_values)
        
            status = f"Afișați {len(rows)} donatori" + (" (filtrat)" if search_term else "")
            self.show_status(status)
        
        except Exception as e:
            messagebox.showerror("Eroare", f"Eroare la încărcarea donatorilor:\n{str(e)}")
            import traceback
            traceback.print_exc()
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
        window.grab_set()  # Modal
        
        # Titlu
        tk.Label(window, text="DATE DONATOR NOU", font=('Arial', 16, 'bold'), 
                bg=self.color_bg, fg=self.color_fg).pack(pady=20)
        
        # Frame pentru formular
        form_frame = tk.Frame(window, bg=self.color_bg)
        form_frame.pack(padx=40, pady=10)
        
        # Campuri
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
        
        # Gen (Radio buttons)
        tk.Label(form_frame, text="Gen*", bg=self.color_bg, fg=self.color_fg, 
                font=('Arial', 10)).grid(row=len(fields), column=0, sticky=tk.W, pady=8)
        gender_frame = tk.Frame(form_frame, bg=self.color_bg)
        gender_frame.grid(row=len(fields), column=1, pady=8, sticky=tk.W)
        
        self.gender_var = tk.StringVar(value="M")
        tk.Radiobutton(gender_frame, text="Masculin", variable=self.gender_var, 
                      value="M", bg=self.color_bg).pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(gender_frame, text="Feminin", variable=self.gender_var, 
                      value="F", bg=self.color_bg).pack(side=tk.LEFT, padx=10)
        
        # Grupa sanguina (Combobox)
        tk.Label(form_frame, text="Grupa Sanguina*", bg=self.color_bg, fg=self.color_fg, 
                font=('Arial', 10)).grid(row=len(fields)+1, column=0, sticky=tk.W, pady=8)
        self.blood_group_var = tk.StringVar()
        blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', '0+', '0-']
        blood_combo = ttk.Combobox(form_frame, textvariable=self.blood_group_var, 
                                  values=blood_groups, width=37)
        blood_combo.grid(row=len(fields)+1, column=1, pady=8, padx=10)
        blood_combo.current(0)
        
        # Butoane
        button_frame = tk.Frame(window, bg=self.color_bg)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Salveaza", command=lambda: self.save_donor(window)).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Anuleaza", command=window.destroy).pack(side=tk.LEFT, padx=10)
    
    def save_donor(self, window):
        """Salveaza donatorul nou in baza de date."""
        # Validare
        required = ['nume', 'prenume', 'cnp', 'data_nasterii']
        for field in required:
            if not self.donor_entries[field].get().strip():
                messagebox.showwarning("Validare", f"Campul '{field}' este obligatoriu!")
                return
        
        # Validare CNP
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
            self.load_donors()  # Reincarca lista
            
        except pyodbc.IntegrityError:
            messagebox.showerror("Eroare", "CNP-ul exista deja in sistem!")
        except Exception as e:
            messagebox.showerror("Eroare", f"Eroare la salvare:\n{str(e)}")
        finally:
            cursor.close()
            conn.close()
    
    def edit_donor(self):
        """Editează donatorul selectat."""
        selection = self.donor_tree.selection()
        if not selection:
            messagebox.showwarning("Selecție", "Selectează un donator din listă!")
            return
    
        item = self.donor_tree.item(selection[0])
        values = item['values']
    
        # DEBUG: Afișează ce valori primești
        print(f"DEBUG - Valori selectate: {values}")
        print(f"DEBUG - Tip valori: {type(values)}")
        print(f"DEBUG - Lungime: {len(values)}")
        for i, val in enumerate(values):
            print(f"  Col {i}: {repr(val)} (tip: {type(val)})")
    
        if not values:
            messagebox.showerror("Eroare", "Nu s-au găsit date pentru donatorul selectat!")
            return
    
        # PRIMA valoare este ID-ul
        donor_id = values[0]
        print(f"DEBUG - ID extras: {donor_id}")
    
        # Verifică dacă ID-ul este valid
        if donor_id is None:
            messagebox.showerror("Eroare", "ID-ul donatorului este NULL!")
            return
    
        # Încearcă conversia la int
        try:
            donor_id_int = int(donor_id)
            print(f"DEBUG - ID convertit: {donor_id_int}")
        except (ValueError, TypeError) as e:
            messagebox.showerror("Eroare", f"ID invalid pentru donator: {donor_id}\nEroare: {str(e)}")
            return
        # Deschide fereastra de editare
        self.edit_donor_window(donor_id_int)
    
    def edit_donor_window(self, donor_id):
        """Fereastra pentru editare donator."""
        # Obtine datele curente
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
        
        # Fereastra de editare
        window = tk.Toplevel(self.root)
        window.title(f"Editare Donator ID: {donor_id}")
        window.geometry("500x650")
        window.configure(bg=self.color_bg)
        window.grab_set()
        
        tk.Label(window, text="EDITARE DONATOR", font=('Arial', 16, 'bold'), 
                bg=self.color_bg, fg=self.color_fg).pack(pady=20)
        
        form_frame = tk.Frame(window, bg=self.color_bg)
        form_frame.pack(padx=40, pady=10)
        
        # Campuri (similar cu adaugarea)
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
        
        # Gen
        tk.Label(form_frame, text="Gen*", bg=self.color_bg, fg=self.color_fg).grid(row=len(fields), column=0, sticky=tk.W, pady=8)
        gender_frame = tk.Frame(form_frame, bg=self.color_bg)
        gender_frame.grid(row=len(fields), column=1, pady=8, sticky=tk.W)
        
        self.edit_gender_var = tk.StringVar(value=row[4])
        tk.Radiobutton(gender_frame, text="Masculin", variable=self.edit_gender_var, 
                      value="M", bg=self.color_bg).pack(side=tk.LEFT, padx=10)
        tk.Radiobutton(gender_frame, text="Feminin", variable=self.edit_gender_var, 
                      value="F", bg=self.color_bg).pack(side=tk.LEFT, padx=10)
        
        # Grupa sanguina
        tk.Label(form_frame, text="Grupa Sanguina*", bg=self.color_bg, fg=self.color_fg).grid(row=len(fields)+1, column=0, sticky=tk.W, pady=8)
        self.edit_blood_var = tk.StringVar(value=row[5])
        blood_combo = ttk.Combobox(form_frame, textvariable=self.edit_blood_var, 
                                  values=['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', '0+', '0-'], width=37)
        blood_combo.grid(row=len(fields)+1, column=1, pady=8, padx=10)
        
        # Eligibilitate
        tk.Label(form_frame, text="Eligibil", bg=self.color_bg, fg=self.color_fg).grid(row=len(fields)+2, column=0, sticky=tk.W, pady=8)
        self.eligible_var = tk.BooleanVar(value=row[9] == 1)
        tk.Checkbutton(form_frame, variable=self.eligible_var, bg=self.color_bg).grid(row=len(fields)+2, column=1, sticky=tk.W, pady=8)
        
        # Butoane
        button_frame = tk.Frame(window, bg=self.color_bg)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Salveaza Modificari", 
                  command=lambda: self.update_donor(donor_id, window)).pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="Anuleaza", command=window.destroy).pack(side=tk.LEFT, padx=10)
    
    def update_donor(self, donor_id, window):
        """Actualizeaza donatorul in baza de date."""
        # Validare (similar cu adaugarea)
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
                                     f"Esti sigur ca vrei sa stergi donatorul:\n{nume} {prenume}?\n\nAceasta actiune va sterge si toate datele asociate (analize, programari, etc.)!")
        
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
    
    def view_analyses(self):
        """Afiseaza analizele donatorului selectat."""
        selection = self.donor_tree.selection()
        if not selection:
            messagebox.showwarning("Selectie", "Selecteaza un donator din lista!")
            return
        
        item = self.donor_tree.item(selection[0])
        donor_id, nume, prenume = item['values'][0], item['values'][1], item['values'][2]
        
        # Aici poti implementa vizualizarea analizelor
        messagebox.showinfo("Analize", f"Analize pentru {nume} {prenume}\n\nAceasta functie va fi implementata in versiunea completa.")
    
    def view_diseases(self):
        """Afiseaza bolile donatorului selectat."""
        selection = self.donor_tree.selection()
        if not selection:
            return
        
        item = self.donor_tree.item(selection[0])
        donor_id, nume, prenume = item['values'][0], item['values'][1], item['values'][2]
        messagebox.showinfo("Boli", f"Boli restrictive pentru {nume} {prenume}\n\nFunctie in dezvoltare.")
    
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
    
    def show_status(self, message):
        """Afiseaza un mesaj de status."""
        # Poti adauga o bara de status in viitor
        print(f"Status: {message}")
    
    # Functii pentru celelalte module (de implementat)
    def show_diseases(self):
        self.clear_content()
        tk.Label(self.content_frame, text="BOLI RESTRICTIVE (in constructie)", 
                font=('Arial', 18), bg=self.color_bg, fg=self.color_fg).pack(pady=100)
    
    def show_analyses(self):
        self.clear_content()
        tk.Label(self.content_frame, text="ANALIZE MEDICALE (in constructie)", 
                font=('Arial', 18), bg=self.color_bg, fg=self.color_fg).pack(pady=100)
    
    def show_appointments(self):
        self.clear_content()
        tk.Label(self.content_frame, text="PROGRAMaRI (in constructie)", 
                font=('Arial', 18), bg=self.color_bg, fg=self.color_fg).pack(pady=100)
    
    def show_donations(self):
        self.clear_content()
        tk.Label(self.content_frame, text="DONAtII (in constructie)", 
                font=('Arial', 18), bg=self.color_bg, fg=self.color_fg).pack(pady=100)
    
    def show_stock(self):
        self.clear_content()
        tk.Label(self.content_frame, text="STOC SaNGE (in constructie)", 
                font=('Arial', 18), bg=self.color_bg, fg=self.color_fg).pack(pady=100)
    
    def show_reports(self):
        self.clear_content()
        tk.Label(self.content_frame, text="RAPOARTE (in constructie)", 
                font=('Arial', 18), bg=self.color_bg, fg=self.color_fg).pack(pady=100)

# RULARE APLICATIE
if __name__ == "__main__":
    try:
        import pyodbc
    except ImportError:
        print("EROARE: PyODBC nu este instalat!")
        print("Instaleaza cu: pip install pyodbc pandas")
        input("Apasa Enter pentru a iesi...")
        exit()
    
    root = tk.Tk()
    app = BloodDonationApp(root)
    root.mainloop()