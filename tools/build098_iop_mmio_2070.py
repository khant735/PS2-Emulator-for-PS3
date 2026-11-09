#!/usr/bin/env python3
"""Build 098: isolated IOP 0x1F802070 diagnostic MMIO register; no invented device effects."""
from pathlib import Path
r=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
h=r/"include/emu_core.h";c=r/"source/emu_core.cpp";u=r/"source/emu_ui.inc"
def patch(p,a,b):
 s=p.read_text()
 if s.count(a)!=1:raise RuntimeError(f"Build098 anchor {p.name}: {a[:100]!r} count={s.count(a)}")
 p.write_text(s.replace(a,b,1))
patch(h,"uint64_t iop_memctrl_1004_reads,iop_memctrl_1004_writes;","uint64_t iop_memctrl_1004_reads,iop_memctrl_1004_writes;\n uint64_t iop_mmio_2070_reads,iop_mmio_2070_writes;\n uint32_t iop_mmio_2070_value,iop_mmio_2070_last_pc,iop_mmio_2070_last_value;")
patch(c,"iop_memctrl_1004_reads=iop_memctrl_1004_writes=0;","iop_memctrl_1004_reads=iop_memctrl_1004_writes=0;\n iop_mmio_2070_reads=iop_mmio_2070_writes=0;\n iop_mmio_2070_value=iop_mmio_2070_last_pc=iop_mmio_2070_last_value=0;")
patch(c,"if(pa==0x1f801004u){\n   iop_memctrl_1004_value=iop_gpr[rt];","if(pa==0x1f802070u){\n   iop_mmio_2070_value=iop_gpr[rt];\n   iop_mmio_2070_last_pc=addr;iop_mmio_2070_last_value=iop_gpr[rt];\n   ++iop_mmio_2070_writes;\n  }else if(pa==0x1f801004u){\n   iop_memctrl_1004_value=iop_gpr[rt];")
patch(c,"if(pa!=0x1f801010u&&pa!=0x1f801020u&&pa!=0x1f80101cu&&pa!=0x1f801004u){iop_ram[pa]","if(pa!=0x1f801010u&&pa!=0x1f801020u&&pa!=0x1f80101cu&&pa!=0x1f801004u&&pa!=0x1f802070u){iop_ram[pa]")
patch(c,"if(!src&&pa==0x1f801004u){","if(!src&&pa==0x1f802070u){\n    iop_gpr[rt]=iop_mmio_2070_value;iop_lw_value=iop_gpr[rt];\n    ++iop_mmio_2070_reads;++iop_lw_reads;iop_lw_reject=0;\n   }else if(!src&&pa==0x1f801004u){")
patch(c,'fprintf(f,"BUILD 097 IOP MEMORY CONTROL 1004:', '''fprintf(f,"BUILD 098 IOP MMIO 2070: WRITES=%llu READS=%llu LAST_PC=%08X LAST_VALUE=%08X CURRENT=%08X (diagnostic latch; hardware effects unimplemented)\n",
 (unsigned long long)iop_mmio_2070_writes,(unsigned long long)iop_mmio_2070_reads,
 iop_mmio_2070_last_pc,iop_mmio_2070_last_value,iop_mmio_2070_value);
 fprintf(f,"BUILD 097 IOP MEMORY CONTROL 1004:''')
patch(c,"(RAM and 1004/1010/101C/1020 diagnostic MMIO; other MMIO rejected)","(RAM and 1004/1010/101C/1020/2070 diagnostic MMIO; other MMIO rejected)")
patch(u,"BUILD 097 - IOP MEMCTRL 1004","BUILD 098 - IOP MMIO 2070")
print("Build 098 IOP 0x1F802070 isolated diagnostic register applied")
