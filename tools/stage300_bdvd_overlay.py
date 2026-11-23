#!/usr/bin/env python3
"""Stage 300: read-only BDVD diagnostic inside the existing PS2 Emulator UI."""
from pathlib import Path
import re
root=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
ui=root/"source/emu_ui.inc"
s=ui.read_text()
def once(a,b):
 global s
 n=s.count(a)
 if n!=1:raise SystemExit("Stage300 anchor mismatch "+str(n)+": "+a[:85])
 s=s.replace(a,b,1)
m=re.search(r'static const char\* diagnostics\[\]=\{[^;]+;',s)
if not m:raise SystemExit("Build103 diagnostics menu missing")
once(m.group(0),m.group(0).replace('"RUN GS RESET TEST"','"RUN GS RESET TEST","RUN READ-ONLY BDVD PROBE"'))
probe=r'''
/* Read-only optical-drive probe integrated into existing PS3 UI. */
static void bdvd_probe(){
 const char *dir="/dev_hdd0/game/BDVP00300/USRDIR/logs";
 const char *log="/dev_hdd0/game/BDVP00300/USRDIR/logs/bdvd-stage300.txt";
 mkdir(dir,0777);
 FILE *f=fopen(log,"wb");
 if(!f){char b[140];snprintf(b,sizeof(b),"BDVD: LOG CREATE FAILED errno=%d",errno);notice(b);return;}
 fprintf(f,"STAGE=300\nTITLE_ID=BDVP00300\nMODE=READ_ONLY\n");fflush(f);
 const char *paths[]={"/dev_bdvd","/dev_bdvd/PS3_DISC.SFB","/dev_bdvd/SYSTEM.CNF;1"};
 for(unsigned t=0;t<3;t++){
  int fd=-1,ret=sysLv2FsOpen(paths[t],SYS_O_RDONLY,&fd,0,NULL,0);
  fprintf(f,"PATH=%s OPEN=0x%08X\n",paths[t],(unsigned)ret);fflush(f);
  if(ret)continue;
  unsigned char sector[2048];unsigned n=(t==0?17:1),done=0;
  for(unsigned i=0;i<n;i++){
   uint64_t got=0;ret=sysLv2FsRead(fd,sector,sizeof(sector),&got);
   fprintf(f,"READ_INDEX=%u RET=0x%08X BYTES=%llu\n",i,(unsigned)ret,(unsigned long long)got);fflush(f);
   if(ret||got!=2048)break;
   done++;
   if(t==0&&i==16){
    int valid=sector[0]==1&&memcmp(sector+1,"CD001",5)==0&&sector[6]==1;
    fprintf(f,"ISO9660_PVD=%d\n",valid);fflush(f);
   }
  }
  fprintf(f,"SECTORS_READ=%u CLOSE=0x%08X\n",done,(unsigned)sysLv2FsClose(fd));fflush(f);
 }
 int ok=!ferror(f);if(fflush(f))ok=0;if(fclose(f))ok=0;
 notice(ok?"BDVD PROBE: REPORT SAVED TO USRDIR/logs":"BDVD PROBE: REPORT WRITE FAILED");
}
'''
once('static void gif_smoke(){',probe+'\nstatic void gif_smoke(){')
once('case 12:gs_smoke();break;','case 12:gs_smoke();break;case 13:bdvd_probe();break;')
s='#include <sys/file.h>\n#include <errno.h>\n'+s
ui.write_text(s)
changed=[]
for p in root.rglob('*'):
 if not p.is_file():continue
 if p.suffix.lower() not in ('.c','.cpp','.h','.hpp','.inc','.xml','.txt','.ini','.mk','') and p.name!='Makefile':continue
 try:old=p.read_text()
 except UnicodeDecodeError:continue
 new=old.replace('P2E000001','BDVP00300')
 if old!=new:p.write_text(new);changed.append(str(p.relative_to(root)))
for p in root.rglob('*'):
 if p.is_file() and p.suffix.lower() in ('.c','.cpp','.h','.hpp','.inc','.xml','.txt','.ini'):
  try:t=p.read_text()
  except UnicodeDecodeError:continue
  if 'P2E000001' in t:raise SystemExit('Unisolated path: '+str(p))
makefile=root/"Makefile"
text_make=makefile.read_text()
import re as _re
text_make,n=_re.subn(r"(?m)^TITLE :=.*$", "TITLE := BDVD Stage300 Read-Only Probe", text_make)
if n!=1:raise SystemExit("Could not isolate XMB application title")
makefile.write_text(text_make)
print("Stage300 uses emulator UI and logging; isolated BDVP00300; modified",changed)
