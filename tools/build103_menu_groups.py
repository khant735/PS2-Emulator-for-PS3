#!/usr/bin/env python3
"""Build 103: group existing diagnostics and BIOS selection under menus.
No fake save-state functionality: settings entries show accurate availability.
"""
from pathlib import Path
import re
p=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE/source/emu_ui.inc"
s=p.read_text()
def once(a,b):
 global s
 n=s.count(a)
 if n!=1:raise SystemExit("Build103 anchor count %d: %s"%(n,a[:100]))
 s=s.replace(a,b,1)
a=re.search(r'static const char\* home\[\]=\{[^;]+;',s)
if not a:raise SystemExit("home array missing")
once(a.group(0),'''static const char* home[]={"BOOT PS2 BIOS","SELECT PS2 ELF","LOAD SELECTED ELF","SELECT ELF FROM DISC","LOAD DISC BOOT ELF (SYSTEM.CNF)","SETTINGS","TESTS & DIAGNOSTICS","ABOUT / IMPLEMENTATION STATUS","EXIT TO XMB"};
static const char* diagnostics[]={"RUN ORIGINAL CPU TEST","RUN SYSTEM CPU TEST","CPU STATUS","MEMORY DETAILS","RUN UI TIMING TEST (60 FRAMES)","RUN TLB TEST","RUN 128-BIT TEST","RUN COP1 / SERIAL TEST","RUN DVE BUS TEST","RUN IOP RAM TEST","RUN IOP REGISTER TEST","RUN GIF CONTROL TEST","RUN GS RESET TEST"};
static const char* settings_extra[]={"MEMORY CARDS (CARD 1 / CARD 2)","SAVE STATES (NOT YET IMPLEMENTED)"};
static int submenu_parent=0;
static const int home_count=sizeof(home)/sizeof(home[0]);
static const int diagnostics_count=sizeof(diagnostics)/sizeof(diagnostics[0]);
static const int settings_count=10;''')
once('screen==5?"LEFT/RIGHT OR L1/R1: CPU RAM / GPU VRAM', 'screen==5?"LEFT/RIGHT OR L1/R1: CPU RAM / GPU VRAM') if False else None
once('screen==4?"IMPLEMENTATION STATUS":screen==5?"MEMORY DETAILS"', 'screen==4?"IMPLEMENTATION STATUS":screen==5?"MEMORY DETAILS":screen==6?"TESTS & DIAGNOSTICS"')
once('if(screen==0){int first=menu_sel>=rows?menu_sel-rows+1:0;for(int i=0;i<rows&&first+i<21;i++)row(i,home[first+i],first+i==menu_sel);}', '''if(screen==0||screen==6){const char**list=screen==0?home:diagnostics;
  int count=screen==0?home_count:diagnostics_count;
  int first=menu_sel>=rows?menu_sel-rows+1:0;
  for(int i=0;i<rows&&first+i<count;i++)row(i,list[first+i],first+i==menu_sel);
 }''')
once('if(screen==2){for(int i=0;i<8&&i<rows;i++){char b[1200];if(i<7)snprintf(b,sizeof(b),"%s: %s",slot_names[i],settings.path(i)[0]?base_name(settings.path(i)):"NOT SET");else snprintf(b,sizeof(b),"INSTRUCTIONS PER BATCH: %u",settings.batch);row(i,b,i==menu_sel);}}', '''if(screen==2){int first=menu_sel>=rows?menu_sel-rows+1:0;
  for(int i=0;i<rows&&first+i<settings_count;i++){int k=first+i;char b[1200];
   if(k<7)snprintf(b,sizeof(b),"%s: %s",slot_names[k],settings.path(k)[0]?base_name(settings.path(k)):"NOT SET");
   else if(k==7)snprintf(b,sizeof(b),"INSTRUCTIONS PER BATCH: %u",settings.batch);
   else snprintf(b,sizeof(b),"%s",settings_extra[k-8]);
   row(i,b,k==menu_sel);
  }}''')
a=re.search(r'if\(screen==0\)\{switch\(menu_sel\)\{.*?\}\}',s)
if not a:raise SystemExit("main switch missing")
once(a.group(0),'''if(screen==0){switch(menu_sel){
 case 0:load_guest(settings.bios,true);break;
 case 1:open_browser(1,0);break;
 case 2:load_guest(settings.elf,false);break;
 case 3:open_disc_browser();break;
 case 4:load_disc_boot();break;
 case 5:screen=2;menu_sel=0;break;
 case 6:screen=6;menu_sel=0;break;
 case 7:screen=4;break;
 case 8:running=0;break;
 }}
 else if(screen==6){switch(menu_sel){
 case 0:smoke();break;case 1:system_smoke();break;
 case 2:screen=3;break;case 3:screen=5;break;
 case 4:start_ui_test();break;case 5:tlb_smoke();break;
 case 6:quad_smoke();break;case 7:cop1_smoke();break;
 case 8:dve_smoke();break;case 9:iop_ram_smoke();break;
 case 10:iop_register_smoke();break;case 11:gif_smoke();break;
 case 12:gs_smoke();break;
 }}''')
once('else if(screen==2){if(menu_sel<7)open_browser(menu_sel,2);else{settings.batch=settings.batch==1?100:settings.batch==100?1000:settings.batch==1000?10000:1;save_settings();}}','''else if(screen==2){if(menu_sel<7)open_browser(menu_sel,2);
 else if(menu_sel==7){settings.batch=settings.batch==1?100:settings.batch==100?1000:settings.batch==1000?10000:1;save_settings();}
 else if(menu_sel==8)notice("Card 1 / Card 2 paths are configurable above; emulation pending");
 else notice("Save-state integration pending; no restore available yet");
 }''')
once('if(screen==0||screen==2){int count=screen==0?21:8;', 'if(screen==0||screen==2||screen==6){int count=screen==0?home_count:screen==2?settings_count:diagnostics_count;')
once('else{screen=0;menu_sel=0;}}','else if(screen==2||screen==6){screen=0;menu_sel=0;}else{screen=0;menu_sel=0;}}')
# Browser return stays mapped to the existing settings slot.
p.write_text(s)
print("Build103: main menu reorganized; diagnostics submenu and settings entries installed")
