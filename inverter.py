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
        self._inv = PySolarmanV5(
            INVERTER_IP,
            INVERTER_SERIAL,
            port=INVERTER_PORT,
            mb_slave_id=INVERTER_MB_SLAVE_ID,
        )

    def _read_block(self, start: int, end: int) -> dict:
        """Read a contiguous register block in chunks, returns {addr: value}."""
        length = end - start + 1
        result = {}
        for offset in range(start, start + length, CHUNK_SIZE):
            size = min(CHUNK_SIZE, start + length - offset)
            values = self._inv.read_holding_registers(offset, size)
            for i, val in enumerate(values):
                result[offset + i] = val
        return result

    def read_all(self) -> dict:
        """Read all configured register blocks and return a merged {addr: value} dict."""
        regs = {}
        for start, end in REGISTER_BLOCKS:
            regs.update(self._read_block(start, end))
        return regs
