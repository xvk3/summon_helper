#!/usr/bin/env python3
import random
import argparse
from collections import Counter

rsc = "\033[1;37;40m"
rob = "\033[1;31;40m"
gob = "\033[1;32;40m"
yob = "\033[1;33;40m"
bob = "\033[1;34;40m"

NUMBER_OF_PLAYERS = 6
NUMBER_OF_DUELS   = 100
NUMBER_OF_FCRS    = 7

fcrsc = 1
fcrsa = []
players = []
names = {"Alanne": 100, "Beatrice": 100, "Mich": 100, "Phantasm": 100, "Sitri": 100, "Zokye": 100}
duels = 10

def resetPlayers(pa):
  for player in range(0, len(pa)): pa[player].Reset()

def dumpPlayers(pa):
  print("  Name    | Wins | Losses | Total Duels | Longest Wait |")
  for player in range(0, len(pa)):
    pa[player].printTimelinePretty()

def dumpPlayed(pa):
  for player in range(0, len(pa)):
    played = pa[player].getPlayed()
    played_opponents = list(Counter(played).keys())
    played_count     = list(Counter(played).values())
    pmax = 0
    opponent = 0
    for opponent in range(0, len(played_opponents)):
      if played_count[opponent] > pmax:
        pmax = played_count[opponent]
        index = opponent     
    print(f"{pa[player].getName()} played {pa[played_opponents[index]].getName()} {pmax} times, this is {round((pmax/pa[player].getTD())*100)}% of their duels") 

def doBattleRandom(first, second):
  r = random.random() * 100
  firstd = abs(first.getSkill() - r)
  secondd = abs(second.getSkill() -r)
  if firstd >= secondd:
    return (first, second)
  else:
    return (second, first)

def doBattle5050(first, second):
  r = random.randint(0, 1)
  if r == 0:
    return (first, second)
  else:
    return (second, first)  

def doBattle(first, second):
  return doBattle5050(first, second)
  p1s = first.getSkill()
  p2s = second.getSkill()
  d = p1s - p2s + (random.random() * 100) - 50
  if d > 0:
    return (first,second)
  else:
    return (second, first)

class Player:

  def __init__(self, name, skill):
    self.name           = name
    self.skill          = skill
    self.current_streak = 0
    self.total_wins     = 0
    self.total_losses   = 0
    self.total_duels    = 0
    self.inactive_count = 0
    self.longest_wait   = 0
    self.timeline       = []
    self.played         = []

  def Reset(self):
    self.__init__(self.name, self.skill)

  def Won(self, loser_index):
    self.total_wins     += 1
    self.total_duels    += 1
    self.current_streak += 1
    if self.inactive_count > self.longest_wait:
      self.longest_wait = self.inactive_count
    self.inactive_count = 0
    self.timeline.append(gob + "\u2588" + rsc)
    self.played.append(loser_index)

  def Lost(self, winner_index):
    self.total_losses   += 1
    self.total_duels    += 1
    self.current_streak = 0
    if self.inactive_count > self.longest_wait:
      self.longest_wait = self.inactive_count
    self.inactive_count = 0
    self.timeline.append(rob + "\u2588" + rsc)
    self.played.append(winner_index)

  def Timeout(self):
    self.current_streak = 0
    self.inactive_count = 0

  def Watching(self):
    self.inactive_count += 1
    if self.inactive_count > self.longest_wait:
      self.longest_wait = self.inactive_count
    self.timeline.append(yob + "\u2588" + rsc)

  def getName(self):
    return self.name

  def getSkill(self):
    return self.skill

  def getTimeline(self):
    return self.timeline

  def printTimelinePretty(self):
    print(f"{self.name.ljust(10)}|{str(self.total_wins).center(6)}|{str(self.total_losses).center(8)}|{str(self.total_duels).center(13)}|{str(self.longest_wait).center(14)}|",end=' ')
    print(''.join(self.timeline))

  def getPlayed(self):
    return self.played

  def getLastPlayed(self):
    try:
      return self.played[-1]
    except IndexError:
      return -1 

  def setSkill(self, skill):
    self.skill = skill
    return

  def getCS(self):
    return self.current_streak

  def getTW(self):
    return self.total_wins

  def getTL(self):
    return self.total_losses

  def getTD(self):
    return self.total_duels

  def getIC(self):
    return self.inactive_count

  def getLW(self):
    return self.longest_wait

  def setIC(self, ic):
    self.inactive_count = ic

