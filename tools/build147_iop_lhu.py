#!/usr/bin/env python3
"""Build 147: IOP R3000A LHU, zero-extended aligned halfword loads."""
from pathlib import Path
r=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
h=r/"include/emu_core.h";c=r/"source/emu_core.cpp"
def patch(p,a,b):
 s=p.read_text()
 if s.count(a)!=1:raise SystemExit(f"Build147 anchor mismatch {p.name}: {a[:90]!r} ({s.count(a)})")
 p.write_text(s.replace(a,b,1))
patch(h,"uint64_t iop_sh_writes,iop_sh_ram_writes,iop_sh_spu2_writes;", """uint64_t iop_lhu_reads,iop_lhu_ram_reads,iop_lhu_rom_reads,iop_lhu_spu2_reads;
 uint32_t iop_lhu_last_pc,iop_lhu_last_va,iop_lhu_last_pa,iop_lhu_last_value,iop_lhu_fault;
 uint64_t iop_sh_writes,iop_sh_ram_writes,iop_sh_spu2_writes;""")
patch(c,"iop_sh_writes=iop_sh_ram_writes=iop_sh_spu2_writes=0;", """iop_lhu_reads=iop_lhu_ram_reads=iop_lhu_rom_reads=iop_lhu_spu2_reads=0;
 iop_lhu_last_pc=iop_lhu_last_va=iop_lhu_last_pa=iop_lhu_last_value=iop_lhu_fault=0;
 iop_sh_writes=iop_sh_ram_writes=iop_sh_spu2_writes=0;""")
patch(c,"else if(op==33){ // R3000 LH: signed little-endian 16-bit read", """else if(op==37){ // R3000 LHU: zero-extended little-endian 16-bit read
  const uint32_t va=iop_gpr[rs]+(uint32_t)imm;
  uint32_t pa=va;
  if(va>=0x80000000u&&va<0xc0000000u)pa=va&0x1fffffffu;
  iop_lhu_last_pc=addr;iop_lhu_last_va=va;iop_lhu_last_pa=pa;
  if(va&1u){
   iop_lhu_fault=1;
   snprintf(iop_stop_reason,sizeof(iop_stop_reason),
    "IOP LHU unaligned PC=%08X VA=%08X",addr,va);
   iop_running=false;return false;
  }
  uint32_t value=0;
  if(pa<IOP_RAM && IOP_RAM-pa>=2u){
   value=(uint32_t)iop_ram[pa]|((uint32_t)iop_ram[pa+1]<<8);
   ++iop_lhu_ram_reads;
  }else if(pa>=0x1fc00000u && pa-0x1fc00000u<ROM &&
           ROM-(pa-0x1fc00000u)>=2u){
   const uint32_t off=pa-0x1fc00000u;
   value=(uint32_t)rom[off]|((uint32_t)rom[off+1]<<8);
   ++iop_lhu_rom_reads;
  }else if(pa>=0x1f801c00u && pa<=0x1f801ffeu){
   // Existing Build146 SPU2 register storage. No audio/IRQ/DMA emulation.
   value=iop_spu2_registers[(pa-0x1f801c00u)>>1];
   ++iop_lhu_spu2_reads;
  }else{
   iop_lhu_fault=2;
   snprintf(iop_stop_reason,sizeof(iop_stop_reason),
    "IOP LHU unmapped PC=%08X VA=%08X PA=%08X",addr,va,pa);
   iop_running=false;return false;
  }
  iop_gpr[rt]=value;
  iop_lhu_last_value=value;++iop_lhu_reads;iop_lhu_fault=0;
 }
 else if(op==33){ // R3000 LH: signed little-endian 16-bit read""")
patch(c,'fprintf(f,"BUILD 146 IOP SH:', '''fprintf(f,"BUILD 147 IOP LHU: READS=%llu RAM=%llu ROM=%llu SPU2=%llu LAST_PC=%08X LAST_VA=%08X LAST_PA=%08X LAST_VALUE=%08X FAULT=%u (zero-extended little-endian halfword; strict mapping)\\n",
 (unsigned long long)iop_lhu_reads,(unsigned long long)iop_lhu_ram_reads,
 (unsigned long long)iop_lhu_rom_reads,(unsigned long long)iop_lhu_spu2_reads,
 iop_lhu_last_pc,iop_lhu_last_va,iop_lhu_last_pa,iop_lhu_last_value,iop_lhu_fault);
 fprintf(f,"BUILD 146 IOP SH:''')
print("Build147: IOP LHU installed")
