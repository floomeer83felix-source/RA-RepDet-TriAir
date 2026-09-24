# Task Blocker

## M3OT native-process interruption and recovery (2026-09-24)

The original queue stopped in `reliability_rgbt_seed0` epoch 24 near step
1500/2158. Exit code: `-1073740791`; the stdout reports `Unhandled exception
caught in c10/util/AbortHandler.h`. This is a native CUDA/PyTorch process
failure, but the exact cause is not established. No OOM or Python exception
was reported. The original evidence remains in local
`runs/m3ot_supervised_rgbt_v1/orchestrator.stdout.log` and
`orchestrator.stderr.log`.

Attempted recovery: loaded `training/reliability_rgbt_seed0/weights/last.pt`
read-only; its epoch 23 matches the status file and all 23 history rows, and
model, optimizer, and RNG states are present. Restored tracked `tools/`
scripts into this sparse checkout. A first resume launcher attempt failed
before training because sparse-checkout had removed its script; its own log
is `orchestrator.resume1.stderr.log`. The second attempt started at 22:24
CST without changing training code or protocol. It skipped completed early
seed 0 and resumed dynamic seed 0 from epoch 24; its first 200 logged steps
match the pre-crash run. No active blocker is asserted while this retry runs.

Repair options if the native failure repeats:

1. Preserve the new crash log and resume again from the latest verified
   epoch-boundary checkpoint under the same frozen protocol.
2. Pause the six-run queue and diagnose Windows CUDA/driver, PyTorch, and
   DataLoader behavior in isolated reproductions before another attempt;
   do not silently alter batch size, workers, model, thresholds, or seeds.

Related files: `tools/train_m3ot_supervised.py`,
`tools/run_m3ot_six_seed.ps1`,
`runs/m3ot_supervised_rgbt_v1/training/reliability_rgbt_seed0/status.json`.

Last 50 lines of the original stdout error tail (native stack, plus the
separate stderr launcher exit cited above):

```text
00007FFA60E6218700007FFA60E62170 ucrtbase.dll!terminate [<unknown file> @ <unknown line number>]
00007FFA301B1911 <unknown symbol address> VCRUNTIME140_1.dll!<unknown symbol> [<unknown file> @ <unknown line number>]
00007FFA301B218F <unknown symbol address> VCRUNTIME140_1.dll!<unknown symbol> [<unknown file> @ <unknown line number>]
00007FFA301B21E9 <unknown symbol address> VCRUNTIME140_1.dll!<unknown symbol> [<unknown file> @ <unknown line number>]
00007FFA301B4019000007FFA301B3F70 VCRUNTIME140_1.dll!_CxxFrameHandler4 [<unknown file> @ <unknown line number>]
00007FFA637854FF00007FFA63785460 ntdll.dll!_chkstk [<unknown file> @ <unknown line number>]
00007FFA636EBD2500007FFA636EB6D0 ntdll.dll!RtlWow64GetCurrentMachine [<unknown file> @ <unknown line number>]
00007FFA6362F88D00007FFA6362F700 ntdll.dll!RtlRaiseException [<unknown file> @ <unknown line number>]
00007FFA60FC41CA00007FFA60FC4140 KERNELBASE.dll!RaiseException [<unknown file> @ <unknown line number>]
00007FFA3025526700007FFA302551D0 VCRUNTIME140.dll!CxxThrowException [<unknown file> @ <unknown line number>]
00007FF9CD3D6C6E00007FF9CD3D6C00 c10.dll!c10::detail::torchCheckFail [<unknown file> @ <unknown line number>]
00007FF9DAA4384F00007FF9DAA43550 c10_cuda.dll!c10::cuda::c10_cuda_check_implementation [<unknown file> @ <unknown line number>]
00007FF8E9520C3C00007FF8E9520B30 torch_cuda.dll!at::cuda::CUDAEvent::record [<unknown file> @ <unknown line number>]
00007FF8E952E3C9000007FF8E952D6B0 torch_cuda.dll!at::cuda::getCachingHostAllocator [<unknown file> @ <unknown line number>]
00007FF8E952D08900007FF8E952B930 torch_cuda.dll!at::cuda::flush_icache [<unknown file> @ <unknown line number>]
00007FF9CD39BC9D00007FF9CD39BAD0 c10.dll!c10::SymBool::operator| [<unknown file> @ <unknown line number>]
00007FF9CD38F1D2000007FF9CD38F160 c10.dll!c10::ConstantSymNodeImpl<bool>::~ConstantSymNodeImpl<bool> [<unknown file> @ <unknown line number>]
00007FF9CD3BF94500007FF9CD3BF8D0 c10.dll!c10::TensorImpl::~TensorImpl [<unknown file> @ <unknown line number>]
00007FF8E0D8DE6500007FF8E0D8C640 torch_cpu.dll!at::DynamicLibrary::sym [<unknown file> @ <unknown line number>]
00007FF8E0D353C8000007FF8E0D35340 torch_cpu.dll!at::TensorBase::reset [<unknown file> @ <unknown line number>]
00007FF95AE0D01500007FF95AE00D60 torch_python.dll!initModule [<unknown file> @ <unknown line number>]
00007FF95AE9035500007FF95AE60950 torch_python.dll!THPPointer<THPStorage>::THPPointer<THPStorage> [<unknown file> @ <unknown line number>]
00007FF95AE99B5D00007FF95AE97640 torch_python.dll!THPVariable_Wrap [<unknown file> @ <unknown line number>]
00007FF9C9BC704700007FF9C9BC5C44 python39.dll!PyUnicode_InternInPlace [<unknown file> @ <unknown line number>]
00007FF9C9BC704700007FF9C9BC5C44 python39.dll!PyUnicode_InternInPlace [<unknown file> @ <unknown line number>]
00007FF9C9BBFC3600007FF9C9BBF6B0 python39.dll!Py_NewReference [<unknown file> @ <unknown line number>]
00007FF9C9BE3FEC00007FF9C9BE1E20 python39.dll!PyBytes_FromStringAndSize [<unknown file> @ <unknown line number>]
00007FF9C9BD43C400007FF9C9BCB6F0 python39.dll!PyEval_EvalFrameDefault [<unknown file> @ <unknown line number>]
00007FF9C9BC9B2F00007FF9C9BC9200 python39.dll!PyFunction_Vectorcall [<unknown file> @ <unknown line number>]
00007FF9C9BCE80A00007FF9C9BCB6F0 python39.dll!PyEval_EvalFrameDefault [<unknown file> @ <unknown line number>]
00007FF9C9BCD66900007FF9C9BCB6F0 python39.dll!PyEval_EvalFrameDefault [<unknown file> @ <unknown line number>]
00007FF9C9BC9B2F00007FF9C9BC9200 python39.dll!PyFunction_Vectorcall [<unknown file> @ <unknown line number>]
00007FF9C9B9127900007FF9C9B911D0 python39.dll!PyEval_EvalCodeWithName [<unknown file> @ <unknown line number>]
00007FF9C9BAD13B00007FF9C9BAD0A0 python39.dll!PyEval_EvalCodeEx [<unknown file> @ <unknown line number>]
00007FF9C9BAD09900007FF9C9BAD06C python39.dll!PyEval_EvalCode [<unknown file> @ <unknown line number>]
00007FF9C9BACDBA00007FF9C9BACC24 python39.dll!PyType_LookupId [<unknown file> @ <unknown line number>]
00007FF9C9BACD3A00007FF9C9BACC24 python39.dll!PyType_LookupId [<unknown file> @ <unknown line number>]
00007FF9C9C624A700007FF9C9C622D0 python39.dll!PyDict_DelItemString [<unknown file> @ <unknown line number>]
00007FF9C9C6222C00007FF9C9C620A8 python39.dll!PyImport_GetMagicNumber [<unknown file> @ <unknown line number>]
00007FF9C9C6308300007FF9C9C63034 python39.dll!PyRun_SimpleFileExFlags [<unknown file> @ <unknown line number>]
00007FF9C9C9393C00007FF9C9C938F0 python39.dll!PyRun_AnyFileExFlags [<unknown file> @ <unknown line number>]
00007FF9C9C9371200007FF9C9C9118C python39.dll!PyLong_FromNbInt [<unknown file> @ <unknown line number>]
00007FF9C9C14A4800007FF9C9C148BC python39.dll!Py_RunMain [<unknown file> @ <unknown line number>]
00007FF9C9C148D100007FF9C9C148BC python39.dll!Py_RunMain [<unknown file> @ <unknown line number>]
00007FF9C9C156FB00007FF9C9C15620 python39.dll!PyArgv_AsWstrList [<unknown file> @ <unknown line number>]
00007FF9C9CD196500007FF9C9CD1940 python39.dll!Py_Main [<unknown file> @ <unknown line number>]
00007FF73FEC1264 <unknown symbol address> python.exe!<unknown symbol> [<unknown file> @ <unknown line number>]
00007FFA61C7CD8700007FFA61C7CD70 KERNEL32.DLL!BaseThreadInitThunk [<unknown file> @ <unknown line number>]
00007FFA636CCAEC00007FFA636CCAC0 ntdll.dll!RtlUserThreadStart [<unknown file> @ <unknown line number>]
```

