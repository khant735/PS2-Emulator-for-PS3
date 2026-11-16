#!/usr/bin/env python3
"""SIF SBUS set/clear contract tests for the PS2 BIOS bring-up.

Standalone executable specification, NOT a test of the emulator's current
Core::mmioRead/mmioWrite.  Wire the real MMIO backend into these cases after
reconstructing the latest generated source.  No synthetic ready bits.
"""
import unittest

EE_F200 = 0x1000F200
EE_F210 = 0x1000F210
EE_F220 = 0x1000F220
EE_F230 = 0x1000F230

class SharedSbusModel:
    """Minimal shared-bit set/clear register model, not a full SIF device."""
    def __init__(self):
        self.flags = 0
        self.history = []

    def ee_write(self, address, value):
        value &= 0xffffffff
        if address == EE_F220:
            self.flags = (self.flags | value) & 0xffffffff
        elif address == EE_F230:
            self.flags = (self.flags & ~value) & 0xffffffff
        else:
            raise ValueError("not a modelled set/clear address")
        self.history.append((address, value, self.flags))

    def iop_read_shared_flags(self):
        # Logical shared state only: physical IOP MMIO alias needs verification.
        return self.flags

class SbusContractTests(unittest.TestCase):
    def test_reset(self):
        self.assertEqual(SharedSbusModel().iop_read_shared_flags(), 0)

    def test_set_visible_from_iop(self):
        bus = SharedSbusModel()
        bus.ee_write(EE_F220, 0x000000A5)
        self.assertEqual(bus.iop_read_shared_flags(), 0xA5)

    def test_clear_only_selected_bits(self):
        bus = SharedSbusModel()
        bus.ee_write(EE_F220, 0xF5)
        bus.ee_write(EE_F230, 0x30)
        self.assertEqual(bus.iop_read_shared_flags(), 0xC5)

    def test_repeated_set_and_clear_are_idempotent(self):
        bus = SharedSbusModel()
        bus.ee_write(EE_F220, 0x80000001)
        bus.ee_write(EE_F220, 0x80000001)
        self.assertEqual(bus.iop_read_shared_flags(), 0x80000001)
        bus.ee_write(EE_F230, 0x80000000)
        bus.ee_write(EE_F230, 0x80000000)
        self.assertEqual(bus.iop_read_shared_flags(), 1)

    def test_no_fabricated_handshake(self):
        bus = SharedSbusModel()
        for _ in range(1000):
            self.assertEqual(bus.iop_read_shared_flags(), 0)
        self.assertEqual(bus.history, [])

    def test_32bit_masking(self):
        bus = SharedSbusModel()
        bus.ee_write(EE_F220, 0x1_0000_0001)
        self.assertEqual(bus.iop_read_shared_flags(), 1)

if __name__ == "__main__":
    unittest.main(verbosity=2)
