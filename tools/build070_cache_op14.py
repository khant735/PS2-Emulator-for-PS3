#!/usr/bin/env python3
"""Build 070: recognize EE CACHE op 0x14 in cacheless interpreter."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
def change(path,a,b):
 s=path.read_text()
 if s.count(a)!=1:raise SystemExit(f"Build 070 anchor mismatch {path}: {a[:100]!r} count={s.count(a)}")
 path.write_text(s.replace(a,b,1))
h=root/"include/emu_core.h"
change(h,"uint32_t fpu_control[32];","uint64_t cache_op14_count;uint32_t cache_op14_last_addr;uint32_t fpu_control[32];")
p=root/"source/emu_core.cpp"
change(p,"memset(fpu_control,0,sizeof(fpu_control));","cache_op14_count=0;cache_op14_last_addr=0;memset(fpu_control,0,sizeof(fpu_control));")
change(p,'if(rt!=7&&rt!=22)return halt(UNSUPPORTED,"CACHE operation not implemented (only IXIN/DXIN supported)");\n  // IXIN/DXIN invalidate by cache index, not a translated data address.\n  // This cacheless interpreter has no cached instructions or dirty data.', '''if(rt!=7&&rt!=22&&rt!=20)return halt(UNSUPPORTED,"CACHE operation not implemented (IXIN/DXIN/op14 only)");
  // Diagnostic cacheless approximation: no separate EE cache tags or dirty lines.
  // For op 0x14, record effective address but do not touch guest memory.
  if(rt==20){++cache_op14_count;cache_op14_last_addr=addr;}
  // Other accepted operations retain their previous no-op behavior.''')
change(p,'fprintf(f,"FPU COP1 control', 'fprintf(f,"EE CACHE op14 (cacheless approximation): COUNT=%llu LAST_ADDR=%08X\\n",(unsigned long long)cache_op14_count,cache_op14_last_addr);\n fprintf(f,"FPU COP1 control')
change(root/"source/emu_ui.inc","BUILD 069 - FPU CONTROL","BUILD 070 - EE CACHE OP14")
print("Build 070 EE CACHE op14 applied")
