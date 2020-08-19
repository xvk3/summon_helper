from ctypes import *
from ctypes.wintypes import *
from pprint import pprint
import time

import win32api
import win32process
import win32con

import psutil
from mem_edit import Process

import struct

import PySimpleGUI as sg

# Function Declarations
OpenProcess = ctypes.windll.kernel32.OpenProcess
ReadProcessMemory = ctypes.windll.kernel32.ReadProcessMemory
CloseHandle = ctypes.windll.kernel32.CloseHandle
GetModuleHandleA = ctypes.windll.kernel32.GetModuleHandleA
GetLastError = ctypes.windll.kernel32.GetLastError

# :)
rsc = "\033[1;37;40m"
rob = "\033[1;31;40m"
gob = "\033[1;32;40m"
yob = "\033[1;33;40m"
bob = "\033[1;34;40m"

# Globals
PROCESS_NAME       = "DarkSoulsRemastered.exe"
PROCESS_PID        = 0x00000000
PROCESS_ALL_ACCESS = 0x001F0FFF
PROCESS_HANDLE     = 0x00000000
PROCESS_BASE       = 0x00000000

BASES              = range(16)
BASE_NAMES         = ["BaseA", "BaseB", "BaseC", "BaseD", "BaseE", "BaseP", "BaseX", "BaseZ", "LockBonusBase", "BaseMB", "BaseR", "BaseMenu", "BaseN2", "BaseCAR", "BaseNS2", "XC"]
BASE_ADDRESSES     = {}

"""
Duel Class
"""
class FightClub:
  def __init__(self, players):
    self.fc             = "FC_RuleSet_7 - Best?"
    self.players        = players

  def startFC(self, previous_winner):

    ca = 0
    cb = 1
    caHP = 0
    cbHP = 0

    # do something with previous_winner

    # players are dueling
    # log curHP over time
    # if curHP == 1 then player lost
    while self.players[ca].getCurHP() > 1 and self.players[cb].getCurHP() > 1:
      caHP = self.players[ca].getCurHP()
      cbHP = self.players[cb].getCurHP()
      self.players[ca].logCurHP()
      self.players[cb].logCurHP()
      time.sleep(0.5)

    print("caHP = " + str(caHP))
    print("cbHP = " + str(cbHP))
 
    if caHP > cbHP:   # Combatant A wins
      print(self.players[ca].getName() + " beat " + self.players[cb].getName())
      self.players[ca].Won(cb)
      self.players[cb].Lost(ca)
      wp = ca

    elif cbHP > caHP: # Combatant B wins
      print(self.players[cb].getName() + " beat " + self.players[ca].getName())
      self.players[ca].Lost(cb)
      self.players[cb].Won(ca)
      wp = cb

    else:             # Draw
      print(self.players[ca].getName() + " drew with " + self.players[cb].getName())
      self.players[ca].Lost(cb)
      self.players[cb].Lost(ca)
      wp = -1


    print("--------")
    #print timelines of all players
    for player in self.players:
      print(player.getName())
      print(player.getTimeline())
      print(player.getCurHPlog())
      print("---")
      
    #startFC(wp)
    
      
