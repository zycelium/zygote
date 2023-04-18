"""
Zygote Signals.
"""
from async_signals.dispatcher import Signal

# Database signals
database_started = Signal()
database_stopped = Signal()
