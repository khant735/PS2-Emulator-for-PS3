#!/usr/bin/env python3
"""Build 088: bounded IOP SW RAM writes, address diagnostics, register dump."""
from pathlib import Path
r=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
h=r/"include/emu_core.h";c=r/"source/emu_core.cpp";u=r/"source/emu_ui.inc"
def patch(p,a,b):
 s=p.read_text()
 if s.count(a)!=1:raise RuntimeError(f"Build088 anchor {p.name}: {a[:80]!r} count={s.count(a)}")
 p.write_text(s.replace(a,b,1))
patch(h,"uint64_t iop_instructions;bool iop_running,iop_delay;","uint64_t iop_instructions,iop_sw_writes;uint32_t iop_last_sw_va,iop_last_sw_pa,iop_last_sw_value;bool iop_running,iop_delay;")
patch(c,"iop_hi=iop_lo=iop_last_opcode=0;iop_instructions=0;","iop_hi=iop_lo=iop_last_opcode=0;iop_instructions=iop_sw_writes=0;iop_last_sw_va=iop_last_sw_pa=iop_last_sw_value=0;")
patch(c,"else if(op==15)iop_gpr[rt]=ins<<16;","""else if(op==43){ // R3000 SW: validate alignment, physical mapping, and RAM bounds
  uint32_t va=iop_gpr[rs]+(uint32_t)imm,pa=va;
  iop_last_sw_va=va;iop_last_sw_value=iop_gpr[rt];
  if(va>=0x80000000u&&va<0xc0000000u)pa=va&0x1fffffffu;
  iop_last_sw_pa=pa;
  if(va&3u){snprintf(iop_stop_reason,sizeof(iop_stop_reason),"IOP SW unaligned PC=%08X VA=%08X",addr,va);iop_running=false;return false;}
  if(pa>IOP_RAM||IOP_RAM-pa<4u){
   snprintf(iop_stop_reason,sizeof(iop_stop_reason),"IOP SW unmapped PC=%08X VA=%08X PA=%08X",addr,va,pa);
   iop_running=false;return false;
  }
  uint32_t value=iop_gpr[rt];
  iop_ram[pa]=(unsigned char)value;
  iop_ram[pa+1]=(unsigned char)(value>>8);
  iop_ram[pa+2]=(unsigned char)(value>>16);
  iop_ram[pa+3]=(unsigned char)(value>>24);
  ++iop_sw_writes;
 }
 else if(op==15)iop_gpr[rt]=ins<<16;""")
patch(c,'fprintf(f,"BUILD 087 IOP COP0:', '''fprintf(f,"BUILD 088 IOP SW: WRITES=%llu LAST_VA=%08X LAST_PA=%08X LAST_VALUE=%08X (RAM only; MMIO rejected)\\n",
 (unsigned long long)iop_sw_writes,iop_last_sw_va,iop_last_sw_pa,iop_last_sw_value);
 for(unsigned i=0;i<32;++i)fprintf(f,"IOP R%02u=%08X\\n",i,iop_gpr[i]);
 fprintf(f,"BUILD 087 IOP COP0:''')
patch(u,"BUILD 087 - IOP COP0","BUILD 088 - IOP SW DIAGNOSTICS")
print("Build 088 IOP SW patch applied")
