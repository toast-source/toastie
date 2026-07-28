# Aseprite Action Viewer v0.5.8.3.1 Tcl/Tk Runtime Build Fix

Status: **Interim package smoke checks passed**

The application version remains `v0.5.8.3`; `.1` identifies this packaging
hotfix and does not change project data or application behavior.

## Build diagnosis and fix

- Python: `C:\Dev\aitsb\Scripts\python.exe`, 3.12.13 venv.
- Development tkinter: import and hidden `Tk()` initialization passed.
- Tcl/Tk patchlevel: 8.6.12.
- PyInstaller: 6.21.0.
- Root cause: Tcl initialization was blocked in the previous restricted build
  context, causing PyInstaller to exclude tkinter. The Python installation
  itself is healthy.
- The successful clean build uses PyInstaller's standard `hook-_tkinter.py`
  and `pyi_rth__tkinter.py`. No custom runtime hook, manual Tcl data path,
  binary path, or hidden import was needed.
- The existing one-file/windowed policy and `Icon.ico` remain unchanged.

## Validation

- Source pycompile, `--check`, `--check-sidebar-ui`, and `git diff --check`:
  passed.
- Nine targeted independent test modules: 50 tests passed; one optional real
  SporeHeart fixture integration skipped explicitly.
- EXE `--check`: exit code 0; reports Tcl 8.6.12 and external examples 0/9.
- EXE `--check-sidebar-ui`: exit code 0.
- Lingering EXE processes after checks: 0.
- Final candidate:
  `dist_v0.5.8.3_tkfix2/ase_viewer.exe`
- EXE size: `18,136,854 bytes`
- EXE SHA-256:
  `299EF579A110C76C85A4122A6363B81E9360A41957E2D2AD7EFE001F877D0DBF`

The previous `dist_v0.5.8.3_icon_final/ase_viewer.exe` remains a failed,
non-release diagnostic artifact and must not be distributed.

The release ZIP contains only the EXE, README, manual checklist, and this
release note. It intentionally excludes user JSON, real resources, source,
tests, caches, prior builds, `.git`, and `.gemini`. Verify the ZIP with its
companion `.sha256` file before running it.

External ZIP record:

- ZIP: `ase_viewer_v0.5.8.3_tkfix.zip`
- Size: `17,907,557 bytes`
- SHA-256:
  `FC40F85DF40287302DABAD77CDDF4241CF86F9C00E9D4A2A781B741BD4BB9A3D`

The ZIP cannot contain an authoritative copy of its own hash. Use the
companion `.sha256` file or the current workspace release note.

## Unsigned build notice

이 빌드는 코드 서명 인증서를 적용하지 않은 테스트/중간 배포용 빌드입니다.
Windows에서 “알 수 없는 게시자” 또는 SmartScreen 경고가 표시될 수 있습니다.
배포된 ZIP의 SHA-256 값을 확인한 뒤 실행해 주세요.

This is an unsigned interim/test build.
Windows may show an Unknown Publisher or SmartScreen warning.
Verify the SHA-256 hash of the distributed ZIP before running it.

Code signing remains follow-up work.

## Company-internal package with examples

Status: **EX1/EX2 resource checks passed**

`ase_viewer_v0.5.8.3_with_examples.zip` places
`resources/examples` next to the verified tkfix2 EXE. This transparent
external-resource layout matches the frozen application's executable-directory
lookup and needs no source, spec, or EXE rebuild.

Included example scope:

- `resources/examples/ex1`
- `resources/examples/ex2`
- `resources/examples/shared`
- 10 files / 2,790,927 bytes
- 9 runtime-required assets plus `resources/examples/README.md`

Staging validation:

- Frozen `--check`: exit 0, `example_resources=9/9`, Tcl 8.6.12.
- Frozen `--check-sidebar-ui`: exit 0.
- Lingering processes: 0.
- Packaged-path and example suites: 16 tests passed.
- Actual EX1/EX2 source preparation and EX2 six-layer parallax rendering:
  passed.

The earlier `ase_viewer_v0.5.8.3_tkfix.zip` intentionally lacks examples and
may show a missing-resource message when EX1/EX2 is selected. It remains
unchanged and is not the company-internal EX deployment candidate.

The new ZIP excludes project/settings JSON, all non-example resources, user
data, tests, source, caches, `.git`, `.gemini`, and earlier build/dist output.

External package record:

- ZIP: `ase_viewer_v0.5.8.3_with_examples.zip`
- Size: `20,612,661 bytes`
- ZIP SHA-256:
  `7F5D7B75014CC355D5DC7D06499429B3BE7A3342FE8514871C4CE57622DD05B8`
- EXE SHA-256:
  `299EF579A110C76C85A4122A6363B81E9360A41957E2D2AD7EFE001F877D0DBF`

The authoritative ZIP hash is external because an archive cannot contain its
own final hash. Use the companion `.sha256` file or current workspace release
note.

이 빌드는 코드 서명 인증서를 적용하지 않은 테스트/중간 배포용 빌드입니다.
Windows에서 “알 수 없는 게시자” 또는 SmartScreen 경고가 표시될 수 있습니다.
배포된 ZIP의 SHA-256 값을 확인한 뒤 실행해 주세요.

This is an unsigned interim/test build.
Windows may show an Unknown Publisher or SmartScreen warning.
Verify the SHA-256 hash of the distributed ZIP before running it.
