#!/usr/bin/env python3
"""Build 138: correct EE SBUS F220/F230 bitwise write semantics.

F220 sets bits, F230 clears bits (PCSX2 HwWrite.cpp).  This patch does NOT
pretend to implement IOP-visible SBUS, SIF DMA or interrupts.  Those require
a separate verified IOP bus bridge and are intentionally not fabricated.
"""
from pathlib import Path

root=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
core=root/"source/emu_core.cpp"
ui=root/"source/emu_ui.inc"

def replace_once(p, old, new):
    s=p.read_text()
    n=s.count(old)
    if n!=1:
        raise SystemExit(f"Build 138 anchor mismatch: {p.name}: {n} occurrences of {old[:85]!r}")
    p.write_text(s.replace(old,new,1))

# F220 is an atomic-style set-bits register, not an assignment latch.
replace_once(core,
    "ee_sif_f2xx[i]=uint32_t(v);++ee_sif_f2xx_writes[i];",
    """if(i==1u)ee_sif_f2xx[i]|=uint32_t(v); // SBUS_F220: set selected bits
  else ee_sif_f2xx[i]=uint32_t(v);       // SBUS_F200: ordinary store
  ++ee_sif_f2xx_writes[i];""")

# F230 clears selected bits of its own SBUS register; it does not store
# the mask directly. Keep all Build 085 polling counters untouched.
replace_once(core,
    "ee_sif_f230=uint32_t(v);++ee_sif_f230_writes;",
    """ee_sif_f230&=~uint32_t(v); // SBUS_F230: clear selected bits
  ++ee_sif_f230_writes;""")

replace_once(core,
    "EE SIF 1000F230 diagnostic latch (unverified reset value=0; no IOP effects)",
    "EE SIF 1000F230 bit-clear register (IOP sharing/DMA not yet modeled)")
replace_once(core,
    "EE SIF %08X diagnostic latch (no IOP/DMA effects)",
    "EE SIF %08X EE-side register (F220 bit-set; no IOP/DMA effects)")
# No UI banner anchor: Build 137 does not change the banner.
print("Build 138: EE F220 set-bits and F230 clear-bits installed; IOP bridge still pending")
