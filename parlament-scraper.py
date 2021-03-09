import requests
from bs4 import BeautifulSoup as Soup
import re
import json

url = "https://de.wikipedia.org/wiki/Liste_der_Mitglieder_des_Deutschen_Bundestages_(19._Wahlperiode)"

html_item = requests.get(url).text
soup_item = Soup(html_item, 'html.parser')

name_found = 0

landerliste = {
    "Thüringen" : "Thüringen",
    "Schleswig-Holstein" : "Schleswig-Holstein",
    "Sachsen-Anhalt" : "Sachsen-Anhalt",
    "Sachsen" : "Sachsen",
    "Saarland" : "Saarland",
    "Rheinland-Pfalz" : "Rheinland-Pfalz",
    "Nordrhein-Westfalen" : "Nordrhein-Westfalen",
    "Niedersachsen" : "Niedersachsen",
    "Mecklenburg-Vorpommern" : "Mecklenburg-Vorpommern",
    "Hessen" : "Hessen",
    "Hamburg" : "Hamburg",
    "Bremen" : "Bremen",
    "Brandenburg" : "Brandenburg",
    "Berlin" : "Berlin",
    "Bayern" : "Bayern",
    "Baden-Württemberg" : "Baden-Württemberg"
}

parteienliste = {
    "CDU/CSU (CDU)" : "CDU",
    "CDU/CSU (CSU)" : "CSU",
    "FDP" : "FDP",
    "SPD" : "SPD",
    "Grüne" : "Grüne",
    "Linke" : "Linke",
    "AfD" : "AfD"
}

counter = 0

for objects in soup_item.find_all("table"):
    if "wikitable" in objects["class"]:
        objects_previous = objects
        #if objects.find(attrs={"class": re.compile(r".*\b)})
        while counter == 0:
            try:
                objects_previous = objects_previous.previous_sibling
                if objects_previous.name == "h2":
                    for child in objects_previous.children:
                        if child.has_attr("id"):
                            if (child["id"]) == "Abgeordnete":
                                print(child["id"])
                                new_table = objects
                                counter = 1
            except AttributeError:
                break

abgeordneten_daten = {}
list_1 = []

for politician in new_table.tbody:
    if politician.name == "tr":
        new_politician = []
        counter = 0
        for names in politician.find_all("td"):
            list_1.append(names.string)
            if names.has_attr("data-sort-value"):
                if names["data-sort-value"].find("nachgerückt") < 0:
                    key_value = names["data-sort-value"]
                    counter = 1
            if names.string is not None:
                if names.string != "\n":
                    try:
                        names_2 = names.string.replace("\n", "")
                    except Exception as E:
                        continue
                    if len(names_2) == 4:
                        birthyear = names_2
                        new_politician.append(birthyear)
                    if names_2 in parteienliste:
                        parteienzugehoerigkeit = parteienliste.get(names_2)
                        new_politician.append(parteienzugehoerigkeit)
                    if names_2 in landerliste:
                        land = landerliste.get(names_2)
                        new_politician.append(land)
                    #if len(names.children) > 0:
                    if len(list(names.children)) > 0:
                        for items in names.children:
                            if items.find("%") >= 0:
                                prozent = items.replace("\xa0", " ").replace("\n", "")
                                prozent = prozent.replace(",", ".")
                                new_politician.append(prozent)
                            # if items.has_attr("title"):
                            #     new_title = items["title"]
                            #     if new_title.find("wahlkreis") >= 0:
                            #         wahlkreis = items.string
                            #         new_politician.append(wahlkreis)
                            #         print(wahlkreis)
                        # if names.a["title"].find("wahlkreis") >= 0:
                        #     wahlkreis = names.a["title"]
                        #     new_politician.append(wahlkreis)
        if counter == 1:
            for names in politician.find_all("a"):
                if names.has_attr("title") and names["title"].find("wahlkreis") >= 0:
                    wahlkreis = names.string
                    new_politician.append(wahlkreis)
        try:
            abgeordneten_daten.update({key_value: new_politician})
        except NameError:
            pass



# for elements in list_1:
#     if elements is not None:
#         print(elements)
#print(abgeordneten_daten)
print(abgeordneten_daten)
print(str(len(abgeordneten_daten.keys())) + " - Länge der Liste")
print("Beispiel: ")
print(abgeordneten_daten.get("Noll, Michaela"))

def save_to_file_json(input_liste):
    with open("parlament_abgeordnete.json", "w") as f:
        json.dump(input_liste, f)

# wichtige informationen
# länge der informationen bezüglich ;
# müsste der count wert angepasst werden

def save_to_file_csv(input_liste):
    delimiter = ";"
    csv_list = []
    for parlamentarier in input_liste.keys():
        complete_string = ""
        nachname = parlamentarier.split(",", 1)[0]
        vorname = parlamentarier.split(",", 1)[1].replace(" ", "", 1)
        if vorname.find("von") >= 0:
            vorname = vorname.replace("von", "").replace(" ", "", 1)
            nachname = "von " + nachname
        complete_string = "{};{}".format(nachname, vorname)
        if input_liste.get(parlamentarier)[1] not in parteienliste.values():
            for information in input_liste.get(parlamentarier):
                if complete_string.count(";") == 2:
                    complete_string = complete_string + ";"
                complete_string = complete_string + ";" + information
        else:
            for information in input_liste.get(parlamentarier):
                complete_string = complete_string + ";" + information
        while complete_string.count(";") < 6:
            complete_string = complete_string + ";"
        csv_list.append(complete_string)
    with open("parlament_abgeordnete.csv", "w") as f:
        f.write("Name;Vorname;Geburtsjahr;Partei;Land;Prozent;Wahlkreis\n")
        for items in csv_list:
            f.write(items + "\n")

save_to_file_json(abgeordneten_daten)
save_to_file_csv(abgeordneten_daten)
