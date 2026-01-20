# Platformă de Donare Sânge

## Descriere Proiect
Aplicație pentru gestionarea donatorilor, programărilor, analizelor medicale și stocurilor de sânge într-un centru de transfuzii. Proiectul implementează o bază de date relațională completă cu interfață vizuală în Python.

## Cerințe Funcționale
- **Gestionare Donatori** (adaugare, modificare, ștergere, căutare)
- **Gestionare Boli Restrictive** și asocierea acestora cu donatori
- **Gestionare Analize Medicale** și rezultate
- **Gestionare Programări** (creare, confirmare, anulare, finalizare)
- **Înregistrare Donații** și actualizare automată a stocului
- **Gestionare Stoc Sânge** pe grupe sanguine
- **Rapoarte și Statistici** (6 interogări simple + 4 interogări complexe)

## Structura Bazei de Date

### Tabele Principale (9 tabele)
1. **Donatori** - informații personale donatori
2. **BoliRestrictive** - catalog boli care restricționează donarea
3. **DonatoriBoli** - tabel de legătură N:N donatori-boli
4. **AnalizeMedicale** - tipuri de analize medicale
5. **RezultateAnalize** - rezultate analize pentru donatori
6. **Programari** - programări pentru donare
7. **Donatii** - istoric donații
8. **StocSange** - stoc curent pe grupe sanguine
9. **Utilizatori** - medici și administratori 

### Relații
- **2 relații 1:N**: Donatori → RezultateAnalize, Donatori → Programări
- **1 relație N:N**: Donatori ↔ BoliRestrictive (prin DonatoriBoli)

## Tehnologii Utilizate

### Backend
- **Azure SQL Database** sau SQL Server
- **PyODBC** pentru conectare Python-SQL
- **Pandas** pentru procesare date

### Frontend
- **Tkinter** pentru interfața grafică
- **TTK** pentru widget-uri moderne
- **Custom styling** cu scheme de culori roz

## Instalare și Configurare

### 1. Instalare Dependințe
```bash
pip install pyodbc pandas
pip install tkcalendar
```

### 2. Configurare Baza de Date
1. Creați baza de date în Azure SQL sau SQL Server
2. Rulați scriptul SQL pentru crearea tabelelor
3. Configurați conexiunea în fișierul Python:
```python
server = 'sqlsbd.database.windows.net'
database = 'BD_DonareSange'
username = 'adminstudent'
password = 'parola_ta'
driver = '{ODBC Driver 18 for SQL Server}'
```

### 3. Rulare Aplicație
```bash
python app_donare_sange.py
```

## Interogări SQL Implementate

### 6 Interogări Simple (JOIN)
1. **Donatori pe grupe sanguine** - GROUP BY pe grupe
2. **Donatori cu boli restrictive** - JOIN Donatori-Boli
3. **Analize anormale** - JOIN cu limite normale
4. **Programări viitoare** - filtrare pe data curentă
5. **Top donatori** - ORDER BY după număr donații
6. **Donatori eligibili** - filtrare pe câmpul de eligibilitate

### 4 Interogări Complexe (Subcereri)
1. **Donații pe lună** - GROUP BY lună + agregare
2. **Stoc critic** - WITH, COALESCE, LEFT JOIN, HAVING
3. **Statistici eligibilitate** - CASE, calcul procente
4. **Donatori cu risc ridicat** - subcereri corelate, scor calculat

## Interfața Grafică

### Structura Interfeței
- **Meniu lateral** cu 7 module principale
- **Culori tematice** (roz pentru donare sânge)
- **Tabele cu sortare** și scrollbar
- **Formulare validate** pentru input
- **Fereastre modale** pentru operații CRUD

### Module Implementate
1. **Donatori** - CRUD complet + export CSV
2. **Boli Restrictive** - gestionare boli + asociere donatori
3. **Analize Medicale** - analize + rezultate + verificare automată
4. **Programări** - calendar + gestionare stări
5. **Donații** - înregistrare + actualizare stoc
6. **Stoc Sânge** - vizualizare + detectare critice
7. **Rapoarte** - 10 rapoarte (6 simple + 4 complexe)

