# Summon Helper

\Simple program to help hosts summon phantoms in a fair order.

Program to analyse the different FC rules
- [ ] finish FC_RuleSet_7
- [ ] test reading memory from DS process (use CE to find addresses) (vsantiago113/ReadWriteMemory)

Sample output:

![Output](FC_RuleSet_Testing.png)

# scrape_DSR.py

## Instructions

1. Start DarkSoulsRemastered.exe
2. Start CheatEngine.exe and attach to the DSR process
3. Open DarkSoulsRemastered.CT and enable the table
4. Execute scrape_DSR.py

# TODO:

- [ ] make a list of python dependencies
- [x] implement player class
- [ ] implement better functions for following pointers and offsets
- [ ] implement FC class
- [ ] integrate with fctest.py
-- [ ] FC_RuleSet_7
- [ ] complete inline TODOs
- [ ] GUI
- [ ] Send less junk to stdout

