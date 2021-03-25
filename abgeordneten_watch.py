#!/usr/bin/python

# abgeordneten-watch - alle infos und klassen

import requests # GET method
from selenium import webdriver # webdriver
from bs4 import BeautifulSoup # html parser
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options # options for headless chrome
import time
import os
import json
import csv

# Hier folgen Klassen
# darunter folgen Funktionen, die diese verwenden

class Web_Parser:
    def __init__(self):
        # self.driver is firefox selenium driver
        self.function = ""

    def webdriver_create(self):
        firefox_options = Options()

        # possible options
        #firefox_options.add_argument("--disable_extensions")
        #firefox_options.add_argument("--disable-gpu")
        #firefox_options.add_argument("--no-sandbox") # only linux

        # current options - driver is starting without gui
        firefox_options.add_argument("--headless")

        self.driver = webdriver.Firefox(options=firefox_options)

        return self.driver

    # exits webdriver
    def webdriver_quit(self, webdriver):
        # exits webdriver
        try:
            webdriver.quit() # exits passed webdriver
            time.sleep(1)
            print("driver succesfully exited")
        except Exception as e:
            print("no driver available")

    # returns beautisoup object
    def get_html_and_soup(self, url):
        self.driver.get(url)

        self.html = self.driver.page_source
        self.soup_item = BeautifulSoup(self.html, 'html.parser')

        return self.soup_item

