# <img src="python_logo.png" alt="Python_logo" height="128px">


# PasswdMGR

## Program został przetestowany na:

| System operacyjny              | Wspierane |
| ------------------------------ | --------- |
| Windows 11 24H2                | ✅        |
| Debian - Parrot OS 6.0         | ✅        |

*Program został przetestowany i zweryfikowany na systemach operacyjnych wymienionych powyżej. Nie gwarantujemy pełnej kompatybilności działania na innych dystrybucjach Linuxa,
które nie zostały wyraźnie wskazane jako wspierane.*

## Wprowadzenie
Projekt jest rozbudowanym menedżerem haseł napisanym w języku Python. Aplikacja pozwala użytkownikowi na przechowywanie haseł w sposób bezpieczny, 
oferując takie funkcje jak szyfrowanie haseł, zarządzanie bazą danych, generowanie haseł oraz obsługę sesji użytkownika.

## Funkcjonalnośći

***Bezpieczne logowanie***
 - Logowanie do aplikacji wymaga wprowadzenia hasła głównego (Master Password), które jest haszowane za pomocą algorytmu SHA-512.
 - Mechanizm ochrony przed atakami siłowymi: blokada po trzech nieudanych próbach logowania.

***Przechowywanie danych***
 - Aplikacja przechowuje dane (adresy stron internetowych, nazwy użytkowników i hasła) w lokalnej bazie danych SQLite.
 - Hasła są szyfrowane za pomocą algorytmu symetrycznego Fernet z biblioteki cryptography

***Interfejs użytkownika***
 - Responsywny i intuicyjny interfejs oparty na CustomTkinter.
 - Lista zapisanych wpisów z możliwością przeszukiwania i filtrowania danych.
 - Okna dialogowe z powiadomieniami i błędami.

***Zarządzanie hasłami***
- Dodawanie, odczytywanie, usuwanie i kopiowanie haseł do schowka.
- Generowanie silnych haseł z możliwością dostosowania długości i składu znakowego.

***Zarządzanie sesją***
- Automatyczne wylogowanie po upływie 3 minut bezczynności.

***Bezpieczeństwo***
- Dane użytkownika są chronione przed nieautoryzowanym dostępem dzięki szyfrowaniu oraz unikalnym kluczom szyfrowania.

## Opis kodu programu

### Importowanie bibliotek oraz definiowanie nazwy bazy danych

```python
from CTkListbox import *
import customtkinter as ctk
import tkinter.messagebox as messagebox
import hashlib
import os
import sqlite3
import time
import random
import string
from cryptography.fernet import Fernet

DB_FILENAME = "password_manager.db"
```
***from CTkListbox import****  - importuje wszystkie klasy i funkcje z modułu CTkListbox, który jest rozszerzeniem dla biblioteki CustomTkinter. Moduł ten pozwala na użycie zaawansowanych widżetów listy (listbox) w graficznym interfejsie użytkownika.

***import customtkinter as ctk*** - importuje bibliotekę CustomTkinter, która jest nowoczesnym rozszerzeniem dla standardowego Tkintera. Umożliwia ona tworzenie aplikacji z bardziej estetycznym i nowoczesnym interfejsem graficznym. Skrót ctk pozwala na bardziej zwięzłe odwoływanie się do tej biblioteki w kodzie.

***import tkinter.messagebox as messagebox*** - importuje moduł messagebox z biblioteki Tkinter, który służy do wyświetlania okien dialogowych z wiadomościami, takimi jak komunikaty o błędach, ostrzeżenia czy informacje.

***import hashlib*** - importuje moduł hashlib, który umożliwia wykorzystanie kryptograficznych funkcji skrótu, takich jak SHA-512. Jest on używany w tej aplikacji do bezpiecznego haszowania hasła głównego (Master Password).

***import os*** - importuje moduł os, który dostarcza funkcje do interakcji z systemem operacyjnym. W tym projekcie moduł ten jest wykorzystywany do sprawdzania istnienia plików i zarządzania kluczami szyfrowania.

***import sqlite3*** - importuje wbudowaną w Pythona bibliotekę sqlite3, która umożliwia zarządzanie bazami danych SQLite. Aplikacja korzysta z SQLite do przechowywania haseł i danych użytkownika.

***import time*** - importuje moduł time, który dostarcza funkcje do zarządzania czasem, takie jak mierzenie czasu w sekundach od epoki UNIX-a (Unix Epoch Time). W aplikacji wykorzystywany jest do zarządzania sesjami i blokadą po nieudanych próbach logowania.

