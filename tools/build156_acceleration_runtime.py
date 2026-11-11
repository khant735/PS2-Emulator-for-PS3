#!/usr/bin/env python3
"""Build 156: interpreter-only runtime acceleration config.ini integration.
Do not change execution backends or existing UI navigation.
"""
from pathlib import Path
r=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
p=r/"source/emu_ui.inc"
s=p.read_text()
def patch(old,new):
 global s
 n=s.count(old)
 if n!=1:raise SystemExit(f"Build156 anchor count={n}: {old[:110]!r}")
 s=s.replace(old,new,1)
patch('static const char* config_file="/dev_hdd0/game/P2E000001/USRDIR/config.ini";',
'''#include "../../../tools/acceleration/acceleration_ini.h"
static const char* config_file="/dev_hdd0/game/P2E000001/USRDIR/config.ini";
static ps2accel::Config acceleration_config;
static void init_acceleration_config(){
 // Never overwrite an existing unsupported backend request; fail closed.
 if(ps2accel::ensure_ini(config_file)){
  ps2accel::Config requested;
  if(ps2accel::load_ini(config_file,requested))
   acceleration_config=ps2accel::resolve(requested,ps2accel::Capabilities());
 }
}''')
patch('mkdir(bios_dir,0777);mkdir(memcards_dir,0777);mkdir(sstates_dir,0777);',
'''mkdir(bios_dir,0777);mkdir(memcards_dir,0777);mkdir(sstates_dir,0777);
 init_acceleration_config();''')
p.write_text(s)
print("Build156: config.ini interpreter-only acceleration fields initialized without changing CPU execution")
