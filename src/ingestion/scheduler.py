"""Scheduler for polling email inbox."""
import logging
import signal
import sys
import time
from typing import Callable, Optional

import schedule

logger = logging.getLogger(__name__)


class EmailScheduler:
    """Schedule periodic email polling."""
    
    def __init__(self, poll_interval_minutes: int = 2):
        """Initialize scheduler.
        
        Args:
            poll_interval_minutes: Polling interval in minutes
        """
        self.poll_interval_minutes = poll_interval_minutes
        self._running = False
        self._setup_signal_handlers()
    
    def _setup_signal_handlers(self) -> None:
        """Setup signal handlers for graceful shutdown."""
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum: int, frame: Optional[object]) -> None:
        """Handle shutdown signals.
        
        Args:
            signum: Signal number
            frame: Current stack frame
        """
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self._running = False
    
    def start(self, job: Callable[[], None]) -> None:
        """Start the scheduler with the given job.
        
        Args:
            job: Function to execute periodically
        """
        logger.info(f"Starting scheduler with {self.poll_interval_minutes} minute interval")
        
        # Schedule the job
        schedule.every(self.poll_interval_minutes).minutes.do(job)
        
        # Run the job immediately on startup
        logger.info("Running initial poll...")
        try:
            job()
        except Exception as e:
            logger.error(f"Error during initial poll: {e}")
        
        # Start the polling loop
        self._running = True
        while self._running:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error in scheduler loop: {e}")
                # Continue running despite errors
        
        logger.info("Scheduler stopped")
        sys.exit(0)
