#!/usr/bin/env python3
"""Build 140: observed IOP 0x1F801060 32-bit access diagnostic.

The BIOS writes 0x00002BBD at BFC023B0. Preserve the written value for
readback, but do not claim timing, bus configuration or SIF effects.
"""
from pathlib import Path
import re
root=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
h=root/"include/emu_core.h"
c=root/"source/emu_core.cpp"
def once(path,a,b):
 s=path.read_text()
 if s.count(a)!=1:raise SystemExit(f"Build140 anchor mismatch {path.name} count={s.count(a)}: {a[:100]!r}")
 path.write_text(s.replace(a,b,1))
once(h,"uint64_t iop_lb_reads;", """uint64_t iop_1060_reads,iop_1060_writes;
 uint32_t iop_1060_value,iop_1060_last_pc,iop_1060_last_write;
 uint64_t iop_lb_reads;""")
once(c,"iop_lb_reads=0;", """iop_1060_reads=iop_1060_writes=0;
 iop_1060_value=iop_1060_last_pc=iop_1060_last_write=0;
 iop_lb_reads=0;""")
s=c.read_text()
for op in (43,35):
 pattern=r'(else if\(op=='+str(op)+r'\)\{[^\n]*\n)'
 matches=list(re.finditer(pattern,s))
 if len(matches)!=1:raise SystemExit(f"Build140 op={op} handler count={len(matches)}")
 m=matches[0]
 start=s.find('{',m.start(),m.end())
 depth=0;end=None
 for i in range(start,len(s)):
  if s[i]=='{':depth+=1
  elif s[i]=='}':
   depth-=1
   if depth==0:end=i;break
 if end is None:raise SystemExit("Build140 unbalanced handler")
 if op==43:
  inject="""  const uint32_t b140_va=iop_gpr[rs]+(uint32_t)imm;
  const uint32_t b140_pa=(b140_va>=0x80000000u&&b140_va<0xc0000000u)?(b140_va&0x1fffffffu):b140_va;
  if(b140_pa==0x1f801060u){
   if((b140_va&3u)!=0u){
    snprintf(iop_stop_reason,sizeof(iop_stop_reason),"IOP SW unaligned 1060 PC=%08X VA=%08X",addr,b140_va);
    iop_running=false;return false;
   }
   iop_1060_value=iop_gpr[rt];iop_1060_last_write=iop_gpr[rt];
   iop_1060_last_pc=addr;++iop_1060_writes;++iop_sw_writes;
  }else{
"""
 else:
  inject="""  const uint32_t b140_va=iop_gpr[rs]+(uint32_t)imm;
  const uint32_t b140_pa=(b140_va>=0x80000000u&&b140_va<0xc0000000u)?(b140_va&0x1fffffffu):b140_va;
  if(b140_pa==0x1f801060u){
   if((b140_va&3u)!=0u){
    snprintf(iop_stop_reason,sizeof(iop_stop_reason),"IOP LW unaligned 1060 PC=%08X VA=%08X",addr,b140_va);
    iop_running=false;return false;
   }
   iop_gpr[rt]=iop_1060_value;iop_lw_value=iop_gpr[rt];
   iop_lw_va=b140_va;iop_lw_pa=b140_pa;iop_lw_reject=0;
   ++iop_1060_reads;++iop_lw_reads;
  }else{
"""
 s=s[:end]+" } // end Build140 IOP 1060 alternate path\n"+s[end:]
 s=s[:m.end()]+inject+s[m.end():]
anchor='fprintf(f,"BUILD 139 IOP LB:'
if s.count(anchor)!=1:raise SystemExit("Build140 trace anchor missing")
s=s.replace(anchor,'''fprintf(f,"BUILD 140 IOP 1F801060: WRITES=%llu READS=%llu LAST_PC=%08X LAST_WRITE=%08X VALUE=%08X (diagnostic readback only; hardware side effects not modeled)\\n",
 (unsigned long long)iop_1060_writes,(unsigned long long)iop_1060_reads,
 iop_1060_last_pc,iop_1060_last_write,iop_1060_value);
 '''+anchor,1)
c.write_text(s)
print("Build140: strict 1F801060 IOP SW/LW diagnostic mapping installed")
