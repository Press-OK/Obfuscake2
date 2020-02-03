#=============================================================
# Obfuscake 2
# By Sean Berwick (PressOK)
#
# configmanager.py:
# Allows the configuration of the weekly schedules for events,
# called by the main script with the CLarg "-c"
#=============================================================

import sys

class ConfigManager:
    # Return value indicating whether we just quit, or quit
    # and run whitezombie.py's Main()
    quitAndRun = False

    #=======================================================
    # Run the config manager
    #
    # RETURNS: boolean based on whether to quit or quit/run
    #=======================================================
    def Run(self):
        # Display the main config menu and then exit
        self.MainMenu()
        print("\n\n\tGoodbye!\n")
        return self.quitAndRun

    #========================
    # Displays the main menu
    #========================
    def MainMenu(self):
        selection = "0"
        while selection != "4" and selection != "q":
            # Print the header
            print("\n\n\tWhitezombie Configuration Manager")
            print("\t=================================\n\n")
            print("\t1. Edit recording schedule")
            print("\t2. Edit playback schedule")
            print("\t3. Quit and run Obfuscake")
            print("\t4. Quit")
            # Get the user selection and proceed
            selection = input("\n\t > ").lower()
            if selection == "1":
                self.EditRecordingMenu()
            elif selection == "2":
                self.EditPlaybackMenu()
            elif selection == "3":
                self.quitAndRun = True
                break

    #===============================================
    # Displays the menu for editing recording times
    #===============================================
    def EditRecordingMenu():
        print("REC")
             
    #==============================================
    # Displays the menu for editing playback times
    #============================================== 
    def EditPlaybackMenu():
        print("PLAY")