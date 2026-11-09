#!/usr/bin/env python3
"""Build 114: add explicit checkpoint validation at the real Core API boundary.

Validation does not mutate the emulator or enable partial state restore.
"""
from pathlib import Path
root=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
h=root/"include/emu_core.h"
c=root/"source/emu_core.cpp"

def patch(path,old,new):
    src=path.read_text()
    if src.count(old)!=1:
        raise SystemExit("Build114 anchor mismatch: "+str(path)+" "+repr(old))
    path.write_text(src.replace(old,new,1))

patch(h,"bool captureIopCpu(IopCpuCheckpoint& out) const;",
"""bool captureIopCpu(IopCpuCheckpoint& out) const;
 // Validation only. A future complete-machine restore will apply these
 // checkpoints together with RAM, DMA, timers, and device state.
 static bool validateEeCpuCheckpoint(const EeCpuCheckpoint& in);
 static bool validateIopCpuCheckpoint(const IopCpuCheckpoint& in);""")

patch(c,"Core::Core():",
"""bool Core::validateEeCpuCheckpoint(const EeCpuCheckpoint& in) {
 // EE PC/next are 32-bit aligned MIPS instruction addresses.
 if(in.version!=1u || (in.pc&3u)!=0u || (in.next&3u)!=0u)return false;
 return true;
}
bool Core::validateIopCpuCheckpoint(const IopCpuCheckpoint& in) {
 if(in.version!=1u || (in.pc&3u)!=0u || (in.next&3u)!=0u)return false;
 if(in.running>1u || in.delay>1u || in.gpr[0]!=0u)return false;
 return true;
}
Core::Core():""")
print("Build114: Core EE/IOP checkpoint validation added; no partial restore enabled")
