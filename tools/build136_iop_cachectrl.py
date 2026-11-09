#!/usr/bin/env python3
"""Build 136: IOP cache-control MMIO at FFFE0130, with strict address matching.
The R3000 cache remains a cacheless interpreter; no invented cache timing.
"""
from pathlib import Path
import re
root=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
h=root/"include/emu_core.h";c=root/"source/emu_core.cpp"
def replace_once(path,old,new):
 s=path.read_text()
 if s.count(old)!=1:raise SystemExit(f"Build136 anchor {path.name} count={s.count(old)}: {old[:100]}")
 path.write_text(s.replace(old,new,1))
replace_once(h,"uint64_t iop_sb_writes,iop_sb_ram_writes,iop_sb_2070_writes;", """uint64_t iop_cachectrl_reads,iop_cachectrl_writes;
 uint32_t iop_cachectrl_value,iop_cachectrl_last_pc;
 uint64_t iop_sb_writes,iop_sb_ram_writes,iop_sb_2070_writes;""")
replace_once(c,"iop_sb_writes=iop_sb_ram_writes=iop_sb_2070_writes=0;", """iop_cachectrl_reads=iop_cachectrl_writes=0;
 iop_cachectrl_value=iop_cachectrl_last_pc=0;
 iop_sb_writes=iop_sb_ram_writes=iop_sb_2070_writes=0;""")
s=c.read_text()
# Intercept exactly the known hardware-control address ahead of existing SW/LW
# dispatch, preserving all earlier strict MMIO classification and counters.
for opcode,kind in ((43,"write"),(35,"read")):
 pattern=r'(else if\(op=='+str(opcode)+r'\)\{[^\n]*\n)'
 matches=list(re.finditer(pattern,s))
 if len(matches)!=1:raise SystemExit(f"Build136 {kind} opcode anchor count={len(matches)}")
 m=matches[0]
 if kind=="write":
  inject="""  if((iop_gpr[rs]+(uint32_t)imm)==0xfffe0130u){
   iop_cachectrl_value=iop_gpr[rt];iop_cachectrl_last_pc=addr;
   ++iop_cachectrl_writes;++iop_sw_writes;
  }else{
"""
 else:
  inject="""  if((iop_gpr[rs]+(uint32_t)imm)==0xfffe0130u){
   iop_gpr[rt]=iop_cachectrl_value;
   iop_lw_value=iop_gpr[rt];iop_lw_va=iop_lw_pa=0xfffe0130u;
   iop_lw_reject=0;++iop_lw_reads;++iop_cachectrl_reads;
  }else{
"""
 # Find matching brace for the opcode handler to close the newly introduced else.
 start=s.find('{',m.start(),m.end())
 depth=0;end=None
 for i in range(start,len(s)):
  if s[i]=='{':depth+=1
  elif s[i]=='}':
   depth-=1
   if depth==0:end=i;break
 if end is None:raise SystemExit("Build136 unmatched handler")
 s=s[:end]+" } // end cache-control alternate path\n"+s[end:]
 s=s[:m.end()]+inject+s[m.end():]
# insert diagnostic ahead of Build 135 report
anchor='fprintf(f,"BUILD 135 IOP SB:'
if s.count(anchor)!=1:raise SystemExit("Build136 trace anchor missing")
s=s.replace(anchor,'''fprintf(f,"BUILD 136 IOP CACHECTRL FFFE0130: WRITES=%llu READS=%llu VALUE=%08X LAST_PC=%08X (R3000 cache-control register; cache timing/isolation not yet modeled)\\n",
 (unsigned long long)iop_cachectrl_writes,(unsigned long long)iop_cachectrl_reads,iop_cachectrl_value,iop_cachectrl_last_pc);
 '''+anchor,1)
c.write_text(s)
print("Build136: strict FFFE0130 cache-control read/write dispatch installed")
