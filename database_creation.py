#!/usr/bin/python3

import csv
import json
import mysql.connector
import os
import re
import random

# Klasse beinhaltet die Einzelnen Abstimmungen und deren Ergebnisse

class Abstimm:
    def __init__(self):
        # in diesem Ordner befinden sich alle abstimmungen als einzelne dateien sowie meta_info als index
        self.path = os.getcwd() + "/Abstimmung/"
        # list_dir sind alle abstimmungen ohne meta_info, informationen über alle abstimmungen und deren vollständigkeit
        self.list_dir = [elements for elements in os.listdir(self.path) if "meta_info.csv" not in elements]
        self.list_length = len(self.list_dir)

        # eine datei wird nacheinander aufgerufen, jedes mal, wenn eine abstimmung nach sql übertragen wurde,
        # wird diese funktion aufgerufen
    def get_abstimm_data(self, index):
        with open(self.path + self.list_dir[index], "r", encoding="utf-8") as f:
            self.abstimm_data = json.load(f)

        temp_name = self.list_dir[index]
        self.abstimm_name = temp_name.replace(".json", "")

        return self.abstimm_data

    def get_information_abstimm_data(self, abstimmung):
        list_key = [" von ", " Graf ", " in der", " de ", " De ", " Gösta"]
        self.name_list = {}
        key_id = 0
        for keys, values in abstimmung.items():
            new_string = None
            if any(elements in keys for elements in list_key):
                for elements in list_key:
                    if new_string is not None:
                        continue
                    new_string = re.search(elements, keys)
                if new_string:
                    nachname = keys[new_string.start()+1:]
                    vorname = keys[:new_string.start()]
                    self.name_list.update({key_id: [nachname, vorname]})
                    key_id += 1
                    continue
            if len(keys.split()) == 2:
                vorname = keys.split()[0]
                nachname = keys.split()[1]
                self.name_list.update({key_id: [nachname, vorname]})
                key_id += 1
            else:
                temp = keys.split()
                vorname = "{} {}".format(temp[0], temp[1])
                nachname = temp[len(temp)-1]
                self.name_list.update({key_id: [nachname, vorname]})
                key_id += 1

    def create_new_names(self): # beinhaltet "vorname name: [nachname, vorname]"
        self.new_names = {}
        for values in self.name_list.values():
            new_key = "{} {}".format(values[1], values[0])
            self.new_names.update({new_key: values})

    # erstellt im grunde das selbe wie die haupt liste
    # also unnötig
    def create_info(self): # name: info
        self.info_dict = {}
        for keys in self.new_names.keys():
            info = self.abstimm_data.get(keys)
            self.info_dict.update({keys: info})


