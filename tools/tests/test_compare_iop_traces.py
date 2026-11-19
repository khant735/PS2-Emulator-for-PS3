"""Deterministic, self-contained checks for the IOP trace comparator."""
import importlib.util
import tempfile
import unittest
import zipfile
from pathlib import Path

spec=importlib.util.spec_from_file_location("compare_iop_traces",Path(__file__).with_name("compare_iop_traces.py"))
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def record(n,pc=0xBFC00000,op=0,registers=None):
    registers=registers or {}
    fields=[f"N={n}",f"PC={pc:08X}",f"OP={op:08X}","HI=00000000","LO=00000000"]
    fields.extend(f"R{i:02}={registers.get(i,0):08X}" for i in range(32))
    return "[IOP] "+" ".join(fields)+"\n"

class TraceComparisonTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
    def txt(self,name,rows):
        path=self.root/name
        path.write_text("".join(rows))
        return str(path)
    def test_matching(self):
        x=self.txt("a.txt",[record(0),record(1)])
        y=self.txt("b.txt",[record(0),record(1)])
        self.assertEqual(mod.compare(x,y)["status"],"match")
    def test_register_first_divergence(self):
        x=self.txt("a.txt",[record(0),record(1)])
        y=self.txt("b.txt",[record(0),record(1,registers={2:1})])
        result=mod.compare(x,y)
        self.assertEqual((result["status"],result["n"]),("divergence",1))
        self.assertEqual(result["differences"]["R02"]["candidate"],"00000001")
    def test_index_mismatch(self):
        x=self.txt("a.txt",[record(0),record(1)])
        y=self.txt("b.txt",[record(0),record(2)])
        self.assertEqual(mod.compare(x,y)["status"],"index_mismatch")
    def test_truncation_is_not_success(self):
        x=self.txt("a.txt",[record(0),record(1)])
        y=self.txt("b.txt",[record(0)])
        self.assertEqual(mod.compare(x,y)["status"],"length_mismatch")
    def test_zip_chunk_order(self):
        path=self.root/"trace.zip"
        with zipfile.ZipFile(path,"w") as z:
            z.writestr("trace_00002.txt",record(1))
            z.writestr("trace_00001.txt",record(0))
        plain=self.txt("ref.txt",[record(0),record(1)])
        self.assertEqual(mod.compare(plain,str(path))["status"],"match")
    def test_incomplete_record_rejected(self):
        with self.assertRaises(ValueError):
            mod.parse("[IOP] N=0 PC=BFC00000 OP=00000000")
    def test_limit(self):
        x=self.txt("a.txt",[record(0),record(1)])
        y=self.txt("b.txt",[record(0),record(1,registers={2:1})])
        self.assertEqual(mod.compare(x,y,limit=1)["status"],"limit_reached")

if __name__=="__main__":
    unittest.main()