class Scraper_abstimmungen_und_abgeordnete:
    def __init__(self):
        self.page_url = "https://www.abgeordnetenwatch.de/bundestag/abstimmungen?page=" # ends with number
        self.abstimmungen_url = [] # contains list of url for bundestags - abstimmungen - pages
        self.url_main_page = "https://www.abgeordnetenwatch.de"
        self.parser = Web_Parser()
        self.driver = self.parser.webdriver_create()
        self.iterate_value = False
        self.dict_ident = None
        self.csv_data = None
        self.extra_items = []

    def quit_webdriver(self):
        self.parser.webdriver_quit(self.driver)

    # scrapes the abstimmungen_pages
    def search_for_abstimmungen_main(self):
        counter = 0 # counter for iterating over all pages
        page_list = [] # indexes all pages
        temp_list = [] # working list while scraping over items

        html_local = requests.get("https://www.abgeordnetenwatch.de/bundestag/abstimmungen").text
        soup_item = BeautifulSoup(html_local, 'html.parser')

        # ich nutze das um nur das eine main content element zu finden
        # temp_soup = None
        # while temp_soup is None:
        #     temp_soup = soup_item.find("main", id="content")

        for items in soup_item.find_all("a"):
            try:
                if items.span is not None:
                    if items.span.string == "Letzte Seite":
                        new_item = items.get("href")
            except Exception as e:
                continue

        last_page = int(new_item.replace("?page=", ""))

        # holt alle abstimmungsnamen und urls
        while counter <= last_page:
            html_local = requests.get(self.page_url + str(counter)).text
            soup_item = BeautifulSoup(html_local, 'html.parser')

            # ich nutze das um nur das eine main content element zu finden
            temp_soup = None
            while temp_soup is None:
                temp_soup = soup_item.find("main", id="content")

            for items in temp_soup.find_all("a"):
                try:
                    if items is not None:
                        abstimmungen = items["href"]
                        if abstimmungen.startswith("/abstimmungen"):
                            abstimmungen = self.url_main_page + abstimmungen
                            if abstimmungen.find("#comments") >= 0:
                                abstimmungen = abstimmungen.replace("#comments", "")
                            temp_list.append(abstimmungen)
                        if abstimmungen.startswith("/bundestag"):
                            abstimmungen = self.url_main_page + abstimmungen
                            if abstimmungen.find("#comments") >= 0:
                                abstimmungen = abstimmungen.replace("#comments", "")
                            temp_list.append(abstimmungen)
                except Exception as e:
                    continue

            counter += 1

        for items in temp_list:
            if items not in self.abstimmungen_url:
                self.abstimmungen_url.append(items)

    def open_json_dict(self, string_name):
        with open(os.getcwd + "/Abstimmung/" + string_name + ".json", "r", encoding="utf-8") as f:
            dict = json.load(f)

        return dict

    # holt die abstimmungen und abgeordneten und erstellt ein dict
    # nutzt self.driver und get_html_and_soup(url) und self.parser
    def abstimm_seite_get(self, url, string_rename):
        local_dict = {}
        self.string_rename = string_rename
        appendix = "/tabelle#filterbar?constituency=All&fraction=All&page=0"
        starting_page = 0
        self.page_abgeordnete_stimmverhalten = self.open_json_dict(self.string_rename)

        print("check - iterate_value = " + str(self.iterate_value))

        # diese zeile wird später noch bearbeitet
        #first_url = url + appendix + str(starting_page)

        while url.endswith(" "):
            url = url[:-1]

        self.url = url + appendix

        soup_item = self.parser.get_html_and_soup(self.url)
        time.sleep(5)

        print("hole - " + self.string_rename)
        print(self.url)

        new_item = None
        while new_item is None:
            new_item = soup_item.find("a", title='Zur letzten Seite')

        new_item = new_item["href"]

        try:
            last_page = int(new_item[new_item.find("&page=")+6:])
        except Exception as e:
            last_page = int(new_item[new_item.find("?page=")+6:])

        # such nach der gesamtmenge der abgeordneten
        abgeordnete_ges = None
        while abgeordnete_ges is None:
            ab_temp = soup_item.find_all("div")
            for items in ab_temp:
                if abgeordnete_ges is not None:
                    continue
                try:
                    new_items = items.text.replace("\n", "")
                    new_items = new_items[new_items.find("insgesamt"):new_items.find("Abgeordneten")]
                    while new_items.endswith(" "):
                        new_items = new_items[:-1]
                    new_items = new_items.split()
                    abgeordnete_ges = int(new_items[1])
                except Exception as e:
                    pass
            break

        def scrape_page(self):

            for items in self.temp_soup.find_all("tr"):
                polit_name = ""
                polit_party = ""
                polit_wahlkreis = ""
                polit_wahl = ""
                for new_items in items.find_all("td"):
                    # such name des politikers
                    try:
                        if new_items is not None:
                            if new_items["class"][1] == "views-field-last-name":
                                polit_name = new_items.a.string
                    except Exception as e:
                        pass

                    # partei
                    try:
                        if new_items is not None:
                            if new_items["class"][1] == "views-field-short-name":
                                polit_party = new_items.string
                                while polit_party.endswith(" "):
                                    polit_party = polit_party[:-1]
                    except Exception as e:
                        pass

                    # wahlkreis
                    try:
                        if new_items is not None:
                            if new_items["class"][1] == "views-field-number":
                                polit_wahlkreis = new_items.string
                                while polit_wahlkreis.endswith(" "):
                                    polit_wahlkreis = polit_wahlkreis[:-1]
                    except Exception as e:
                        pass

                    # stimmverhalten
                    try:
                        if new_items is not None:
                            if new_items["class"][1] == "views-field-vote":
                                polit_wahl = new_items.text.replace("\n", "")
                                while polit_wahl.endswith(" "):
                                    polit_wahl = polit_wahl[:-1]
                    except Exception as e:
                        pass

                new_politician = {polit_name: [polit_party, polit_wahlkreis, polit_wahl]}
                print(new_politician)

                self.page_abgeordnete_stimmverhalten.update(new_politician)

            if self.iterate_value is True and len(self.page_abgeordnete_stimmverhalten.keys()) == int(abgeordnete_ges):
                return True

        print(str(last_page) + " Seiten gesamt\n" + str(abgeordnete_ges) + " Abgeordnete gesamt" + "\n")

        # aendere stimmverhalten mit der button.click() methode
        if self.iterate_value is True:
            stimm_button = self.parser.driver.find_elements_by_xpath("//a[@title='Nach Stimmverhalten sortieren']")[0]
            stimm_button.click()

        while starting_page <= last_page:

            time.sleep(1.5)

            source = self.parser.driver.page_source
            soup_item = BeautifulSoup(source, 'html.parser')

            # ich nutze das um nur das eine main content element zu finden
            self.temp_soup = None
            while self.temp_soup is None:
                self.temp_soup = soup_item.find("tbody")

            if self.iterate_value is True:
                return_value = False
                return_value = scrape_page(self)
                if return_value is True:
                    print("Anzahl benötigter Elemente gefunden - überspringe")
                    break
            else:
                scrape_page(self)

            try:
                button = self.parser.driver.find_elements_by_xpath("//a[@title='Zur nächsten Seite']")[0]
                button.click()
            except Exception as e:
                print("Letzte Seite erreicht")

            if starting_page < last_page:
                print("Auf Seite " + str(starting_page))
            starting_page += 1

        # wiederholt letzte seite, falls keys ungleich abgeordnete
        if len(self.page_abgeordnete_stimmverhalten.keys()) != int(abgeordnete_ges):
            soup_item = self.parser.get_html_and_soup(url + appendix)
            time.sleep(10)

            try:
                button = self.parser.driver.find_elements_by_xpath("//a[@title='Zur letzten Seite']")[0]
                button.click()
            except Exception as e:
                print("Fehler auf letzter Seite")

            self.temp_soup = None
            while self.temp_soup is None:
                self.temp_soup = soup_item.find("tbody")

            scrape_page(self)

            print("extradurchlauf")

        if len(self.page_abgeordnete_stimmverhalten.keys()) == int(abgeordnete_ges):
            print("Anzahl Abgeordnetenstimmen ist identisch mit Keys")
            self.dict_ident = True
        else:
            print("Fehler - Anzahl Keys ungleich Anzahl Abgeordnetenstimmen")
            self.dict_ident = False

        print("Abgeordnetenstimmen = " + str(abgeordnete_ges))
        print("Gesamtzahl Keys = " + str(len(self.page_abgeordnete_stimmverhalten.keys())))

        # schreibe meta info
        string = "{};{};{}".format(self.string_rename, str(abgeordnete_ges), str(len(self.page_abgeordnete_stimmverhalten.keys())))

        with open(os.getcwd() + "/Abstimmung/meta_info.csv", "a") as f:
            f.write(string + "\n")

        return self.page_abgeordnete_stimmverhalten

