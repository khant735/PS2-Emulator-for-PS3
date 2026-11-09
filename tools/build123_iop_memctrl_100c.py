#!/usr/bin/env python3
"""Build 123: IOP 1F80100C diagnostic memory-control latch.
Capture guest writes/readbacks; no fabricated SIF acknowledgement or timing.
"""
from pathlib import Path
r=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
h=r/"include/emu_core.h";c=r/"source/emu_core.cpp"
def patch(path,old,new):
 s=path.read_text()
 if s.count(old)!=1:raise SystemExit(f"Build123 anchor {path.name}: {old[:95]!r} count={s.count(old)}")
 path.write_text(s.replace(old,new,1))
patch(h,"uint64_t iop_memctrl_1018_reads,iop_memctrl_1018_writes;","uint64_t iop_memctrl_100c_reads,iop_memctrl_100c_writes;\n uint32_t iop_memctrl_100c_value,iop_memctrl_100c_last_pc,iop_memctrl_100c_last_value;\n uint64_t iop_memctrl_1018_reads,iop_memctrl_1018_writes;")
patch(c,"iop_memctrl_1018_reads=iop_memctrl_1018_writes=0;","iop_memctrl_100c_reads=iop_memctrl_100c_writes=0;\n iop_memctrl_100c_value=iop_memctrl_100c_last_pc=iop_memctrl_100c_last_value=0;\n iop_memctrl_1018_reads=iop_memctrl_1018_writes=0;")
patch(c,"if(pa==0x1f801018u){\n   iop_memctrl_1018_value=iop_gpr[rt];","if(pa==0x1f80100cu){\n   iop_memctrl_100c_value=iop_gpr[rt];\n   iop_memctrl_100c_last_pc=addr;iop_memctrl_100c_last_value=iop_gpr[rt];\n   ++iop_memctrl_100c_writes;\n  }else if(pa==0x1f801018u){\n   iop_memctrl_1018_value=iop_gpr[rt];")
patch(c,"&&pa!=0x1f801014u&&pa!=0x1f801018u){iop_ram[pa]","&&pa!=0x1f801014u&&pa!=0x1f801018u&&pa!=0x1f80100cu){iop_ram[pa]")
patch(c,"if(!src&&pa==0x1f801018u){","if(!src&&pa==0x1f80100cu){\n    iop_gpr[rt]=iop_memctrl_100c_value;iop_lw_value=iop_gpr[rt];\n    ++iop_memctrl_100c_reads;++iop_lw_reads;iop_lw_reject=0;\n   }else if(!src&&pa==0x1f801018u){")
patch(c,'fprintf(f,"BUILD 122 IOP MEMORY CONTROL 1018:', '''fprintf(f,"BUILD 123 IOP MEMORY CONTROL 100C: WRITES=%llu READS=%llu LAST_PC=%08X LAST_VALUE=%08X CURRENT=%08X (diagnostic latch; timing effects not modeled)\\n",
 (unsigned long long)iop_memctrl_100c_writes,(unsigned long long)iop_memctrl_100c_reads,
 iop_memctrl_100c_last_pc,iop_memctrl_100c_last_value,iop_memctrl_100c_value);
 fprintf(f,"BUILD 122 IOP MEMORY CONTROL 1018:''')
patch(c,"(RAM and 1000/1004/1008/1010/1014/1018/101C/1020/2070 diagnostic MMIO; other MMIO rejected)","(RAM and 1000/1004/1008/100C/1010/1014/1018/101C/1020/2070 diagnostic MMIO; other MMIO rejected)")
print("Build123: IOP 1F80100C write/read capture installed")
