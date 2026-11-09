#!/usr/bin/env python3
"""Build 105: PS3 storage layout for BIOS, memory cards, save states.
Constrain BIOS and memory-card selections to their dedicated directories.
No claims of implemented PS2 card I/O or live save-state restoration.
"""
from pathlib import Path
p=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE/source/emu_ui.inc"
s=p.read_text()
def change(old,new):
 global s
 n=s.count(old)
 if n!=1:raise SystemExit(f"Build105 anchor count {n}: {old[:100]!r}")
 s=s.replace(old,new,1)
change('static const char* config_file="/dev_hdd0/game/P2E000001/USRDIR/config.ini";',
'''static const char* config_file="/dev_hdd0/game/P2E000001/USRDIR/config.ini";
static const char* bios_dir="/dev_hdd0/game/P2E000001/USRDIR/bios";
static const char* memcards_dir="/dev_hdd0/game/P2E000001/USRDIR/memcards";
static const char* sstates_dir="/dev_hdd0/game/P2E000001/USRDIR/sstates";
static bool within_dir(const char*path,const char*dir){
 size_t n=strlen(dir);return path&&strncmp(path,dir,n)==0&&path[n]=='/'&&path[n+1]!=0;
}''')
change('"CARD 1 (RESERVED)","CARD 2 (RESERVED)"','"CARD 1 (FILE)","CARD 2 (FILE)"')
change('if(!path_exists_dir(cwd))strcpy(cwd,"/dev_hdd0");refresh_fs();',
'''if(slot==0&&!within_dir(p,bios_dir))strcpy(cwd,bios_dir);
 if((slot==3||slot==4)&&!within_dir(p,memcards_dir))strcpy(cwd,memcards_dir);
 if(!path_exists_dir(cwd))strcpy(cwd,"/dev_hdd0");refresh_fs();''')
change('strcpy(settings.path(pick_slot),p);save_settings();screen=pick_return;',
'''if(pick_slot==0&&!within_dir(p,bios_dir)){notice("BIOS files must be in USRDIR/bios");return;}
 if((pick_slot==3||pick_slot==4)&&!within_dir(p,memcards_dir)){
  notice("Memory card files must be in USRDIR/memcards");return;
 }
 strcpy(settings.path(pick_slot),p);save_settings();screen=pick_return;''')
change('mkdir("/dev_hdd0/game/P2E000001",0777);mkdir(data_dir,0777);',
'''mkdir("/dev_hdd0/game/P2E000001",0777);mkdir(data_dir,0777);
 mkdir(bios_dir,0777);mkdir(memcards_dir,0777);mkdir(sstates_dir,0777);''')
p.write_text(s)
print("Build105: BIOS/card selection paths restricted; storage directories created")
