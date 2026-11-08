#!/usr/bin/env python3
"""Build 071: diagnostic support for EE CACHE op 0x0C."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
def change(path,a,b):
 s=path.read_text()
 if s.count(a)!=1:raise SystemExit(f"Build 071 anchor mismatch {path}: {a[:100]!r} count={s.count(a)}")
 path.write_text(s.replace(a,b,1))
h=root/"include/emu_core.h"
change(h,"uint64_t cache_op14_count;","uint64_t cache_op0c_count;uint32_t cache_op0c_last_addr;uint64_t cache_op14_count;")
p=root/"source/emu_core.cpp"
change(p,"cache_op14_count=0;cache_op14_last_addr=0;","cache_op0c_count=0;cache_op0c_last_addr=0;cache_op14_count=0;cache_op14_last_addr=0;")
change(p,'if(rt!=7&&rt!=22&&rt!=20)return halt(UNSUPPORTED,"CACHE operation not implemented (IXIN/DXIN/op14 only)");','if(rt!=7&&rt!=22&&rt!=20&&rt!=12)return halt(UNSUPPORTED,"CACHE operation not implemented (IXIN/DXIN/op14/op0C only)");')
change(p,'if(rt==20){++cache_op14_count;cache_op14_last_addr=addr;}','if(rt==20){++cache_op14_count;cache_op14_last_addr=addr;}\n  if(rt==12){++cache_op0c_count;cache_op0c_last_addr=addr;}')
change(p,'fprintf(f,"EE CACHE op14', 'fprintf(f,"EE CACHE op0C (cacheless approximation): COUNT=%llu LAST_ADDR=%08X\\n",(unsigned long long)cache_op0c_count,cache_op0c_last_addr);\n fprintf(f,"EE CACHE op14')
change(root/"source/emu_ui.inc","BUILD 070 - EE CACHE OP14","BUILD 071 - EE CACHE OP0C")
print("Build 071 EE CACHE op0C applied")
