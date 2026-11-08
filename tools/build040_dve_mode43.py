#!/usr/bin/env python3
"""Build 040: accept observed DVE mode 43 command 81 as a control phase, not fabricated data."""
from pathlib import Path
root=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
p=root/"include/ee_dve.h"
s=p.read_text()
old='if(mode==0x43){if((v&15)!=2||bus[8]>255)return false;current=bus[8];selected=true;device[current]=bus[9];known[current]=true;}'
new='''if(mode==0x43){
     if((v&15)==1){
      // BIOS issues 0x81 in mode 0x43. This is a control phase, not
      // a register-data write. Acknowledge the control latch only.
      // No device registers become known and no data is synthesized.
      selected=false;
     }else if((v&15)==2){
      if(bus[8]>255)return false;
      current=bus[8];selected=true;device[current]=bus[9];known[current]=true;
     }else return false;
    }'''
if s.count(old)!=1:raise SystemExit("DVE command pattern mismatch")
p.write_text(s.replace(old,new))
ui=root/"source/emu_ui.inc"
s=ui.read_text()
old="BUILD 039 - DVE FAULT DIAGNOSTICS"
if s.count(old)!=1:raise SystemExit("UI version pattern mismatch")
ui.write_text(s.replace(old,"BUILD 040 - DVE COMMAND 81"))
print("Build 040: mode 43 command 81 control-phase handling applied")
