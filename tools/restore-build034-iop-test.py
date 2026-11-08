#!/usr/bin/env python3
"""Restore the Build 034 IOP register smoke test to Build 035 sources."""
from pathlib import Path
root = Path(__file__).resolve().parents[1] / "src" / "PS2-PS3-Bringup-035-SOURCE"
ui = root / "source" / "emu_ui.inc"
core = root / "source" / "emu_core.cpp"
hdr = root / "include" / "emu_core.h"
def replace_once(path, old, new):
    text = path.read_text()
    if text.count(old) != 1:
        raise SystemExit(f"Expected one occurrence in {path}: {old[:90]!r}; got {text.count(old)}")
    path.write_text(text.replace(old, new, 1))
replace_once(hdr, "uint32_t intc_stat,intc_mask;", "uint32_t intc_stat,intc_mask;\n uint16_t iop_compat_latch[2];")
replace_once(core, "intc_stat=intc_mask=0;dve.reset();", "intc_stat=intc_mask=0;iop_compat_latch[0]=iop_compat_latch[1]=0;dve.reset();")
replace_once(core, "if(size==1&&p==0x1f80146eu){v=0;iop_probe_reads++;return true;}", """if(size==1&&p==0x1f80146eu){v=0;iop_probe_reads++;return true;}
 // Build 034 IOP register smoke test: experimental 16-bit readback latches.
 if(size==2&&(p==0x1f801470u||p==0x1f801472u)){v=iop_compat_latch[(p-0x1f801470u)/2];return true;}""")
replace_once(core, "if(size==4&&p==0x12001004u)return true;", """if(size==2&&(p==0x1f801470u||p==0x1f801472u)){iop_compat_latch[(p-0x1f801470u)/2]=uint16_t(v);return true;}
 if(size==4&&p==0x12001004u)return true;""")
replace_once(core, 'fprintf(f,"INTC register storage', 'fprintf(f,"IOP compatibility latches (experimental, not verified hardware): 1470=%04X 1472=%04X\\n",iop_compat_latch[0],iop_compat_latch[1]);\n fprintf(f,"INTC register storage')
test = """static void iop_register_smoke(){
 auto_run=false;unsigned char*rom=(unsigned char*)calloc(1,4*1024*1024);
 if(!rom){notice("Not enough memory for IOP register test");return;}
 // Exact MIPS guest words recovered from the stripped Build 034 ELF.
 const unsigned words[]={0x3c02bf80,0x34421470,0x2404022a,0xa4400000,0xa4440002,0x94450000,0x94460002,0x0000000d};
 for(unsigned i=0;i<sizeof(words)/sizeof(words[0]);i++)
  for(unsigned j=0;j<4;j++)rom[4*i+j]=(words[i]>>(8*j))&255;
 bool loaded=core->loadBios(rom,4*1024*1024);free(rom);
 if(!loaded){notice(core->error);return;}
 snprintf(guest_label,sizeof(guest_label),"Built-in IOP register test");
 core_loaded=true;screen=3;cpu_page=0;run_batch(100);
 bool ok=core->stop==Core::BREAKPOINT&&core->reg[5]==0x22a&&core->reg[6]==0x22a&&
  core->iop_compat_latch[0]==0x22a&&core->iop_compat_latch[1]==0x22a;
 notice(ok?"IOP REGISTER TEST PASS: compatibility latch readback":"IOP REGISTER TEST FAILED - see last-trace.txt");
}
"""
replace_once(ui, "static void gif_smoke(){", test+"static void gif_smoke(){")
replace_once(ui, '"RUN IOP RAM TEST","RUN GIF CONTROL TEST"', '"RUN IOP RAM TEST","RUN IOP REGISTER TEST","RUN GIF CONTROL TEST"')
replace_once(ui, "case 18:gif_smoke();break;case 19:gs_smoke();break;case 20:running=0;", "case 18:iop_register_smoke();break;case 19:gif_smoke();break;case 20:gs_smoke();break;case 21:running=0;")
print("Build 036: restored IOP register test and compatibility latch readback")
