#!/usr/bin/env python3
"""Audit reconstructed Core source for real EE/IOP SIF integration.

This is a source-level guard, not proof of hardware emulation. It reports
unimplemented IOP aliases and refuses to treat EE diagnostic latches as
working cross-processor handshakes.
"""
import json
import re
import sys
from pathlib import Path

def audit(source):
    ee_read = source.split("bool Core::mmioRead(", 1)[1].split("bool Core::mmioWrite(", 1)[0]
    ee_write = source.split("bool Core::mmioWrite(", 1)[1].split("bool Core::", 1)[0]
    iop = source.split("bool Core::iopStep(", 1)[-1] if "bool Core::iopStep(" in source else source
    checks = {
        "ee_f220_bit_set": "ee_sif_f2xx[i]|=uint32_t(v)" in ee_write,
        "ee_f230_bit_clear": "ee_sif_f230&=~uint32_t(v)" in ee_write,
        "ee_f240_latch": "ee_sif_ctrl=uint32_t(v)" in ee_write,
        "ee_f230_poll_counters": "ee_sif_f230_zero_reads" in ee_read,
        "iop_sif_1d000000_literal": bool(re.search(r"0x1[dD]000[0-9a-fA-F]{3}[uU]?", iop)),
        "explicit_no_sif_side_effects": "no SIF, DMA or interrupt side effects" in source,
    }
    return checks

def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: audit_generated_sif.py <generated emu_core.cpp>")
    checks = audit(Path(sys.argv[1]).read_text())
    print(json.dumps(checks, indent=2, sort_keys=True))
    if not all(checks[k] for k in ("ee_f220_bit_set", "ee_f230_bit_clear",
                                   "ee_f240_latch", "ee_f230_poll_counters")):
        raise SystemExit("Expected existing EE SIF semantics missing")
    if not checks["iop_sif_1d000000_literal"]:
        print("GAP: no literal IOP 0x1D000xxx SIF register dispatch detected")
    print("NOTE: a source match is not a functional SIF/DMA/IRQ test")

if __name__ == "__main__":
    main()
