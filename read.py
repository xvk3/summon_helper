#!/usr/bin/env python3
import ReadWriteMemory
import random
import argparse
from collections import Counter

rsc = "\033[1;37;40m"
rob = "\033[1;31;40m"
gob = "\033[1;32;40m"
yob = "\033[1;33;40m"
bob = "\033[1;34;40m"

if __name__ == "__main__":
  rwm = ReadWriteMemory()
  process = rwm.get_process_by_name('notepad.exe')
  process.open()
  print('\nPrint the Process information.')
  print(process.__dict__)
  data = process.readEx(0x0BBf8808)
  print(data)
  player_name = process.get_pointer(0x0BBF8808, offsets=[0x10])
  print(f"player_name = {player_name}")