class Base_methods:
    def __init__(self):
        pass

    def write_to_file_text(self, list, name):
        if os.path.isfile(name) is False:
            with open(name, "w") as f:
                for strings in list:
                    f.write('%s \n' % strings)

        self.list_abstimm = list
        print("succesfull")

    def write_dict_to_json(self, dict, name):
        pass

    def write_to_html(self, html, name):
        pass

# Ab hier folgen die abrufenden Funktionen der Klassen

def get_abstimm_urls():

    abstimm = Scraper_abstimmungen_und_abgeordnete()
    abstimm.search_for_abstimmungen_main()
    print(len(abstimm.abstimmungen_url))

    base = Base_methods()
    base.write_to_file_text(abstimm.abstimmungen_url, "abstimmungen.txt")

# übergibt alle urls nacheinander an scraper_list usw.
def iterate_through_all_urls():
    with open("abstimmungen.txt", "r") as f:
        list = f.readlines()

    path = os.getcwd()
    save_folder = "/Abstimmung"

    try:
        os.mkdir("Abstimmung")
    except Exception as e:
        print("Ordner Abstimmung Existiert bereits")

    if os.path.isfile(path + "/Abstimmung/meta_info.csv") is False:
        with open(path + "/Abstimmung/meta_info.csv", "a") as f:
            f.write("ABSTIMMUNG_NAME;ABGEORDNETE_GES;DICT_KEYS\n")

    for urls in list:
    # ruft die Klasse auf und dessen webdriver object
    # für jedes element wird die methode neu zugewiesen

        # print Fortschritt
        print_string = "{} von {}".format(str(list.index(urls)+1), str(len(list)))
        print(print_string)

        # bereinige url
        urls = urls.replace("\n", "")
        while urls.endswith(" "):
            urls = urls[:-1]

        # erste operation, falls datei schon existent, überspringen
        string_rename = urls[urls.rfind("/")+1:]

        try:
            if type(int(string_rename)) is int:
                string_rename = urls
                while string_rename.count("/") > 1:
                    string_rename = string_rename[string_rename.find("/")+1:]
        except Exception as e:
            pass

        string_rename = string_rename.replace("/", "-")

        save_page_name = path + save_folder + "/" + string_rename + ".json"

        if os.path.isfile(save_page_name):
            continue
        else:
            abstimm = Scraper_abstimmungen_und_abgeordnete()
            try:
                dict = abstimm.abstimm_seite_get(urls, string_rename)
            except Exception as e:
                print(e)
                abstimm.parser.webdriver_quit(abstimm.driver)

            with open(save_page_name, "w", encoding="utf-8") as f:
                json.dump(dict, f, ensure_ascii=False)

            abstimm.parser.webdriver_quit(abstimm.driver)

