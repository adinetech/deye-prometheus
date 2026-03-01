"""
inverter.py — PySolarmanV5 client: connects to the Deye data logger and reads registers.
"""
from pysolarmanv5 import PySolarmanV5
from config import (
    INVERTER_IP,
    INVERTER_SERIAL,
    INVERTER_PORT,
    INVERTER_MB_SLAVE_ID,
)

# Register blocks to read (start, end) — matches deye_hybrid.yaml requests section
REGISTER_BLOCKS = [
    (0x0003, 0x0070),
    (0x0096, 0x00F9),
    (0x00FA, 0x0117),
]

CHUNK_SIZE = 100  # max registers per Modbus request


class InverterClient:
    """Wraps PySolarmanV5 and provides a single read_all() snapshot."""

    def __init__(self):
        # We don't connect here anymore — we connect on every poll to avoid stale sockets
        pass

    def read_all(self) -> dict:
        """Connect, read all configured register blocks, disconnect, and return a merged dict."""
        inv = PySolarmanV5(
            INVERTER_IP,
            INVERTER_SERIAL,
            port=INVERTER_PORT,
            mb_slave_id=INVERTER_MB_SLAVE_ID,
        )
        
        regs = {}
        try:
            for start, end in REGISTER_BLOCKS:
                length = end - start + 1
                for offset in range(start, start + length, CHUNK_SIZE):
                    size = min(CHUNK_SIZE, start + length - offset)
                    values = inv.read_holding_registers(offset, size)
                    for i, val in enumerate(values):
                        regs[offset + i] = val
        finally:
            inv.disconnect()
            
        return regs
