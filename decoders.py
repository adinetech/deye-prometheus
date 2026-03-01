"""
decoders.py — Low-level register value decoders for Deye inverters.

Rules reference (from home_assistant_solarman by StephanJoubert):
  1 = unsigned 16-bit raw
  2 = signed 16-bit
  3 = unsigned 32-bit (two registers: lo, hi)
  4 = signed 32-bit   (two registers: lo, hi)
  5 = string (skip — returns None)
  6 = bitwise OR across multiple registers
  9 = same as rule 1 (used for time-of-use time slots)
"""


def s16(v: int) -> int:
    """Interpret a raw 16-bit register value as a signed integer."""
    return v - 65536 if v > 32767 else v


def s32(lo: int, hi: int) -> int:
    """Interpret two 16-bit registers as a signed 32-bit integer."""
    val = (hi << 16) | lo
    return val - 4_294_967_296 if val > 2_147_483_647 else val


def u32(lo: int, hi: int) -> int:
    """Interpret two 16-bit registers as an unsigned 32-bit integer."""
    return (hi << 16) | lo


def decode(param: dict, regs: dict) -> float | None:
    """
    Decode one parameter from a register snapshot.

    Args:
        param: A parameter definition dict (name, rule, registers, scale, offset, mask, isstr).
        regs:  Dict mapping register address (int) → raw value (int).

    Returns:
        Decoded float value, or None if the param is a string/unsupported type.
    """
    # String parameters can't be expressed as Prometheus gauges
    if param.get("isstr", False) or param.get("rule", 1) == 5:
        return None

    rule      = param.get("rule", 1)
    scale     = param.get("scale", 1)
    offset    = param.get("offset", 0)
    mask      = param.get("mask", None)
    registers = param["registers"]

    if rule == 1:
        val = regs.get(registers[0], 0)
    elif rule == 2:
        val = s16(regs.get(registers[0], 0))
    elif rule == 3:
        val = u32(regs.get(registers[0], 0), regs.get(registers[1], 0))
    elif rule == 4:
        val = s32(regs.get(registers[0], 0), regs.get(registers[1], 0))
    elif rule == 6:
        val = 0
        for r in registers:
            val |= regs.get(r, 0)
    elif rule == 9:
        val = regs.get(registers[0], 0)
    else:
        return None

    if mask is not None:
        val = val & mask

    return (val - offset) * scale
