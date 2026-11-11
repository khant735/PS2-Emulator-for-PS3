#!/usr/bin/env python3
"""Build 139: implement R3000A LB (opcode 0x20) with sign extension and strict memory bounds.

Observed BIOS IOP stop: BFC023A8 / 81100002 = LB s0,2(t0).
Only RAM and BIOS ROM are mapped. Unknown MMIO addresses fault explicitly.
"""
from pathlib import Path
root=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
h=root/"include/emu_core.h"
c=root/"source/emu_core.cpp"

def once(path,old,new):
    s=path.read_text()
    n=s.count(old)
    if n!=1:
        raise SystemExit(f"Build139 anchor {path.name}: count={n} {old[:95]!r}")
    path.write_text(s.replace(old,new,1))

once(h,"uint64_t iop_cachectrl_reads,iop_cachectrl_writes;",
"""uint64_t iop_lb_reads;
 uint32_t iop_lb_last_pc,iop_lb_last_va,iop_lb_last_pa,iop_lb_last_value,iop_lb_fault;
 uint64_t iop_cachectrl_reads,iop_cachectrl_writes;""")

once(c,"iop_cachectrl_reads=iop_cachectrl_writes=0;",
"""iop_lb_reads=0;
 iop_lb_last_pc=iop_lb_last_va=iop_lb_last_pa=iop_lb_last_value=iop_lb_fault=0;
 iop_cachectrl_reads=iop_cachectrl_writes=0;""")

once(c,"else if(op==40){ // R3000 SB: byte addressing, strict physical mapping",
"""else if(op==32){ // R3000 LB: signed 8-bit read, no alignment restriction
  const uint32_t va=iop_gpr[rs]+(uint32_t)imm;
  uint32_t pa=va;
  if(va>=0x80000000u&&va<0xc0000000u)pa=va&0x1fffffffu;
  iop_lb_last_pc=addr;iop_lb_last_va=va;iop_lb_last_pa=pa;
  const unsigned char* src=NULL;
  if(pa<IOP_RAM)src=iop_ram+pa;
  else if(pa>=0x1fc00000u && pa-0x1fc00000u<ROM)
   src=rom+(pa-0x1fc00000u);
  if(!src){
   iop_lb_fault=2;
   snprintf(iop_stop_reason,sizeof(iop_stop_reason),
    "IOP LB unmapped PC=%08X VA=%08X PA=%08X",addr,va,pa);
   iop_running=false;return false;
  }
  const int32_t signed_byte=(int32_t)(int8_t)(*src);
  iop_gpr[rt]=(uint32_t)signed_byte;
  iop_lb_last_value=iop_gpr[rt];++iop_lb_reads;iop_lb_fault=0;
 }
 else if(op==40){ // R3000 SB: byte addressing, strict physical mapping""")

once(c,'fprintf(f,"BUILD 136 IOP CACHECTRL',
'''fprintf(f,"BUILD 139 IOP LB: READS=%llu LAST_PC=%08X LAST_VA=%08X LAST_PA=%08X LAST_VALUE=%08X FAULT=%u (signed byte, RAM/BIOS ROM; MMIO unmapped)\\n",
 (unsigned long long)iop_lb_reads,iop_lb_last_pc,iop_lb_last_va,iop_lb_last_pa,iop_lb_last_value,iop_lb_fault);
 fprintf(f,"BUILD 136 IOP CACHECTRL''')
print("Build139: R3000A LB signed-byte RAM/ROM handling installed")
