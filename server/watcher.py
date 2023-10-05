import os
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from subprocess import Popen, PIPE

APP_SCRIPT = "main-page.py"

class FileChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith((".py", ".html")):
            print("Changes detected. Reloading the server...")
            os.system("pkill -f " + APP_SCRIPT)
            time.sleep(1)
            Popen(["python3", APP_SCRIPT], stdout=PIPE, stderr=PIPE)

print("Current working directory:", os.getcwd())


if __name__ == "__main__":
    event_handler = FileChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path=".", recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
