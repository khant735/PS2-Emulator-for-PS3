#!/usr/bin/env python3
"""Build 128: isolated IOP MMIO 0x1F808250 diagnostic latch, no hardware effects."""
from pathlib import Path
r=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
h=r/"include/emu_core.h";c=r/"source/emu_core.cpp"
def patch(p,a,b):
 s=p.read_text()
 if s.count(a)!=1:raise SystemExit(f"Build128 anchor {p.name}: {a[:100]!r} count={s.count(a)}")
 p.write_text(s.replace(a,b,1))
patch(h,"uint64_t iop_mmio_8248_reads,iop_mmio_8248_writes;","uint64_t iop_mmio_8250_reads,iop_mmio_8250_writes;\n uint32_t iop_mmio_8250_value,iop_mmio_8250_last_pc,iop_mmio_8250_last_value;\n uint64_t iop_mmio_8248_reads,iop_mmio_8248_writes;")
patch(c,"iop_mmio_8248_reads=iop_mmio_8248_writes=0;","iop_mmio_8250_reads=iop_mmio_8250_writes=0;\n iop_mmio_8250_value=iop_mmio_8250_last_pc=iop_mmio_8250_last_value=0;\n iop_mmio_8248_reads=iop_mmio_8248_writes=0;")
patch(c,"if(pa==0x1f808248u){\n   iop_mmio_8248_value=iop_gpr[rt];","if(pa==0x1f808250u){\n   iop_mmio_8250_value=iop_gpr[rt];\n   iop_mmio_8250_last_pc=addr;iop_mmio_8250_last_value=iop_gpr[rt];\n   ++iop_mmio_8250_writes;\n  }else if(pa==0x1f808248u){\n   iop_mmio_8248_value=iop_gpr[rt];")
patch(c,"&&pa!=0x1f808240u&&pa!=0x1f808248u){iop_ram[pa]","&&pa!=0x1f808240u&&pa!=0x1f808248u&&pa!=0x1f808250u){iop_ram[pa]")
patch(c,"if(!src&&pa==0x1f808248u){","if(!src&&pa==0x1f808250u){\n    iop_gpr[rt]=iop_mmio_8250_value;iop_lw_value=iop_gpr[rt];\n    ++iop_mmio_8250_reads;++iop_lw_reads;iop_lw_reject=0;\n   }else if(!src&&pa==0x1f808248u){")
patch(c,'fprintf(f,"BUILD 127 IOP MMIO 8248:', '''fprintf(f,"BUILD 128 IOP MMIO 8250: WRITES=%llu READS=%llu LAST_PC=%08X LAST_VALUE=%08X CURRENT=%08X (unknown device; diagnostic latch only, no side effects)\\n",
 (unsigned long long)iop_mmio_8250_writes,(unsigned long long)iop_mmio_8250_reads,
 iop_mmio_8250_last_pc,iop_mmio_8250_last_value,iop_mmio_8250_value);
 fprintf(f,"BUILD 127 IOP MMIO 8248:''')
patch(c,"(RAM and 1000/1004/1008/100C/1010/1014/1018/101C/1020/10F0/2070/8268/8240/8248 diagnostic MMIO; other MMIO rejected)","(RAM and 1000/1004/1008/100C/1010/1014/1018/101C/1020/10F0/2070/8268/8240/8248/8250 diagnostic MMIO; other MMIO rejected)")
print("Build128: IOP 1F808250 diagnostic latch installed")
