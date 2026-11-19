# PCSX2 direct IOP interpreter trace — SIF reference (first 1,000,000 instructions)

Source: user-supplied `pcsx2_iop_trace.zip` (10,000,000 instruction records, 1,000 ZIP entries). The counts below are restricted to the first 100 ZIP entries, representing N=0 through N=999,999. Rechecked directly against the uploaded archive on 2026-11-19.

## Observed effective-address accesses

| IOP physical address | Opcode family | Count | First N | First PC | First opcode |
| --- | --- | ---: | ---: | --- | --- |
| 0x1D000060 | LW | 2 | 565106 | 00016A74 | 8C820000 |
| 0x1D000020 | LW | 18238 | 634822 | 00016AC4 | 8C420000 |

The first accesses use virtual addresses BD000060 and BD000020 respectively; masking to the IOP 29-bit physical address gives the values above. The register snapshot immediately after each of the first observed loads has the destination register equal to zero. This alone does not establish constant-zero hardware behaviour.

## Engineering implications

- Build 158's IOP SIF read handling is incomplete: it has no explicit 0x1D000060 read case.
- A trace-only match does not validate EE/IOP flag sharing, SIF DMA, interrupts, or load delay semantics.
- Do not hard-code zero for the entire 0x1D0000xx region based on these observations.
- Record before/after register state, effective address and nearby branch behaviour when comparing PCSX2 to PS3.
- Next: compare the PS3 emulator's first divergent IOP instruction against the PCSX2 reference; only implement MMIO side effects with supporting evidence.
