#=============================================================
# Obfuscake 2
# By Sean Berwick (PressOK)
#
# eventprocessor.py:
# Pre-processing for captured events is handled here before
# being returned.
#=============================================================

from lib import keyboard, mouse

class EventProcessor:

    #==================================================================================
    # Takes a set of recorded events, processes them, and returns the processed events
    #==================================================================================
    def Process(self, recordedEvents):
        # Make sure we aren't overwriting the original events in case the processing
        # fails, so use a working copy of the events
        recordedEvents = recordedEvents.copy()

        #=========================================================================
        # Try passing the events through all of our processing methods one by one
        #
        if not self.ReduceMouseEvents(recordedEvents):
            return None
        #
        #=========================================================================

        # If we reach here, all processing was OK, we return the new events object
        return recordedEvents


    #==================================================================================
    # Remove bulk mouse.MoveEvents from the mouse event list which dramatically
    # reduces the filesize of saved events
    #==================================================================================
    def ReduceMouseEvents(self, recordedEvents):
        try:
            mEvents = recordedEvents["mouse"]
            mEventsCopy = []
            lastX = 0
            lastY = 0
            discardShortDistancePx = 100
            for me in mEvents:
                keep = False
                if isinstance(me, mouse.MoveEvent):
                    if mEvents.index(me) == 0 or mEvents.index(me) == len(mEvents)-1 or not isinstance(mEvents[(mEvents.index(me)+1)], mouse.MoveEvent):
                        keep = True
                    else:
                        distance = abs(me.x - lastX) + abs(me.y - lastY)
                        if distance > discardShortDistancePx:
                            keep = True
                else:
                    mEventsCopy.append(me)
                if keep:
                    mEventsCopy.append(me)
                    lastX = me.x
                    lastY = me.y
            recordedEvents["mouse"] = mEventsCopy
        except:
            print("Failed to reduce the number of mouse events!")
            return None
        return recordedEvents
