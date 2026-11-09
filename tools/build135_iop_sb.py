#!/usr/bin/env python3
"""Build 135: IOP R3000 SB instruction with strict RAM and observed 2070 byte-latch handling."""
from pathlib import Path
r=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
h=r/"include/emu_core.h"; c=r/"source/emu_core.cpp"
def patch(p,a,b):
 s=p.read_text()
 n=s.count(a)
 if n!=1: raise SystemExit(f"Build135 anchor count={n} {p.name}: {a[:110]!r}")
 p.write_text(s.replace(a,b,1))
patch(h,"uint64_t iop_mmio_2070_reads,iop_mmio_2070_writes;", """uint64_t iop_sb_writes,iop_sb_ram_writes,iop_sb_2070_writes;
 uint32_t iop_sb_last_pc,iop_sb_last_va,iop_sb_last_pa,iop_sb_last_value,iop_sb_reject;
 uint64_t iop_mmio_2070_reads,iop_mmio_2070_writes;""")
patch(c,"iop_mmio_2070_reads=iop_mmio_2070_writes=0;", """iop_sb_writes=iop_sb_ram_writes=iop_sb_2070_writes=0;
 iop_sb_last_pc=iop_sb_last_va=iop_sb_last_pa=iop_sb_last_value=iop_sb_reject=0;
 iop_mmio_2070_reads=iop_mmio_2070_writes=0;""")
patch(c,"else if(op==43){ // R3000 SW: validate alignment, physical mapping, and RAM bounds", """else if(op==40){ // R3000 SB: byte addressing, strict physical mapping
  uint32_t va=iop_gpr[rs]+(uint32_t)imm,pa=va;
  if(va>=0x80000000u&&va<0xc0000000u)pa=va&0x1fffffffu;
  uint32_t value=iop_gpr[rt]&255u;
  iop_sb_last_pc=addr;iop_sb_last_va=va;iop_sb_last_pa=pa;iop_sb_last_value=value;
  if(pa<IOP_RAM){
   iop_ram[pa]=(unsigned char)value;++iop_sb_ram_writes;
  }else if(pa==0x1f802070u){
   // Diagnostic latch only: preserve upper 24 bits; do not synthesize IRQ/DMA.
   iop_mmio_2070_value=(iop_mmio_2070_value&0xffffff00u)|value;
   iop_mmio_2070_last_pc=addr;iop_mmio_2070_last_value=iop_mmio_2070_value;
   ++iop_mmio_2070_writes;++iop_sb_2070_writes;
  }else{
   iop_sb_reject=2;
   snprintf(iop_stop_reason,sizeof(iop_stop_reason),"IOP SB unmapped PC=%08X VA=%08X PA=%08X",addr,va,pa);
   iop_running=false;return false;
  }
  ++iop_sb_writes;iop_sb_reject=0;
 }
 else if(op==43){ // R3000 SW: validate alignment, physical mapping, and RAM bounds""")
patch(c,'fprintf(f,"BUILD 134 IOP BOOT BANK:', '''fprintf(f,"BUILD 135 IOP SB: WRITES=%llu RAM=%llu MMIO_2070=%llu LAST_PC=%08X LAST_VA=%08X LAST_PA=%08X LAST_BYTE=%02X REJECT=%u (byte-store only; 2070 diagnostic latch; other MMIO rejected)\\n",
 (unsigned long long)iop_sb_writes,(unsigned long long)iop_sb_ram_writes,(unsigned long long)iop_sb_2070_writes,
 iop_sb_last_pc,iop_sb_last_va,iop_sb_last_pa,iop_sb_last_value,iop_sb_reject);
 fprintf(f,"BUILD 134 IOP BOOT BANK:''')
print("Build135: IOP SB RAM and observed MMIO 2070 byte-latch support installed")
