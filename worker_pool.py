###
# worker_pool.py
# Thread pool management for efficient worker thread handling in OSSL2Gif
# OSSL2Gif Version 2.0.0 © 2026 by Manfred Zainhofer
###

from typing import Callable, Optional, Any
from concurrent.futures import ThreadPoolExecutor, Future
import logging

logger = logging.getLogger(__name__)

class WorkerPool:
	"""
	Effiziente Thread-Pool für Worker-Tasks.
	Vermeidet ständiges Erstellen/Löschen von neuen Threads.
	
	Nutzung:
		pool = WorkerPool(max_workers=2)
		future = pool.submit(_process_gif_frame_worker, self, frame_idx, ...)
		# Später abfragen: future.result(timeout=0.1)  # Non-blocking
	"""
	
	def __init__(self, max_workers: int = 2):
		"""
		Args:
			max_workers: Maximale Anzahl gleichzeitiger Worker-Threads
		"""
		self.max_workers = max_workers
		self.executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="OSSL2Gif-Worker")
		self.active_futures: dict[str, Future] = {}
		logger.info(f"WorkerPool initialized with {max_workers} workers")
	
	def submit(self, task_name: str, func: Callable, *args: Any, **kwargs: Any) -> Future:
		"""
		Submittet eine Task zum Pool.
		
		Args:
			task_name: Eindeutiger Name für die Task (z.B. 'gif_frame_0', 'texture_preview')
			func: Die zu execagutierende Funktion
			*args, **kwargs: Argumente für die Funktion
		
		Returns:
			Future-Objekt zum Abfragen des Ergebnisses
		"""
		# Wenn bereits eine Task mit diesem Namen läuft, ignorieren (Rate-Limiting)
		if task_name in self.active_futures:
			existing = self.active_futures[task_name]
			if not existing.done():
				logger.debug(f"Task '{task_name}' already running, skipping")
				return existing
			else:
				# Task ist fertig, kann gelöscht werden
				del self.active_futures[task_name]
		
		future = self.executor.submit(func, *args, **kwargs)
		self.active_futures[task_name] = future
		logger.debug(f"Task '{task_name}' submitted to pool")
		
		# Cleanup wenn fertig
		def cleanup(f):
			if task_name in self.active_futures:
				del self.active_futures[task_name]
				logger.debug(f"Task '{task_name}' completed and cleaned up")
		
		future.add_done_callback(cleanup)
		return future
	
	def wait_all(self, timeout: Optional[float] = None) -> bool:
		"""
		Wartet darauf, dass alle aktiven Tasks fertig sind.
		
		Args:
			timeout: Maximalzeit zum Warten in Sekunden
		
		Returns:
			True wenn all Tasks fertig, False bei Timeout
		"""
		if not self.active_futures:
			return True
		
		try:
			from concurrent.futures import wait, ALL_COMPLETED
			futures = list(self.active_futures.values())
			done, not_done = wait(futures, timeout=timeout, return_when=ALL_COMPLETED)
			return len(not_done) == 0
		except Exception as e:
			logger.error(f"Error waiting for tasks: {e}", exc_info=False)
			return False
	
	def shutdown(self, wait: bool = True) -> None:
		"""
		Sauberer Shutdown des Pools.
		
		Args:
			wait: Wenn True, warten bis alle Tasks fertig sind
		"""
		logger.info(f"Shutting down WorkerPool (wait={wait})")
		self.executor.shutdown(wait=wait)
	
	def get_active_count(self) -> int:
		"""Returns number of currently active tasks"""
		return len([f for f in self.active_futures.values() if not f.done()])

# Global singleton instance
_pool_instance: Optional[WorkerPool] = None

def get_worker_pool(max_workers: int = 2) -> WorkerPool:
	"""Gibt die globale WorkerPool-Instanz zurück"""
	global _pool_instance
	if _pool_instance is None:
		_pool_instance = WorkerPool(max_workers=max_workers)
	return _pool_instance

def shutdown_worker_pool() -> None:
	"""Sauberer Shutdown des Worker Pools (beim Programmende)"""
	global _pool_instance
	if _pool_instance is not None:
		_pool_instance.shutdown(wait=True)
		_pool_instance = None
