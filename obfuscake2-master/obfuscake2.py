#=============================================================
# Obfuscake 2
# By Sean Berwick (PressOK)
#
# obfuscake2.py:
# The main application script, generates and plays events
# during periods of user inactivity
#=============================================================

import sys
from eventmanager import EventManager
from configmanager import ConfigManager

#=============
# Main method
#=============
def Main():
    em = EventManager()

    recordedEvents = em.Record(10)

    em.WriteToFile()

    em.Play()

#==========================================================
# Entry point of the program, handles command args:
#   -c      Run ConfigManager
#==========================================================
if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "-c":
            doRunAfterConfig = ConfigManager().Run()
            if doRunAfterConfig:
                Main()
    else:
        Main()