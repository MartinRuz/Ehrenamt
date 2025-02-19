from urllib.request import urlopen
import numpy as np
import csv
import itertools
from tabulate import tabulate


# filter out empty lines
def is_empty(line):
    return line.strip() == ''


# filter out empty strings
def remove_blank(x):
    return x != ''


# print the tournament list in a nicely readable way
def nice_print(tournaments):
    print(tournaments)
    results = ''
    for tournament in tournaments:
        if results == '':
            results += tournament[0].replace('_', ' ') + ' (' + tournament[1] + ')' # name of tournament, and number of wins in that tournament
        else:
            results += ', ' + tournament[0].replace('_', ' ') + ' (' + tournament[1] + ')' # whene there are more than one tournament, seperate them with a comma
    results.removesuffix(',') # remove trailing comma
    return results


# different tournament classes get different weights. D (online) is not counted at all.
def tournament_factor_from_pin(pin, tournament_list):
    for tournament in tournament_list:
        if tournament[0] == pin:
            if tournament[1] == 'A':
                return 1
            elif tournament[1] == 'B':
                return 0.75
            elif tournament[1] == 'C':
                return 0.5
            elif tournament[1] == 'D':
                return 0


# get the name of a tournament from its pin
def tournament_name_from_pin(pin, tournament_list):
    for tournament in tournament_list:
        if tournament[0] == pin:
            return tournament[2]


# main function to manage the tournaments
def manage_tournaments(players, year):
    outfile = open('cup_'+year+'.txt', 'w', encoding='latin-1') # save in a file for each year
    tournament_list = []
    # this input file is a txt file, where every line contains the pin of the tournament, the class and the location, seperated by spaces
    with open('tournaments_'+year+'.txt', 'r') as f:
        for line in f:
            tournament_list.append(line.split(' '))
    tournament_pins = [] # tournament_pins are the first column of the tournament_list, collect them
    for tournament in tournament_list:
        tournament_pins.append(tournament[0])
    with open('all.hst.txt', 'r', encoding='latin-1') as f: # read the history file, gathered from the egd https://europeangodatabase.eu/EGD/EGD_2_0/downloads/all.hst
        lines = f.readlines()
    groups = itertools.groupby(lines, key=is_empty) # group the lines by players (which are seperated by empty lines)
    competing_players = []
    for key, group in groups:
        if not key:
            batch = list(group)
            last = batch[-1].split(' ') # get the last tournament as a sample entry
            content_filter = filter(remove_blank, last)
            content = list(content_filter)
            pin = content[0]
            for player in players:
                if player[2] == pin: # if this player is one of our members, keep analyzing this batch
                    player_tournaments = []
                    player_points = 0
                    for entry in batch:
                        split = entry.split(' ')
                        content_filter = filter(remove_blank, split)
                        content = list(content_filter)
                        if content[6] in tournament_pins: # for every tournament, check whether the id matches one of our bw-tournaments
                            player_tournaments.append([tournament_name_from_pin(content[6], tournament_list), content[7]]) # if so, add the name and the number of wins to the player's tournament list
                            player_points += tournament_factor_from_pin(content[6], tournament_list)*int(content[7]) # add the weighted points to the player's total points
                    if player_tournaments != []: # if the player has played in at least one of our tournaments, add him to the list of competing players
                        competing_players.append([player[0], player[1], player_points, player_tournaments])
    print(competing_players)
    competing_players = sorted(competing_players, key=lambda x: x[2], reverse=True) # sort the players by points
    table = []
    i = 1
    for player in competing_players:
        outfile.write(player[0] + ' ' + player[1] + ': ' + str(player[2]) + ' auf folgenden Turnieren: ' + str(player[3]) + '\n') # one semi-human-readable line per player
        table.append([i, player[0], player[1], player[2], len(player[3]), nice_print(player[3])])
        i+=1
    # write the table in html format, with header and formatting
    html_table = tabulate(table, tablefmt='unsafehtml', headers=['Rang', 'Vorname', 'Nachname', 'Punkte', 'Turniere', 'Turniere (Siege)'], colalign=('center', 'left', 'left', 'center', 'center', 'left'))
    outfile.write(html_table)

if __name__ == '__main__':
    players = np.loadtxt('egd_pins.csv', delimiter=';', dtype=str, encoding='latin-1') # csv file mit Vorname, Nachname, EGD-Pin
    manage_tournaments(players, '2024')