'''
FC_RuleSet_7
Players are matched to prioritise the following:
 1. minimise inactive_count / waiting time
 2. minimise the range of the players' total_duels
 3. maximise the duel variation for each player
 4. maximise the duel variation for the stream/host
Players are never Timeout()
'''
class FC_RuleSet_7:

  def __init__(self, players, rounds, seed):
    self.fc             = "FC_RuleSet_7 - Best?"
    self.players        = players
    self.rounds         = rounds
    self.seed           = seed
    self.cround         = 0
    self.ic_weight      = 4
    self.td_weight      = 3

  def setupDuel(self, previous_winner):

    self.cround += 1
    if self.cround > self.rounds:
      dumpPlayers(self.players)
      dumpPlayed(self.players)
      resetPlayers(self.players) # required?
      return
    if self.cround == 1:
      print(bob + "\n" + self.fc + rsc)

    p1 = self.players[0]
    p2 = self.players[0]

    wplayers = []
    hplayers = []

    ic_total = 0
    td_total = 0
    # Loop through players and generate stats
    for player in self.players:
      ic_total += player.getIC()
      td_total += player.getTD() 
    ic_average = ic_total / len(self.players)
    td_average = td_total / len(self.players)

    highest = -9999
    for player in self.players:
      score = player.getIC() * self.ic_weight# + (1 - player.getTD() * self.td_weight)
      print(f"{player.getName()} score = {score}")
      highest = score if score > highest else highest
      wplayers.append(score)
    # wplayers is a list of scores addressable using the same index as self.players
    
    for index in range(0, len(wplayers)):
      print(bob+f"{self.players[index].getName()} score = {wplayers[index]}"+rsc)
      if wplayers[index] == highest:
        hplayers.append(index)
    # hplayers is a list of indexes to the highest scoring players

    for index in range(0, len(hplayers)):
      print(rob+f"{self.players[hplayers[index]].getName()}"+rsc)
      print(rob+f"{self.players[hplayers[index]].getName()} last played {self.players[hplayers[index]].getLastPlayed()}"+rsc)    
 
    if len(hplayers) == 2:
      print(gob+f"{self.players[hplayers[0]].getLastPlayed()}")
      # If the next two players to play have recently played eachother, swap one player out
      if self.players[hplayers[0]].getLastPlayed() == hplayers[1]:
        # Swap to the player with the longest IC
        print(rob+"swap to player with longest IC")
        highest_ic = -1
        highest_ic_indexes = []
        for index in range(0, len(self.players)):
          if self.players[index].getIC() >= highest_ic:
            highest_ic = self.players[index].getIC()
        for index in range(0, len(self.players)):
          if self.players[index].getIC() == highest_ic:
            highest_ic_indexes.append(index)           
        print(highest_ic_indexes)
        for index in range(0, len(highest_ic_indexes)):
          r = random.randint(0, 1)
          if self.players[highest_ic_indexes[index]] != self.players[hplayers[0]]:
            if r == 0: 
              p2 = self.players[highest_ic_indexes[index]]
            else:
              p1 = self.players[highest_ic_indexes[index]]
          else:
            p1 = self.players[hplayers[0]]
            p2 = self.players[hplayers[1]]
            flag = 1
            while flag == 1 or p1 == p2:
              if r == 0:
                p1 = self.players[random.randint(0, len(self.players)-1)]
              else:
                p2 = self.players[random.randint(0, len(self.players)-1)] 
              flag = 0 
      else:
        p1 = self.players[hplayers[0]]
        p2 = self.players[hplayers[1]]
    elif len(hplayers) == 1:
      p1 = self.players[hplayers[0]]
      p2 = p1
      while p1 == p2:
        p2 = self.players[random.randint(0, len(self.players)-1)] 
    else:
      while p1 == p2:
        print(hplayers)
        p1 = self.players[hplayers[random.randint(0, len(hplayers)-1)]]
        p2 = self.players[hplayers[random.randint(0, len(hplayers)-1)]]

    print(p1.getName())
    print(p2.getName())
    dumpPlayers(self.players)

    i = input()

    # Make all other players watch
    for player in self.players:
      if player != p1 and player != p2:
        player.Watching()

    # Do battle
    w,l = doBattle(p1, p2)
    w.Won(players.index(l))
    l.Lost(players.index(w))

    self.setupDuel(w)