***import random*** - importuje moduł random, który jest używany do generowania losowych danych. W tej aplikacji jest on wykorzystywany do tworzenia losowych, silnych haseł.

***import string*** - importuje moduł string, który dostarcza stałe zawierające zestawy znaków, takie jak litery alfabetu (małe i wielkie), cyfry czy znaki specjalne. Moduł ten jest również wykorzystywany do generowania haseł.

***from cryptography.fernet import Fernet*** - importuje klasę Fernet z modułu cryptography. Jest to algorytm szyfrowania symetrycznego, który zapewnia bezpieczne szyfrowanie i deszyfrowanie danych. W tej aplikacji służy do zabezpieczania przechowywanych haseł.

***DB_FILENAME = "password_manager.db0"*** - Definiuje nazwę pliku bazy danych SQLite jako "password_manager.db". Plik ten będzie wykorzystywany do przechowywania wszystkich danych związanych z użytkownikami, takimi jak hasła, nazwy użytkowników oraz inne informacje. Jeśli plik nie istnieje, zostanie utworzony podczas inicjalizacji bazy danych.

### Funkcje i mechanizmy odpowiedzialne za bezpieczeństwo aplikacji

Ten fragment kodu stanowi kluczowy element bezpieczeństwa aplikacji. Funkcje te zapewniają, że hasło główne jest zabezpieczone przed nieautoryzowanym dostępem dzięki nieodwracalnemu haszowaniu, a pozostałe hasła użytkownika są chronione przed nieuprawnionym odczytem dzięki szyfrowaniu symetrycznemu. Zarządzanie kluczem szyfrowania pozwala na trwałe i bezpieczne zabezpieczenie danych w pliku, co zwiększa odporność aplikacji na potencjalne ataki.

```python
def hash_master_password(password: str) -> str:
    return hashlib.sha512(password.encode()).hexdigest()

def load_key():
    if os.path.exists("secret.key"):
        with open("secret.key", "rb") as key_file:
            key = key_file.read()
    else:
        key = Fernet.generate_key()
        with open("secret.key", "wb") as key_file:
            key_file.write(key)
    return key

key = load_key()
cipher_suite = Fernet(key)

def encrypt_password(plain_text_password: str) -> str:
    return cipher_suite.encrypt(plain_text_password.encode()).decode()

def decrypt_password(encrypted_password: str) -> str:
    return cipher_suite.decrypt(encrypted_password.encode()).decode()
```
***hash_master_password***\
Funkcja ```hash_master_password``` służy do haszowania hasła głównego użytkownika. Wykorzystuje algorytm SHA-512 z biblioteki ```hashlib```, który generuje unikalny, 128-znakowy skrót w formacie szesnastkowym. Aby uzyskać skrót, hasło jest najpierw zamieniane na bajty za pomocą metody ```encode()```, a następnie haszowane, a wynik jest zwracany jako ciąg tekstowy. Proces ten zapewnia, że hasło główne nigdy nie jest przechowywane w bazie w formie jawnej, co zwiększa bezpieczeństwo danych.

***load_key***\
Funkcja ```load_key``` zarządza kluczem szyfrowania używanym w aplikacji. Najpierw sprawdza, czy w bieżącym katalogu istnieje plik o nazwie ```secret.key```. Jeśli plik istnieje, funkcja otwiera go w trybie binarnym i odczytuje zapisany klucz szyfrowania. Jeśli plik nie istnieje, generowany jest nowy klucz za pomocą metody ```Fernet.generate_key()```, który następnie jest zapisywany w pliku ```secret.key``` w trybie binarnym. Funkcja zwraca klucz w postaci binarnej. Dzięki temu klucz szyfrowania jest trwały między sesjami i przypisany do konkretnej instalacji aplikacji.

***encrypt_password***\
Funkcja encrypt_password służy do szyfrowania haseł użytkownika. Przyjmuje hasło w postaci tekstowej, które najpierw jest zamieniane na bajty za pomocą metody encode(). Następnie obiekt cipher_suite szyfruje dane, a wynik, będący zaszyfrowanym ciągiem bajtów, jest konwertowany na tekst za pomocą decode(). Funkcja zwraca zaszyfrowane hasło jako ciąg tekstowy, co umożliwia jego przechowywanie w bazie danych w sposób bezpieczny.

