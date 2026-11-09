#!/usr/bin/env python3
"""Build 097: IOP memory-control 0x1F801004 diagnostic latch."""
from pathlib import Path
r=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
h=r/"include/emu_core.h";c=r/"source/emu_core.cpp";u=r/"source/emu_ui.inc"
def patch(p,a,b):
 s=p.read_text()
 if s.count(a)!=1:raise RuntimeError(f"Build097 anchor {p.name}: {a[:100]!r} count={s.count(a)}")
 p.write_text(s.replace(a,b,1))
patch(h,"uint64_t iop_memctrl_101c_reads,iop_memctrl_101c_writes;","uint64_t iop_memctrl_101c_reads,iop_memctrl_101c_writes;\n uint64_t iop_memctrl_1004_reads,iop_memctrl_1004_writes;\n uint32_t iop_memctrl_1004_value,iop_memctrl_1004_last_pc,iop_memctrl_1004_last_value;")
patch(c,"iop_memctrl_101c_reads=iop_memctrl_101c_writes=0;","iop_memctrl_101c_reads=iop_memctrl_101c_writes=0;\n iop_memctrl_1004_reads=iop_memctrl_1004_writes=0;\n iop_memctrl_1004_value=iop_memctrl_1004_last_pc=iop_memctrl_1004_last_value=0;")
patch(c,"if(pa==0x1f80101cu){\n   iop_memctrl_101c_value=iop_gpr[rt];","if(pa==0x1f801004u){\n   iop_memctrl_1004_value=iop_gpr[rt];\n   iop_memctrl_1004_last_pc=addr;iop_memctrl_1004_last_value=iop_gpr[rt];\n   ++iop_memctrl_1004_writes;\n  }else if(pa==0x1f80101cu){\n   iop_memctrl_101c_value=iop_gpr[rt];")
patch(c,"if(pa!=0x1f801010u&&pa!=0x1f801020u&&pa!=0x1f80101cu){iop_ram[pa]","if(pa!=0x1f801010u&&pa!=0x1f801020u&&pa!=0x1f80101cu&&pa!=0x1f801004u){iop_ram[pa]")
patch(c,"if(!src&&pa==0x1f80101cu){","if(!src&&pa==0x1f801004u){\n    iop_gpr[rt]=iop_memctrl_1004_value;iop_lw_value=iop_gpr[rt];\n    ++iop_memctrl_1004_reads;++iop_lw_reads;iop_lw_reject=0;\n   }else if(!src&&pa==0x1f80101cu){")
patch(c,'fprintf(f,"BUILD 096 IOP MEMORY CONTROL 101C:', '''fprintf(f,"BUILD 097 IOP MEMORY CONTROL 1004: WRITES=%llu READS=%llu LAST_PC=%08X LAST_VALUE=%08X CURRENT=%08X (diagnostic latch; timing effects not modeled)\\n",
 (unsigned long long)iop_memctrl_1004_writes,(unsigned long long)iop_memctrl_1004_reads,
 iop_memctrl_1004_last_pc,iop_memctrl_1004_last_value,iop_memctrl_1004_value);
 fprintf(f,"BUILD 096 IOP MEMORY CONTROL 101C:''')
patch(c,"(RAM and 1010/101C/1020 diagnostic MMIO; other MMIO rejected)","(RAM and 1004/1010/101C/1020 diagnostic MMIO; other MMIO rejected)")
patch(u,"BUILD 096 - IOP MEMCTRL 101C","BUILD 097 - IOP MEMCTRL 1004")
print("Build 097 IOP memory-control 0x1F801004 diagnostic latch applied")