'''
FC_RuleSet_6
Players are matched to minimise waiting time
Players are not Timeout()
'''
class FC_RuleSet_6:

  def __init__(self, players, rounds, seed):
    self.fc             = "FC_RuleSet_6 - Minimise IC / Waiting Time, No Timeout()"
    self.players        = players
    self.rounds         = rounds
    self.seed           = seed
    self.cround         = 0

  def setupDuel(self, previous_winner):

    self.cround += 1
    if self.cround > self.rounds:
      dumpPlayers(self.players)
      dumpPlayed(self.players)
      resetPlayers(self.players)
      return   
    if self.cround == 1:
      print("\n" + self.fc)

    p1 = self.players[0]
    p2 = self.players[1]

    # Find players with the highest IC
    for player in self.players:
      if player.getIC() > p1.getIC() and player != p2:
        p1 = player
      if player.getIC() > p2.getIC() and player != p1:
        p2 = player 

    # Make all other players watch
    for player in self.players:
      if player != p1 and player != p2:
        player.Watching()

    # Do battle
    w,l = doBattle(p1, p2)
    w.Won(players.index(l))
    l.Lost(players.index(w))

    self.setupDuel(0)

'''
FC_Ruleset_5
Players are matched randomly
Players are Timeout() after a three win streak
'''
class FC_RuleSet_5:

  def __init__(self, players, rounds, seed):
    self.fc             = "FC_RuleSet_5 - Random, Timeout() after 3 CS"
    self.players        = players
    self.rounds         = rounds
    self.seed           = seed
    self.cround         = 0

  def setupDuel(self, previous_winner):

    self.cround += 1
    if self.cround > self.rounds:
      dumpPlayers(self.players)
      dumpPlayed(self.players)
      resetPlayers(self.players)
      return   
    if self.cround == 1:
      print("\n" + self.fc)

    # Check previous winner
    if previous_winner != 0:
      p1 = previous_winner
      p2 = self.players[random.randint(0, len(self.players)-1)]
    else:
      p1 = self.players[0]
      p2 = self.players[0]

    # While the p1 == p2 randomise both
    while p1 == p2:
      if p1 != previous_winner: # Only randomise p1 if w == 0
        p1 = self.players[random.randint(0, len(self.players)-1)]
      p2 = self.players[random.randint(0, len(self.players)-1)]

    # Make all other players watch
    for player in self.players:
      if player != p1 and player != p2:
        player.Watching() 

    # Do battle
    w,l = doBattle(p1, p2)
    w.Won(players.index(l))
    l.Lost(players.index(w))


    # Check if winner needs to Timeout()
    if w.getCS() >= 3:
      w = 0
    self.setupDuel(w)

'''
FC_Ruleset_4
Players are matched randomly
Players are never Timeout()
'''
class FC_RuleSet_4:

  def __init__(self, players, rounds, seed):
    self.fc             = "FC_RuleSet_4 - Random, No Timeout()"
    self.players        = players
    self.rounds         = rounds
    self.seed           = seed
    self.cround         = 0

  def setupDuel(self, previous_winner):

    self.cround += 1
    if self.cround > self.rounds:
      dumpPlayers(self.players)
      dumpPlayed(self.players)
      resetPlayers(self.players)
      return   
    if self.cround == 1:
      print("\n" + self.fc)
 
    # Initialise both p1 and p2 to the same value 
    p1 = self.players[0]
    p2 = self.players[0]

    # While the p1 == p2 randomise both
    while p1 == p2:
      p1 = self.players[random.randint(0, len(self.players)-1)]
      p2 = self.players[random.randint(0, len(self.players)-1)]

    # Make all other players watch
    for player in self.players:
      if player != p1 and player != p2:
        player.Watching()

    # Do battle
    w,l = doBattle(p1, p2)
    w.Won(players.index(l))
    l.Lost(players.index(w))

    self.setupDuel(0)

