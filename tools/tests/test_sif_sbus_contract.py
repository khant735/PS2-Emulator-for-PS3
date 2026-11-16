#!/usr/bin/env python3
"""Isolated SBUS register semantics tests, not emulator integration tests.

Build 138 implements *separate* F220 and F230 register values. F220 sets bits
in F220; F230 clears bits in F230. They must not be conflated into one flag.
No IOP MMIO aliases, DMA, interrupt or handshake are asserted by this model.
"""
import unittest

F220 = 0x1000F220
F230 = 0x1000F230

class SbusEeRegisterModel:
    def __init__(self, f220=0, f230=0):
        self.values = {F220: f220 & 0xffffffff, F230: f230 & 0xffffffff}
        self.writes = []

    def read(self, addr):
        return self.values[addr]

    def write(self, addr, value):
        value &= 0xffffffff
        if addr == F220:
            self.values[addr] |= value
        elif addr == F230:
            self.values[addr] &= ~value & 0xffffffff
        else:
            raise ValueError("unknown register")
        self.writes.append((addr, value))

class SbusContractTests(unittest.TestCase):
    def test_reset(self):
        bus = SbusEeRegisterModel()
        self.assertEqual((bus.read(F220), bus.read(F230)), (0, 0))

    def test_f220_sets_only_its_own_bits(self):
        bus = SbusEeRegisterModel(f230=0xffffffff)
        bus.write(F220, 0x85)
        bus.write(F220, 0x30)
        self.assertEqual(bus.read(F220), 0xb5)
        self.assertEqual(bus.read(F230), 0xffffffff)

    def test_f230_clears_only_its_own_bits(self):
        bus = SbusEeRegisterModel(f220=0x7, f230=0xf5)
        bus.write(F230, 0x30)
        self.assertEqual(bus.read(F230), 0xc5)
        self.assertEqual(bus.read(F220), 0x7)

    def test_repeated_writes_idempotent(self):
        bus = SbusEeRegisterModel(f230=0xffffffff)
        for _ in range(2):
            bus.write(F220, 0x80000001)
            bus.write(F230, 0x80000000)
        self.assertEqual(bus.read(F220), 0x80000001)
        self.assertEqual(bus.read(F230), 0x7fffffff)

    def test_polling_does_not_create_ready_state(self):
        bus = SbusEeRegisterModel()
        for _ in range(1000):
            self.assertEqual(bus.read(F230), 0)
        self.assertEqual(bus.writes, [])

    def test_32bit_mask(self):
        bus = SbusEeRegisterModel(f230=0xffffffff)
        bus.write(F220, 0x100000001)
        bus.write(F230, 0x100000001)
        self.assertEqual(bus.read(F220), 1)
        self.assertEqual(bus.read(F230), 0xfffffffe)

if __name__ == "__main__":
    unittest.main(verbosity=2)