***decrypt_password***
Funkcja ```decrypt_password``` wykonuje proces odwrotny, czyli odszyfrowuje wcześniej zaszyfrowane hasło. Przyjmuje zaszyfrowane hasło w formie tekstowej, które zamienia na bajty za pomocą ```encode()```. Obiekt ```cipher_suite``` deszyfruje dane, odzyskując pierwotną postać hasła jako bajty. Ostatecznie wynik jest konwertowany na tekst za pomocą metody ```decode()``` i zwracany użytkownikowi. Dzięki temu funkcja umożliwia przywrócenie oryginalnego hasła w celu jego odczytu lub użycia.

### Inicjalizację bazy danych oraz sprawdzenie hasła głównego

Ten fragment kodu pełni kluczową rolę w aplikacji, ponieważ zapewnia prawidłową inicjalizację bazy danych podczas pierwszego uruchomienia oraz umożliwia sprawdzenie, czy użytkownik ustawił już hasło główne. 

```python
def initialize_database():
    first_run = False

    if not os.path.exists(DB_FILENAME):
        first_run = True

    conn = sqlite3.connect(DB_FILENAME)
    cursor = conn.cursor()

    if first_run:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS passwords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                website TEXT NOT NULL,
                username TEXT NOT NULL,
                password TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS master_password (
                id INTEGER PRIMARY KEY,
                password_hash TEXT,
                attempt_count INTEGER DEFAULT 0,
                lock_until REAL
            )
        """)
        conn.commit()

    return conn, cursor

conn, cursor = initialize_database()

cursor.execute("SELECT password_hash FROM master_password LIMIT 1")
row = cursor.fetchone()
MASTER_PASSWORD_SET = True if (row and row[0]) else False
```
Funkcja ```initialize_database``` rozpoczyna swoje działanie od ustawienia zmiennej ```first_run``` na ```False```. Następnie sprawdza, czy plik bazy danych o nazwie zapisanej w zmiennej ```DB_FILENAME``` istnieje w katalogu roboczym. Jeśli plik nie zostanie znaleziony, zmienna ```first_run``` zostaje ustawiona na ```True```, co oznacza, że aplikacja uruchamiana jest po raz pierwszy.

Funkcja nawiązuje połączenie z bazą danych SQLite za pomocą metody ```sqlite3.connect(DB_FILENAME)``` i tworzy obiekt kursora ```cursor```, który umożliwia wykonywanie zapytań SQL. Jeśli aplikacja jest uruchamiana po raz pierwszy, funkcja tworzy w bazie danych dwie tabele. Pierwsza tabela, ```passwords```, jest przeznaczona do przechowywania danych użytkownika, takich jak identyfikator (```id```), adres strony internetowej (```website```), nazwa użytkownika (```username```) oraz zaszyfrowane hasło (```password```). Druga tabela, ```master_password```, służy do przechowywania informacji o haśle głównym. Zawiera takie pola jak identyfikator (```id```), skrót hasła głównego (```password_hash```), licznik nieudanych prób logowania (```attempt_count```) oraz czas odblokowania (```lock_until```).

Po utworzeniu tabel zmiany w bazie danych są zatwierdzane za pomocą metody ```conn.commit()```. Następnie funkcja zwraca obiekty ```conn``` (połączenie z bazą danych) oraz ```cursor``` (do wykonywania operacji na bazie).

Po wywołaniu funkcji ```initialize_database``` kod sprawdza, czy hasło główne zostało już ustawione. W tym celu wykonuje zapytanie SQL, które pobiera wartość skrótu hasła głównego z tabeli ```master_password```. Wynik tego zapytania jest przypisywany do zmiennej ```row```. Na podstawie zawartości zmiennej ```row``` ustalana jest wartość zmiennej ```MASTER_PASSWORD_SET```. Jeśli zmienna ```row``` zawiera dane, oznacza to, że hasło główne zostało ustawione, a zmienna ```MASTER_PASSWORD_SET``` przyjmuje wartość ```True```. W przeciwnym razie ustawiana jest wartość ```False```.

### Wyśrodkowanie i zarządzanie priorytetem wyświetlania okna

