#==============================================================
# Obfuscake 2
# By Sean Berwick (PressOK)
#
# eventmanager.py:
# Manages the recording, playing, saving, and loading of events
#==============================================================

from lib import keyboard, mouse
from multiprocessing import Process, Queue
from eventprocessor import EventProcessor
import subprocess
import os, platform, time, datetime
import pickle, bz2

class EventManager:
    recordedEvents = []

    #=======================================================
    # Plays a provided set of recorded events, or if none is
    # given, it will use the events stored locally in the
    # class (from the last LoadFromFile, Record, or Play)
    #
    # RETURNS: Success boolean
    #=======================================================
    def Play(self, recordedEvents=None):
        recordedEvents = self.recordedEvents if recordedEvents == None else recordedEvents

        # Ensure we have events to play
        if len(recordedEvents) > 0:
            # Create two processes for keyboard/mouse
            kbProcess = Process(target=keyboard.play, args=(recordedEvents["keyboard"],1.2,))
            mProcess = Process(target=mouse.play, args=(recordedEvents["mouse"],1.2,))

            # Determine which events start first based on the first
            # event time of each, since there is no delay stored for
            # the initial events
            keyboardFirst = False
            delay = 0
            try:
                firstKBEventTime = recordedEvents["keyboard"][0].time
                firstMEventTime = recordedEvents["mouse"][0].time
                delay = abs(firstKBEventTime - firstMEventTime)
                keyboardFirst = True if firstKBEventTime < firstMEventTime else False
            except:
                pass

            # If keyboard goes first, start it, otherwise mouse
            kbProcess.start() if keyboardFirst else mProcess.start()

            # Sleep for the difference in start times
            time.sleep(delay)

            # If keyboard was second, start it, otherwise mouse
            mProcess.start() if keyboardFirst else kbProcess.start()

            # Sleep for the entire duration of the events
            time.sleep(recordedEvents["duration"])

            # Clean up the spawned processes
            kbProcess.join()
            mProcess.join()
            return True
        else:
            print("Playback failed, events object was empty!")
            return False

    #=======================================================
    # Records events for a provided number of seconds, then
    # passes them off to be processed/cleaned up before
    # returning them to the caller
    #
    # RETURNS: A set of recorded events
    #=======================================================
    def Record(self, seconds):
        # Take a snapshot of running processes
        initialProcessList = self.GetProcessList()

        # Set up the keyboard/mouse recording processes and
        # the Queue which they will push events into, and
        # also start recording
        kbQueue = Queue()
        kbProcess = Process(target=self.RecordKeyboard, args=(seconds,kbQueue,))
        kbProcess.start()
        mQueue = Queue()
        mProcess = Process(target=self.RecordMouse, args=(seconds,mQueue,))
        mProcess.start()
        
        # Each get() will block until the process returns
        # the results (which should happen ~simultaneously)
        kbEvents = kbQueue.get()
        mEvents = mQueue.get()

        # Clean up the spawned processes
        kbProcess.join()
        mProcess.join()
        
        # Get a final snapshot of the running processes
        allProcesses = self.GetProcessList()

        # Determine which processes are new by seeing if they
        # spawned since the initial snapshot
        newProcesses = []
        for p in allProcesses:
            if p not in initialProcessList:
                newProcesses.append(p)

        # Put all of our results into an object
        self.recordedEvents = {
            "duration": seconds,
            "allProcesses": allProcesses,
            "newProcesses": newProcesses,
            "keyboard": kbEvents,
            "mouse": mEvents
            }

        # Perform all the pre-processing on the events
        processedEvents = EventProcessor().Process(self.recordedEvents)
        if not processedEvents:
        	print("Event processing failed!")
        	return None
        else:
        	self.recordedEvents = processedEvents
        	return self.recordedEvents

    #====================================================
    # Writes a provided set of recorded events to a file
    #
    # RETURNS: Success boolean
    #====================================================
    def WriteToFile(self, recordedEvents=None):
        try:
            # If no events provided, attempt to use recent/local
            if not recordedEvents:
                recordedEvents = self.recordedEvents
            now = datetime.datetime.now()
            # Create a compressed file
            compressedFile = bz2.BZ2File("./rec/" + "-".join([
                str(now.hour),
                str(now.minute),
                str(now.second),
                str(now.year),
                str(now.month),
                str(now.day)
                ]) + ".wze", "wb")
            # Write to it, pickled and compressed
            compressedFile.write(pickle.dumps(recordedEvents))
            compressedFile.close()
            return True
        except:
            return False

    #=================================================
    # Loads a set of events from a provided file path
    #
    # RETURNS: Set of events, or None if unsuccessful
    #=================================================
    def LoadFromFile(self, filePath):
        # Check if it exists
        if os.path.isfile(filePath):
            try:
                # Load the compressed file
                compressedFile = bz2.BZ2File(filePath, "rb")
                # Set our events to the unpickled, uncompressed file
                self.recordedEvents = pickle.loads(compressedFile.read())
                compressedFile.close()
                return self.recordedEvents
            except:
                print("Unable to read " + filePath +"! It appears to be empty.")
                return None
        else:
            print("Unable to read " + filePath +"! File not found.")
            return None

    #=================================================
    # Reaches out to our modified keyboard library to
    # record events asynchronously and stores them in
    # the result queue, which is required for passing
    # data between processes
    #=================================================
    def RecordKeyboard(self, seconds, resultQueue):
        events = keyboard.record_for_seconds(seconds)
        resultQueue.put(events)

    #=================================================
    # Same as above, but for the mouse
    #=================================================
    def RecordMouse(self, seconds, resultQueue):
        events = mouse.record_for_seconds(seconds)
        resultQueue.put(events)

    #=================================================
    # OS-dependent method of getting a list of running
    # processes. It is not very good, and Linux has
    # been limited to the most recent 15 processes
    # since it lists too many. Also TODO; Mac
    #
    # RETURNS: List of running processes
    #=================================================
    def GetProcessList(self):
        processList = []
        if platform.system() == "Linux":
            # Run shell cmd and pipe output for parsing
            for pl in str(subprocess.Popen(["ps", "--ppid", "2", "-p", "2", "--deselect"], stdout=subprocess.PIPE).communicate()[0]).split():
                # Use only the last column of the output (which ends in byte values for "\n")
                if pl[-1] == "n":
                    # Strip the "newline"
                    s = pl[:-2]
                    # Add to list
                    if s not in processList:
                        processList.append(s)
            processList = processList[-15:]
        elif platform.system() == "Windows":
            # Run shell cmd and pipe output for parsing
            for pl in str(subprocess.Popen(['tasklist'], stdout=subprocess.PIPE).communicate()[0]).split():
                # Extract all lines with ".exe" as our processes
                if pl.find(".exe") >= 0:
                    # Strip the extension
                    s = pl[2:-1]
                    # Add to list
                    if s not in processList:
                        processList.append(s)
        return processList