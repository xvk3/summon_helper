#!/usr/bin/env python3
import random
import argparse

rsc = "\033[1;37;40m"
rob = "\033[1;31;40m"
gob = "\033[1;32;40m"
yob = "\033[1;33;40m"

NUMBER_OF_PLAYERS = 6
NUMBER_OF_DUELS   = 100
NUMBER_OF_FCRS    = 6

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

def doBattle(first, second):
  p1s = first.getSkill()
  p2s = second.getSkill()
  d = p1s - p2s + (random.random() * 100) - 50
  #print(d)
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
    self.timeline = []

  def Reset(self):
    self.__init__(self.name, self.skill)

  def Won(self):
    self.total_wins     += 1
    self.total_duels    += 1
    self.current_streak += 1
    if self.inactive_count > self.longest_wait:
      self.longest_wait = self.inactive_count
    self.inactive_count = 0
    self.timeline.append(gob + "\u2588" + rsc)

  def Lost(self):
    self.total_losses   += 1
    self.total_duels    += 1
    self.current_streak = 0
    if self.inactive_count > self.longest_wait:
      self.longest_wait = self.inactive_count
    self.inactive_count = 0
    self.timeline.append(rob + "\u2588" + rsc)

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

  def printTimeline(self):
    return self.timeline

  def printTimelinePretty(self):
    print(f"{self.name.ljust(10)}|{str(self.total_wins).center(6)}|{str(self.total_losses).center(8)}|{str(self.total_duels).center(13)}|{str(self.longest_wait).center(14)}|",end=' ')
    print(''.join(self.timeline))

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
FC_Ruleset_6
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
    w.Won()
    l.Lost() 
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
    w.Won()
    l.Lost()

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
    w.Won()
    l.Lost()
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
    w.Won()
    l.Lost()

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
    w.Won()
    l.Lost()

    #dumpPlayers(self.players)
    #i = input()

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
    w.Won()
    l.Lost()

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

  # run FCs
  for fcrs in range(0, NUMBER_OF_FCRS):
    fcrsa[fcrs].setupDuel(0)