```python
def center_window(win, window_width=400, window_height=200, topmost=False):
    win.resizable(False, False)

    screen_width = win.winfo_screenwidth()
    screen_height = win.winfo_screenheight()
    x = (screen_width - window_width) // 2
    y = (screen_height - window_height) // 2

    win.geometry(f"{window_width}x{window_height}+{x}+{y}")

    if topmost:
        win.lift()
        win.attributes("-topmost", True)
```
Funkcja ```center_window``` służy do ustawiania okna aplikacji w centralnym punkcie ekranu, z możliwością oznaczenia okna jako najwyższego (topmost). Funkcja przyjmuje jako argumenty referencję do okna (```win```), opcjonalne parametry szerokości (window_width) i wysokości (```window_height```), które domyślnie wynoszą odpowiednio 400 i 200 pikseli, oraz opcjonalny parametr ```topmost```, który domyślnie ma wartość ```False```.

Na początku działania funkcja wyłącza możliwość zmiany rozmiaru okna przez użytkownika, ustawiając właściwość ```resizable``` na ```False``` dla obu osi (poziomej i pionowej). Następnie pobiera wymiary ekranu użytkownika za pomocą metod ```winfo_screenwidth()``` oraz ```winfo_screenheight()``` i oblicza współrzędne punktu, w którym okno powinno zostać wyświetlone, aby było wycentrowane. Współrzędne te są obliczane w taki sposób, aby od środka ekranu odjąć połowę szerokości i wysokości okna.

Funkcja ustawia geometrię okna za pomocą metody ```geometry()```, podając szerokość, wysokość oraz współrzędne wyśrodkowanego punktu w formacie ```{szerokość}x{wysokość}+{x}+{y}```.

Jeśli parametr ```topmost``` ma wartość ```True```, funkcja ustawia okno jako najwyższe za pomocą metod ```lift()``` i ```attributes("-topmost", True)```. Dzięki temu okno będzie zawsze widoczne na wierzchu innych okien.

### Lista do wyświetlania danych z bazy

Klasa SelectListBox jest rozszerzeniem klasy CTkFrame z biblioteki CustomTkinter. Służy ona do tworzenia widżetu listy, który wyświetla dane pobrane z bazy danych w przyjaznym użytkownikowi formacie. Klasa zawiera konstruktor oraz dwie metody do zarządzania zawartością listy.

```python
class SelectListBox(ctk.CTkFrame):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)

        # Create a CTkListbox widget
        self.listbox = CTkListbox(self, **kwargs)  # Set height and width as per your need
        self.listbox.pack(padx=10, pady=10, fill="both", expand=True)

        self.populate_listbox()

    def populate_listbox(self):
        # Clear the existing items in the listbox
        self.listbox.delete(0, ctk.END)

        # Fetch data from the database and populate the listbox
        cursor.execute("SELECT website, username FROM passwords")
        results = cursor.fetchall()

        if results:
            for website, username in results:
                self.listbox.insert(ctk.END, f"Website: {website}, User: {username}")
        else:
            self.listbox.insert(ctk.END, "No entries found")

    def refresh_listbox(self):
        """Refresh the listbox data after adding a new entry."""
        self.populate_listbox()
```

Konstruktor klasy ```SelectListBox``` inicjalizuje obiekt i tworzy widżet ```CTkListbox``` wewnątrz ramki (```CTkFrame```). Widżet listy (```listbox```) jest konfigurowany z wykorzystaniem przekazanych argumentów ```**kwargs```, które umożliwiają dostosowanie jego wyglądu i rozmiaru. Następnie widżet jest rozmieszczany w ramce za pomocą metody ```pack()```, która zapewnia odpowiednie odstępy (```padx=10```, ```pady=10```) oraz pozwala listboxowi na rozciąganie się, aby wypełnić całą ramkę (```fill="both", expand=True```). Po utworzeniu widżetu konstruktor wywołuje metodę ```populate_listbox```, która wypełnia listę danymi z bazy danych.

Metoda ```populate_listbox``` jest odpowiedzialna za pobieranie danych z bazy danych oraz wyświetlanie ich w widżecie listy. Na początku metoda usuwa wszystkie istniejące elementy w liście za pomocą ```self.listbox.delete(0, ctk.END)```. Następnie wykonuje zapytanie SQL do tabeli ```passwords```, aby pobrać pary danych ```website``` (adres strony internetowej) i ```username``` (nazwa użytkownika). Wyniki zapytania są przechowywane w zmiennej ```results```.

Jeśli w bazie danych znajdują się wpisy, metoda iteruje przez wyniki i dodaje każdy z nich do widżetu listy w sformatowanej postaci: ```"Website: {website}, User: {username}"```. W przypadku, gdy w bazie danych nie ma żadnych wpisów, metoda wyświetla komunikat ```"No entries found"``` w widżecie listy.