"""
Player Class
"""
class Player:
  def __init__(self, base, offset):
    # Config
    self.base           = BASE_ADDRESSES[base]
    self.offset         = offset
    self.host           = True if offset == 0x00 else False
    # Stats
    self.name           = None
    self.SL             = 0
    self.maxHP          = 0
    self.curHP          = 0
    self.curHPptr       = 0
    self.status         = 0
    # FC
    self.current_streak = 0
    self.total_wins     = 0
    self.total_losses   = 0
    self.total_duels    = 0
    self.inactive_count = 0
    self.longest_wait   = 0
    self.timeline       = []
    self.played         = []
    self.getState()
    # Duel
    self.curHPlog       = []

  def Won(self, loser_index):
    self.total_duels    += 1
    self.current_streak += 1
    if self.inactive_count > self.longest_wait:
      self.longest_wait = self.inactive_count
    self.inactive_count = 0
    self.timeline.append(1)
    self.played.append(loser_index)
    
  def Lost(self, winner_index):
    self.total_losses   += 1
    self.total_duels    += 1
    self.current_streak = 0
    if self.inactive_count > self.longest_wait:
      self.longest_wait = self.inactive_count
    self.inactive_count = 0
    self.timeline.append(-1)
    self.played.append(winner_index)

  def Timeout(self):
    self.current_streak = 0
    self.inactive_count = 0

  def Watching(self):
    self.inactive_count += 1
    if self.inactive_count > self.longest_wait:
      self.longest_wait = self.inactive_count
    self.timeline.append(0)

  def getTimeline(self):
    return self.timeline

  def getState(self):
    ptr = self.follow(self.base) + 0x68
    ptr = self.follow(ptr) + 0x18
    ptr = self.follow(ptr) + self.offset
    ptr = self.follow(ptr)
    self.status = 0 if ptr == 0 else 1
    return self.status

  def getName(self):
    if not self.name:
      ptr = self.follow(self.base) + 0x68
      ptr = self.follow(ptr) + 0x18
      ptr = self.follow(ptr) + self.offset
      ptr = self.follow(ptr) + 0x578
      ptr = self.follow(ptr) + 0xA8
      buf = myReadProcessMemory(PROCESS_HANDLE, ptr, 0, 32)
      nam = buf.raw.decode("utf-16") if buf else ""
      self.name = nam
      return nam
    else:
      return self.name
    
  def getMaxHP(self):
    if not self.maxHP:
      ptr = self.follow(self.base) + 0x68
      ptr = self.follow(ptr) + 0x18
      ptr = self.follow(ptr) + self.offset
      ptr = self.follow(ptr) + 0x578
      ptr = self.follow(ptr) + 0x18
      buf = myReadProcessMemory(PROCESS_HANDLE, ptr, 0, 2)
      mhp = struct.unpack('<H', buf.raw)[0] if buf else 0
      self.maxHP = mhp
      return mhp
    else:
      return self.maxHP

  def getCurHP(self):
    if not self.curHPptr:
      ptr = self.follow(self.base) + 0x68
      ptr = self.follow(ptr) + 0x18
      ptr = self.follow(ptr) + self.offset
      ptr = self.follow(ptr) + 0x578
      ptr = self.follow(ptr) + 0x14
      buf = myReadProcessMemory(PROCESS_HANDLE, ptr, 0, 2)
      self.curHPptr = ptr if buf else 0
      return struct.unpack('<H', buf.raw)[0] if buf else 0
    else:
      buf = myReadProcessMemory(PROCESS_HANDLE, self.curHPptr, 0, 2)
      return struct.unpack('<H', buf.raw)[0] if buf else 0

  def logCurHP(self):
    self.curHPlog.append(self.getCurHP())

  def getCurHPlog(self):
    return self.curHPlog

  def getSL(self):
    ptr = self.follow(self.base) + 0x68
    ptr = self.follow(ptr) + 0x18
    ptr = self.follow(ptr) + self.offset
    ptr = self.follow(ptr) + 0x578
    ptr = self.follow(ptr) + 0x90
    buf = myReadProcessMemory(PROCESS_HANDLE, ptr, 0, 2)
    return struct.unpack('<H', buf.raw)[0] if buf else 0

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
  
  def follow(self, ptr):
    # Read 8 bytes from ptr
    buf = myReadProcessMemory(PROCESS_HANDLE, ptr, 0, 8)
    t = ""
    if isinstance(buf, int):
      return 0
    for c in range(len(buf.raw)-1, -1, -1): # Loop over the bytes in reverse
      t = t + str(hex(buf.raw[c])[2:].zfill(2)) # Build string
    return int(t, 16) # Convert string to int

