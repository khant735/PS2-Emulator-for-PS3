#!/usr/bin/env python3
"""Build 125: isolated diagnostic capture for unknown IOP MMIO 0x1F808268.
No peripheral, IRQ, DMA, or SIF side effects are simulated.
"""
from pathlib import Path
r=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
h=r/"include/emu_core.h";c=r/"source/emu_core.cpp"
def patch(p,a,b):
 s=p.read_text()
 if s.count(a)!=1:raise SystemExit(f"Build125 anchor {p.name}: {a[:100]!r} count={s.count(a)}")
 p.write_text(s.replace(a,b,1))
patch(h,"uint64_t iop_memctrl_10f0_reads,iop_memctrl_10f0_writes;","uint64_t iop_mmio_8268_reads,iop_mmio_8268_writes;\n uint32_t iop_mmio_8268_value,iop_mmio_8268_last_pc,iop_mmio_8268_last_value;\n uint64_t iop_memctrl_10f0_reads,iop_memctrl_10f0_writes;")
patch(c,"iop_memctrl_10f0_reads=iop_memctrl_10f0_writes=0;","iop_mmio_8268_reads=iop_mmio_8268_writes=0;\n iop_mmio_8268_value=iop_mmio_8268_last_pc=iop_mmio_8268_last_value=0;\n iop_memctrl_10f0_reads=iop_memctrl_10f0_writes=0;")
patch(c,"if(pa==0x1f8010f0u){\n   iop_memctrl_10f0_value=iop_gpr[rt];","if(pa==0x1f808268u){\n   iop_mmio_8268_value=iop_gpr[rt];\n   iop_mmio_8268_last_pc=addr;iop_mmio_8268_last_value=iop_gpr[rt];\n   ++iop_mmio_8268_writes;\n  }else if(pa==0x1f8010f0u){\n   iop_memctrl_10f0_value=iop_gpr[rt];")
patch(c,"&&pa!=0x1f80100cu&&pa!=0x1f8010f0u){iop_ram[pa]","&&pa!=0x1f80100cu&&pa!=0x1f8010f0u&&pa!=0x1f808268u){iop_ram[pa]")
patch(c,"if(!src&&pa==0x1f8010f0u){","if(!src&&pa==0x1f808268u){\n    iop_gpr[rt]=iop_mmio_8268_value;iop_lw_value=iop_gpr[rt];\n    ++iop_mmio_8268_reads;++iop_lw_reads;iop_lw_reject=0;\n   }else if(!src&&pa==0x1f8010f0u){")
patch(c,'fprintf(f,"BUILD 124 IOP MEMORY CONTROL 10F0:', '''fprintf(f,"BUILD 125 IOP MMIO 8268: WRITES=%llu READS=%llu LAST_PC=%08X LAST_VALUE=%08X CURRENT=%08X (unknown device; diagnostic latch only, no side effects)\\n",
 (unsigned long long)iop_mmio_8268_writes,(unsigned long long)iop_mmio_8268_reads,
 iop_mmio_8268_last_pc,iop_mmio_8268_last_value,iop_mmio_8268_value);
 fprintf(f,"BUILD 124 IOP MEMORY CONTROL 10F0:''')
patch(c,"(RAM and 1000/1004/1008/100C/1010/1014/1018/101C/1020/10F0/2070 diagnostic MMIO; other MMIO rejected)","(RAM and 1000/1004/1008/100C/1010/1014/1018/101C/1020/10F0/2070/8268 diagnostic MMIO; other MMIO rejected)")
print("Build125: unknown IOP 1F808268 isolated diagnostic latch installed")
