#!/usr/bin/env python3
"""Build 137: conservative adaptive SIF F230 poll watchdog.
Only fires for the observed no-response BIOS loop, not arbitrary repeated PCs.
The 30M hard safety cap remains intact.
"""
from pathlib import Path
r=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
h=r/"include/emu_core.h";c=r/"source/emu_core.cpp";u=r/"source/emu_ui.inc"
def once(p,a,b):
 s=p.read_text()
 if s.count(a)!=1:raise SystemExit(f"Build137 anchor {p.name} count={s.count(a)} {a[:90]}")
 p.write_text(s.replace(a,b,1))
once(h,"INSTRUCTION_LIMIT };","INSTRUCTION_LIMIT, ADAPTIVE_STALL };")
once(h,"bool stopAtInstructionLimit(uint64_t limit);","bool stopAtInstructionLimit(uint64_t limit);\n bool stopAtAdaptiveStall(const char* detail);")
once(c,'case INSTRUCTION_LIMIT:return "BIOS instruction limit reached";','case INSTRUCTION_LIMIT:return "BIOS instruction limit reached";case ADAPTIVE_STALL:return "Adaptive BIOS watchdog: no observed SIF progress";')
once(c,"bool Core::stopAtInstructionLimit(uint64_t limit){",'''bool Core::stopAtAdaptiveStall(const char* detail){return halt(ADAPTIVE_STALL,detail);}
bool Core::stopAtInstructionLimit(uint64_t limit){''')
once(u,"static bool log_stop(){",'''static uint64_t adaptive_last_retired=0,adaptive_last_zero=0,adaptive_last_iop=0;
static uint64_t adaptive_last_sif_writes=0;
static unsigned adaptive_inactive_windows=0;
static bool adaptive_watchdog_enabled=true;
static const uint64_t adaptive_window_instructions=1000000ull;
static const unsigned adaptive_confirm_windows=3;
static bool log_stop(){''')
once(u,"static void run_batch(unsigned n){",'''// Build 137: conservative observation of known F230 polling.  The IOP
// diagnostic interpreter does not yet provide functional SIF handshakes.
// No stall decision is made solely from repeated instruction addresses.
static void adaptive_reset(){
 adaptive_last_retired=adaptive_last_zero=adaptive_last_iop=adaptive_last_sif_writes=0;
 adaptive_inactive_windows=0;
}
static void adaptive_check(){
 if(!adaptive_watchdog_enabled||!watchdog_bios||core->stop!=Core::NONE)return;
 if(core->instructions-adaptive_last_retired<adaptive_window_instructions)return;
 const uint64_t zeros=core->ee_sif_f230_zero_reads;
 const uint64_t writes=core->ee_sif_f230_writes;
 const uint64_t iop=core->iop_instructions;
 const bool polling=core->ee_sif_f230_reads>1000 &&
    zeros>adaptive_last_zero+1000 &&
    core->ee_sif_f230_nonzero_reads==0;
 const bool iop_idle=(!core->iop_running && iop==adaptive_last_iop);
 const bool sif_idle=(writes==adaptive_last_sif_writes);
 if(polling&&iop_idle&&sif_idle)++adaptive_inactive_windows;
 else adaptive_inactive_windows=0;
 adaptive_last_retired=core->instructions;adaptive_last_zero=zeros;
 adaptive_last_iop=iop;adaptive_last_sif_writes=writes;
 if(adaptive_inactive_windows>=adaptive_confirm_windows){
  char reason[240];
  snprintf(reason,sizeof(reason),
   "SIF F230 returned zero for %llu reads; no IOP instructions or F230 writes in %u consecutive %llu-instruction windows; IOP PC=%08X, IOP stop=%s",
   (unsigned long long)zeros,adaptive_inactive_windows,
   (unsigned long long)adaptive_window_instructions,core->iop_pc,
   core->iop_stop_reason[0]?core->iop_stop_reason:"none");
  core->stopAtAdaptiveStall(reason);
 }
}
static void run_batch(unsigned n){''')
once(u,"  core->step();\n }","  core->step();\n  if(watchdog_bios && (core->instructions%10000ull)==0)adaptive_check();\n }")
# Reset after loading a new guest; keep previous settings untouched.
once(u,"if(ok){watchdog_bios=bios;ips_reset();}","if(ok){watchdog_bios=bios;ips_reset();adaptive_reset();}")
# Include an explicit explanation in the diagnostic log, not a claim of full deadlock detection.
once(u,'fprintf(f,"EE PERFORMANCE:', '''fprintf(f,"BUILD 137 ADAPTIVE WATCHDOG: ENABLED=%u WINDOW_INSTRUCTIONS=%llu CONFIRM_WINDOWS=%u INACTIVE_WINDOWS=%u LAST_SAMPLE_RETIRED=%llu (specific SIF F230 no-response detection; not general deadlock detection)\\n",
 adaptive_watchdog_enabled?1u:0u,(unsigned long long)adaptive_window_instructions,
 adaptive_confirm_windows,adaptive_inactive_windows,(unsigned long long)adaptive_last_retired);
 fprintf(f,"EE PERFORMANCE:''')
print("Build137 adaptive SIF watchdog installed")
