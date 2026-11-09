#!/usr/bin/env python3
"""Build 133: centralized strict IOP boot-register address classifier.
Keeps Build 132 per-register diagnostic latches and their read/write counters.
This is a bus-dispatch foundation, NOT device emulation.
"""
from pathlib import Path
r=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
c=r/"source/emu_core.cpp"
s=c.read_text()
def patch(a,b):
 global s
 n=s.count(a)
 if n!=1:raise SystemExit(f"Build133 anchor count={n}: {a[:110]!r}")
 s=s.replace(a,b,1)
# The macro is a strict whitelist: not a permissive 0x1F8082xx range.
classifier="""/* Build 133: strict, shared IOP boot-table register classifier.
 * Only observed 32-bit diagnostic latches are mapped. All other 82xx
 * addresses remain unmapped until their hardware semantics are established.
 */
#define IOP_BOOT_MMIO_KNOWN(pa) (\\
 (pa)==0x1f808240u || (pa)==0x1f808244u || \\
 (pa)==0x1f808248u || (pa)==0x1f80824cu || \\
 (pa)==0x1f808250u || (pa)==0x1f808254u || \\
 (pa)==0x1f808258u || (pa)==0x1f808268u)
"""
s=classifier+"\n"+s
patch("&&pa!=0x1f808268u&&pa!=0x1f808240u&&pa!=0x1f808248u&&pa!=0x1f808250u&&pa!=0x1f808258u&&pa!=0x1f808244u&&pa!=0x1f80824cu&&pa!=0x1f808254u){iop_ram[pa]", "&&!IOP_BOOT_MMIO_KNOWN(pa)){iop_ram[pa]")
# Preserve existing individual register read/write side effects. Validate the
# classifier covers each currently supported boot register at patch time.
for address in ("8240","8244","8248","824c","8250","8254","8258","8268"):
 if f"if(pa==0x1f808{address}u)" not in s and f"else if(pa==0x1f808{address}u)" not in s:
  raise SystemExit(f"Build133 missing write handler for {address}")
 if f"pa==0x1f808{address}u" not in s:raise SystemExit(f"Build133 missing MMIO address {address}")
patch('fprintf(f,"BUILD 132 IOP MMIO 8254:', '''fprintf(f,"BUILD 133 IOP BUS: strict boot MMIO whitelist=8240,8244,8248,824C,8250,8254,8258,8268; other 82xx unmapped; no hardware side effects\\n");
 fprintf(f,"BUILD 132 IOP MMIO 8254:''')
c.write_text(s)
print("Build133: strict shared IOP boot MMIO address classifier installed")
