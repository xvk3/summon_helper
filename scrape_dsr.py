from ctypes import *
from ctypes.wintypes import *
from pprint import pprint
import time

import win32api
import win32process
import win32con

import psutil
from mem_edit import Process

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

# Function Definitions
def myReadProcessMemoryA(processHandle, address, buffer, bufferSize):
    if not buffer and bufferSize:
        #buffer = c_char_p(b"A"*bufferSize)
        #bufferSize = len(buffer.value)
        buffer = create_string_buffer(b'\x00', bufferSize)
    bytesRead = c_ulong(0)
    if ReadProcessMemory(processHandle, address, buffer, bufferSize, byref(bytesRead)):
        print("Read " + str(bytesRead.value))
        return buffer
    else:
        print("Error ReadProcessMemory failed: " + str(GetLastError()))
    return buffer

def myReadProcessMemoryW(processHandle, address, buffer, bufferSize):
    if not buffer and bufferSize:
        #buffer = c_wchar_p(u"W"*bufferSize)
        #bufferSize = len(buffer.value)
        buffer = create_string_buffer(b'\x00', bufferSize)
    bytesRead = c_ulong(0)
    if ReadProcessMemory(processHandle, address, buffer, bufferSize, byref(bytesRead)):
        print("Read " + str(bytesRead.value))
        return buffer
    else:
        print("Error ReadProcessMemory failed: " + str(GetLastError()))
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
    address = myReadProcessMemoryA(PROCESS_HANDLE, ptr, 0, 8)
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
header = myReadProcessMemoryA(PROCESS_HANDLE, PROCESS_BASE, 0, 2)
if(header.value == b"MZ"): print("Found MZ/PE header")

#print(type(BASE_ADDRESSES["BaseB"]))
#print(type(int(BASE_ADDRESSES["BaseB"])))
newptr = myFollowPointer(BASE_ADDRESSES["BaseB"])
newptr = newptr + 16
finptr = myFollowPointer(newptr)
finptr = finptr + 0x12C

buf = myReadProcessMemoryW(PROCESS_HANDLE, finptr, 0, 32)
print(buf.value)
pprint(buf.raw)


# Attempt to get P[12345] from Session Info -> Current Player
baseX = myFollowPointer(BASE_ADDRESSES["BaseX"])
print(baseX)
PX_S1 = baseX + 0x68
print(PX_S1)
PX_S2 = myFollowPointer(PX_S1) + 0x18
print(PX_S2)
PX_S3 = myFollowPointer(PX_S2) + 0x38
PX_S4 = myFollowPointer(PX_S3) + 0x578
P1_Name = myFollowPointer(PX_S4) + 0xA8

buf = myReadProcessMemoryW(PROCESS_HANDLE, P1_Name, 0, 32)
print(buf.value)
pprint(buf.raw)


# To get to Name String:
# Directly follow BaseB first
# ^ + 10 and follow
# ^ + 12C

# Follow points in the same way as the CE script
# Use offsets from CE script to acquire information






CloseHandle(PROCESS_HANDLE)
















