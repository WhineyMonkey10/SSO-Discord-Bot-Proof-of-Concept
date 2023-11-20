import multiprocessing
import subprocess
import logging
import signal
import sys

def runBot():
    logging.info("Starting Discord bot...")
    try:
        subprocess.run(['python', 'bot.py'])
    except Exception as e:
        logging.error("Error in bot process: %s", e)

def runPanel():
    logging.info("Starting Flask server...")
    try:
        subprocess.run(['python', 'panel.py'])
    except Exception as e:
        logging.error("Error in panel process: %s", e)

def signal_handler(sig, frame):
    logging.info("Shutting down...")
    # Add any cleanup code here if necessary
    sys.exit(0)

if __name__ == '__main__':
    multiprocessing.freeze_support()

    logging.basicConfig(level=logging.INFO)
    signal.signal(signal.SIGINT, signal_handler)

    botProcess = multiprocessing.Process(target=runBot, daemon=True)
    panelProcess = multiprocessing.Process(target=runPanel, daemon=True)

    botProcess.start()
    panelProcess.start()

    botProcess.join()
    panelProcess.join()