def verify_data_integrity():
    with open("abstimmungen.txt", "r") as f:
        list = f.readlines()

    path = os.getcwd()
    save_folder = "/Abstimmung"

    with open(path + "/Abstimmung/meta_info.csv", "a") as f:
        f.write("#########################################################\n")

    with open(path + "Abstimmung/meta_info.csv", "r") as f:
        repo = f.readlines()
        list_index_length = len(repo) -1
        while list_index_length >= 0:
            if repo[list_index_length] == "#########################################################\n":
                start_value = list_index_length
                break
            else:
                list_index_length -= 1

    file = open(path + "/Abstimmung/meta_info.csv", "r", newline='')
    csv_data = csv.reader(file, delimiter=';')

    for elements in csv_data:
        if csv_data.index(elements) <= start_value:
            continue

        abstimm_name = elements[0]
        # hier wird geschaut, ob ich vorher schonmal ein / durch ein - ausgetauscht habe
        try:
            temp_el = elements[elements.rfind("-")+1:]
            if type(int(temp_el)) is int:
                new_string = "/{}".format(temp_el)
                abstimm_name = elements[0].replace("-" + temp_el, new_string)
        except Exception as e:
            pass

        try:
            if elements[1] == elements[2]:
                continue
        except Exception as e:
            continue

        exit_value = 0 # wenn url gefunden, kann ich damit das iterieren beschleunigen
        cur_url = None # setze ich jetz schon, weil in der meta datei durchaus noch falsche eintraege
        # sein könnten dich ich überspringen kann

        for urls in list:
            if exit_value == 1:
                continue
            if urls.find(abstimm_name) >= 0:
                cur_url = urls.replace("\n", "")
                exit_value = 1

        if cur_url is None:
            continue

        # grundsaetzlich der selbe ablauf wie im haupablauf

        abstimm = Scraper_abstimmungen_und_abgeordnete()
        abstimm.iterate_value = True
        #abstimm.csv_data = csv_data

        save_page_name = path + "/Abstimmung/" + elements[0] + ".json"
        print("Wiederhole - " + elements[0] + "\n")

        try:
            dict = abstimm.abstimm_seite_get(cur_url, elements[0]) # elements ist das gerade iterierte objekt
        except Exception as e:
            print(e)
            abstimm.parser.webdriver_quit(abstimm.driver)

        with open(save_page_name, "w", encoding="utf-8") as f:
            json.dump(dict, f, ensure_ascii=False)

        abgeschlossene_abstimmung_liste.append(abstimm)

    file.close()

    print("Alle Objekte durchgegangen")

if __name__ == "__main__":

    print("Sammelt Informationen über alle Bundestagsabstimmungen")
    get_abstimm_urls()

    print("Durchsucht alle Bundestagsabstimmungen nach verwertbaren Informationen")
    iterate_through_all_urls()

    print("Verifiziert die gesammelten Daten auf Komplettheit")
    verify_data_integrity()
