###
# threading_utils.py
# This file contains threading utilities for the OSSL2Gif application.
# Version 2.0.0 © 2026 by Manfred Zainhofer
###

import threading
import queue
import logging

# Logging-Konfiguration für Threads (optional, falls nicht global gesetzt)
logging.basicConfig(level=logging.INFO, format='[%(levelname)s][Thread] %(message)s')

# Globale Queue für Thread-Kommunikation
frame_queue = queue.Queue()