## Structura Fișierelor
```
Proiect_SBD/
├── app_donare_sange.py          # Aplicația principală Python
├── schema_baza_date.sql         # Script creare tabele + date test
├── README.md                    # Documentația proiectului
├── donatori_export.csv          # Export exemplu (generat)
├── raport_donatii.csv           # Raport exemplu (generat)
└── stoc_sange_export.csv        # Stoc export (generat)
```

## Caracteristici Avansate

### Validări și Constrângeri
- **CNP unic** și validare 13 cifre
- **Grupă sanguină validă** (A+, A-, B+, etc.)
- **Gen valid** (M/F)
- **Cantitate donație** (400-500 ml)
- **Integritate referențială** cu ON DELETE CASCADE

### Funcționalități Specifice
- **Calcul automat eligibilitate** pe baza analizelor
- **Actualizare automată stoc** la înregistrare donație
- **Detectare grupe critice** (sub 200 ml)
- **Export CSV** pentru toate modulele
- **Căutare avansată** cu filtre multiple

## Cerințe Îndeplinite

| Cerință | Status | Detalii |
|---------|--------|---------|
| Minim 5 tabele | ✅ | 9 tabele create |
| Minim 2 relații 1:N | ✅ | 3 relații 1:N implementate |
| Minim 1 relație N:N | ✅ | Donatori ↔ BoliRestrictive |
| CRUD pe minim 2 tabele | ✅ | CRUD pe toate tabelele principale |
| 6 interogări simple (JOIN) | ✅ | Implementate în modulul Rapoarte |
| 4 interogări complexe | ✅ | Cu subcereri, GROUP BY, HAVING, CASE |
| Interfață vizuală Python | ✅ | Tkinter complet funcțional |
| Parametri variabili interogări | ✅ | Căutare avansată cu filtre dinamice |

## Capturi de Ecran

### Fereastra Principală
```
+------------------------------------------+
|  🏥 PLATFORMĂ DE DONARE SÂNGE            |
+-------------------+----------------------+
|                   |                      |
|  👥 Donatori      |  [Tabel donatori]    |
|  🏥 Boli          |  [Butoane CRUD]      |
|  🩸 Analize       |  [Căutare]           |
|  📅 Programări    |                      |
|  💉 Donații       |                      |
|  📊 Stoc          |                      |
|  📈 Rapoarte      |                      |
|  🚪 Ieșire        |                      |
|                   |                      |
+-------------------+----------------------+
```

### Exemplu Raport Complex
```sql
-- Donatori cu risc ridicat (interogare complexă)
SELECT 
    d.Nume + ' ' + d.Prenume as Donator,
    -- Subcerere pentru boli
    (SELECT COUNT(*) FROM DonatoriBoli db WHERE db.IDDonator = d.IDDonator) as NrBoli,
    -- Subcerere pentru analize anormale  
    (SELECT COUNT(*) FROM RezultateAnalize ra WHERE ra.IDDonator = d.IDDonator AND ra.EsteInLimitaNormala = 0) as NrAnalizeAnormale,
    -- Calcul scor risc (CASE complex)
    CASE WHEN d.EsteEligibil = 0 THEN 3 ELSE 0 END +
    (SELECT COUNT(*) FROM DonatoriBoli db WHERE db.IDDonator = d.IDDonator) * 2 as ScorRisc
FROM Donatori d
ORDER BY ScorRisc DESC;
```

## Depanare

### Probleme Comune
1. **Eroare conexiune ODBC**
   ```bash
   # Instalați driver ODBC
   # Descărcați: https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server
   ```

2. **Firewall Azure**
   - Adăugați IP-ul în Azure Portal → SQL Database → Networking

3. **Module Python lipsă**
   ```bash
   pip install pyodbc pandas
   ```

### Logging și Debug
Aplicația afișează mesaje de debug în consolă:
- Conexiune reușită/erată
- Număr de înregistrări returnate
- Erori SQL detaliate



## Licență
Proiect academic pentru cursul de Sisteme de Baze de Date. Poate fi folosit ca referință pentru alte proiecte similare.

---

**Proiect realizat de:** Ana-Maria Roberta NECULA  
**Disciplina:** Sisteme de Baze de Date  
**Universitatea:** Universitatea Politehnica Bucuresti  
**Anul academic:** 2025-2026
