#!/usr/bin/env python3
"""Inventory emulated state for a future versioned DEFLATE checkpoint format.
Read-only: this audit deliberately does not claim save-state correctness.
"""
from pathlib import Path
import re, json
root=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
files=[root/"include/emu_core.h",root/"source/emu_core.cpp",root/"source/emu_ui.inc"]
for p in files:
    if not p.is_file(): raise SystemExit("Missing extracted source: "+str(p))
patterns={
 "cpu_registers":r"\b(?:ee|iop)_(?:gpr|pc|hi|lo|cop0|cp0|running|retired|next_pc)\b",
 "memory":r"\b(?:ee|iop)_(?:ram|scratchpad|rom|bios|memory)\b",
 "devices":r"\b(?:sif|dmac|dma|timer|gif|gs|vif|vu0|vu1|ipu|intc|irq)_[A-Za-z0-9_]+",
 "state_lifecycle":r"\b(?:reset|init|shutdown|serialize|deserialize|save_state|load_state)\w*\b",
}
report={"audit":"Build 101 checkpoint readiness","format_proposal":{"container":"ZIP","compression":"DEFLATE","level":1,"version":1},"files":{},"matches":{},"blockers":[
 "Full machine-state ownership and pointer-safe serialization not yet verified",
 "Pending timers, interrupts, DMA, SIF and in-flight execution must be captured atomically",
 "Restore compatibility, BIOS identity and regression tests required before fast resume is enabled"
]}
for p in files:
 s=p.read_text(errors="replace")
 report["files"][str(p.relative_to(root))]={"lines":s.count("\n")+1,"bytes":len(s.encode())}
 for category,pattern in patterns.items():
  names=sorted(set(re.findall(pattern,s,re.I)))
  report["matches"].setdefault(category,{})[p.name]=names[:250]
out=Path("checkpoint-readiness-build101.json")
out.write_text(json.dumps(report,indent=2)+"\n")
print("Checkpoint readiness inventory:",out)
for k,v in report["matches"].items():
 print(k,":",sum(len(x) for x in v.values()),"matched symbols")
print("Status: AUDIT ONLY; no checkpoint save/restore implementation enabled")
