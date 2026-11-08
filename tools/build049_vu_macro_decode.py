#!/usr/bin/env python3
"""Build 049: isolate unimplemented VU macro opcode without fabricating state."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
def change(path,a,b):
 s=path.read_text()
 if s.count(a)!=1:raise SystemExit(f"Build 049 anchor mismatch {path}: {a[:90]!r} count={s.count(a)}")
 path.write_text(s.replace(a,b,1))
p=root/"source/emu_core.cpp"
change(p,'else return halt(UNSUPPORTED,"COP2 operation not implemented");',
'''else if(opcode==0x4BE0006Cu){
   // VU macro opcode encountered during VU1 initialization.
   // Deliberately halt: no fabricated vector result or state changes.
   return halt(UNSUPPORTED,"VU macro 4BE0006C: rs=31 rt=0 rd=0 sa=1 fn=2C; semantics pending verification");
  }
  else return halt(UNSUPPORTED,"COP2 operation not implemented");''')
change(root/"source/emu_ui.inc","BUILD 048 - VU0 QMFC2","BUILD 049 - VU MACRO DECODE")
print("Build 049 explicit VU macro diagnostic applied")
