import os
import sys 
import time

class Watcher(object):
    running = True
    refresh_delay_secs = 1

    # Constructor
    def __init__(self, watch_file, call_func_on_change=None):
        self._cached_stamp = 0
        self.filename = watch_file
        self.call_func_on_change = call_func_on_change

    # Look for changes
    def look(self):
        stamp = os.stat(self.filename).st_mtime
        if stamp != self._cached_stamp:
            self._cached_stamp = stamp
            # File has changed, so do something...
            print('File changed')
            if self.call_func_on_change is not None:
                self.call_func_on_change()

    # Keep watching in a loop        
    def watch(self):
        while self.running: 
            try: 
                # Look for changes
                time.sleep(self.refresh_delay_secs) 
                self.look() 
            except KeyboardInterrupt: 
                print('\nDone') 
                break 
            except FileNotFoundError:
                # Action on file not found
                pass
            except: 
                print('Unhandled error: %s' % sys.exc_info()[0])

watch_file = 'send.txt'

# Call this function each time a change happens
def custom_action():
    with open(watch_file) as f:
        data = f.read()
        print(data)

# watcher = Watcher(watch_file)  # simple
watcher = Watcher(watch_file, custom_action)  # also call custom action function
watcher.watch()  # start the watch going
