#!/usr/bin/env python3
"""Build 038: preserve unique failure traces, avoid empty BIOS snapshots."""
from pathlib import Path
p=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE/source/emu_ui.inc"
s=p.read_text()
def rep(a,b):
 global s
 n=s.count(a)
 if n!=1: raise SystemExit("Expected one occurrence, found %d: %s"%(n,a[:110]))
 s=s.replace(a,b,1)
rep('static unsigned report_total=0,report_failed=0;',"""static unsigned report_total=0,report_failed=0;
static unsigned report_serial=0;
static unsigned long long report_run_start=0;
static bool report_attempted=false;
static char last_report_path[1200]="";""")
rep(' char path[1200],sum[1200];\n snprintf(path,sizeof(path),"%s/logs/%s-trace.txt",data_dir,active_report);\n if(!core->writeReport(path,guest_label))return false;',""" // Do not replace a real failure with an unexecuted or already captured BIOS session.
 if(core->instructions==0)return false;
 char path[1200],sum[1200],latest[1200];
 struct timeval tv;
 if(gettimeofday(&tv,NULL))return false;
 // Wall-clock timestamp plus per-process monotonic serial prevents collisions.
 unsigned serial=++report_serial;
 snprintf(path,sizeof(path),"%s/logs/%s-%llu-%06ld-%04u-trace.txt",
  data_dir,active_report,(unsigned long long)tv.tv_sec,(long)tv.tv_usec,serial);
 snprintf(latest,sizeof(latest),"%s/logs/%s-trace.txt",data_dir,active_report);
 if(!core->writeReport(path,guest_label))return false;
 // Keep the familiar per-test filename pointing at the latest completed run.
 // Never write this alias for an unexecuted session.
 if(!core->writeReport(latest,guest_label)){
  snprintf(core->report_error,sizeof(core->report_error),"Unique trace saved; latest alias failed");
 }
 snprintf(last_report_path,sizeof(last_report_path),"%s",path);""")
rep(' fprintf(f,"TEST=%s RESULT=%s STOP=%s PC=%08X OPCODE=%08X INSTRUCTIONS=%llu TRACE=%s\\n",\n  active_report,result,core->reason(),core->pc,core->opcode,\n  (unsigned long long)core->instructions,path);',""" fprintf(f,"TEST=%s RESULT=%s STOP=%s PC=%08X OPCODE=%08X INSTRUCTIONS=%llu TRACE=%s\\n",
  active_report,result,core->reason(),core->pc,core->opcode,
  (unsigned long long)core->instructions,path);""")
rep(' active_report=name;report_written=false;', ' active_report=name;report_written=false;report_attempted=false;report_run_start=ui_now_us();')
rep(' bool saved=save_test_report(test_result);report_written=saved;', ' report_attempted=true;bool saved=save_test_report(test_result);report_written=saved;')
rep('if(!report_written){\n   bool saved=save_test_report(test_result);', 'if(!report_written&&!report_attempted&&core->instructions>0){\n   report_attempted=true;bool saved=save_test_report(test_result);')
rep('if(screen==3&&core_loaded&&!report_written){report_written=save_test_report("MANUAL STOP");if(!report_written)notice(core->report_error);}', 'if(screen==3&&core_loaded&&!report_written&&!report_attempted&&core->instructions>0){report_attempted=true;report_written=save_test_report("MANUAL STOP");if(!report_written)notice(core->report_error);}')
rep('BUILD 037 - AUTO REPORTS','BUILD 038 - UNIQUE AUTO REPORTS')
# Keep the last-trace SELECT action for explicit snapshots only.
p.write_text(s)
print("Build 038: unique per-run traces; skip zero-instruction overwrite; once-only stop reports")
