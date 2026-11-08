#!/usr/bin/env python3
"""Build 083: bounded BIOS execution and circular trace diagnostics."""
from pathlib import Path
r=Path(__file__).resolve().parents[1]/'src/PS2-PS3-Bringup-035-SOURCE'
def sub(path,a,b):
 p=r/path;s=p.read_text()
 if s.count(a)!=1:raise RuntimeError(f'{path}: anchor count {s.count(a)}: {a[:65]}')
 p.write_text(s.replace(a,b,1))
h='include/emu_core.h';c='source/emu_core.cpp';u='source/emu_ui.inc'
sub(h,'enum Stop { NONE, BREAKPOINT, UNSUPPORTED, MEMORY, CONTROL };','enum Stop { NONE, BREAKPOINT, UNSUPPORTED, MEMORY, CONTROL, INSTRUCTION_LIMIT };')
sub(h,'struct Trace { uint32_t pc,opcode; bool delay,fetched; };','enum { TRACE_CAPACITY=4096 };\n struct Trace { uint32_t pc,opcode; bool delay,fetched; };\n uint64_t trace_repeated_pc,trace_same_64_block;\n uint32_t trace_last_pc;')
sub(h,'bool step(); bool read32','bool stopAtInstructionLimit(uint64_t limit);\n bool step(); bool read32')
sub(h,'Trace history[64];','Trace history[TRACE_CAPACITY];')
sub(c,'history_head=history_count=0;memset(history,0,sizeof(history));','history_head=history_count=0;trace_repeated_pc=trace_same_64_block=0;trace_last_pc=0;memset(history,0,sizeof(history));')
sub(c,'case CONTROL:return "Branch in delay slot unsupported";','case CONTROL:return "Branch in delay slot unsupported";case INSTRUCTION_LIMIT:return "BIOS instruction limit reached";')
sub(c,'out=history[(history_head+64-history_count+index)%64];','out=history[(history_head+TRACE_CAPACITY-history_count+index)%TRACE_CAPACITY];')
sub(c,'bool Core::halt(Stop why,const char* detail){','bool Core::stopAtInstructionLimit(uint64_t limit){\n char msg[160];snprintf(msg,sizeof(msg),"Retired %llu instructions (limit %llu)",(unsigned long long)instructions,(unsigned long long)limit);return halt(INSTRUCTION_LIMIT,msg);\n}\nbool Core::halt(Stop why,const char* detail){')
sub(c,'fprintf(f,"Last %u instruction attempts, oldest first:\\n",history_count);','fprintf(f,"BIOS WATCHDOG: RETIRED=%llu HISTORY_CAPACITY=%u REPEATED_ADJACENT_PC=%llu REPEATED_64_INSTRUCTION_BLOCKS=%llu\\n",(unsigned long long)instructions,unsigned(TRACE_CAPACITY),(unsigned long long)trace_repeated_pc,(unsigned long long)trace_same_64_block);\n fprintf(f,"Last %u instruction attempts, oldest first:\\n",history_count);')
sub(c,'fprintf(f,"%02u PC=%08X OP=%08X DELAY=%u FETCHED=%u\\n",i,t.pc,t.opcode,unsigned(t.delay),unsigned(t.fetched));','fprintf(f,"%04u PC=%08X OP=%08X DELAY=%u FETCHED=%u\\n",i,t.pc,t.opcode,unsigned(t.delay),unsigned(t.fetched));')
sub(c,'Trace &attempt=history[history_head];attempt.pc=pc;attempt.opcode=opcode;attempt.delay=delay;attempt.fetched=fetched;\n history_head=(history_head+1)%64;if(history_count<64)history_count++;','if(history_count && trace_last_pc==pc)++trace_repeated_pc;\n trace_last_pc=pc;\n if(history_count>=128 && (history_head%64)==0){\n  bool same=true;for(unsigned j=0;j<64;j++)if(history[(history_head+TRACE_CAPACITY-64+j)%TRACE_CAPACITY].pc!=history[(history_head+TRACE_CAPACITY-128+j)%TRACE_CAPACITY].pc){same=false;break;}\n  if(same)++trace_same_64_block;\n }\n Trace &attempt=history[history_head];attempt.pc=pc;attempt.opcode=opcode;attempt.delay=delay;attempt.fetched=fetched;\n history_head=(history_head+1)%TRACE_CAPACITY;if(history_count<TRACE_CAPACITY)history_count++;')
sub(u,'static void run_batch(unsigned n){','static bool watchdog_bios=false;\nstatic const uint64_t bios_instruction_limit=30000000ull; // Build 083 default.\nstatic void run_batch(unsigned n){')
sub(u,'for(unsigned i=0;i<n&&core->stop==Core::NONE;i++)core->step();','for(unsigned i=0;i<n&&core->stop==Core::NONE;i++){\n  if(watchdog_bios && core->instructions>=bios_instruction_limit){core->stopAtInstructionLimit(bios_instruction_limit);break;}\n  core->step();\n }')
sub(u,'ok=bios?core->loadBios(b,(size_t)n):core->loadElf(b,(size_t)n);free(b);','ok=bios?core->loadBios(b,(size_t)n):core->loadElf(b,(size_t)n);free(b);if(ok)watchdog_bios=bios;')
sub(u,'BUILD 082 - EE SIF F230','BUILD 083 - BIOS WATCHDOG')
print('Build 083: 64-bit counter verified; 30M watchdog; 4096-entry history')
