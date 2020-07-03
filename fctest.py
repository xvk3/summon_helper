#!/usr/bin/env python3
import random
import argparse

rsc = "\033[1;37;40m"
rob = "\033[1;31;40m"
gob = "\033[1;32;40m"
yob = "\033[1;33;40m"

NUMBER_OF_PLAYERS = 6
NUMBER_OF_DUELS   = 20
NUMBER_OF_FCRS    = 1

fcrsc = 1
fcrsa = []
players = []
names = {"Alanne": 100, "Beatrice": 100, "Mich": 100, "Phantasm": 100, "Sitri": 100, "Zokye": 100}
duels = 10


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

  def Won(self):
    self.total_wins += 1
    self.total_duels += 1
    self.current_streak +=1
    self.inactive_count = 0

  def Lost(self):
    self.total_losses += 1
    self.total_duels += 1
    self.current_streak = 0
    self.inactive_count = 0

  def Timeout(self):
    self.current_streak = 0
    self.inactive_count = 0

  def Watching(self):
    self.inactive_count += 1

  def getName(self):
    return self.name

  def getSkill(self):
    return self.skill

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

  def setIC(self, ic):
    self.inactive_count = ic

# Sets up matches with the two players who have been waiting the longest
# Take a break after a 3 win streak
class FC_RuleSet_1:
  
  def __init__(self, players, rounds, seed):
    self.players        = players
    for player in range(0, len(self.players)):
      self.players[player].setSkill(round(random.random() * 100))
      self.players[player].setIC(0)
    self.rounds         = rounds
    self.seed           = seed
    self.cround         = 0
    self.dump()

  def dump(self):
    for player in range(0, len(self.players)):
      print(f"{self.players[player].getName()}, s={self.players[player].getSkill()}, ic={self.players[player].getIC()}, cs={self.players[player].getCS()}")

  def fdump(self):
    print("|  Name       |   Wins   |  Losses  |  Duels  |")
    for player in self.players:
      print(f"{player.getName()},  {player.getTW()},  {player.getTL()},   {player.getTD()}")
    exit()

  def setupDuel(self, previous_winner):

    self.cround += 1
    if self.cround > self.rounds: self.fdump()
    if self.cround == 1:
      print("First round")

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

    # make all other players watch
    for player in self.players:
        if player != p1 and player != p2:
          player.Watching()
    #print(p1.getName())
    #print(p2.getName())
    w,l = doBattle(p1, p2)
    w.Won()
    l.Lost()
    print(rsc + f"Round {self.cround}: " + gob + w.getName() + rsc + " vs " + rob +  l.getName() + rsc)
    if w.getCS() >= 3:
      w.Timeout()
      #self.dump()
      self.setupDuel(0)
    else:
      #self.dump()
      self.setupDuel(w)

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description='FC Ruleset Statistical Analysis Tool')
  parser.add_argument('-s', '--seed', help='Some junk data to seed the PRNG', required=True)
  args = vars(parser.parse_args())
  if not args['seed']:
    print("Problem with seed")
    exit(0);
  random.seed((args['seed']))

  # build player list
  for player in range(0, NUMBER_OF_PLAYERS):
    players.append(Player(list(names.keys())[player], list(names.values())[player]))

  # build FCs
  for fcrs in range(0, NUMBER_OF_FCRS):
    r = random.random()
    fcrsa.append(FC_RuleSet_1(players, NUMBER_OF_DUELS, r))

  # run FCs
  for fcrs in range(0, NUMBER_OF_FCRS):
    #fcrsa[fcrs].dump()
    fcrsa[fcrs].setupDuel(0)



