#!/usr/bin/env python3
"""Build 134: consolidated IOP boot-table MMIO bank, bounded diagnostics.
Observed boot-table offsets only; no fabricated peripheral side effects.
"""
from pathlib import Path
r=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
h=r/"include/emu_core.h"
c=r/"source/emu_core.cpp"
def patch(p,a,b):
 s=p.read_text()
 n=s.count(a)
 if n!=1:raise SystemExit(f"Build134 anchor count={n} {p.name}: {a[:100]!r}")
 p.write_text(s.replace(a,b,1))
patch(h,"uint64_t iop_mmio_8254_reads,iop_mmio_8254_writes;", """uint64_t iop_mmio_825c_reads,iop_mmio_825c_writes;
 uint32_t iop_mmio_825c_value,iop_mmio_825c_last_pc,iop_mmio_825c_last_value;
 uint64_t iop_mmio_8254_reads,iop_mmio_8254_writes;""")
patch(c,"iop_mmio_8254_reads=iop_mmio_8254_writes=0;", """iop_mmio_825c_reads=iop_mmio_825c_writes=0;
 iop_mmio_825c_value=iop_mmio_825c_last_pc=iop_mmio_825c_last_value=0;
 iop_mmio_8254_reads=iop_mmio_8254_writes=0;""")
patch(c,"if(pa==0x1f808254u){\n   iop_mmio_8254_value=iop_gpr[rt];", """if(pa==0x1f80825cu){
   iop_mmio_825c_value=iop_gpr[rt];
   iop_mmio_825c_last_pc=addr;iop_mmio_825c_last_value=iop_gpr[rt];
   ++iop_mmio_825c_writes;
  }else if(pa==0x1f808254u){
   iop_mmio_8254_value=iop_gpr[rt];""")
patch(c,"if(!src&&pa==0x1f808254u){", """if(!src&&pa==0x1f80825cu){
    iop_gpr[rt]=iop_mmio_825c_value;iop_lw_value=iop_gpr[rt];
    ++iop_mmio_825c_reads;++iop_lw_reads;iop_lw_reject=0;
   }else if(!src&&pa==0x1f808254u){""")
patch(c,"(pa)==0x1f808258u || (pa)==0x1f808268u)", "(pa)==0x1f808258u || (pa)==0x1f80825cu || (pa)==0x1f808268u)")
patch(c,'fprintf(f,"BUILD 133 IOP BUS:', '''fprintf(f,"BUILD 134 IOP BOOT BANK: mapped observed offsets 8240,8244,8248,824C,8250,8254,8258,825C,8268; unknown offsets rejected; diagnostic storage only\\n");
 fprintf(f,"BUILD 134 IOP MMIO 825C: WRITES=%llu READS=%llu LAST_PC=%08X LAST_VALUE=%08X CURRENT=%08X (diagnostic latch only; no hardware side effects)\\n",
 (unsigned long long)iop_mmio_825c_writes,(unsigned long long)iop_mmio_825c_reads,
 iop_mmio_825c_last_pc,iop_mmio_825c_last_value,iop_mmio_825c_value);
 fprintf(f,"BUILD 133 IOP BUS:''')
patch(c,"/8244/824C/8254 diagnostic MMIO; other MMIO rejected)","/8244/824C/8254/825C diagnostic MMIO; other MMIO rejected)")
print("Build134: IOP boot bank extended to observed 825C with strict MMIO rejection")