Metoda ```refresh_listbox``` pozwala na odświeżenie zawartości widżetu listy. Wywołuje wewnętrznie metodę ```populate_listbox```, która usuwa dotychczasowe dane i ponownie pobiera aktualne informacje z bazy danych. Dzięki temu zmiany wprowadzone w bazie danych, takie jak dodanie nowego wpisu, są od razu widoczne w interfejsie użytkownika.

### Personalizowane okno dialogowe

Klasa ```CTkMessageBox``` jest rozszerzeniem klasy ```CTkToplevel``` z biblioteki CustomTkinter i służy do tworzenia prostych, personalizowanych okien dialogowych, które wyświetlają komunikaty dla użytkownika. Klasa zawiera konstruktor oraz metodę umożliwiającą zamykanie okna.,

```python
class CTkMessageBox(ctk.CTkToplevel):
    def __init__(self, title, message, button_text="OK"):
        super().__init__()
        self.title(title)

        self.geometry("300x150")
        #self.resizable(False, False)

        self.label_message = ctk.CTkLabel(self, text=message, wraplength=250, font=("Arial", 12))
        self.label_message.pack(pady=20, padx=10)

        self.button = ctk.CTkButton(self, text=button_text, command=self.close)
        self.button.pack(pady=10)

        center_window(self,300, 150, topmost=True)
        self.grab_set()  # Make the messagebox modal
        self.focus_set()


    def close(self):
        self.destroy()
```
***Konstruktor ```__init__```***

Konstruktor klasy inicjalizuje obiekt okna dialogowego z przekazanymi argumentami ```title```, ```message``` oraz opcjonalnym ```button_text``` (domyślnie ustawionym na ```"OK"```). Oto szczegóły działania konstruktora:
1. *Tytuł okna:*
   - Tytuł okna dialogowego jest ustawiany za pomocą ```self.title(title)```, gdzie ```title``` to wartość przekazana podczas wywołania klasy.
     
2. *Wymiary okna:*
   - Geometria okna jest ustawiona na 300 pikseli szerokości i 150 pikseli wysokości za pomocą ```self.geometry("300x150")```. Okno jest wystarczająco duże, aby wyświetlić wiadomość i przycisk.

3. *Etykieta z wiadomością:*
   - Treść komunikatu jest wyświetlana za pomocą etykiety ```CTkLabel```, która korzysta z argumentu ```message```. Właściwość ```wraplength=250``` zapewnia, że tekst jest zawijany, jeśli przekracza szerokość 250 pikseli, co poprawia czytelność. Etykieta jest pakowana z odstępami ```padx=10``` i ```pady=20```.

4. *Przycisk zamykający:*
   - Przycisk ```CTkButton``` z tekstem ```button_text``` umożliwia zamknięcie okna dialogowego. Działanie przycisku jest powiązane z metodą ```close```, która niszczy okno. Przycisk jest pakowany z pionowym odstępem ```pady=10```.

5. *Centrowanie i ustawienia modalne:*
   - Funkcja ```center_window``` jest wywoływana, aby wycentrować okno na ekranie. Parametr ```topmost=True``` sprawia, że okno jest wyświetlane zawsze na wierzchu. Dodatkowo, metoda ```grab_set``` ustawia okno jako modalne, co oznacza, że użytkownik nie może wchodzić w interakcję z innymi oknami aplikacji, dopóki to okno dialogowe nie zostanie zamknięte. Metoda ```focus_set``` zapewnia, że okno dialogowe otrzymuje fokus.

***Metoda ```close```***

Metoda ```close``` jest wywoływana po kliknięciu przycisku zamykającego okno dialogowe. Funkcja ta niszczy obiekt okna za pomocą metody ```self.destroy()```, co powoduje zamknięcie okna i przywrócenie interakcji z pozostałymi elementami aplikacji.

###Okno ustawiania hasła głównego

Klasa ta zawiera konstruktor odpowiedzialny za tworzenie interfejsu graficznego oraz metody obsługujące ustawienie hasła i zamykanie okna.

