from ctypes import *
from ctypes.wintypes import *
from pprint import pprint
from tkinter import ttk
import tkinter as tk
from tkinter import ttk
from mem_edit import Process

import time
import threading
import win32api
import win32process
import win32con
import psutil
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

PLAYERS            = []

BASES              = range(16)
BASE_NAMES         = ["BaseA", "BaseB", "BaseC", "BaseD", "BaseE", "BaseP", "BaseX", "BaseZ", "LockBonusBase", "BaseMB", "BaseR", "BaseMenu", "BaseN2", "BaseCAR", "BaseNS2", "XC"]
BASE_ADDRESSES     = {}


"""
GUI Class
"""
class GUI:
  def __init__(self):
    self.root = tk.Tk()
    self.root.configure(background='black')
    style = ttk.Style(self.root)
    style.configure('TLabel', background='black', foreground='white')
    style.configure('TFrame', background='black')
    self.frame = ttk.Frame(self.root)
    self.frame.grid(column=0, row=0)
    self.update()
   
  def update(self):
    while True:
      self.drawPlayers()
      self.drawCurrent()
      self.root.update_idletasks()
      self.root.update()
      time.sleep(0.1)

  def drawPlayers(self):
    for index in range(0, len(PLAYERS)):
      ttk.Label(self.frame, text="Name", font='Helvetica 10 bold').grid(column=1, row=0)
      ttk.Label(self.frame, text="Stats", font='Helvetica 10 bold').grid(column=2, row=0)
      ttk.Label(self.frame, text="SL", font='Helvetica 10 bold').grid(column=3, row=0)
      ttk.Label(self.frame, text="Timeline", font='Helvetica 10 bold').grid(column=4, row=0)
      if PLAYERS[index].getState():
        ttk.Label(self.frame, text=PLAYERS[index].getName()).grid(column=1, row=index+1)
        ttk.Label(self.frame, text=PLAYERS[index].getStats()).grid(column=2, row=index+1)
        ttk.Label(self.frame, text=PLAYERS[index].getSL()).grid(column=3, row=index+1)
        for rindex in range(0, len(PLAYERS[index].getTimeline())):
          if PLAYERS[index].getTimeline()[rindex] == -1:
            ttk.Label(self.frame, text="\u2588", foreground="red").grid(column=4 + rindex, row=index+1)
          elif PLAYERS[index].getTimeline()[rindex] == 1:
            ttk.Label(self.frame, text="\u2588", foreground="green").grid(column=4 + rindex, row=index+1)
          else:
            ttk.Label(self.frame, text="\u2588", foreground="yellow").grid(column=4 + rindex, row=index+1)
      else:
        ttk.Label(self.frame, text="Player" + str(index)).grid(column=1, row=index+1)
        ttk.Label(self.frame, text="??/??/??/??/??/??/??/??").grid(column=2, row=index+1)
        ttk.Label(self.frame, text="??").grid(column=3, row=index+1)
        ttk.Label(self.frame, text="?").grid(column=3, row=index+1)

  def drawCurrent(self):
    #for index in 
    ttk.Label(self.frame, text="Current Duel", font='Helvetica 10 bold').grid(column=1, row=7, sticky=EW)

"""
Duel Class
"""
class FightClub:
  def __init__(self, players):
    self.fc             = "FC_RuleSet_7 - Best?"
    self.players        = players
    self.gui            = GUI()

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

    #self.gui.update()
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
    self.stats          = {"VIT":0, "ATN":0, "END":0, "STR":0, "DEX":0, "RES":0, "INT":0, "FTH":0}
    # FC
    self.current_streak = 0
    self.total_wins     = 0
    self.total_losses   = 0
    self.total_duels    = 0
    self.inactive_count = 0
    self.longest_wait   = 0
    self.timeline       = [1,0,-1,1,0,0,1,1,-1,0,0,0,-1,1,1,0,-1,1]
    self.played         = []
    # Duel
    self.curHPlog       = []
    # Init Functions
    self.luStats()
    self.getState()
    
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

  def luStats(self):
    ptr = self.follow(self.base) + 0x68
    ptr = self.follow(ptr) + 0x18
    ptr = self.follow(ptr) + self.offset
    ptr = self.follow(ptr) + 0x578
    arr = self.follow(ptr) + 0x40
    for stat in range(0, 8):
      off = arr + (stat * 0x08)
      buf = myReadProcessMemory(PROCESS_HANDLE, off, 0, 2)
      self.stats[list(self.stats.keys())[stat]] = struct.unpack('<H', buf.raw)[0] if buf else 0

  def getStats(self):
    return "/".join("{0}".format(l) for l in list(self.stats.values()))

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
    for item in psutil.process_iter():
      if item.name() == processName:
        return item.pid

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

def myDumpPlayer(player):
    print("Name   = " + player.getName())
    print("SL     = " + str(player.getSL()))
    print("Stats  = " + player.getStats())
    print("MaxHP  = " + str(player.getMaxHP()))
    print("CurHP  = " + str(player.getCurHP()))
 
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

# Generate players
for p in range(0, 6):
  PLAYERS.append(Player("BaseX", 0x38 * p))

# Dump host info
myDumpPlayer(PLAYERS[0])

FC = FightClub(PLAYERS)
fct = threading.Thread(target=FC.startFC, args=(-1,))
fct.start()

# Check for active players
x = 0
while x < 2:
  for index in range(0, len(PLAYERS)):
    print("Player " + str(index) + " is " + str(PLAYERS[index].getState()))
    x = x + PLAYERS[index].getState()
  time.sleep(5)
  if x < 2:
    x = 0

g = GUI()
g.update()

CloseHandle(PROCESS_HANDLE)
