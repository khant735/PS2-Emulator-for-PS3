#!/usr/bin/env python3
"""Build 096: IOP memory-control 0x1F80101C diagnostic latch and accurate reporting."""
from pathlib import Path
r=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
h=r/"include/emu_core.h";c=r/"source/emu_core.cpp";u=r/"source/emu_ui.inc"
def patch(p,a,b):
 s=p.read_text()
 if s.count(a)!=1:raise RuntimeError(f"Build096 anchor {p.name}: {a[:100]!r} count={s.count(a)}")
 p.write_text(s.replace(a,b,1))
patch(h,"uint64_t iop_memctrl_1020_reads,iop_memctrl_1020_writes;","uint64_t iop_memctrl_1020_reads,iop_memctrl_1020_writes;\n uint64_t iop_memctrl_101c_reads,iop_memctrl_101c_writes;\n uint32_t iop_memctrl_101c_value,iop_memctrl_101c_last_pc,iop_memctrl_101c_last_value;")
patch(c,"iop_memctrl_1020_reads=iop_memctrl_1020_writes=0;","iop_memctrl_1020_reads=iop_memctrl_1020_writes=0;\n iop_memctrl_101c_reads=iop_memctrl_101c_writes=0;\n iop_memctrl_101c_value=iop_memctrl_101c_last_pc=iop_memctrl_101c_last_value=0;")
patch(c,"if(pa==0x1f801020u){\n   iop_memctrl_1020_value=iop_gpr[rt];","if(pa==0x1f80101cu){\n   iop_memctrl_101c_value=iop_gpr[rt];\n   iop_memctrl_101c_last_pc=addr;iop_memctrl_101c_last_value=iop_gpr[rt];\n   ++iop_memctrl_101c_writes;\n  }else if(pa==0x1f801020u){\n   iop_memctrl_1020_value=iop_gpr[rt];")
patch(c,"if(pa!=0x1f801010u&&pa!=0x1f801020u){iop_ram[pa]","if(pa!=0x1f801010u&&pa!=0x1f801020u&&pa!=0x1f80101cu){iop_ram[pa]")
patch(c,"if(!src&&pa==0x1f801020u){","if(!src&&pa==0x1f80101cu){\n    iop_gpr[rt]=iop_memctrl_101c_value;iop_lw_value=iop_gpr[rt];\n    ++iop_memctrl_101c_reads;++iop_lw_reads;iop_lw_reject=0;\n   }else if(!src&&pa==0x1f801020u){")
patch(c,'fprintf(f,"BUILD 095 IOP MEMORY CONTROL 1020:', '''fprintf(f,"BUILD 096 IOP MEMORY CONTROL 101C: WRITES=%llu READS=%llu LAST_PC=%08X LAST_VALUE=%08X CURRENT=%08X (diagnostic latch; timing effects not modeled)\\n",
 (unsigned long long)iop_memctrl_101c_writes,(unsigned long long)iop_memctrl_101c_reads,
 iop_memctrl_101c_last_pc,iop_memctrl_101c_last_value,iop_memctrl_101c_value);
 fprintf(f,"BUILD 095 IOP MEMORY CONTROL 1020:''')
patch(c,"(provisional zero; memory timing effects unimplemented)","(diagnostic readback; memory timing effects unimplemented)")
patch(c,"(RAM only; MMIO rejected)","(RAM and 1010/101C/1020 diagnostic MMIO; other MMIO rejected)")
patch(c,"(0=none 1=unaligned 2=unmapped; RAM/ROM only)","(0=none 1=unaligned 2=unmapped; RAM/ROM and memory-control diagnostic MMIO)")
patch(u,"BUILD 095 - IOP MEMCTRL 1020","BUILD 096 - IOP MEMCTRL 101C")
print("Build 096 IOP memory-control 0x1F80101C diagnostic latch applied")
