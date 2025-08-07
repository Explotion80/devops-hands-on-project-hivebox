# Używamy lekkiego obrazu z Pythonem
FROM python:3.11-slim

# Ustawiamy katalog roboczy wewnątrz kontenera
WORKDIR /app

# Kopiujemy pliki do kontenera
COPY . /app

# (Opcjonalnie) instalujemy zależności
# Jeśli plik requirements.txt będzie pusty, to to nie zaszkodzi
RUN pip install --no-cache-dir -r requirements.txt

# Ustawiamy domyślny punkt wejścia
CMD ["python", "main.py"]