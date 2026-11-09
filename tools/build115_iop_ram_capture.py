#!/usr/bin/env python3
"""Build 115: expose a bounded, read-only snapshot of actual emulated IOP RAM.
Does not mutate guest state or enable partial save-state restoration.
"""
from pathlib import Path
root=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
h=root/"include/emu_core.h"
c=root/"source/emu_core.cpp"
def patch(path,old,new):
 s=path.read_text()
 if s.count(old)!=1:raise SystemExit("Build115 anchor mismatch "+str(path)+" "+repr(old))
 path.write_text(s.replace(old,new,1))
patch(h,"static bool validateIopCpuCheckpoint(const IopCpuCheckpoint& in);",
"""static bool validateIopCpuCheckpoint(const IopCpuCheckpoint& in);
 // Caller owns destination buffer; no host pointers are serialized.
 static uint32_t iopRamCheckpointBytes(){return 2097152u;}
 bool captureIopRam(void* destination,uint32_t bytes) const;""")
patch(c,"Core::Core():",
"""bool Core::captureIopRam(void* destination,uint32_t bytes) const {
 if(!destination||bytes!=iopRamCheckpointBytes())return false;
 memcpy(destination,iop_ram,bytes);
 return true;
}
Core::Core():""")
print("Build115: read-only IOP RAM capture available; restore remains disabled")
