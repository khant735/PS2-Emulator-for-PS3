#!/usr/bin/env python3
"""Build 146: IOP R3000 SH, strict RAM bounds and SPU2 halfword register bank."""
from pathlib import Path
r=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
h=r/"include/emu_core.h";c=r/"source/emu_core.cpp"
def patch(p,a,b):
 s=p.read_text()
 if s.count(a)!=1:raise SystemExit(f"Build146 anchor mismatch {p.name}: {a[:90]!r} ({s.count(a)})")
 p.write_text(s.replace(a,b,1))
patch(h,"uint64_t iop_post3_writes;", """uint16_t iop_spu2_registers[0x400];
 uint64_t iop_sh_writes,iop_sh_ram_writes,iop_sh_spu2_writes;
 uint32_t iop_sh_last_pc,iop_sh_last_va,iop_sh_last_pa,iop_sh_last_value,iop_sh_fault;
 uint64_t iop_post3_writes;""")
patch(c,"iop_post3_writes=0;", """memset(iop_spu2_registers,0,sizeof(iop_spu2_registers));
 iop_sh_writes=iop_sh_ram_writes=iop_sh_spu2_writes=0;
 iop_sh_last_pc=iop_sh_last_va=iop_sh_last_pa=iop_sh_last_value=iop_sh_fault=0;
 iop_post3_writes=0;""")
patch(c,"else if(op==43){ // R3000 SW: validate alignment, physical mapping, and RAM bounds", """else if(op==41){ // R3000 SH: aligned little-endian halfword store
  const uint32_t va=iop_gpr[rs]+(uint32_t)imm;
  uint32_t pa=va;
  if(va>=0x80000000u&&va<0xc0000000u)pa=va&0x1fffffffu;
  const uint32_t value=iop_gpr[rt]&0xffffu;
  iop_sh_last_pc=addr;iop_sh_last_va=va;iop_sh_last_pa=pa;iop_sh_last_value=value;
  if(va&1u){
   iop_sh_fault=1;
   snprintf(iop_stop_reason,sizeof(iop_stop_reason),"IOP SH unaligned PC=%08X VA=%08X",addr,va);
   iop_running=false;return false;
  }
  if(pa<IOP_RAM && IOP_RAM-pa>=2u){
   iop_ram[pa]=(unsigned char)value;
   iop_ram[pa+1]=(unsigned char)(value>>8);
   ++iop_sh_ram_writes;
  }else if(pa>=0x1f801c00u && pa<=0x1f801ffeu){
   // SPU2 register window, halfword-addressed. Storage-only initial model:
   // no sound generation, DMA, IRQ, or timing side effects.
   iop_spu2_registers[(pa-0x1f801c00u)>>1]=(uint16_t)value;
   ++iop_sh_spu2_writes;
  }else{
   iop_sh_fault=2;
   snprintf(iop_stop_reason,sizeof(iop_stop_reason),
    "IOP SH unmapped PC=%08X VA=%08X PA=%08X",addr,va,pa);
   iop_running=false;return false;
  }
  ++iop_sh_writes;iop_sh_fault=0;
 }
 else if(op==43){ // R3000 SW: validate alignment, physical mapping, and RAM bounds""")
patch(c,'fprintf(f,"BUILD 145 IOP POST3:', '''fprintf(f,"BUILD 146 IOP SH: WRITES=%llu RAM=%llu SPU2=%llu LAST_PC=%08X LAST_VA=%08X LAST_PA=%08X LAST_VALUE=%04X FAULT=%u (aligned little-endian; SPU2 storage-only, no sound/DMA/IRQ)\\n",
 (unsigned long long)iop_sh_writes,(unsigned long long)iop_sh_ram_writes,(unsigned long long)iop_sh_spu2_writes,
 iop_sh_last_pc,iop_sh_last_va,iop_sh_last_pa,iop_sh_last_value,iop_sh_fault);
 fprintf(f,"BUILD 145 IOP POST3:''')
print("Build146: IOP SH and bounded SPU2 register bank installed")
