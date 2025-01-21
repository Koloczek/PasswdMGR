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

