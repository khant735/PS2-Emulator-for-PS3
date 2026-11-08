#!/usr/bin/env python3
"""Build 037: automatic per-test reports, corrected IOP assertion and run summary."""
from pathlib import Path
p=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE/source/emu_ui.inc"
s=p.read_text()
def rep(a,b):
 global s
 if s.count(a)!=1: raise SystemExit("Expected one match, got %d: %s"%(s.count(a),a[:85]))
 s=s.replace(a,b,1)
rep('#include <sys/time.h>','#include <sys/time.h>\n#include <errno.h>')
rep('static void run_batch(unsigned n){',"""
static const char* active_report="cpu-manual";
static bool report_written=false;
static char test_result[160]="RUNNING";
static unsigned report_total=0,report_failed=0;
static bool save_test_report(const char*result){
 if(!core_loaded||!core)return false;
 mkdir("/dev_hdd0/game/P2E000001/USRDIR/logs",0777);
 char path[1200],sum[1200];
 snprintf(path,sizeof(path),"%s/logs/%s-trace.txt",data_dir,active_report);
 if(!core->writeReport(path,guest_label))return false;
 snprintf(sum,sizeof(sum),"%s/logs/test-summary.txt",data_dir);
 FILE*f=fopen(sum,"ab");
 if(!f){snprintf(core->report_error,sizeof(core->report_error),"Cannot append test-summary.txt");return false;}
 fprintf(f,"TEST=%s RESULT=%s STOP=%s PC=%08X OPCODE=%08X INSTRUCTIONS=%llu TRACE=%s\\n",
  active_report,result,core->reason(),core->pc,core->opcode,
  (unsigned long long)core->instructions,path);
 bool ok=!ferror(f);if(fflush(f))ok=false;if(fclose(f))ok=false;
 report_total++;if(!ok)report_failed++;
 return ok;
}
static void begin_test(const char*name){
 active_report=name;report_written=false;
 snprintf(test_result,sizeof(test_result),"STOPPED");
}
static void finish_test(bool ok,const char*pass,const char*fail){
 snprintf(test_result,sizeof(test_result),"%s",ok?"PASS":"FAIL");
 bool saved=save_test_report(test_result);report_written=saved;
 notice(saved?(ok?pass:fail):core->report_error);
}
static void run_batch(unsigned n){""")
rep('if(core->stop!=Core::NONE){auto_run=false;notice(core->reason());if(!log_stop())notice(core->report_error);}dirty=true;',"""if(core->stop!=Core::NONE){
  auto_run=false;
  if(!report_written){
   bool saved=save_test_report(test_result);
   report_written=saved;
   notice(saved?"TEST STOPPED - REPORT SAVED":core->report_error);
  }
 }dirty=true;""")
# Set active report after guest is loaded, before any execution.
rep('core_loaded=true;screen=3;cpu_page=0;notice(bios?', 'core_loaded=true;begin_test(bios?"bios":"elf");screen=3;cpu_page=0;notice(bios?')
# Each smoke gets a label before running and saves the final validated result.
labels={
 'smoke':'cpu-original','system_smoke':'cpu-system','tlb_smoke':'tlb',
 'quad_smoke':'128bit','cop1_smoke':'cop1-serial','dve_smoke':'dve-bus',
 'iop_ram_smoke':'iop-ram','iop_register_smoke':'iop-register',
 'gif_smoke':'gif-control','gs_smoke':'gs-reset'
}
import re
for func,label in labels.items():
 m=re.search(r'static void '+func+r'\(\)\{',s)
 if not m: raise SystemExit("Missing test "+func)
 start=m.end();end=s.find('\nstatic void ',start)
 if end<0: raise SystemExit("No end "+func)
 block=s[start:end]
 # Begin immediately before batch, so early loader errors do not generate bogus reports.
 if 'run_batch(100);' not in block: raise SystemExit("Missing batch "+func)
 block=block.replace('run_batch(100);','begin_test("'+label+'");run_batch(100);',1)
 # Prevent intermediate STOPPED report; final assertion owns report.
 block=block.replace('begin_test("'+label+'");run_batch(100);','begin_test("'+label+'");report_written=true;run_batch(100);report_written=false;',1)
 notice=re.search(r'notice\(ok\?(".*?"):(".*?")\);',block)
 if not notice: raise SystemExit("Missing PASS/FAIL notice "+func)
 block=block[:notice.start()]+'finish_test(ok,'+notice.group(1)+','+notice.group(2)+');'+block[notice.end():]
 s=s[:start]+block+s[end:]
rep('core->reg[5]==0x22a&&core->reg[6]==0x22a&&','core->reg[5]==0&&core->reg[6]==0x22a&&')
rep('core->iop_compat_latch[0]==0x22a&&core->iop_compat_latch[1]==0x22a','core->iop_compat_latch[0]==0&&core->iop_compat_latch[1]==0x22a')
# When returning from a manually stopped trace, capture a snapshot.
rep('if(press&CIRCLE){ui_test_remaining=0;auto_run=false;',"""if(press&CIRCLE){ui_test_remaining=0;
   if(screen==3&&core_loaded&&!report_written){report_written=save_test_report("MANUAL STOP");if(!report_written)notice(core->report_error);}
   auto_run=false;""")
# Fix on-screen build label and manual help.
rep('BUILD 035 - BIOS TRACE','BUILD 037 - AUTO REPORTS')
rep('SELECT SAVE  O BACK','AUTO SAVE  SELECT SNAPSHOT  O BACK')
p.write_text(s)
print("Build 037 automatic reporting patch applied")