class Sql:
    def __init__(self, database_name):
        self.database_name = database_name
        self.init_connector() # self.cursor self.connector
        self.get_database_info() # self.database_list
        self.key_dict = {}

        if self.database_name in self.database_list:
            self.cursor.execute("USE {}".format(self.database_name))

        self.table_list = self.get_table_list()

        if "ABSTIMM_INDEX" not in self.table_list:
            self.abstimmung_index()
            self.index_info = self.get_info_from_index()
        else:
            self.index_info = self.get_info_from_index()

    def get_info_from_index(self):
        query = self.query_creation("get_index")
        self.cursor.execute(query)
        info = self.cursor.fetchall()
        index_tuple = [i for i in info]
        self.index_info = dict(index_tuple)

        return self.index_info

    def get_database_info(self):
        query = self.query_creation("show_database")
        self.cursor.execute(query)

        list = self.cursor.fetchall()
        self.database_list = [ data[0] for data in list ]

        return self.database_list

    def init_connector(self):
        self.connector = mysql.connector.connect(user="root", host="127.0.0.1")
        self.cursor = self.connector.cursor()

    def get_table_list(self):
        query = self.query_creation("show_tables")
        self.cursor.execute(query)
        tables = self.cursor.fetchall()
        self.table_list = [ items[0] for items in tables]

        return self.table_list

    def query_creation(self, query_name):
        dict = {
                "database_create" : "CREATE DATABASE database_name",
                "table_create_index" : "CREATE TABLE ABSTIMM_INDEX ( ABSTIMM_KEY VARCHAR(255) NOT NULL UNIQUE, ABSTIMM_NAME varchar (255), PRIMARY KEY (ABSTIMM_KEY))",
                "show_database" : "SHOW DATABASES",
                "create_table_abstimmung": "CREATE TABLE table_name ( ID_0 int NOT NULL AUTO_INCREMENT, LastName varchar (255), FirstName varchar (255), Partei varchar (255), Stimmverhalten varchar (255), PRIMARY KEY (ID_0))",
                "insert_table_abstimmung": "INSERT INTO table_name ( LastName, FirstName, Partei, Stimmverhalten ) VALUES ( ",
                "show_tables": "SHOW TABLES",
                "drop_table": "DROP TABLE ",
                "get_index": "SELECT * FROM ABSTIMM_INDEX",
                "insert_to_index" : "INSERT INTO ABSTIMM_INDEX ( ABSTIMM_KEY, ABSTIMM_NAME ) VALUES ( "
                }

        return dict.get(query_name)

    def delete_content(self):
        info = self.get_info_from_index()
        for keys in info.keys():
            query = self.query_creation("drop_table") + keys
            self.cursor.execute(query)
            self.connector.commit()

        self.cursor.execute("DROP TABLE ABSTIMM_INDEX")
        self.connector.commit()
        print("deleting of Tables succesful")

    def drop_table(name):
        query = self.query_creation("drop_table")
        query = query + name

        self.cursor.execute(query)
        self.connector.commit()

    def create_database(self, name):
        query = "CREATE DATABASE {}".format(name)
        self.cursor.execute(query)
        self.connector.commit()

    def abstimmung_index(self):
        first_query = self.query_creation("table_create_index")
        self.cursor.execute(first_query)
        self.connector.commit()

    def insert_to_index(self, appending_dict):
        query = self.query_creation("insert_to_index")
        for keys, values in appending_dict.items():
            id = keys
            name = values
        query += "'{}', '{}' )".format(id, name)

        self.cursor.execute(query)
        self.connector.commit()

    def create_table_abstimmung(self, abstimm_name, name_dict, info_dict):
        first_query = self.query_creation("create_table_abstimmung")

        index = self.get_info_from_index()

        while True:
            string = ""
            while len(string) < 8:
                string += str(random.randrange(0, 9))
            if "id" + str(string) not in index.keys():
                if "id" + str(string) in self.get_table_list():
                    self.drop_table("id" + str(string))
                    break
                else:
                    break

        appending_dict = {"id" + str(string) : abstimm_name}
        self.key_dict.update(appending_dict)

        # ID LastName FirstName Partei Stimmverhalten
        first_query = first_query.replace("table_name", "id" + str(string))
        insert_to = self.query_creation("insert_table_abstimmung")
        self.cursor.execute(first_query)

        skip_key_one = True

        for keys, values in name_dict.items():
            if skip_key_one:
                skip_key_one = False
                continue
            LastName = values[0]
            FirstName = values[1]
            info_values = info_dict.get(keys)
            Partei = info_values[0]
            Stimmverhalten = info_values[2]
            final_string = "'{}', '{}', '{}', '{}' )".format(LastName, FirstName, Partei, Stimmverhalten)
            query = insert_to.replace("table_name", "id" + str(string)) + final_string
            self.cursor.execute(query)

        self.insert_to_index(appending_dict)

        self.connector.commit()

class Meta:
    def __init__(self):
        # muss daran denken, das beim eintragen in die datenbank der erste key übersprungen wird
        # wird gebraucht, weil die werte sonst nicht verglichen werden können
        self.name_list = {0: [0, 0]}

    # diese funktion ist obsolete
    def old_update_names(self, dict):
        temp_dict = {}
        dict_length = len(self.name_list)
        for values in dict.values():
            for names in self.name_list.values():
                if values[0] == names[0] and values[1] == names[1]:
                    continue
                dict_length += 1
                temp_key = {dict_length: [values[0], values[1]]}
                temp_dict.update(temp_key)

        for key, values in temp_dict.items():
            self.name_list.update({key: values})

    def update_names(self, dict):
        temp_dict = {}
        for keys, values in dict.items():
            if keys is not self.name_list.keys():
                temp_dict.update({keys: values})

        for keys, values in temp_dict.items():
            self.name_list.update({keys: values})

        self.database_append = {}
        for keys, values in temp_dict.items():
            self.database_append.update({keys: values})

if __name__ == "__main__":

    data_name = "Parlament"
    sql = Sql(data_name)

    abstimmung = Abstimm()

    for items in abstimmung.list_dir:
        if ".json" not in items:
            continue
        index = abstimmung.list_dir.index(items)
        print("Processing Data {} of {}".format(index, len(abstimmung.list_dir)))

        # abstimmung.list_length ist die länge der list zum iterieren und des index
        abstimmung.get_information_abstimm_data(abstimmung.get_abstimm_data(index))
        abstimmung.create_new_names()
        abstimmung.create_info()
        meta = Meta()
        meta.update_names(abstimmung.new_names)

        sql.create_table_abstimmung(abstimmung.abstimm_name, meta.name_list, abstimmung.info_dict)

    print("Finished processing\nend")
