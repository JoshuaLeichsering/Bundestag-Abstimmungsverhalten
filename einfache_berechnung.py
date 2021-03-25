#!/usr/bin/python

# Einfache Berechnungen - test

import csv
import os
import sys
import json

def iterate_file(file):
    return_list_afd = [0, 0, 0, 0] # dafür, dagegen, enthalten, nicht abgestimmt
    return_list_cdu = [0, 0, 0, 0]

    for keys in file.keys():
        politiker = file.get(keys)
        if politiker[0] == "AfD":
            if politiker[2] == "Dafür gestimmt":
                return_list_afd[0] += 1
            elif politiker[2] == "Dagegen gestimmt":
                return_list_afd[1] += 1
            elif politiker[2] == "Enthalten":
                return_list_afd[2] +=1
            elif politiker[2] == "Nicht beteiligt":
                return_list_afd[3] += 1
        elif politiker[0] == "CDU/CSU":
            if politiker[2] == "Dafür gestimmt":
                return_list_cdu[0] += 1
            elif politiker[2] == "Dagegen gestimmt":
                return_list_cdu[1] += 1
            elif politiker[2] == "Enthalten":
                return_list_cdu[2] +=1
            elif politiker[2] == "Nicht beteiligt":
                return_list_cdu[3] += 1

    return_item = [return_list_afd, return_list_cdu]
    return return_item

def open_files():
    path = os.getcwd() + "/Abstimmung/"
    folder_file = os.listdir(path)
    afd = {}
    cdu = {}

    print(str(len(folder_file)-1) + " Abstimmungen in Ordner")

    for abstimm in folder_file:
        if abstimm == "meta_info.csv":
            continue
        if abstimm == ".DS_Store":
            continue

        print(abstimm)

        with open(path + abstimm, "r", encoding="utf-8") as f:
            file = json.load(f)

        return_item = iterate_file(file)

        return_list_afd = return_item[0] # dafür, dagegen, enthalten, nicht abgestimmt
        return_list_cdu = return_item[1]

        verhältnis_afd = return_list_afd[0] / (return_list_afd[1] + return_list_afd[2] + return_list_afd[3] + return_list_afd[0])
        verhältnis_cdu = return_list_cdu[0] / (return_list_cdu[1] + return_list_cdu[2] + return_list_cdu[3] + return_list_cdu[0])

        afd.update({abstimm: verhältnis_afd})
        cdu.update({abstimm: verhältnis_cdu})

    verhältnisse = [afd, cdu]
    return verhältnisse

def calculation(afd, cdu):

    list_calc = []

    if len(afd.keys()) == len(cdu.keys()):
        print("listen sind identisch")

        complete_string = "\n\nDifferenz der Abstimmungsergebnisse von AfD und CDU/CSU\n\n"
        zweiter_end_string = "Differenz der Abstimmungsergebnisse von weniger als 20 Prozent\n\n"
        naechste_liste = []

        for abstimm in afd.keys():
            differenz = abs(afd.get(abstimm) - cdu.get(abstimm))
            print(differenz)
            if differenz < 0.2:
                zweit_string = "AfD: {0:.2f} - CDU: {1:.2f} - Differenz: {2:.2f} - {3}\n".format(afd.get(abstimm)*100, cdu.get(abstimm)*100, differenz*100, abstimm)
                zweiter_end_string += zweit_string
                naechste_liste.append(differenz)
            list_calc.append(differenz)
            string = "AfD: {0:.2f} - CDU: {1:.2f} - Differenz: {2:.2f} - {3}\n".format(afd.get(abstimm)*100, cdu.get(abstimm)*100, differenz*100, abstimm)
            complete_string += string

        i = 0
        x = 0

        for numbers in  list_calc:
            i += numbers

        for numbers in naechste_liste:
            x += numbers

        end_value = i / len(list_calc)
        zweiter_end_value = x / len(naechste_liste)
        return_value = [end_value, str(complete_string), i, zweiter_end_string, zweiter_end_value, str(len(naechste_liste)), str(len(list_calc)), x]

        return return_value

    else:
        print("Listen haben nicht gleiche Anzahl")

verhaeltnisse = open_files()

afd = verhaeltnisse[0]
cdu = verhaeltnisse[1]

end_value = calculation(afd, cdu)

complete_string = end_value[1]
verhaeltnis = end_value[0]
i = end_value[2]
c = end_value[3]
d = end_value[4]
list_value = end_value[5]
list_value_two = end_value[6]
x = end_value[7]

end_string = complete_string + "\n{0:.2f} - ges. Abweichung\n".format(i*100) + "{0:.2f} Durchschnittliche Prozentpunkte Unterschied pro Abstimmung\n \n".format(verhaeltnis*100)
end_string_two = "\nListe mit besonderer Übereinstimmung \n" + c + "\n{0:.2f} - ges. Abweichung\n".format(x*100) + "{0:.2f} Durchschnittliche Prozentpunkte Unterschied pro Abstimmung\n".format(d*100)+ "Bei {} von {} Abstimmungen".format(list_value, list_value_two)

with open("ergebnis.txt", "w") as f:
    f.write(end_string)
    f.write(end_string_two)

print(end_string)
print(end_string_two)
