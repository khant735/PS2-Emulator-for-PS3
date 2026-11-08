#!/usr/bin/env python3
"""Build 059: trace-backed PS2 memory-region inventory.
Report declared emulated region capacities, not fabricated host allocation measurements.
"""
from pathlib import Path
root=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
def change(path,old,new):
 s=path.read_text()
 if s.count(old)!=1:raise SystemExit(f"Build 059 anchor mismatch {path}: {old[:90]!r} count={s.count(old)}")
 path.write_text(s.replace(old,new,1))
p=root/"source/emu_core.cpp"
change(p,'fprintf(f,"VIF1 FIFO ingress (capture only;', '''fprintf(f,"PS2 MEMORY INVENTORY (hardware capacities; NOT host heap usage):\\n");
 fprintf(f,"EE_RAM=33554432 bytes (32 MiB; target hardware capacity)\\n");
 fprintf(f,"IOP_RAM=2097152 bytes (2 MiB; EE mirror windows do not add storage)\\n");
 fprintf(f,"SPU2_RAM=2097152 bytes (2 MiB; target hardware capacity, not proof of allocation)\\n");
 fprintf(f,"GS_VRAM=4194304 bytes (4 MiB; target hardware capacity, not proof of allocation)\\n");
 fprintf(f,"EE_SCRATCHPAD=16384 bytes (16 KiB; target hardware capacity)\\n");
 fprintf(f,"VU0_MICRO=4096 VU0_DATA=4096 VU1_MICRO=16384 VU1_DATA=16384 bytes (hardware capacities)\\n");
 fprintf(f,"HOST_MEMORY_USED=N/A HOST_MEMORY_FREE=N/A HOST_MEMORY_TOTAL=N/A (no allocator/OS telemetry in this build)\\n");
 fprintf(f,"VIF1 FIFO ingress (capture only;''')
change(root/"source/emu_ui.inc","BUILD 058 - EE F510 PROBE","BUILD 059 - MEMORY INVENTORY")
print("Build 059 memory inventory trace patch applied")
