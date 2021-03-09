import csv
import mysql.connector

# import von csv und mysql connector
# der host ist localhost und der user root, falls passwortabfrage besteht, geschieht das mit dem parameter "password"
# die datenbank muss schon bestehen; hier "Parlament"

connector = mysql.connector.connect(user="root", host="127.0.0.1", database="Parlament")
cursor = connector.cursor()

# USE Parlament;
# folgendes ist der Befehl zum erstellen der Tabelle

# CREATE TABLE `Bundestag` (
#     `Prime_id` int unsigned NOT NULL AUTO_INCREMENT,
#     `Name` varchar(50) NOT NULL,
#     `Vorname` varchar(50) NOT NULL,
#     `Geburtsjahr` int NOT NULL,
#     `Partei` varchar(20) NOT NULL,
#     `Land`varchar(30) NOT NULL,
#     `Prozent`varchar(10),
#     `Wahlkreis`varchar(100),
#     PRIMARY KEY (`Prime_id`)
#     ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

# Letzte Zeile wurde weggelassen, nur der vollständigkeit halber aufgeführt

# execute führt eingegebene Befehle aus, Semikolon muss nicht verwendet werden
# cursor.execute()

# öffnen der zuvor erstellten abgeordnete liste, hier als csv datei
file = open('parlament_abgeordnete.csv', newline='')
csv_data = csv.reader(file, delimiter=';')

skipHeader = True # falls erste Zeile der csv der Header ist, wird die erste zeile beim iterieren ausgelassen

def create_database(): # erstellt datenbank
    query = "CREATE DATABASE Parlament"
    cursor.execute(query)
    connector.commit()

def create_table(): # erstellt table
    query = "CREATE TABLE `Bundestag` (`Prime_id` int unsigned NOT NULL AUTO_INCREMENT, `Name` varchar(50) NOT NULL, `Vorname` varchar(50) NOT NULL, `Geburtsjahr` int NOT NULL, `Partei` varchar(20) NOT NULL, `Land` varchar(30) NOT NULL, `Prozent` varchar(10), `Wahlkreis`varchar(100), PRIMARY KEY (`Prime_id`)"
    cursor.execute(query)
    connector.commit()

cursor.execute("SHOW DATABASES")

if "Parlament" not in cursor: # schaut, ob datenbank erstellt wurde, andernfalls tut das skript das
    create_database()
    create_table()

for row in csv_data:
    if skipHeader: # hier warheitsabfrage, erste zeile ist noch True, danach False
        skipHeader = False
        continue
    else:
        query = "INSERT INTO Bundestag(Name, Vorname, Geburtsjahr, Partei, Land, Prozent, Wahlkreis) VALUES('%s', '%s', '%s', '%s', '%s', '%s', '%s')" % tuple(row)
        # if len(row[6]) > 25:
        #     print(row[6])
        cursor.execute(query)

connector.commit() # damit wird die datenbank dann tatsächlich bearbeitet

file.close() # datei wird wieder geschlossen
