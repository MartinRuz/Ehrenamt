import json
import os

import numpy as np
import pandas as pd
import itertools
import matplotlib.pyplot as plt
import re


def remove_blank(x):
    return x != ''


def is_empty(line):
    return line.strip() == ''


special_char_map = {ord('ä'): 'ae', ord('ü'): 'ue', ord('ö'): 'oe', ord('ß'): 'ss'}


if __name__ == '__main__':
    year = '24' # hier kann man das Jahr der Analyse eintragen
    # erstellt einen ordner für die Analyse, wenn noch keiner existiert
    if not os.path.exists('20'+year):
        os.mkdir('20'+year)
    names_full = np.loadtxt('egd_pins.csv', delimiter=';', dtype=str, encoding='latin-1') # csv file mit Vorname, Nachname, EGD-Pin
    names_2d = names_full[:, :3]
    empty_strings = np.empty((names_2d.shape[0], 4), dtype=str) # 4 freie einträge, für anzahl turniere, jahr der letzten turnierteilnahme, spielstärke, kfz, pin
    empty_strings.fill('')
    names = np.concatenate((names_2d, empty_strings), axis=1)
    names = np.char.translate(names, special_char_map)
    with open('all.hst.txt', 'r', encoding='latin-1') as f: # history file mit allen turnierergebnissen von https://europeangodatabase.eu/EGD/EGD_2_0/downloads/all.hst
        lines = f.readlines()
    groups = itertools.groupby(lines, key=is_empty)
    names_active = []
    for key, group in groups:
        if not key:
            batch = list(group)
            last = batch[-1].split(' ') # wir sind für die analyse nur am letzten turnier interessiert
            content_filter = filter(remove_blank, last)
            content = list(content_filter)
            name = np.char.lower(content[2])
            surname = np.char.lower(content[1])
            pin = content[0]
            for player in names:
                if player[2] == pin:
                    player[3] = len(batch) # anzahl turniere
                    tmp = content[6][1:3]
                    if int(tmp) < 90: # jahr der letzten turnierteilnahme
                        player[4] = '20' + tmp
                    else:
                        player[4] = '19' + tmp
                    player[5] = content[5] # spielstärke
                    player[6] = content[4] # kfz
                    names_active.append(player)

    for player in names: # falls ein spieler kein turnier gespielt hat, wird die anzahl turniere auf 0 gesetzt
        if player[2] == '':
            player[3] = '0'
            player[4] = '0'
    np.savetxt('output.csv', names, delimiter=';', fmt='%s', encoding='latin-1')
    full_year = '20' + year
    full_year = int(full_year)
    bins_years = [0, 1995, 2000, 2010, 2015, 2020, full_year-3, full_year-2, full_year-1, full_year] # dynamische Zeitspannen für die Analyse, wann das letzte Turnier war
    bin_indices = np.digitize(names[:, 4].astype(int), bins_years) # ordnet jedem Mitglied ein Intervall zu
    bins_num = [0, 1, 5, 10, 20, 50] # Intervalle, wieviele Turniere gespielt wurden
    bin_indices_num = np.digitize(names[:, 3].astype(int), bins_num) # ordnet jedem Mitglied ein Intervall zu
    values3, counts3 = np.unique(bin_indices_num, return_counts=True) # zählt wie viele spieler in welche zeitspanne fallen
    values4, counts4 = np.unique(bin_indices, return_counts=True) # zählt wie viele spieler in welches intervall fallen

    labels_years = [f"{bins_years[i]}" if bins_years[i] == bins_years[i + 1] - 1
                       else f"{bins_years[i]}-{bins_years[i + 1] - 1}"
                       for i in range(len(bins_years) - 1)
                   ] + [f"{bins_years[-1]}+"] # labels für die jahre, je nachdem als Zeitspanne oder als einzelnes Jahr
    labels_years[0] = 'keine Turnierteilnahme'

    labels_num = [f"{bins_num[i]}-{bins_num[i + 1] - 1}" for i in range(len(bins_num) - 1)] + [
        f"{bins_num[-1]}+"] # labels für die anzahl der turniere
    labels_num[0] = 'keine Turnierteilnahme'

    os.chdir('20'+year) # wechselt in den Ordner für die Analyse
    plt.pie(counts3, labels=labels_num, autopct='%1.1f%%')
    plt.title('Anzahl Turnierteilnahmen')
    plt.savefig('anzahl_teilnahmen_'+year+'.png', dpi=300) # plots speichern, gelabelt mit dem Jahr
    plt.show()

    plt.pie(counts4, labels=labels_years, autopct='%1.1f%%')
    plt.title('Jahr der letzten Turnierteilnahmen')
    plt.savefig('letzte_teilnahme_'+year+'.png', dpi=300)
    plt.show()

    categories = ["DDK", "SDK", "Dan"] # für die Spielstärkeanalyse

    pattern_30k_10k = re.compile(r"([1-3]\d)k") #regex pattern für die Spielstärken
    pattern_9k_1k = re.compile(r"([1-9])k")
    pattern_1d_7d = re.compile(r"([1-7])d")
    counts = np.zeros(3)
    for player in names:
        if re.match(pattern_30k_10k, player[5]):
            counts[0] += 1
        elif re.match(pattern_9k_1k, player[5]):
            counts[1] += 1
        elif re.match(pattern_1d_7d, player[5]):
            counts[2] += 1
    labels_strength = [f"{categories[i]}({int(counts[i])})" for i in range(len(categories))]
    plt.pie(counts, labels=labels_strength, autopct='%1.1f%%')
    plt.title('Spielstärken aller Mitglieder die mindestens 1 Turnier gespielt haben')
    plt.savefig('spielstaerke_'+year+'.png', dpi=300) # speichern des plots, gelabelt mit dem Jahr
    plt.show()

    names_active = np.asarray(names_active)

    clubs = []
    freq = []
    rest = []
    clubs_tmp, freq_tmp = np.unique(names_active[:, 6], return_counts=True)
    for i in range(0, len(freq_tmp)):
        if freq_tmp[i] > 1 and not clubs_tmp[i].__contains__('xx'): # nur clubs mit mehr als einem Vertreter auf Turnieren werden berücksichtigt
            clubs.append(clubs_tmp[i])
            freq.append(freq_tmp[i])
        else:
            rest.append(clubs_tmp[i])

    plt.bar(clubs, freq)
    plt.xticks(clubs, clubs)
    plt.savefig('clubs_'+year+'.png', dpi=300)
    plt.show()
