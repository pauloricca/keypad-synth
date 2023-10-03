import os
import platform
import subprocess
import threading

PLATFORM = platform.system()
TICK_AUDIO_FILE = 'tick.wav'

def __getSoundCommand():
    return 'aplay' if PLATFORM == 'Linux' else 'afplay'

def __playAudioFileSync(file):
    try: subprocess.call((__getSoundCommand(), file), stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
    except Exception as e: print('Error playing audio: ' + str(e))

def playTick():
    filePath = getAbsolutePath(TICK_AUDIO_FILE)
    t = threading.Thread(target=__playAudioFileSync, args=(filePath,), daemon=True)
    t.start()

def getAbsolutePath(relativePath: str):
    return os.path.join(os.path.dirname(__file__), relativePath)