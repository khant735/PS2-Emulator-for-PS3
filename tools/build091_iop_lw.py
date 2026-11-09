#!/usr/bin/env python3
"""Build 091: IOP R3000 LW from RAM/BIOS ROM, with strict fault diagnostics."""
from pathlib import Path
r=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
h=r/"include/emu_core.h";c=r/"source/emu_core.cpp";u=r/"source/emu_ui.inc"
def patch(p,a,b):
 s=p.read_text()
 if s.count(a)!=1:raise RuntimeError(f"Build091 anchor {p.name}: {a[:90]!r} count={s.count(a)}")
 p.write_text(s.replace(a,b,1))
patch(h,"uint64_t iop_slti_executed;","uint64_t iop_slti_executed,iop_lw_reads;uint32_t iop_lw_va,iop_lw_pa,iop_lw_value,iop_lw_reject;")
patch(c,"iop_slti_executed=0;","iop_slti_executed=iop_lw_reads=0;iop_lw_va=iop_lw_pa=iop_lw_value=iop_lw_reject=0;")
patch(c,"else if(op==4||op==5){branch=true;",'''else if(op==35){ // R3000 LW: signed offset, aligned, ROM/RAM only
  uint32_t va=iop_gpr[rs]+(uint32_t)imm,pa=va;
  if(va>=0x80000000u&&va<0xc0000000u)pa=va&0x1fffffffu;
  iop_lw_va=va;iop_lw_pa=pa;
  if(va&3u){iop_lw_reject=1;snprintf(iop_stop_reason,sizeof(iop_stop_reason),"IOP LW unaligned PC=%08X VA=%08X",addr,va);iop_running=false;return false;}
  const unsigned char*src=NULL;
  if(pa<=IOP_RAM&&IOP_RAM-pa>=4u)src=iop_ram+pa;
  else if(pa>=0x1fc00000u&&pa-0x1fc00000u<=ROM&&ROM-(pa-0x1fc00000u)>=4u)src=rom+(pa-0x1fc00000u);
  if(!src){iop_lw_reject=2;snprintf(iop_stop_reason,sizeof(iop_stop_reason),"IOP LW unmapped PC=%08X VA=%08X",addr,va);iop_running=false;return false;}
  iop_gpr[rt]=le32(src);iop_lw_value=iop_gpr[rt];++iop_lw_reads;iop_lw_reject=0;
 }
 else if(op==4||op==5){branch=true;''')
patch(c,'fprintf(f,"BUILD 090 IOP SLTI:', '''fprintf(f,"BUILD 091 IOP LW: READS=%llu LAST_VA=%08X LAST_PA=%08X LAST_VALUE=%08X REJECT=%u (0=none 1=unaligned 2=unmapped; RAM/ROM only)\\n",
 (unsigned long long)iop_lw_reads,iop_lw_va,iop_lw_pa,iop_lw_value,iop_lw_reject);
 fprintf(f,"BUILD 090 IOP SLTI:''')
patch(u,"BUILD 090 - IOP SLTI","BUILD 091 - IOP LW")
print("Build 091 IOP LW applied")