```python
class SetMasterPasswordWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        center_window(self, 400, 250)
        self.title("Set Master Password")

        ctk.CTkLabel(self, text="Set your new Master Password:").pack(pady=(10, 5))
        ctk.CTkLabel(self, text="Enter Master Password:").pack()
        self.entry_pass1 = ctk.CTkEntry(self, show="*")
        self.entry_pass1.pack(pady=5)

        ctk.CTkLabel(self, text="Confirm Master Password:").pack()
        self.entry_pass2 = ctk.CTkEntry(self, show="*")
        self.entry_pass2.pack(pady=5)

        btn_set = ctk.CTkButton(self, text="Set Master Password", command=self.set_master_password)
        btn_set.pack(pady=(10, 5))

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def set_master_password(self):
        p1 = self.entry_pass1.get()
        p2 = self.entry_pass2.get()

        if not p1 or not p2:
            CTkMessageBox("Error", "Fields cannot be empty!")
            return
        if p1 != p2:
            CTkMessageBox("Error", "Passwords do not match!")
            return

        hashed = hash_master_password(p1)
        try:
            cursor.execute("""
                INSERT INTO master_password (id, password_hash, attempt_count, lock_until)
                VALUES (?, ?, ?, ?)
            """, (1, hashed, 0, None))
            conn.commit()

            CTkMessageBox("Success", "Master Password has been set!")
            self.destroy()
            main_app = MainApp()
            main_app.mainloop()
        except Exception as e:
            CTkMessageBox("Error", f"Failed to save Master Password: {e}")

    def on_closing(self):
        conn.close()
        self.destroy()
        exit(0)
```

***Konstruktor ```__init__```***

Konstruktor klasy ```SetMasterPasswordWindow``` inicjalizuje okno, które pozwala użytkownikowi wprowadzić i potwierdzić hasło główne. Oto szczegóły działania:

1. *Wygląd i położenie okna:*
    - Funkcja ```center_window``` jest wywoływana, aby wyśrodkować okno na ekranie. Rozmiar okna jest ustawiony na 400 pikseli szerokości i 250 pikseli wysokości. Tytuł okna jest ustawiony na ```"Set Master Password"```.

2. *Etykiety i pola wprowadzania haseł:*
    - Na początku użytkownik widzi etykietę z informacją ```"Set your new Master Password:"```. Następnie wyświetlane są pola wprowadzania dla hasła głównego (```entry_pass1```) i jego potwierdzenia (```entry_pass2```). Oba pola są skonfigurowane z opcją ```show="*"```, aby ukryć wprowadzane znaki.

3. *Przycisk ustawienia hasła:*
    - Przycisk ```"Set Master Password"``` jest połączony z metodą ```set_master_password```, która obsługuje logikę zapisywania hasła głównego do bazy danych. Przycisk jest umieszczony poniżej pól wprowadzania.

4. *Zamykanie okna:*
    - Obsługa zdarzenia zamknięcia okna jest powiązana z metodą ```on_closing```, która zapewnia bezpieczne zamknięcie bazy danych i aplikacji.
  
***Metoda ```set_master_password```***

Metoda ```set_master_password``` odpowiada za walidację i zapisanie hasła głównego w bazie danych. Oto jej szczegóły:

1. *Pobranie wprowadzonych danych:*
    Hasło główne i jego potwierdzenie są odczytywane z pól ```entry_pass1``` i ```entry_pass2```.

2. *Walidacja danych:*
    Metoda sprawdza, czy oba pola nie są puste. Jeśli tak, wyświetlane jest okno dialogowe z błędem. Następnie metoda weryfikuje, czy oba wprowadzone hasła są identyczne. Jeśli nie, użytkownik otrzymuje komunikat o błędzie.

3. *Haszowanie hasła:*
    Po pomyślnej walidacji hasło jest haszowane za pomocą funkcji ```hash_master_password```. Wygenerowany skrót jest następnie zapisywany w tabeli ```master_password``` w bazie danych.

4. *Zapis do bazy i reakcja na wynik:*
    Jeśli hasło zostanie zapisane pomyślnie, użytkownik otrzymuje komunikat o sukcesie, a okno zostaje zamknięte. Następnie uruchamiana jest główna aplikacja za pomocą klasy ```MainApp```. W przypadku błędu podczas zapisu użytkownik otrzymuje komunikat z treścią błędu.

***Metoda ```on_closing```***

Metoda ```on_closing``` obsługuje zamknięcie okna ustawiania hasła głównego. Najpierw zamyka połączenie z bazą danych za pomocą ```conn.close()```, a następnie niszczy okno za pomocą ```self.destroy()``` i kończy działanie programu, wywołując funkcję ```exit(0)```.
