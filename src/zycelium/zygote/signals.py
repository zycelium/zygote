"""
Async signals for zygote.
"""
from async_signals.dispatcher import Signal


process_started = Signal()
process_stopped = Signal()

supervisor_started = Signal()
supervisor_stopped = Signal()
supervisor_cancelled = Signal()
