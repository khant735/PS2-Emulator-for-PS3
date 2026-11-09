#!/usr/bin/env python3
"""Build 100: diagnostic latch for IOP memory control 0x1F801000."""
from pathlib import Path
r=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
h=r/"include/emu_core.h";c=r/"source/emu_core.cpp";u=r/"source/emu_ui.inc"
def patch(p,a,b):
 s=p.read_text()
 if s.count(a)!=1:raise RuntimeError(f"Build100 anchor {p.name}: {a[:100]!r} count={s.count(a)}")
 p.write_text(s.replace(a,b,1))
patch(h,"uint64_t iop_memctrl_1008_reads,iop_memctrl_1008_writes;","uint64_t iop_memctrl_1000_reads,iop_memctrl_1000_writes;\n uint32_t iop_memctrl_1000_value,iop_memctrl_1000_last_pc,iop_memctrl_1000_last_value;\n uint64_t iop_memctrl_1008_reads,iop_memctrl_1008_writes;")
patch(c,"iop_memctrl_1008_reads=iop_memctrl_1008_writes=0;","iop_memctrl_1000_reads=iop_memctrl_1000_writes=0;\n iop_memctrl_1000_value=iop_memctrl_1000_last_pc=iop_memctrl_1000_last_value=0;\n iop_memctrl_1008_reads=iop_memctrl_1008_writes=0;")
patch(c,"if(pa==0x1f801008u){\n   iop_memctrl_1008_value=iop_gpr[rt];","if(pa==0x1f801000u){\n   iop_memctrl_1000_value=iop_gpr[rt];\n   iop_memctrl_1000_last_pc=addr;iop_memctrl_1000_last_value=iop_gpr[rt];\n   ++iop_memctrl_1000_writes;\n  }else if(pa==0x1f801008u){\n   iop_memctrl_1008_value=iop_gpr[rt];")
patch(c,"&&pa!=0x1f801008u){iop_ram[pa]","&&pa!=0x1f801008u&&pa!=0x1f801000u){iop_ram[pa]")
patch(c,"if(!src&&pa==0x1f801008u){","if(!src&&pa==0x1f801000u){\n    iop_gpr[rt]=iop_memctrl_1000_value;iop_lw_value=iop_gpr[rt];\n    ++iop_memctrl_1000_reads;++iop_lw_reads;iop_lw_reject=0;\n   }else if(!src&&pa==0x1f801008u){")
patch(c,'fprintf(f,"BUILD 099 IOP MEMORY CONTROL 1008:', '''fprintf(f,"BUILD 100 IOP MEMORY CONTROL 1000: WRITES=%llu READS=%llu LAST_PC=%08X LAST_VALUE=%08X CURRENT=%08X (diagnostic latch; timing effects not modeled)\\n",
 (unsigned long long)iop_memctrl_1000_writes,(unsigned long long)iop_memctrl_1000_reads,
 iop_memctrl_1000_last_pc,iop_memctrl_1000_last_value,iop_memctrl_1000_value);
 fprintf(f,"BUILD 099 IOP MEMORY CONTROL 1008:''')
patch(c,"(RAM and 1004/1010/101C/1020/2070 diagnostic MMIO; other MMIO rejected)","(RAM and 1000/1004/1008/1010/101C/1020/2070 diagnostic MMIO; other MMIO rejected)")
patch(u,"BUILD 099 - IOP MEMCTRL 1008","BUILD 100 - IOP MEMCTRL 1000")
print("Build 100 IOP memory-control 0x1F801000 diagnostic latch applied")
