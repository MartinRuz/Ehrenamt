# Ehrenamt
Collection of scripts for my Go-related volunteer work. Their common theme is that they use data from the EGD-history file, to analyze players, e.g. their number of wins in a certain year, their number of tournaments and others.

## LV
In this subfolder are two different scripts for the Go-Verein Baden-Württemberg e.V.
### Analysis
The analysis script requires the current all.hst.txt file from https://europeangodatabase.eu/EGD/EGD_2_0/downloads/all.hst to be present in the same folder.
Furthermore, there must be a file egd_pins.csv, which is not publicly available because it contains sensitive data about our members.
It contains ;-separated entries of the form 'first name'; 'last name'; 'egd-pin'.
### Cup
For the Länd-Cup, we also require the current all.hst.txt file from https://europeangodatabase.eu/EGD/EGD_2_0/downloads/all.hst to be present in the same folder.
Additionally, a file tournaments_$year.txt must be present, which has line-separated entries of the form 'EGD-pin' 'class' 'name' of all tournaments that were played in Baden-Württemberg in the $year.
For different usage purposes, this file can contain any other tournaments as well.
Lastly, there must also be a file egd_pins.csv, which is again not publicly available because it contains sensitive data about our members.
It contains ;-separated entries of the form 'first name'; 'last name'; 'egd-pin'.
## KuT
The folder KuT-Pokal does not contain the file scrape_names.py because of privacy concerns.
The script once again requires the current all.hst.txt file from https://europeangodatabase.eu/EGD/EGD_2_0/downloads/all.hst to be present in the same folder.
Additionally, a file automated_names.txt is required, of the form 'first name' 'last name' 'category' (i.e. space-separated). These are the names of the players that fall into each category, and that will be analyzed.
