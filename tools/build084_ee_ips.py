#!/usr/bin/env python3
"""Build 084: real-time EE instructions/second and trace timing."""
from pathlib import Path
r=Path(__file__).resolve().parents[1]/'src/PS2-PS3-Bringup-035-SOURCE'
p=r/'source/emu_ui.inc'
s=p.read_text()
def change(a,b):
 global s
 if s.count(a)!=1:raise RuntimeError('Build 084 anchor mismatch '+repr(a[:90])+' count='+str(s.count(a)))
 s=s.replace(a,b,1)
change('static bool watchdog_bios=false;',"""static unsigned long long ips_start_us=0,ips_sample_us=0,ips_sample_count=0;
static unsigned long long ips_current=0,ips_peak=0,ips_elapsed_us=0;
static bool ips_started=false;
static void ips_reset(){
 ips_start_us=ips_sample_us=ui_now_us();
 ips_sample_count=0;ips_current=ips_peak=ips_elapsed_us=0;ips_started=true;
}
static void ips_update(){
 if(!ips_started||!core_loaded)return;
 unsigned long long now=ui_now_us();
 if(now<ips_start_us||now<ips_sample_us)return;
 ips_elapsed_us=now-ips_start_us;
 unsigned long long dt=now-ips_sample_us;
 if(dt>=1000000ull){
  unsigned long long count=(unsigned long long)core->instructions;
  unsigned long long delta=count>=ips_sample_count?count-ips_sample_count:0;
  ips_current=dt?delta*1000000ull/dt:0;
  if(ips_current>ips_peak)ips_peak=ips_current;
  ips_sample_count=count;ips_sample_us=now;
 }
}
static unsigned long long ips_average(){
 return ips_elapsed_us?((unsigned long long)core->instructions)*1000000ull/ips_elapsed_us:0;
}
static bool watchdog_bios=false;""")
change('static bool log_stop(){',"""static bool log_stop(){
 ips_update();""")
change('return core->writeReport(p,guest_label);',"""if(!core->writeReport(p,guest_label))return false;
 FILE*f=fopen(p,"ab");if(!f)return false;
 fprintf(f,"EE PERFORMANCE: RETIRED=%llu ELAPSED_US=%llu IPS_LATEST=%llu IPS_AVERAGE=%llu IPS_PEAK=%llu SAMPLE_PERIOD_US=1000000\\n",
  (unsigned long long)core->instructions,ips_elapsed_us,ips_current,ips_average(),ips_peak);
 bool ok=!ferror(f);if(fflush(f))ok=false;if(fclose(f))ok=false;return ok;""")

change('if(ok)watchdog_bios=bios;', 'if(ok){watchdog_bios=bios;ips_reset();}')


change('BUILD 083 - BIOS WATCHDOG','BUILD 084 - EE IPS COUNTER')
p.write_text(s)
print('Build 084 EE IPS overlay and trace metrics applied')
