#!/usr/bin/env python3
"""Build 117: bounded combined EE/IOP RAM and CPU diagnostic capture.
Caller must pause guest execution. This is NOT a complete save state.
"""
from pathlib import Path
root=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
h=root/"include/emu_core.h"
c=root/"source/emu_core.cpp"
def patch(path,old,new):
 s=path.read_text()
 if s.count(old)!=1:raise SystemExit("Build117 anchor mismatch "+str(path)+" "+repr(old))
 path.write_text(s.replace(old,new,1))
patch(h,"bool captureEeRam(void* destination,uint32_t bytes) const;",
"""bool captureEeRam(void* destination,uint32_t bytes) const;
 // Diagnostic snapshot only. Caller provides both 32 MiB and 2 MiB buffers.
 // Must be called while the guest is stopped. No restore path is exposed.
 bool captureCpuAndMainRam(EeCpuCheckpoint& ee,IopCpuCheckpoint& iop,
                           void* eeDestination,uint32_t eeBytes,
                           void* iopDestination,uint32_t iopBytes) const;""")
patch(c,"Core::Core():",
"""bool Core::captureCpuAndMainRam(EeCpuCheckpoint& ee,IopCpuCheckpoint& iop,
                                 void* eeDestination,uint32_t eeBytes,
                                 void* iopDestination,uint32_t iopBytes) const {
 // Validate all destinations before writing any output.
 if(!eeDestination||!iopDestination||
    eeBytes!=eeRamCheckpointBytes()||iopBytes!=iopRamCheckpointBytes())
  return false;
 // Caller is responsible for quiescing EE, IOP and all device activity.
 EeCpuCheckpoint e;IopCpuCheckpoint i;
 if(!captureEeCpu(e)||!captureIopCpu(i))return false;
 if(!validateEeCpuCheckpoint(e)||!validateIopCpuCheckpoint(i))return false;
 memcpy(eeDestination,ram,eeBytes);
 memcpy(iopDestination,iop_ram,iopBytes);
 ee=e;iop=i;
 return true;
}
Core::Core():""")
print("Build117: combined diagnostic CPU+main RAM capture; no restore")
