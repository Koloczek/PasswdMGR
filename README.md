# <img src="pliki/python_logo.png" alt="Balancer" height="128px">


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






