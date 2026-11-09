#!/usr/bin/env python3
"""Build 116: bounded read-only EE RAM checkpoint capture.
The caller must pause guest execution to obtain a coherent snapshot.
No restore or save-state UI is enabled.
"""
from pathlib import Path
root=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
h=root/"include/emu_core.h"
c=root/"source/emu_core.cpp"
def patch(path,old,new):
 s=path.read_text()
 if s.count(old)!=1:raise SystemExit("Build116 anchor mismatch "+str(path)+" "+repr(old))
 path.write_text(s.replace(old,new,1))
patch(h,"bool captureIopRam(void* destination,uint32_t bytes) const;",
"""bool captureIopRam(void* destination,uint32_t bytes) const;
 static uint32_t eeRamCheckpointBytes(){return 33554432u;}
 bool captureEeRam(void* destination,uint32_t bytes) const;""")
patch(c,"Core::Core():",
"""bool Core::captureEeRam(void* destination,uint32_t bytes) const {
 if(!destination||bytes!=eeRamCheckpointBytes())return false;
 memcpy(destination,ram,bytes);
 return true;
}
Core::Core():""")
print("Build116: read-only 32 MiB EE RAM capture; no guest-state restore")