## Current M3OT experiment gate (2026-09-24)

No active failure is asserted. The M3OT RGB/IR/GT pairing and visual-review
gates passed on 2026-09-24, and the matched six-run training queue is now
running. The sole unpaired train RGB frame is excluded and documented in the
audit; imperfect RGB/IR pixel alignment is a disclosed limitation, not a
silent annotation correction. V88 remains deferred, and its frozen
scientific claims must not be silently revised. If M3OT training or final
verification fails, record the exact error here before proceeding.

Status: `V87_COMPLETE_NO_ACTIVE_EXPERIMENT_BLOCKER_V88_RELEASE_AUDIT_AUTHORIZED`

Updated: 2026-09-09

## Current state

V87 is complete. The V81 single-modality table, V86 matched event-contribution comparison, same-seed deltas, and bounded interpretation are integrated into the active manuscript. The V73 MM-UAV section has also been restored to the frozen actual metrics after removal of an older idealized reference table.

There is no active experimental blocker and no new experiment is authorized.

## Frozen claim boundary

The manuscript may state that:

- thermal-only is the strongest V81 standalone modality and event-only is the weakest;
- RGB+thermal+event dynamic improves mean AP over matched RGB+thermal dynamic by `+0.0339 +/- 0.0400`;
- the AP improvement is positive for `2/3` seeds and negative for seed 0;
- AP50 is nearly unchanged, while AP75 and AR100 show clearer descriptive mean gains;
- event provides complementary average value under the frozen TriAir development protocol;
- V73 supervised alignment restores MM-UAV performance, but TriAir initialization and reliability-aware fusion do not improve the three-seed mean.

The manuscript must not claim uniform event benefit, statistical significance, calibrated physical sensor health, independent blind external validation, universal cross-dataset superiority, or positive V73 transfer from the removed idealized reference values.

## V88 boundary

V88 may only perform final manuscript consistency, author-metadata, table/figure/reference, build, and release-candidate checks. It may not run training, inference, evaluation, threshold search, checkpoint replacement, or new dataset experiments.
