#!/usr/bin/env python3
"""Build 145: documented PS2 IOP POST3 output at 0x1FA00000 (byte writes)."""
from pathlib import Path
r=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
h=r/"include/emu_core.h";c=r/"source/emu_core.cpp"
def patch(p,a,b):
 s=p.read_text()
 if s.count(a)!=1:raise SystemExit(f"Build145 anchor mismatch {p.name}: {a[:90]!r} ({s.count(a)})")
 p.write_text(s.replace(a,b,1))
patch(h,"uint64_t iop_1fa0_attempts;", "uint64_t iop_post3_writes;uint32_t iop_post3_value,iop_post3_last_pc;\n uint64_t iop_1fa0_attempts;")
patch(c,"iop_1fa0_attempts=0;", "iop_post3_writes=0;iop_post3_value=iop_post3_last_pc=0;\n iop_1fa0_attempts=0;")
patch(c,"}else{\n   if((pa&0xffff0000u)==0x1fa00000u){", """}else if(pa==0x1fa00000u){
   // PS2 POST3 external boot-status output: write-only byte diagnostic port.
   // No SIF, DMA or interrupt side effects.
   iop_post3_value=value;iop_post3_last_pc=addr;++iop_post3_writes;
  }else{
   if((pa&0xffff0000u)==0x1fa00000u){""")
patch(c,'fprintf(f,"BUILD 144 IOP 1FA0 ACCESS:', '''fprintf(f,"BUILD 145 IOP POST3: WRITES=%llu LAST_PC=%08X LAST_BYTE=%02X (PS2 POST3 boot-status output; no SIF/DMA/IRQ side effects)\\n",
 (unsigned long long)iop_post3_writes,iop_post3_last_pc,iop_post3_value);
 fprintf(f,"BUILD 144 IOP 1FA0 ACCESS:''')
print("Build145: documented PS2 IOP POST3 byte output mapped")
