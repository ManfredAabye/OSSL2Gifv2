###
# threading_utils.py
# This file contains threading utilities for the OSSL2Gif application.
# Version 2.0.0 © 2026 by Manfred Zainhofer
###
import threading
import queue

# Globale Queue für Thread-Kommunikation
frame_queue = queue.Queue()
