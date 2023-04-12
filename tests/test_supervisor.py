"""
Test the supervisor.process module. 
"""
import time

from zycelium.zygote.supervisor import Process, Supervisor


def dummy_process() -> None:
    """
    A dummy process.
    """
    while True:
        time.sleep(1)


def test_process() -> None:
    """
    Test the start method.
    """
    process = Process("dummy", dummy_process)
    assert process.name == "dummy"
    process.start()
    assert process.is_alive()
    process.stop()
    process.join()
    assert not process.is_alive()


async def test_supervisor() -> None:
    """
    Test the supervisor.
    """
    supervisor = Supervisor()
    await supervisor.add_process("dummy", dummy_process)
    await supervisor.start()
    assert await supervisor.is_alive("dummy")
    await supervisor.stop()
    assert not await supervisor.is_alive("dummy")
