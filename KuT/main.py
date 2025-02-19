import os
import json
import numpy as np
from urllib.request import urlopen
from tabulate import tabulate
import re

def read_line(players, yearly):
    for player in players:
        print(player) # for debugging, and to show that the script is progressing
        player_surname = player[0]
        player_name = player[1]
        player_finishrank = ''
        file = open('all.hst.txt', 'r', encoding='latin-1')
        line = file.readline()
        while line: # someday, I could optimise this as in the other scripts
            split = line.split(' ')
            content_filter = filter(remove_blank, split)
            content = list(content_filter)
            if len(content) == 12: # this is the number of entries per full line
                name = content[1]
                surname = content[2]
                if (name == player_name) and (surname == player_surname): # then we have found a player
                    wins = content[7]
                    tournament = content[6]
                    year = tournament[1] + tournament[2]
                    if year == yearly: # only count tournaments from the given year
                        if player[5] == '':
                            player[5] = content[5] # start rank
                        if player_finishrank == '':
                            player_finishrank = content[5]
                        else:
                            player_finishrank = higher_rank(player_finishrank, content[5]) # finishrank should be highest rank
                        player[3] += int(wins)
                        player[4].append(tournament)
            line = file.readline()
        if player_finishrank != '':
            player[6] = player_finishrank
    output = open('output.txt', 'w', encoding='latin-1') # save a list of players and their number of wins
    for player in players:
        output.write(player[0] + ' ' + player[1] + ' ' + str(player[3]))
        output.write('\n')
    output.close()

special_char_map = {ord('ä'): 'ae', ord('ü'): 'ue', ord('ö'): 'oe', ord('ß'): 'ss'}

def read_players(names, yearly): # this function is outdated, and was replaced by automated_read_players. It is kept in case we want to revert in the future
    players = []
    player = names.readline()
    while player: # iterate over all players
        split = player.split('\t')
        content_filter = filter(remove_blank, split)
        content = list(content_filter)
        name = content[1]
        surname = content[0]
        year = content[2]
        mail = content[3]
        tmp = content[4:] # read the information about the player and store it in a list
        address = ' '.join(tmp)
        if year != '':
            age = 2000 + int(yearly) - int(year) # subtract the year of birth from the current year
            if (age <= 12) and (age > 1):
                category = 'U12'
                players.append([surname.translate(special_char_map), name.translate(special_char_map), category, 0, [], '', '','', mail, address]) # add the player to the list, with all available information
            elif age <= 18:
                category = 'U18'
                players.append([surname.translate(special_char_map), name.translate(special_char_map), category, 0, [], '', '','', mail, address])
        player = names.readline()
    print(players)
    return players

def automated_read_players(names): # this function reads the players from a file, and is used in the current version of the script
    players = []
    player = names.readline()
    while player:
        #split = player.split(' ')
        split = player.split('\t')
        content_filter = filter(remove_blank, split)
        content = list(content_filter)
        name = content[1]
        surname = content[0]
        # we no longer need the if-else, since the input-file has the information about the category
        players.append([surname.translate(special_char_map), name.translate(special_char_map), content[2][:3], 0, [], '', '','', '',''])
        player = names.readline()
    print(players)
    return players

def higher_rank(s1, s2): # returns the higher Go-rank of two strings. The order is 7d>...>1d>1k>...>30k
    pattern = r"(\d+)([kd])"
    n1, l1 = re.match(pattern, s1).groups()
    n2, l2 = re.match(pattern, s2).groups()
    n1 = int(n1)
    n2 = int(n2)
    result = s1
    if l1 < l2:
        return result
    elif l1 > l2:
        result = s2
        return result
    elif l1 == 'k':
        if n1 < n2:
            return result
        else:
            result = s2
            return result
    else:
        if n1 > n2:
            return result
        else:
            result = s2
            return result

def remove_blank(x):
    return x != ''

def reformat(name, yearly): # returns the desired format for tournament dates, such as 06.01-07.01
    tmp = name.replace(yearly+'-', '')
    date = tmp[3:5]
    month = tmp[0:2]
    date_2 = tmp[9:11]
    month_2 = tmp[6:8]
    result = date + '.' + month + '-' + date_2 + '.' + month_2
    return result