"""
Function Definitions
""" 
def myReadProcessMemory(processHandle, address, buffer, bufferSize):
    if not buffer and bufferSize:
        buffer = create_string_buffer(b'\x00', bufferSize)
    bytesRead = c_ulong(0)
    if ReadProcessMemory(processHandle, address, buffer, bufferSize, byref(bytesRead)):
        return buffer
    else:
        return 0
    return buffer

def myGetPID(processName):
    pid = next(item for item in psutil.process_iter() if item.name() == processName).pid
    # TODO add error handling here, DSR process might not be running
    return pid

def myGetBaseAddress(processHandle):
    module_handles = win32process.EnumProcessModules(processHandle)
    module_handles_count = len(module_handles)
    module_index = 0
    module_handle = module_handles[module_index]
    return module_handle

def myGetBaseAddresses():
    ifile = open("base_addresses.txt", "r").readlines()
    for row in range(0, len(ifile)):
        BASE_ADDRESSES[BASE_NAMES[row]] = int(ifile[row])

def myFollowPointer(ptr):    
    address = myReadProcessMemory(PROCESS_HANDLE, ptr, 0, 8)
    print(type(address.raw))
    print(len(address.raw))
    t = ""
    print(hex(address.raw[0])[2:].zfill(2))
    print(hex(address.raw[1])[2:].zfill(2))
    for c in range(len(address.raw)-1, -1, -1):
        print(hex(address.raw[c]))
        t = t + str(hex(address.raw[c])[2:].zfill(2))
    print(t)
    print(int(t, 16))
    return int(t, 16)

def myDumpPlayer(player):
    # TODO dump information from player object, colorised
    return 0
 
PROCESS_PID    = myGetPID(PROCESS_NAME)
PROCESS_HANDLE = OpenProcess(PROCESS_ALL_ACCESS, False, PROCESS_PID)
PROCESS_BASE   = myGetBaseAddress(PROCESS_HANDLE)
myGetBaseAddresses()

print("Process Name         = " + PROCESS_NAME)
print("Process PID          = " + str(PROCESS_PID))
print("Process Handle       = " + str(PROCESS_HANDLE))
print("Process Base Address = {0:016X}".format(PROCESS_BASE))
print(BASE_ADDRESSES)

# Read two bytes from the PROCESS_BASE, should be "MZ"
header = myReadProcessMemory(PROCESS_HANDLE, PROCESS_BASE, 0, 2)
if(header.value == b"MZ"): print("Found MZ/PE header")

# TODO can the offsets be calculated using the XC base, it seems that XC is an offset to the next player?
# the magic number is 0x38 / 56

P0 = Player("BaseX", 0x00) # Host
P1 = Player("BaseX", 0x38)
P2 = Player("BaseX", 0x70)
P3 = Player("BaseX", 0xA8)
P4 = Player("BaseX", 0xE0)
P5 = Player("BaseX", 0x118)

PLAYERS = []
#If the host wants to play include the following line
PLAYERS.append(P0)
PLAYERS.append(P1)
PLAYERS.append(P2)
PLAYERS.append(P3)
PLAYERS.append(P4)
PLAYERS.append(P5)

# Check for active players
x = 0
while x < 2:
  for index in range(0, len(PLAYERS)):
    print("Player " + str(index) + " is " + str(PLAYERS[index].getState()))
    x = x + PLAYERS[index].getState()
  time.sleep(5)
  if x < 2:
    x = 0

# Print host information
print("Player 0 Name   = " + P0.getName())
print("Player 0 MaxHP  = " + str(P0.getMaxHP()))
print("Player 0 CurHP  = " + str(P0.getCurHP()))
print("Player 0 SL     = " + str(P0.getSL()))
# Print P1 information
print("Player 1 Name   = " + P1.getName())
print("Player 1 MaxHP  = " + str(P1.getMaxHP()))
print("Player 1 CurHP  = " + str(P1.getCurHP()))
print("Player 1 SL     = " + str(P1.getSL()))

FC = FightClub(PLAYERS)
FC.startFC(-1)

CloseHandle(PROCESS_HANDLE)
