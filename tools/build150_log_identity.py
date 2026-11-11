#!/usr/bin/env python3
"""Build 150: authoritative build identity in core diagnostic traces."""
from pathlib import Path
import os,datetime
r=Path(__file__).resolve().parents[1]/"src/PS2-PS3-Bringup-035-SOURCE"
p=r/"source/emu_core.cpp"
s=p.read_text()
anchor='fprintf(f,"BUILD 149 IOP ADD:'
if s.count(anchor)!=1:raise SystemExit(f"Build150 anchor mismatch: {s.count(anchor)}")
def esc(v):return str(v).replace('\\','\\\\').replace('"','\\"').replace('\n',' ')
sha=esc(os.environ.get("GITHUB_SHA","unknown"))
branch=esc(os.environ.get("GITHUB_REF_NAME","unknown"))
run=esc(os.environ.get("GITHUB_RUN_ID","unknown"))
utc=esc(datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"))
header='fprintf(f,"APP=PS2 Emulator for PS3\\nBUILD_NUMBER=150\\nBUILD_VERSION=dev-build.150\\nGIT_COMMIT='+sha+'\\nSOURCE_BRANCH='+branch+'\\nGITHUB_RUN_ID='+run+'\\nBUILD_UTC='+utc+'\\n");\n '
p.write_text(s.replace(anchor,header+anchor,1))
print("Build150 identity: "+sha+" run="+run)
