#!/usr/bin/env python3
"""Build 119: capture EE timer register arrays, read-only.
These timers are currently diagnostic storage, not a running timer engine.
"""
from pathlib import Path
root=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
h=root/"include/emu_core.h";c=root/"source/emu_core.cpp"
def patch(p,old,new):
 s=p.read_text()
 if s.count(old)!=1:raise SystemExit("Build119 anchor mismatch "+str(p)+" "+repr(old))
 p.write_text(s.replace(old,new,1))
patch(h,"bool captureEeDmac(EeDmacCheckpoint& out) const;",
"""bool captureEeDmac(EeDmacCheckpoint& out) const;
 struct EeTimerCheckpoint {
  uint32_t version;
  uint32_t count[4],mode[4],compare[4],hold[4];
 };
 bool captureEeTimers(EeTimerCheckpoint& out) const;""")
patch(c,"Core::Core():",
"""bool Core::captureEeTimers(EeTimerCheckpoint& out) const {
 memset(&out,0,sizeof(out));
 out.version=1;
 memcpy(out.count,ee_timer_count,sizeof(out.count));
 memcpy(out.mode,ee_timer_mode,sizeof(out.mode));
 memcpy(out.compare,ee_timer_comp,sizeof(out.compare));
 memcpy(out.hold,ee_timer_hold,sizeof(out.hold));
 return true;
}
Core::Core():""")
print("Build119: EE timer register snapshot interface added, no restore")
