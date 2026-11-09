#!/usr/bin/env python3
"""Build 130: observe IOP 1F808244 boot-table write; diagnostic latch only."""
from pathlib import Path
r=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
h=r/"include/emu_core.h";c=r/"source/emu_core.cpp"
def patch(p,a,b):
 s=p.read_text()
 if s.count(a)!=1:raise SystemExit(f"Build130 anchor {p.name}: {a[:100]!r} count={s.count(a)}")
 p.write_text(s.replace(a,b,1))
patch(h,"uint64_t iop_mmio_8258_reads,iop_mmio_8258_writes;", """uint64_t iop_mmio_8244_reads,iop_mmio_8244_writes;
 uint32_t iop_mmio_8244_value,iop_mmio_8244_last_pc,iop_mmio_8244_last_value;
 uint64_t iop_mmio_8258_reads,iop_mmio_8258_writes;""")
patch(c,"iop_mmio_8258_reads=iop_mmio_8258_writes=0;", """iop_mmio_8244_reads=iop_mmio_8244_writes=0;
 iop_mmio_8244_value=iop_mmio_8244_last_pc=iop_mmio_8244_last_value=0;
 iop_mmio_8258_reads=iop_mmio_8258_writes=0;""")
patch(c,"if(pa==0x1f808258u){\n   iop_mmio_8258_value=iop_gpr[rt];", """if(pa==0x1f808244u){
   iop_mmio_8244_value=iop_gpr[rt];
   iop_mmio_8244_last_pc=addr;iop_mmio_8244_last_value=iop_gpr[rt];
   ++iop_mmio_8244_writes;
  }else if(pa==0x1f808258u){
   iop_mmio_8258_value=iop_gpr[rt];""")
patch(c,"&&pa!=0x1f808250u&&pa!=0x1f808258u){iop_ram[pa]","&&pa!=0x1f808250u&&pa!=0x1f808258u&&pa!=0x1f808244u){iop_ram[pa]")
patch(c,"if(!src&&pa==0x1f808258u){", """if(!src&&pa==0x1f808244u){
    iop_gpr[rt]=iop_mmio_8244_value;iop_lw_value=iop_gpr[rt];
    ++iop_mmio_8244_reads;++iop_lw_reads;iop_lw_reject=0;
   }else if(!src&&pa==0x1f808258u){""")
patch(c,'fprintf(f,"BUILD 129 IOP MMIO 8258:', '''fprintf(f,"BUILD 130 IOP MMIO 8244: WRITES=%llu READS=%llu LAST_PC=%08X LAST_VALUE=%08X CURRENT=%08X (diagnostic latch only; no hardware side effects)\\n",
 (unsigned long long)iop_mmio_8244_writes,(unsigned long long)iop_mmio_8244_reads,
 iop_mmio_8244_last_pc,iop_mmio_8244_last_value,iop_mmio_8244_value);
 fprintf(f,"BUILD 129 IOP MMIO 8258:''')
patch(c,"/8248/8250/8258 diagnostic MMIO; other MMIO rejected)","/8248/8250/8258/8244 diagnostic MMIO; other MMIO rejected)")
print("Build130: 1F808244 diagnostic latch installed")