'''
FC_Ruleset_3
Players are matched by total_duels then inactive_count
Players are Timeout() after a three win streak
'''
class FC_RuleSet_3:

  def __init__(self, players, rounds, seed):
    self.fc             = "FC_RuleSet_3 - TD > IC, Timeout() after 3 CS"
    self.players        = players
    self.rounds         = rounds
    self.seed           = seed
    self.cround         = 0

  def setupDuel(self, previous_winner):

    self.cround += 1
    if self.cround > self.rounds:
      dumpPlayers(self.players)
      dumpPlayed(self.players)
      resetPlayers(self.players)
      return   
    if self.cround == 1:
      print("\n" + self.fc)
  
    p1 = self.players[0]
    p2 = self.players[1]
    if isinstance(previous_winner, Player):
      p1 = previous_winner
    p1_ic = p1.getIC()
    p1_td = p1.getTD()
    p2_ic = p2.getIC()
    p2_td = p2.getTD()

    for player in self.players:
      # Because p2 is always self.players[1] here we need to loop over all players
      # looking for somebody with a lower total_duels OR the same total_duels
      # but with a higher inactive_count
      if player.getTD() < p2_td or (player.getTD() == p2_td and player.getIC() > p2_ic):
        p2 = player
        p2_ic = p2.getIC()
        p2_td = p2.getTD()

      # If the previous winner has Timeout() OR this is the first round
      if p1 != previous_winner:
        # Check if there is a (player with lower total_duels OR higher inactive_count) AND player != p2
        if (player.getTD() < p1_td or player.getIC() > p1_ic) and player != p2:
          p1 = player
          p1_ic = p1.getIC()
          p1_td = p1.getTD()

    # Make all other players watch
    for player in self.players:
      if player != p1 and player != p2:
        player.Watching()

    # Do battle
    w,l = doBattle(p1, p2)
    w.Won(players.index(l))
    l.Lost(players.index(w))



    # Check if winner needs to Timeout()
    if w.getCS() >= 3:
      w.Timeout()
      w = 0
    self.setupDuel(w)

'''
FC_RuleSet_2
Players are matched by inactive_count then total_duels
Players are Timeout() after a three win streak
'''
class FC_RuleSet_2:

  def __init__(self, players, rounds, seed):
    self.fc             = "FC_RuleSet_2 - IC > TD, Timeout() after 3 CS"
    self.players        = players
    self.rounds         = rounds
    self.seed           = seed
    self.cround         = 0

  def setupDuel(self, previous_winner):

    self.cround += 1
    if self.cround > self.rounds:
      dumpPlayers(self.players)
      dumpPlayed(self.players)
      resetPlayers(self.players)
      return   
    if self.cround == 1:
      print("\n" + self.fc)
 
    p1 = self.players[0]
    p2 = self.players[1]
    if isinstance(previous_winner, Player):
      p1 = previous_winner

    p1_ic = p1.getIC()
    p1_td = p1.getTD()
    p2_ic = p2.getIC()
    p2_td = p2.getTD()

    for player in self.players:
      # Because p2 is always self.players[1] here we need to loop over all players
      # looking for somebody with a higher inactive_count OR the same inactive_count
      # but with less total_duels
      if player.getIC() > p2_ic or (player.getIC() == p2_ic and player.getTD() < p2_td):
        p2 = player
        p2_ic = p2.getIC()
        p2_td = p2.getTD()

      # If the previous winner has Timeout() OR this is the first round
      if p1 != previous_winner:
        # Check if there is a (player with higher inactive_count OR less total_duels) AND player != p2
        if (player.getIC() > p1_ic or player.getTD() < p1_td) and player != p2:
          p1 = player
          p1_ic = p1.getIC()
          p1_td = p1.getTD()

    # Make all other players watch
    for player in self.players:
      if player != p1 and player != p2:
        player.Watching()

    # Do battle
    w,l = doBattle(p1, p2)
    w.Won(players.index(l))
    l.Lost(players.index(w))



    # Check if winner needs to Timeout()
    if w.getCS() >= 3:
      w.Timeout()
      w = 0
    self.setupDuel(w)


