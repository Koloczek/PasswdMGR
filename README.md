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






