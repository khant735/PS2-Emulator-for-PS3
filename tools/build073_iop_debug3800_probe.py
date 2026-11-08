#!/usr/bin/env python3
"""Build 073: isolated unverified IOP debug-region 0x1F803800 read probe."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
def change(p,a,b):
 s=p.read_text()
 if s.count(a)!=1:raise SystemExit(f"Build 073 anchor mismatch {p}: {a[:90]!r} ({s.count(a)})")
 p.write_text(s.replace(a,b,1))
h=root/"include/emu_core.h"
change(h,"uint64_t serial_tx_total,serial_status_reads;","uint64_t iop_debug3800_reads;uint32_t iop_debug3800_last_pc;uint64_t serial_tx_total,serial_status_reads;")
p=root/"source/emu_core.cpp"
change(p,"serial_tx_total=serial_status_reads=0;","serial_tx_total=serial_status_reads=0;iop_debug3800_reads=0;iop_debug3800_last_pc=0;")
change(p,"// Exact unknown IOP probe only: compatibility value, not verified hardware.","""// EXPERIMENTAL: one exact IOP debug-region halfword read; zero is a
 // deliberately unverified compatibility value, NOT a hardware model.
 // All other widths and addresses continue through strict MMIO dispatch.
 if(size==2&&p==0x1f803800u){v=0;++iop_debug3800_reads;iop_debug3800_last_pc=pc;return true;}
 // Exact unknown IOP probe only: compatibility value, not verified hardware.""")
change(p,'fprintf(f,"EE BIOS 1F803800 probe:', 'fprintf(f,"IOP DEBUG 1F803800 EXPERIMENTAL HALFWORD ZERO: READS=%llu LAST_PC=%08X (unverified compatibility value; no peripheral emulation)\\n",(unsigned long long)iop_debug3800_reads,iop_debug3800_last_pc);\n fprintf(f,"EE BIOS 1F803800 probe:')
change(root/"source/emu_ui.inc","BUILD 072 - MMIO 3800 DIAG","BUILD 073 - IOP 3800 PROBE")
print("Build 073: exact 16-bit 1F803800 experimental zero read; unknown MMIO remains strict")
