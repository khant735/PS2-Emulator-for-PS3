#!/usr/bin/env python3
"""Build 039: DVE fault classification, without changing unverified device semantics."""
from pathlib import Path
p=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE/source/emu_ui.inc"
s=p.read_text()
def rep(a,b):
 global s
 n=s.count(a)
 if n!=1:raise SystemExit("Expected exactly one match, got %d: %s"%(n,a[:100]))
 s=s.replace(a,b,1)
# This is intentionally diagnostics-only. Do not acknowledge unimplemented MMIO.
rep('static char last_report_path[1200]="";','''static char last_report_path[1200]="";
static bool bios_dve_fault=false;''')
rep(' active_report=name;report_written=false;report_attempted=false;report_run_start=ui_now_us();',' active_report=name;report_written=false;report_attempted=false;bios_dve_fault=false;report_run_start=ui_now_us();')
rep('  if(!report_written&&!report_attempted&&core->instructions>0){','''  if(!report_written&&!report_attempted&&core->instructions>0){
   // Known BIOS DVE fault signature. Capture it, never silently acknowledge.
   bios_dve_fault=(!strcmp(active_report,"bios")&&core->pc==0x80007D20u&&core->opcode==0xA4A20000u);
   if(bios_dve_fault)snprintf(test_result,sizeof(test_result),"DVE MMIO 16-BIT WRITE FAULT @ BA000000");''')
rep('BUILD 038 - UNIQUE AUTO REPORTS','BUILD 039 - DVE FAULT DIAGNOSTICS')
p.write_text(s)
print("Build 039 DVE fault classification applied (no unverified MMIO bypass)")
