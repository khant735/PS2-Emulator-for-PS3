#!/usr/bin/env python3
"""Build 143: R3000A LH signed halfword load from IOP RAM and BIOS ROM."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
h=root/"include/emu_core.h"
c=root/"source/emu_core.cpp"
def once(path,old,new):
 s=path.read_text()
 if s.count(old)!=1:raise SystemExit(f"Build143 anchor mismatch {path.name}: {old[:80]!r} count={s.count(old)}")
 path.write_text(s.replace(old,new,1))
once(h,"uint64_t iop_batch142_ops;","uint64_t iop_lh_reads;uint32_t iop_lh_last_pc,iop_lh_last_va,iop_lh_last_pa,iop_lh_last_value,iop_lh_fault;\n uint64_t iop_batch142_ops;")
once(c,"iop_batch142_ops=0;","iop_lh_reads=0;iop_lh_last_pc=iop_lh_last_va=iop_lh_last_pa=iop_lh_last_value=iop_lh_fault=0;\n iop_batch142_ops=0;")
anchor='else if(op==32){ // R3000 LB: signed 8-bit read, no alignment restriction'
block="""else if(op==33){ // R3000 LH: signed little-endian 16-bit read
  const uint32_t va=iop_gpr[rs]+(uint32_t)imm;
  uint32_t pa=va;
  if(va>=0x80000000u&&va<0xc0000000u)pa=va&0x1fffffffu;
  iop_lh_last_pc=addr;iop_lh_last_va=va;iop_lh_last_pa=pa;
  if(va&1u){
   iop_lh_fault=1;
   snprintf(iop_stop_reason,sizeof(iop_stop_reason),
    "IOP LH unaligned PC=%08X VA=%08X",addr,va);
   iop_running=false;return false;
  }
  const unsigned char* src=NULL;
  if(pa<IOP_RAM && IOP_RAM-pa>=2u)src=iop_ram+pa;
  else if(pa>=0x1fc00000u && pa-0x1fc00000u<ROM &&
          ROM-(pa-0x1fc00000u)>=2u)src=rom+(pa-0x1fc00000u);
  if(!src){
   iop_lh_fault=2;
   snprintf(iop_stop_reason,sizeof(iop_stop_reason),
    "IOP LH unmapped PC=%08X VA=%08X PA=%08X",addr,va,pa);
   iop_running=false;return false;
  }
  const uint16_t half=(uint16_t)src[0]|((uint16_t)src[1]<<8);
  iop_gpr[rt]=(uint32_t)(int32_t)(int16_t)half;
  iop_lh_last_value=iop_gpr[rt];++iop_lh_reads;iop_lh_fault=0;
 }
 """
once(c,anchor,block+anchor)
once(c,'fprintf(f,"BUILD 142 IOP ALU BATCH:', '''fprintf(f,"BUILD 143 IOP LH: READS=%llu LAST_PC=%08X LAST_VA=%08X LAST_PA=%08X LAST_VALUE=%08X FAULT=%u (signed little-endian halfword; RAM/BIOS ROM only)\\n",
 (unsigned long long)iop_lh_reads,iop_lh_last_pc,iop_lh_last_va,iop_lh_last_pa,iop_lh_last_value,iop_lh_fault);
 fprintf(f,"BUILD 142 IOP ALU BATCH:''')
print("Build143: IOP LH installed")