def manage_tournaments(players, year): # output the list of tournaments in html format
    outfile = open('tournaments_'+year+'.txt', 'w', encoding='latin-1')
    tournament_list = []
    for player in players:
        for t in player[4]:
            tournament_list.append(t)
    tournaments = np.unique(np.array(tournament_list)).tolist()
    #sort tournaments by the substring [1:7] which is a number of type YYMMDD
    tournaments.sort(key=lambda x: int(x[1:7]))
    tournament_to_print = []
    number = 1
    year = '20' + year
    for tournament in tournaments:
        with urlopen('https://europeangodatabase.eu/EGD/Tournament_Card.php?&key=' + tournament) as response: # parse the tournament website for the name, place and date
            for line in response:
                line = line.decode("latin-1")
                if line.__contains__('EV['):
                    name = line
                if line.__contains__('PC['):
                    place = line
                if line.__contains__('DT['):
                    time = line
            left_name = name.find('[')
            right_name = name.find(']')
            name = name[left_name+1:right_name]
            left_place = place.find('[')
            right_place = place.find(']')
            place = place[left_place + 1:right_place]
            left_time = time.find('[')
            right_time = time.find(']')
            time = time[left_time+1:right_time]
            time = reformat(time, year)
            u12 = 0
            u18 = 0
            for player in players: # count the number of players in each category that participated in the tournament
                if tournament in player[4]:
                    if player[7] == '':
                        player[7] = str(number)
                    else:
                        player[7] += ', ' + str(number)
                    if player[2] == 'U12':
                        u12 += 1
                    else:
                        u18 += 1
        tournament_to_print.append([number, name, place, time, u12, u18])
        number += 1
    result = tabulate(tournament_to_print, tablefmt='html', headers=['Nr.', 'Name', 'Ort', 'Datum', 'Teilnehmer U12', ' Teilnehmer U18'],
                      colalign=('center', 'left', 'left', 'center', 'center', 'center')) # save the table in html format for easy usage on the website
    outfile.write(result)
    outfile.close()

def sort_by_wins(p):
    return p[3]

def output_tables(players, year): # output the tables per category in html format
    outfile = open('tables_'+year+'.txt', 'w', encoding='latin-1')
    u12 = []
    u18 = []
    for player in players:
        if len(player[4]) == 0:
            del player
        else:
            if player[2] == 'U12':
                u12.append(player)
            else:
                u18.append(player)
    u12.sort(reverse=True, key=sort_by_wins)
    u18.sort(reverse=True, key=sort_by_wins)
    u18_to_print = u18
    u12_to_print = u12
    placement = 1
    table_u12 = []
    table_u18 = []
    for row in u18_to_print:
        row.insert(0, str(placement))
        placement += 1
        row[5] = len(row[5])
        del row[3]
        table_u18.append(row[:-2])
    placement = 1
    for row in u12_to_print:
        row.insert(0, str(placement))
        placement += 1
        row[5] = len(row[5])
        del row[3]
        table_u12.append(row[:-2])
    print_u18 = tabulate(table_u18, tablefmt='html', headers=['Rang', 'Vorname', 'Nachname', 'Siege', 'Turniere', 'Startrang', 'höchster Rang', 'Turniere'],
                      colalign=('right', 'left', 'left', 'center', 'center', 'center', 'center', 'left'))
    print_u12 = tabulate(table_u12, tablefmt='html', headers=['Rang', 'Vorname', 'Nachname', 'Siege', 'Turniere', 'Startrang', 'höchster Rang', 'Turniere'],
                      colalign=('right', 'left', 'left', 'center', 'center', 'center', 'center', 'left'))
    outfile.write(print_u12)
    outfile.write(print_u18)
    outfile.close()
    for row in u18_to_print:
        del row[7]
        del row[4]
        del row[3]
    for row in u12_to_print:
        del row[7]
        del row[4]
        del row[3]
    steffi = open('adressen_'+year+'.txt', 'w', encoding='latin-1') # this is also outdated for now. It served as a reduced output version with only relevant information for sending prices.
    for line in u12_to_print:
        out = '\t'.join(line)
        steffi.write(out)
    for line in u18_to_print:
        out = '\t'.join(line)
        steffi.write(out)
    steffi.close()

if __name__ == '__main__':
    year = '24'
    names = open('automated_names.txt', 'r', encoding='latin-1')
    players = automated_read_players(names)
    read_line(players, year)
    manage_tournaments(players, year)
    output_tables(players, year)
    names.close()
