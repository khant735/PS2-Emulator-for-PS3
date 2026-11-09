#!/usr/bin/env python3
"""Build 099: diagnostic latch for IOP memory control 0x1F801008."""
from pathlib import Path
r=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
h=r/"include/emu_core.h";c=r/"source/emu_core.cpp";u=r/"source/emu_ui.inc"
def patch(p,a,b):
 s=p.read_text()
 if s.count(a)!=1:raise RuntimeError(f"Build099 anchor {p.name}: {a[:100]!r} count={s.count(a)}")
 p.write_text(s.replace(a,b,1))
patch(h,"uint64_t iop_mmio_2070_reads,iop_mmio_2070_writes;","uint64_t iop_memctrl_1008_reads,iop_memctrl_1008_writes;\n uint32_t iop_memctrl_1008_value,iop_memctrl_1008_last_pc,iop_memctrl_1008_last_value;\n uint64_t iop_mmio_2070_reads,iop_mmio_2070_writes;")
patch(c,"iop_mmio_2070_reads=iop_mmio_2070_writes=0;","iop_memctrl_1008_reads=iop_memctrl_1008_writes=0;\n iop_memctrl_1008_value=iop_memctrl_1008_last_pc=iop_memctrl_1008_last_value=0;\n iop_mmio_2070_reads=iop_mmio_2070_writes=0;")
patch(c,"if(pa==0x1f802070u){\n   iop_mmio_2070_value=iop_gpr[rt];","if(pa==0x1f801008u){\n   iop_memctrl_1008_value=iop_gpr[rt];\n   iop_memctrl_1008_last_pc=addr;iop_memctrl_1008_last_value=iop_gpr[rt];\n   ++iop_memctrl_1008_writes;\n  }else if(pa==0x1f802070u){\n   iop_mmio_2070_value=iop_gpr[rt];")
patch(c,"&&pa!=0x1f802070u){iop_ram[pa]","&&pa!=0x1f802070u&&pa!=0x1f801008u){iop_ram[pa]")
patch(c,"if(!src&&pa==0x1f802070u){","if(!src&&pa==0x1f801008u){\n    iop_gpr[rt]=iop_memctrl_1008_value;iop_lw_value=iop_gpr[rt];\n    ++iop_memctrl_1008_reads;++iop_lw_reads;iop_lw_reject=0;\n   }else if(!src&&pa==0x1f802070u){")
patch(c,'fprintf(f,"BUILD 098 IOP MMIO 2070:', '''fprintf(f,"BUILD 099 IOP MEMORY CONTROL 1008: WRITES=%llu READS=%llu LAST_PC=%08X LAST_VALUE=%08X CURRENT=%08X (diagnostic latch; timing effects not modeled)\\n",
 (unsigned long long)iop_memctrl_1008_writes,(unsigned long long)iop_memctrl_1008_reads,
 iop_memctrl_1008_last_pc,iop_memctrl_1008_last_value,iop_memctrl_1008_value);
 fprintf(f,"BUILD 098 IOP MMIO 2070:''')
patch(c,"(RAM and 1004/1010/101C/1020/2070 diagnostic MMIO; other MMIO rejected)","(RAM and 1004/1008/1010/101C/1020/2070 diagnostic MMIO; other MMIO rejected)")
patch(u,"BUILD 098 - IOP MMIO 2070","BUILD 099 - IOP MEMCTRL 1008")
print("Build 099 IOP memory-control 0x1F801008 diagnostic latch applied")