# Sets up matches with the two players who have been waiting the longest
# Take a break after a 3 win streak
class FC_RuleSet_1:
  
  def __init__(self, players, rounds, seed):
    self.fc             = "FC_RuleSet_1 - IC > TD, Timeout() after 3 CS"
    self.players        = players
    self.rounds         = rounds
    self.seed           = seed
    self.cround         = 0
    self.dump()

  def dump(self):
    for player in range(0, len(self.players)):
      print(f"{self.players[player].getName()}, s={self.players[player].getSkill()}, ic={self.players[player].getIC()}, cs={self.players[player].getCS()}")

  def setupDuel(self, previous_winner):

    self.cround += 1
    if self.cround > self.rounds:
      dumpPlayers(self.players)
      dumpPlayed(self.players)
      resetPlayers(self.players)
      return
    if self.cround == 1:
      print(self.fc)


    p1 = self.players[0]
    p2 = self.players[1]
    if isinstance(previous_winner, Player):
      p1 = previous_winner
    p1s = p1.getIC()
    p2s = p2.getIC()
      
    for player in self.players:
      #print(f"looking at {player.getName()} with ic={player.getIC()}")
      #print(f"current p1= {p1s} and p2= {p2s}")
      if player.getIC() > p2.getIC() and player != p1:
        #print(f"{player.getName()} has been waiting longer than p2 ic={p2s}")
        p2 = player
        p2s = p2.getIC()

      if p2.getIC() > p1.getIC() and p1 != previous_winner and p2 != player:
        #print(f"p2s > p1={p1.getIC()} and p1 != previous winner")
        p1 = p2
        p2 = player

    # Make all other players watch
    for player in self.players:
      if player != p1 and player != p2:
        player.Watching()

    w,l = doBattle(p1, p2)
    w.Won(players.index(l))
    l.Lost(players.index(w))



    if w.getCS() >= 3:
      w.Timeout()
      self.setupDuel(0)
    else:
      self.setupDuel(w)

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='FC Ruleset Statistical Analysis Tool')
  parser.add_argument('-s', '--seed', help='Some junk data to seed the PRNG', required=True)
  args = vars(parser.parse_args())
  if not args['seed']:
    print("Problem with seed")
    exit(0);
  random.seed((args['seed']))

  # rsc
  print(rsc)

  # build player list
  for player in range(0, NUMBER_OF_PLAYERS):
    players.append(Player(list(names.keys())[player], list(names.values())[player]))
    players[player].setSkill(round(random.random() * 100)) # initialise player skill values
    
  # build FCs
  r = random.random()
  fcrsa.append(FC_RuleSet_1(players, NUMBER_OF_DUELS, r))
  fcrsa.append(FC_RuleSet_2(players, NUMBER_OF_DUELS, r))
  fcrsa.append(FC_RuleSet_3(players, NUMBER_OF_DUELS, r))
  fcrsa.append(FC_RuleSet_4(players, NUMBER_OF_DUELS, r))
  fcrsa.append(FC_RuleSet_5(players, NUMBER_OF_DUELS, r))
  fcrsa.append(FC_RuleSet_6(players, NUMBER_OF_DUELS, r))
  fcrsa.append(FC_RuleSet_7(players, NUMBER_OF_DUELS, r))


  # run FCs
  for fcrs in range(0, NUMBER_OF_FCRS):
    fcrsa[fcrs].setupDuel(0)



