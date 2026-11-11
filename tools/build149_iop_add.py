#!/usr/bin/env python3
"""Build 149: enable R3000 ADD dispatch and detect signed overflow safely.
Overflow stops with an explicit diagnostic until COP0 exception delivery exists.
"""
from pathlib import Path
r=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
c=r/"source/emu_core.cpp"
h=r/"include/emu_core.h"
def patch(path,old,new):
 s=path.read_text()
 if s.count(old)!=1:raise SystemExit(f"Build149 anchor mismatch {path.name}: {old[:90]!r} ({s.count(old)})")
 path.write_text(s.replace(old,new,1))
patch(h,"uint64_t iop_jalr_count;", "uint64_t iop_add149_count,iop_add149_overflow;uint32_t iop_add149_pc,iop_add149_a,iop_add149_b,iop_add149_result;\n uint64_t iop_jalr_count;")
patch(c,"iop_jalr_count=0;", "iop_add149_count=iop_add149_overflow=0;iop_add149_pc=iop_add149_a=iop_add149_b=iop_add149_result=0;\n iop_jalr_count=0;")
patch(c,"fn==26||fn==27||fn==35||", "fn==26||fn==27||fn==32||fn==35||")
patch(c,"case 32: // ADD: overflow trapping still pending\n   case 33:iop_gpr[rd]=a+b;break;",
"""case 32:{ // ADD: 32-bit signed arithmetic, no C++ signed-overflow UB
     const uint32_t sum=a+b;
     iop_add149_pc=addr;iop_add149_a=a;iop_add149_b=b;iop_add149_result=sum;
     ++iop_add149_count;
     if(((~(a^b))&(a^sum)&0x80000000u)!=0){
       ++iop_add149_overflow;
       snprintf(iop_stop_reason,sizeof(iop_stop_reason),
        "IOP ADD overflow PC=%08X A=%08X B=%08X SUM=%08X (COP0 exception pending)",
        addr,a,b,sum);
       iop_running=false;return false;
     }
     if(rd)iop_gpr[rd]=sum;
     break;
   }
   case 33:iop_gpr[rd]=a+b;break;""")
patch(c,'fprintf(f,"BUILD 148 IOP JALR:', '''fprintf(f,"BUILD 149 IOP ADD: EXECUTED=%llu OVERFLOW=%llu LAST_PC=%08X A=%08X B=%08X RESULT=%08X (signed overflow detected; COP0 exception delivery pending)\\n",
 (unsigned long long)iop_add149_count,(unsigned long long)iop_add149_overflow,
 iop_add149_pc,iop_add149_a,iop_add149_b,iop_add149_result);
 fprintf(f,"BUILD 148 IOP JALR:''')
print("Build149: ADD dispatch enabled; signed overflow diagnostic installed")
