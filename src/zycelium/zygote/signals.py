"""
Async signals for zygote.
"""
from async_signals.dispatcher import Signal

# Process signals
process_started = Signal()
process_stopped = Signal()

# Supervisor signals
supervisor_started = Signal()
supervisor_stopped = Signal()
supervisor_cancelled = Signal()

# Database signals
database_init = Signal()
