#!/usr/bin/env python3
"""Build 081: exact-address diagnostic storage for EE SIF F200 and F220."""
from pathlib import Path
import re
root=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
def change(path,old,new):
 s=path.read_text()
 if s.count(old)!=1:raise SystemExit(f"Build 081 anchor mismatch {path}: {old[:80]!r} count={s.count(old)}")
 path.write_text(s.replace(old,new,1))
h=root/"include/emu_core.h"
change(h,"uint32_t ee_sif_f260;","uint32_t ee_sif_f2xx[2];uint64_t ee_sif_f2xx_reads[2],ee_sif_f2xx_writes[2];uint32_t ee_sif_f2xx_last_pc[2],ee_sif_f2xx_last_value[2];uint32_t ee_sif_f260;")
p=root/"source/emu_core.cpp"
change(p,"ee_sif_f260=0;","for(unsigned i=0;i<2;++i){ee_sif_f2xx[i]=0;ee_sif_f2xx_reads[i]=ee_sif_f2xx_writes[i]=0;ee_sif_f2xx_last_pc[i]=ee_sif_f2xx_last_value[i]=0;}ee_sif_f260=0;")
s=p.read_text()
for method,body in [
 ("mmioRead",''' if(size==4 && (((a&0x1FFFFFFFu)==0x1000F200u)||((a&0x1FFFFFFFu)==0x1000F220u))){
  unsigned i=((a&0x1FFFFFFFu)==0x1000F220u)?1u:0u;
  v=ee_sif_f2xx[i];++ee_sif_f2xx_reads[i];ee_sif_f2xx_last_pc[i]=pc;return true;
 }
'''),
 ("mmioWrite",''' if(size==4 && (((a&0x1FFFFFFFu)==0x1000F200u)||((a&0x1FFFFFFFu)==0x1000F220u))){
  // Diagnostic storage only; SIF DMA, handshake and IRQ effects not emulated.
  unsigned i=((a&0x1FFFFFFFu)==0x1000F220u)?1u:0u;
  ee_sif_f2xx[i]=uint32_t(v);++ee_sif_f2xx_writes[i];
  ee_sif_f2xx_last_pc[i]=pc;ee_sif_f2xx_last_value[i]=uint32_t(v);return true;
 }
''')]:
 pattern=r"(bool\s+Core::"+method+r"\s*\([^)]*\)\s*\{)"
 matches=list(re.finditer(pattern,s))
 if len(matches)!=1:raise SystemExit(f"Build 081 method missing {method}: {len(matches)}")
 m=matches[0];s=s[:m.end()]+"\n"+body+s[m.end():]
p.write_text(s)
change(p,'fprintf(f,"EE SDL/SDR little-endian stores:', 'for(unsigned i=0;i<2;++i)fprintf(f,"EE SIF %08X diagnostic latch (no IOP/DMA effects): VALUE=%08X READS=%llu WRITES=%llu LAST_PC=%08X LAST_WRITE=%08X\\n",i?0x1000F220u:0x1000F200u,ee_sif_f2xx[i],(unsigned long long)ee_sif_f2xx_reads[i],(unsigned long long)ee_sif_f2xx_writes[i],ee_sif_f2xx_last_pc[i],ee_sif_f2xx_last_value[i]);\n fprintf(f,"EE SDL/SDR little-endian stores:')
change(root/"source/emu_ui.inc","BUILD 080 - EE SIF F260","BUILD 081 - EE SIF F2XX")
print("Build 081 SIF F200/F220 diagnostic storage applied")
