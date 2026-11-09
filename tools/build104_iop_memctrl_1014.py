#!/usr/bin/env python3
"""Build 104: IOP memory-controller 0x1F801014 diagnostic latch.
Captures actual guest writes; does not invent memory-controller timing or SIF handshakes.
"""
from pathlib import Path
r=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
h=r/"include/emu_core.h";c=r/"source/emu_core.cpp"
def patch(path,old,new):
 s=path.read_text()
 if s.count(old)!=1:raise SystemExit(f"Build104 anchor {path.name}: {old[:95]!r} count={s.count(old)}")
 path.write_text(s.replace(old,new,1))
patch(h,"uint64_t iop_memctrl_1000_reads,iop_memctrl_1000_writes;","uint64_t iop_memctrl_1014_reads,iop_memctrl_1014_writes;\n uint32_t iop_memctrl_1014_value,iop_memctrl_1014_last_pc,iop_memctrl_1014_last_value;\n uint64_t iop_memctrl_1000_reads,iop_memctrl_1000_writes;")
patch(c,"iop_memctrl_1000_reads=iop_memctrl_1000_writes=0;","iop_memctrl_1014_reads=iop_memctrl_1014_writes=0;\n iop_memctrl_1014_value=iop_memctrl_1014_last_pc=iop_memctrl_1014_last_value=0;\n iop_memctrl_1000_reads=iop_memctrl_1000_writes=0;")
patch(c,"if(pa==0x1f801000u){\n   iop_memctrl_1000_value=iop_gpr[rt];","if(pa==0x1f801014u){\n   iop_memctrl_1014_value=iop_gpr[rt];\n   iop_memctrl_1014_last_pc=addr;iop_memctrl_1014_last_value=iop_gpr[rt];\n   ++iop_memctrl_1014_writes;\n  }else if(pa==0x1f801000u){\n   iop_memctrl_1000_value=iop_gpr[rt];")
patch(c,"&&pa!=0x1f801008u&&pa!=0x1f801000u){iop_ram[pa]","&&pa!=0x1f801008u&&pa!=0x1f801000u&&pa!=0x1f801014u){iop_ram[pa]")
patch(c,"if(!src&&pa==0x1f801000u){","if(!src&&pa==0x1f801014u){\n    iop_gpr[rt]=iop_memctrl_1014_value;iop_lw_value=iop_gpr[rt];\n    ++iop_memctrl_1014_reads;++iop_lw_reads;iop_lw_reject=0;\n   }else if(!src&&pa==0x1f801000u){")
patch(c,'fprintf(f,"BUILD 100 IOP MEMORY CONTROL 1000:', '''fprintf(f,"BUILD 104 IOP MEMORY CONTROL 1014: WRITES=%llu READS=%llu LAST_PC=%08X LAST_VALUE=%08X CURRENT=%08X (diagnostic latch; timing effects not modeled)\\n",
 (unsigned long long)iop_memctrl_1014_writes,(unsigned long long)iop_memctrl_1014_reads,
 iop_memctrl_1014_last_pc,iop_memctrl_1014_last_value,iop_memctrl_1014_value);
 fprintf(f,"BUILD 100 IOP MEMORY CONTROL 1000:''')
patch(c,"(RAM and 1000/1004/1008/1010/101C/1020/2070 diagnostic MMIO; other MMIO rejected)","(RAM and 1000/1004/1008/1010/1014/101C/1020/2070 diagnostic MMIO; other MMIO rejected)")
print("Build104: IOP 1F801014 write/read capture installed")
