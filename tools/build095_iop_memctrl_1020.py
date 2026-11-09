#!/usr/bin/env python3
"""Build 095: model IOP memory-control 0x1F801020 with explicit read/write diagnostics."""
from pathlib import Path
r=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
h=r/"include/emu_core.h";c=r/"source/emu_core.cpp";u=r/"source/emu_ui.inc"
def patch(p,a,b):
 s=p.read_text()
 if s.count(a)!=1:raise RuntimeError(f"Build095 anchor {p.name}: {a[:100]!r} count={s.count(a)}")
 p.write_text(s.replace(a,b,1))
patch(h,"uint64_t iop_memctrl_writes;","uint64_t iop_memctrl_writes;\n uint64_t iop_memctrl_1020_reads,iop_memctrl_1020_writes;\n uint32_t iop_memctrl_1020_value,iop_memctrl_1020_last_pc,iop_memctrl_1020_last_value;")
patch(c,"iop_memctrl_writes=0;iop_memctrl_last_pc=iop_memctrl_last_value=0;","iop_memctrl_writes=0;iop_memctrl_last_pc=iop_memctrl_last_value=0;\n iop_memctrl_1020_reads=iop_memctrl_1020_writes=0;\n iop_memctrl_1020_value=iop_memctrl_1020_last_pc=iop_memctrl_1020_last_value=0;")
patch(c,"if(pa==0x1f801010u){\n   iop_dma_madr_value=iop_gpr[rt];","if(pa==0x1f801020u){\n   iop_memctrl_1020_value=iop_gpr[rt];\n   iop_memctrl_1020_last_pc=addr;iop_memctrl_1020_last_value=iop_gpr[rt];\n   ++iop_memctrl_1020_writes;\n  }else if(pa==0x1f801010u){\n   iop_dma_madr_value=iop_gpr[rt];")
patch(c,"if(pa!=0x1f801010u){iop_ram[pa]","if(pa!=0x1f801010u&&pa!=0x1f801020u){iop_ram[pa]")
patch(c,"if(!src&&pa==0x1f801010u){","if(!src&&pa==0x1f801020u){\n    iop_gpr[rt]=iop_memctrl_1020_value;iop_lw_value=iop_gpr[rt];\n    ++iop_memctrl_1020_reads;++iop_lw_reads;iop_lw_reject=0;\n   }else if(!src&&pa==0x1f801010u){")
patch(c,'fprintf(f,"BUILD 094 IOP MEMORY CONTROL:', '''fprintf(f,"BUILD 095 IOP MEMORY CONTROL 1020: WRITES=%llu READS=%llu LAST_PC=%08X LAST_VALUE=%08X CURRENT=%08X (diagnostic latch; timing effects not modeled)\\n",
 (unsigned long long)iop_memctrl_1020_writes,(unsigned long long)iop_memctrl_1020_reads,
 iop_memctrl_1020_last_pc,iop_memctrl_1020_last_value,iop_memctrl_1020_value);
 fprintf(f,"BUILD 094 IOP MEMORY CONTROL:''')
patch(u,"BUILD 094 - IOP MEMORY CONTROL","BUILD 095 - IOP MEMCTRL 1020")
print("Build 095 IOP memory-control 0x1F801020 diagnostic latch applied")
