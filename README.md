# Aseprite Action Viewer

Aseprite 프로젝트 파일을 실시간으로 불러와 게임의 물리 엔진, 전투 로직, 그리고 시각적 효과(VFX)를 즉시 시뮬레이션하고 테스트할 수 있는 강력한 파이게임(Pygame) 기반 뷰어입니다.

## 🚀 주요 기능 (Key Features)

### 1. 맵 & 배경 에디터 (Advanced Background & Platform)
- **다중 레이어 패럴랙스 (Multi-layer Parallax):** 여러 장의 배경 이미지를 겹쳐 원경, 중경, 근경에 각기 다른 시차(Parallax) 속도를 부여할 수 있습니다.
- **무한 스크롤 (Loop X):** 각 레이어별로 좌우 무한 반복(`Loop X`) 타일링을 켜고 끌 수 있습니다.
- **인게임 플랫폼 편집:** `EDIT PLAT` 모드에서 마우스 드래그만으로 밟고 올라갈 수 있는 플랫폼과 통과할 수 없는 벽(Solid Box)을 생성, 크기 조절, 삭제(`[X]` 버튼 또는 `Delete` 키)할 수 있습니다.
- **렌더링 최적화:** 뷰포트 클리핑(Culling) 기술을 통해 화면 밖의 배경과 수백 개의 타일 렌더링을 차단하여 화면을 최대로 확대해도 60FPS를 방어합니다.

### 2. 인터랙티브 프랍 시스템 (Interactive Prop System)
- **다단계 파괴 (Multi-stage Destruction):** Aseprite 태그(`Break1`, `Break2`, `Parts`)를 기반으로 타격 횟수에 따라 상자가 반파되고 최종적으로 산산조각 나는 연출을 자동 지원합니다.
- **정밀한 파편 스폰 (Precision Debris):** `Parts` 태그 안에 지정된 여러 개의 슬라이스(Slice) 영역을 오려내어, Aseprite 캔버스 상의 원래 위치에서 파편이 튀어 오르게 합니다.
- **물리 상호작용 (Physics Interaction):** 부서져서 바닥에 굴러다니는 파편들을 플레이어가 다시 타격(Hit)할 수 있으며, 타격 시 물리 엔진에 의해 더 멀리 튀어 오르고 회전합니다. (수명 20초 유지)
- **독립적인 관리 탭:** `PROPS` 전용 설정 탭을 통해 일반 몬스터(NPC)와 섞이지 않게 프랍 리소스를 깔끔하게 관리하고 즉시 스폰(`SPAWN`)할 수 있습니다.

### 3. 액션 & 전투 시뮬레이션 (Action & Combat)
- **콤보 액션 매핑:** Aseprite 파일 내부의 태그(Tag)를 읽어와 3타 콤보 공격(`ComboAttack_1~3`), 점프 공격, 대시, 파워밤 등 다양한 상태에 매핑하여 즉시 시연해 볼 수 있습니다.
- **물리 엔진:** 점프력, 대시 속도, 중력, 공격 시 전진 거리(Attack Forward) 등 게임의 조작감을 픽셀 단위로 미세 조정할 수 있습니다.
- **스왑 시스템 (Swap):** 콤보 도중 `T`키를 눌러 다른 캐릭터(NPC)와 태그 매치 형식으로 교대하며, 자연스러운 `Swap_Enter / Swap_Exit` 애니메이션과 노란색 아웃라인(VFX)을 지원합니다.

### 3. 주스 효과 & 편의성 (Juice & QoL)
- **VFX 설정:** 공격 시 화면 흔들림(Screen Shake) 강도 조절, 대시 중 잔상(Ghost) 효과 켜기/끄기.
- **정밀 수치 입력:** 슬라이더 옆의 수치를 마우스로 클릭하면 키보드로 정확한 숫자(예: 125, 0.5)를 직접 입력할 수 있습니다.
- **단축키 커스텀 (Keybindings):** `CONTROLS` 탭에서 마우스 클릭 후 원하는 키보드 키를 눌러 모든 액션의 단축키를 즉시 변경하고 충돌을 방지합니다.
- **실시간 모니터링:** 좌측 상단에 현재 프레임(FPS)과 카메라 줌(Zoom) 비율을 색상별로 실시간 표시합니다.
- **예제(EXAMPLE) 모드:** 원클릭으로 준비된 완벽한 프리셋(캐릭터, 멀티 배경, 맵 세팅)을 로드할 수 있습니다.

### 4. NPC/PROP Slice PNG 저장

- `SETUP > NPCS`와 `SETUP > PROPS`의 `SAVE`는 같은 내보내기 로직을 사용합니다. 월드 인스턴스는 필요 없지만, 유효한 소스와 `Parts` 태그 및 그 범위에서 불투명 픽셀이 있는 Slice가 하나 이상 있어야 활성화됩니다. 비활성 버튼을 누르면 이유를 안내합니다.
- 기본 `AUTO` 모드는 `Parts`와 `Particles` 태그의 전체 프레임을 검사해 실제 픽셀이 있는 Slice를 분류합니다. 같은 Slice가 양쪽 태그에서 유효하면 이름 힌트를 우선하고, 힌트가 없으면 양쪽 항목을 모두 보존합니다. `NAME` 모드는 기존 `particle` 이름 필터와의 호환용입니다.
- 소스 로딩·프로젝트 복원·예제 준비·F5 새로고침이 성공하면 AUTO 결과를 소스에 한 번 캐시합니다. NPC와 PROP의 SAVE, 피격 Particles, 사망/파괴 Parts는 이 결과를 함께 사용하며, SAVE에서 NAME을 선택해도 런타임 AUTO 결과는 바뀌지 않습니다.
- 결과 파일은 프로필 표시 이름을 기준으로 `<이름>_Parts_01.png`, `<이름>_Particle_01.png`처럼 각 그룹 번호를 따로 매깁니다. Windows에서 사용할 수 없는 이름과 예약 이름을 정리하고, 기존 파일이 있으면 `_2`, `_3`을 붙여 덮어쓰지 않습니다.
- 완료 창은 저장·건너뜀·실패 수와 출력 폴더를 표시합니다. 개별 기술 오류와 traceback은 `ase_debug.log`에 기록됩니다.
- 이 기능은 Aseprite 태그/Slice의 제작용 이미지만 내보냅니다. 런타임 3×3 파편, 파티클, 시체 상태는 저장하지 않습니다.

### 5. 레이어와 NPC 사망

- `OPTIONS > LAYERS`는 렌더용 스프라이트시트 JSON이 아니라 Aseprite 원본에서 별도로 수집한 전체 레이어 인벤토리를 아래→위 스택 순서로 표시합니다. 그룹·자식·빈 레이어·원래 숨긴 레이어도 목록에 유지하고 이름은 들여쓰기로 구분합니다.
- 레이어 표시 상태는 Aseprite UUID를 우선하고, UUID가 없거나 구형 파일에서 다시 열 때 UUID가 재생성되는 경우 원본 인벤토리 인덱스와 전체 경로를 함께 사용합니다. 따라서 같은 이름의 레이어도 독립적으로 숨길 수 있습니다. 구형 이름 기반 상태는 이름이 유일할 때만 적용하며, 동명 레이어는 모두 표시하고 경고를 남깁니다.
- 토글용 Lua는 원본 인벤토리를 먼저 기록한 뒤 임시로 표시 상태만 적용하며 `.aseprite`를 저장하지 않습니다. 새로고침 실패나 불완전한 인벤토리는 기존 목록과 마지막 정상 Surface를 유지합니다.
- NPC 프로필에는 `DEAD_LOOP` 액션 슬롯이 있습니다. `Dead_(Loop)`, `Dead_Loop`, `Dead Loop`, `DeadLoop`와 같은 `Dead`/`Death` 변형을 대소문자 구분 없이 자동 인식하며 수동 매핑을 덮어쓰지 않습니다.
- 사망 처리는 `유효한 DEAD_LOOP 시체 유지 → 유효한 Parts Slice 정밀 파편 → 사망 프레임 3×3 → 단색 효과` 순서입니다. 시체는 사망 위치와 방향을 유지하고 AI·공격 대상에서 제외되며, 프로젝트/예제 초기화나 연결 소스 삭제 때 제거됩니다.
- NPC 피격은 유효한 `Particles` Slice가 있으면 해당 이미지를 사용하고, 태그가 없거나 실제 이미지가 비어 있으면 기존 기본 파티클을 사용합니다. 설정의 NPC/PROP 행에는 `P:n / FX:n / SAVE:ON|OFF`가 표시됩니다.

## 🎬 복구된 내부 예제

- **EX 1:** Cailin PLAYER와 Nisariel NPC_1, 플랫폼 6개, 솔리드 박스 2개, 단일 `로비 컨셉94 (1).png` 배경을 사용하는 로비 환경입니다. 카메라 세로 오프셋은 `-120`입니다.
- **EX 2:** 같은 두 캐릭터 프로필과 지형 위에 `00.png`부터 `레이어 3.png`까지 과거의 6개 패럴랙스 레이어를 순서대로 구성합니다. 카메라 세로 오프셋은 `-100`입니다.
- 두 예제의 소스·프로필 매핑·환경 수치는 Git commit `5598e4d`와 이전
  로컬 runtime의 2026-06-11 저장 JSON을 근거로 복구했습니다. 두 예제가
  같은 캐릭터 소스를 쓰는 것은 과거 데이터와 일치하며, 환경과 카메라
  목적이 다릅니다.
- 예제 리소스는 회사 내부 제작 도구 사용을 위해 `resources/examples`에 원본을 복사해 포함했습니다. 런타임은 과거 폴더를 직접 읽지 않고 애플리케이션 리소스 루트 기준 상대 경로만 사용합니다.
- 과거 프리셋은 NPC_1 인스턴스를 준비하지만 자동 프랍 프로필/소스/스폰 데이터는 포함하지 않았습니다. 근거가 없어 프랍 값은 새로 만들지 않았습니다.

## 🛠️ 설치 및 실행 방법

1. **요구 환경:**
   - Python 3
   - Aseprite (`Aseprite.exe`)

2. **필수 라이브러리 설치:**
   ```bash
   python -m pip install -r requirements.txt
   ```
3. **프로그램 실행:**
   ```bash
   python ase_viewer.py
   ```
   Windows에서는 `run.bat`을 실행해도 됩니다.
4. 처음 Aseprite 파일을 불러올 때 `Aseprite.exe` 위치를 묻는 창이 뜨면 설치 경로를 선택해 주세요. 선택 결과는 `config.json`에 저장됩니다.

## 🧪 테스트 및 빌드

### 테스트

```bash
python -m unittest discover -s tests -v
```

자동 테스트는 저장 안정성, 상대/절대 경로 호환, CLI 실패 처리와 Aseprite 내보내기를 확인합니다. Aseprite가 알려진 설치 경로에 없으면 실제 통합 테스트만 `skip`되고 mock 기반 테스트는 계속 실행됩니다.

### 비대화형 검사

```bash
python ase_viewer.py --check
python ase_viewer.py --check-aseprite
python ase_viewer.py --check-gui
python ase_viewer.py --check-layers
```

- `--check`: dummy SDL 화면에서 pygame 초기화, 설정 읽기, 9개 예제 리소스 해석, 플레이어 생성과 한 프레임 렌더링을 확인합니다.
- `--check-aseprite`: Aseprite CLI를 탐색하고 `Testfiles/Test01.aseprite`를 임시 폴더에 내보냅니다. 사용자 프로젝트와 설정, 원본 애셋은 수정하지 않습니다.
- `--check-gui`: 실제 사용자 JSON을 읽지 않고 메모리 예제로 이동, 대시, 콤보, 교대, NPC, 프랍, 플랫폼과 여러 프레임 렌더링을 확인합니다.
- `--check-layers`: 번들 Aseprite fixture의 원본 레이어 인벤토리, 고유 키, 첫/마지막 토글, 목록 순서 유지와 원본 렌더 복원을 확인합니다. 배치 CLI는 사용자 Aseprite 복구 세션과 분리된 임시 APPDATA를 사용하며 사용자 설정을 쓰지 않습니다.
- 실패 원인은 콘솔에 요약되고 상세 프로세스 출력은 `ase_debug.log`에서 확인할 수 있습니다.

### Windows 실행 파일 빌드

```bash
python -m pip install pyinstaller
python -m PyInstaller --clean ase_viewer.spec
```

빌드가 성공하면 `dist/ase_viewer.exe`가 생성됩니다. `build/`와 `dist/`는 생성 산출물이므로 소스 변경과 분리해서 다루는 것을 권장합니다.

## ⚠️ 알려진 제한사항

- `EX 1`, `EX 2`는 애플리케이션 리소스 루트의 `resources/examples`를 사용합니다. 필수 소스·배경의 누락, 해시 불일치, Aseprite 내보내기, 태그 검증 또는 이미지 로딩 중 하나라도 실패하면 현재 상태를 유지하고 불완전한 예제를 적용하지 않습니다.
- 두 예제는 역사적으로 같은 Cailin/Nisariel 소스와 프로필 매핑, 플랫폼 및 솔리드 박스를 사용합니다. EX 1은 단일 로비 배경, EX 2는 6개 패럴랙스 레이어와 다른 카메라/배경 설정을 사용합니다.
- 과거 데이터에 자동 프랍 구성은 없습니다. NPC_1은 과거 코드처럼 예제 적용 시 하나 준비되지만 저장된 목표 AI 수는 `0`입니다.
- 소스와 배경 경로는 프로젝트/설정 JSON 위치를 기준으로 상대 저장합니다. 다른 드라이브처럼 상대화할 수 없는 경로만 절대 경로로 유지합니다.
- 프로젝트 저장은 기존 `sources` 경로 목록과 함께 선택적 `source_kinds` 및 프로필 `kind`(`player`/`npc`/`prop`)를 기록합니다. 구형 파일에 이 필드가 없으면 첫 프로필은 PLAYER, 이후 프로필은 NPC라는 기존 규칙으로 읽으며, 불러오기만으로 JSON을 다시 쓰지 않습니다.
- 소스를 삭제하면 그 소스를 직접 참조한 프로필과 NPC/PROP 인스턴스를 제거하고, 뒤쪽 소스 및 액션 매핑 인덱스를 1씩 당깁니다. 다른 소스로 자동 재매핑하지 않으며, 활성 플레이어 프로필이 제거되면 잘못된 캐릭터 표시를 피하기 위해 플레이어 렌더링을 비활성화합니다.
- NPC/PROP의 정밀 파편은 공통 `Parts` Slice 크롭을 사용하지만 수명 등 런타임 값은 서로 다릅니다. NPC에 유효한 `DEAD_LOOP`가 있으면 파편 대신 시체를 유지하며, `Parts`가 없을 때만 3×3 분할을 사용합니다.
- 런타임 시체 상태는 프로젝트에 저장되지 않습니다. 공중에서 사망한 시체도 현재는 최소 변경 정책에 따라 사망 순간 위치에 고정됩니다.
- 기존 절대 경로 프로젝트도 그대로 읽습니다. 경로가 사라졌다면 프로젝트 폴더, 애플리케이션 폴더, `Testfiles` 주변만 제한적으로 확인한 뒤 파일 재선택을 요청합니다. 불러온 파일을 자동 변환하거나 덮어쓰지 않습니다.
- 누락 소스가 여러 개면 파일별로 대체 경로를 받습니다. 같은 누락 경로는 한 번만 묻고, 하나라도 취소하거나 내보내기에 실패하면 전체 로드를 취소해 현재 메모리 상태와 JSON을 유지합니다.
- 앱 데이터(`config.json`, `ase_settings.json`, `ase_project.json`, `ase_debug.log`)는 현재 작업 디렉터리가 아니라 `ase_viewer.py` 또는 실행 파일이 위치한 애플리케이션 폴더를 사용합니다.
- Aseprite 경로는 저장된 `config.json`을 우선 사용하고 Steam/Program Files 기본 위치를 탐색합니다. 찾지 못하면 파일 선택 창을 표시합니다.
- 전투, 교대, 플랫폼 편집 등 실제 키보드·마우스 GUI 상호작용은 여전히 수동 확인이 필요합니다.
- 이번 복구에서는 요청 범위에 따라 PyInstaller 데이터 정책을 재설계하지 않았습니다. 기존 spec으로 만든 실행 파일에서 EX 프리셋을 쓰려면 `resources/examples` 구조가 실행 파일 옆에 함께 있어야 합니다.
- PyInstaller 6.16.0 빌드에서 표시되는 `pkg_resources` 사용 중단 예정 경고는 현재 알려진 경고입니다.
- 현재 작업 트리는 사용자 JSON·기존 빌드 산출물과 안정화 변경이 함께 있어 깨끗하지 않습니다. 커밋 전 파일 그룹을 구분해 검토해야 합니다.

### v0.5.3.2 장면 오브젝트 안정화

- 장면 목록은 저장 데이터와 파일명을 바꾸지 않고 `[PLAYER]`, `[NPC 01]`,
  `[PROP 01]` 배지를 표시합니다. 시체로 판정된 NPC는
  `[NPC 02 · CORPSE]`처럼 구분하며, 삭제 뒤 번호는 현재 목록 순서대로
  다시 매겨집니다.
- NPC/PROP 리소스 추가와 리소스 새로고침은 기존 장면 오브젝트의 위치,
  속도, 방향, 스케일, 애니메이션 및 선택 상태를 스냅샷으로 보호합니다.
  새 인스턴스만 기존 기본 배치 규칙을 사용합니다.
- 장면 캐릭터·오브젝트 모드에 `선택 시체 삭제` /
  `Delete Selected Corpse` 버튼을 추가했습니다. 명시적인 corpse/dead
  상태를 우선 확인하며, 살아 있는 NPC가 선택됐거나 시체가 없으면
  아무것도 삭제하지 않고 상태 문구만 표시합니다.
- v0.5.3.1의 단일 사이드바 모드와 고정 헤더/스크롤 콘텐츠 clipping
  정책을 유지합니다.
- 이 변경은 프로젝트 JSON schema를 바꾸지 않습니다. 런타임 시체
  삭제와 UI 표시 번호는 저장되지 않습니다.

### v0.5.4 장면 오브젝트 관리

- 장면 목록에 세션 전용 `전체 / 플레이어 / NPC / 프롭 / 시체` 필터를
  추가했습니다. NPC 필터는 살아 있는 NPC만, 시체 필터는 corpse/remnant
  판정을 통과한 NPC만 표시합니다. 필터는 원본 목록과 프로젝트 데이터를
  변경하지 않으며 `[NPC 02]` 같은 번호는 전체 장면 순서를 유지합니다.
- 필터 밖으로 나간 현재 선택은 지우지 않고 내부 identity를 유지합니다.
  현재 선택이 숨겨졌다는 상태 문구를 표시하며, 전체 또는 해당 타입
  필터로 돌아오면 같은 오브젝트가 다시 선택되어 보입니다.
- `시체 전체 삭제`는 명시적인 corpse/dead 상태로 판정된 NPC 잔여
  오브젝트만 제거합니다. 살아 있는 NPC, PLAYER, PROP은 유지되며 선택된
  대상이 삭제된 경우 현재 필터의 다음 또는 이전 행으로 이동합니다.
- `선택 대상 보기`는 선택한 오브젝트의 `x/y`로 카메라만 이동하고 자동
  추적을 끕니다. 플레이어와 오브젝트 좌표, 물리·애니메이션 상태 및 저장
  데이터는 바꾸지 않습니다.
- 상단 F5 전체 리소스 새로고침도 v0.5.3.2의 scene snapshot/restore 경계를
  사용하도록 보강했습니다. 필터와 선택 상태는 프로젝트/설정 JSON에
  저장하지 않습니다.

### v0.5.5.1 리소스 역할 배정과 Partner 로스터 핫픽스

- 일반 리소스 가져오기와 장면 역할 배정을 분리했습니다. 파일 드롭과
  `+ 소스`는 source만 등록하며 자동으로 NPC profile/instance를 만들지
  않습니다. Resources 탭에서 `플레이어로 사용`, `파트너로 추가`,
  `NPC로 추가`, `프롭으로 추가`를 선택합니다.
- 하나의 source에 역할별 profile을 별도로 만들 수 있습니다.
  Player 배정은 현재 PLAYER profile의 source와 mapping만 교체하며 위치를
  유지합니다. NPC/Prop 배정은 요청한 새 인스턴스만 기본 위치에 추가하고,
  Partner 배정은 `partner_profiles` 대기 로스터에 profile만 등록합니다.
- Partner는 화면에 항상 표시되는 동료 NPC가 아니라 `T` Character Swap의
  대기 후보입니다. 장면 actor, 렌더/update/AI/물리, Focus, scene snapshot,
  NPC 수와 corpse cleanup 대상이 아니며 Scene 필터는
  전체/플레이어/NPC/프롭/시체만 제공합니다. Resources 탭에서 Partner 수와
  다음 후보를 확인할 수 있습니다.
- Character Swap은 Partner profile을 우선 후보로 사용합니다. 스왑하면
  들어오는 Partner가 PLAYER가 되고, 나가는 PLAYER는 로스터 후보로
  남습니다. Player 객체의 위치와 카메라/입력 소유권, NPC/PROP 목록과
  `target_ai_count`는 유지됩니다. 예제의 기존 `NPC_1` 내부 이름은 호환성을 위해 유지하지만
  역할은 Partner입니다. 명시적 Partner가 없는 구형 프로젝트는 기존
  비-PROP 후보를 사용하는 fallback을 유지합니다.
- 프로젝트 schema version은 2를 유지합니다. 새 프로젝트는 profile의
  기존 `kind` 필드에 선택적인 `partner` 값을 기록할 수 있습니다. 구형
  파일에 kind가 없으면 기존과 동일하게 첫 profile은 Player, 나머지는
  NPC로 해석하며 자동 저장이나 강제 migration은 하지 않습니다.
- Player, NPC, PROP은 역할 추가와 F5/개별 리소스 새로고침 동안 위치·속도·
  애니메이션·선택 상태를 함께 보존합니다. Partner는 위치를 갖지 않습니다.
- NPC/Player/Prop 역할 profile은 Aseprite의 명시적 pivot Slice를 우선하고,
  없으면 대표 프레임의 잘린 이미지 하단을 ground anchor로 사용합니다.
  새 NPC는 더 이상 고정 `-100px` 위치에서 이미 grounded 상태로 생성되지
  않아 SporeHeart처럼 높이가 다른 리소스도 바닥선에 맞습니다.

### v0.5.5.2 사이드바 내비게이션과 태그 등록 진입점

- 사이드바 고정 헤더에 `태그 등록` / `OPTIONS` / `배치` / `리소스` 네
  버튼을 같은 위치와 크기로 배치했습니다. `태그 등록`은 새 시스템이
  아니라 기존 `mapping` 모드의 명시적인 진입점입니다.
- 각 버튼은 해당 단일 `sidebar_mode`로만 이동합니다. 현재 버튼을 다시
  눌러도 모드를 유지하며, 태그 매핑으로 돌아가려면 `태그 등록`을
  누릅니다.
- 빈 프로젝트에서도 네 모드를 모두 열 수 있습니다. 태그 등록 화면은
  Resources 또는 `+ 소스`로 파일을 가져오는 방법, 역할 배정 전후에
  애니메이션 매핑을 확인할 수 있다는 안내를 표시합니다.
- Resources import 상태는 다음 단계로 Tag Setup에서 애니메이션을
  확인하도록 안내합니다. Partner 역할은 계속 장면 동료가 아닌 `T`
  교대 후보 roster입니다.
- 기존 70px header/content 경계를 유지해 OPTIONS 스크롤 좌표를 바꾸지
  않았습니다. 최소 창과 한/영 UI에서 네 버튼 겹침, 숨은 컨트롤 및
  툴팁의 header 침범이 없도록 회귀 테스트를 추가했습니다.

### v0.5.5.3 배치 라벨과 첫 실행 흐름 개선

- 한국어 상단 `장면` 버튼을 실제 용도에 맞는 `배치`로 바꾸고, 콘텐츠
  제목을 `배치된 캐릭터·오브젝트`로 명확히 했습니다. 영어 상단 버튼은
  폭과 기존 사용 흐름을 위해 `Scene`을 유지하고 제목만
  `Placed Characters & Objects`로 다듬었습니다.
- 내부 `sidebar_mode="scene"`과 scene 객체 모델, 함수명 및 저장 스키마는
  변경하지 않았습니다.
- 빈 프로젝트 안내는 `리소스 가져오기 → 태그 등록에서 확인 → 리소스에서
  Player/NPC/Prop 역할 배정 → 배치에서 확인` 순서를 설명합니다. Partner는
  계속 화면 배치 대상이 아닌 `T` 교대 후보 roster입니다.
- 네 버튼의 최소 폭, 클릭, active 표시와 header/content clipping 회귀를
  자동 검사합니다. SporeHeart ground alignment 및 Player/NPC/PROP/F5 위치
  보존 로직은 변경하지 않았습니다.
- 관련 14개 모듈의 75개 테스트, `py_compile`, `--check-sidebar-ui`,
  `git diff --check`를 통과했습니다. Aseprite/Example/LAYERS 통합, 전체
  GUI 스모크, PyInstaller 및 릴리즈 패키징은 실행하지 않았습니다.

### v0.5.6 지상 대쉬 FX와 패럴렉스 오프셋 기즈모

- 대쉬 먼지는 대쉬가 지상에서 시작됐고 현재 프레임에도 실제로 지상인
  경우에만 발생합니다. 공중에서 시작한 대쉬, 점프·낙하 중 대쉬 및
  지상 대쉬 후 발판을 벗어난 프레임에는 ground dust가 추가되지 않습니다.
  기존 이동 속도, 위치, 착지 판정과 afterimage는 변경하지 않았습니다.
- `OPTIONS > BG IMAGE`에 기본 OFF인 `패럴렉스 기즈모`를 추가했습니다.
  켜면 현재 선택된 배경 이미지 레이어의 origin에 핸들이 표시되며,
  플레이 화면에서 드래그해 기존 `off_x` / `off_y` 값을 조정할 수 있습니다.
- 슬라이더와 기즈모는 같은 offset 필드를 사용하므로 어느 한쪽에서 바꾼
  값이 다른 쪽의 표시와 위치에 즉시 반영됩니다. 드래그 중에는 카메라와
  플랫폼·PROP 조작보다 기즈모가 우선합니다.
- 기즈모 표시 여부는 session-only이며 settings/project JSON에 저장되지
  않습니다. Offset 자체는 기존 BG IMAGE 슬라이더와 같은
  `ase_settings.json` 저장 경로를 사용합니다. 기즈모는 원본 이미지와
  Aseprite 파일을 수정하지 않습니다.
- Partner roster, T 교대, SporeHeart ground alignment, Player/NPC/PROP/F5
  위치 보존, `태그 등록 / OPTIONS / 배치 / 리소스` 구조를 유지했습니다.
  관련 23개 모듈의 121개 테스트, `py_compile`, `--check-sidebar-ui`,
  `git diff --check`를 통과했습니다.

### v0.5.6.1 패럴렉스 축 고정과 Undo/Redo

- 패럴렉스 기즈모는 중앙 Free 핸들 외에 빨간 X 핸들과 초록 Y 핸들을
  제공합니다. X 핸들은 `off_x`만, Y 핸들은 `off_y`만 바꾸므로 손떨림으로
  반대 축 값이 섞이지 않습니다.
- 중앙 핸들은 기존처럼 자유 이동합니다. 중앙 드래그 중 Shift를 누르면
  현재 누적 이동량이 더 큰 축만 적용하며, Shift를 놓으면 같은 드래그에서
  다시 Free 이동으로 돌아옵니다.
- 패럴렉스 offset 전용 세션 history를 추가했습니다. 기즈모 또는 offset
  slider 드래그 1회는 mouse-up에서 command 1개로 기록되며, 드래그 중
  매 프레임 history를 만들지 않습니다. X/Y 숫자 입력도 Enter commit 한
  번으로 기록됩니다.
- `Ctrl+Z`는 undo, `Ctrl+Y`와 `Ctrl+Shift+Z`는 redo입니다. 단축키는 앱
  전체에서 마지막 패럴렉스 편집에 적용되지만, offset을 포함한 텍스트
  입력 중에는 기존 입력을 우선해 가로채지 않습니다.
- History는 최대 100개이며 session-only입니다. 새 편집은 redo stack을
  비우고, 삭제되거나 교체된 레이어 command는 안전하게 건너뜁니다.
  기존 앱에 offset reset 기능이 없어 새 reset UI는 추가하지 않았습니다.
- History, redo stack, 축 상태, 기즈모 toggle은 JSON에 저장하지 않습니다.
  실제 offset만 기존 `bg.layers[].off_x/off_y` 경로로 저장하며 원본 이미지와
  Aseprite 파일은 수정하지 않습니다.
- 지상 대쉬 먼지 조건, Partner roster/T 교대, SporeHeart 정렬, 위치 보존,
  네 사이드바 모드와 clipping을 유지했습니다. 관련 25개 모듈의 138개
  테스트와 문법·사이드바·공백 검사를 통과했습니다.

### v0.5.7 지상 Intro 소환과 NPC 행동 설정

- NPC 또는 PROP 프로필을 자동 매핑할 때 `Intro`, `Spawn_Intro`, `Summon`,
  `Emerge`, `Appear`, `Entrance` 계열 태그를 독립 `INTRO` 슬롯에 등록합니다.
  공격 등의 다른 action에 붙은 `Attack_Intro`는 소환 Intro로 오인하지
  않습니다.
- NPC/PROP 생성 시 Player가 공중에 있더라도 Player의 현재 Y를 그대로
  복사하지 않습니다. 소환 X 아래에서 가장 가까운 플랫폼을 우선하고,
  없으면 월드 지면에 생성한 뒤 Intro를 한 번 재생합니다. 기존 pivot 및
  visible-bottom ground alignment는 그대로 적용됩니다.
- `OPTIONS > AI & COMBAT > NPC 행동`에서 NPC 프로필별 행동을 클릭해
  순환 선택할 수 있습니다.

  - `균형`: 기존의 다양한 랜덤 행동
  - `대기`: 제자리 유지
  - `추적`: 일정 거리 밖에서 Player를 따라감
  - `공격`: Player를 추적하고 근거리에서 공격
  - `경비`: 가까운 Player에 대응하고 멀어지면 생성 지점으로 복귀
  - `순찰`: 생성 지점 주변을 좌우로 순찰
  - `회피`: Player가 가까우면 반대 방향으로 이동

- 행동은 프로필의 선택적 `ai_behavior` 필드로 기존 project schema 안에
  저장됩니다. 구형 프로젝트나 잘못된 값은 `balanced`로 해석하며, settings
  및 원본 Aseprite에는 기록하지 않습니다.
- Partner roster/T 교대, 지상 대쉬 먼지, 패럴렉스 기즈모/history,
  SporeHeart ground alignment, 위치 보존, corpse/prop 파괴와 사이드바
  clipping을 유지했습니다. Stub/temp 기반 33개 모듈의 181개 테스트와
  문법·사이드바·공백 검사를 통과했습니다.

### v0.5.7.1 NPC 전투 판정 / Intro 재생 핫픽스

- NPC 공격은 시작 시 방향과 action을 잠그고 애니메이션이 끝날 때까지
  행동 판단이나 피격 action으로 덮어쓰지 않습니다. 종료 후 650ms
  recovery/cooldown 동안 재공격하지 않으며 이 런타임 상태는 저장하지
  않습니다.
- 공격 판정은 Aseprite의 `Hit` Slice가 있으면 이를 우선 사용합니다.
  없으면 NPC 지면 좌표 기준 전방 125x80 사각형을 사용하며, 전체 공격
  시간의 35~60%를 active window로 봅니다. 같은 공격 instance는
  Player에게 최대 한 번만 5 damage를 적용합니다.
- 행동별 공격 정책은 기존과 같습니다. `균형`은 랜덤 공격 선택 시,
  `공격`은 추적 후 근거리에서, `경비`는 감지 범위 안의 근거리에서
  lock/cooldown이 적용된 공격을 합니다. `대기`, `추적`, `순찰`, `회피`는
  공격하지 않습니다.
- `OPTIONS > AI & COMBAT > NPC 행동` 아래의 `Intro 다시 재생` 버튼은
  배치에서 선택된 살아 있는 NPC를 우선하고, 없으면 현재 NPC 프로필의
  살아 있는 인스턴스들을 재생합니다. 새 NPC를 만들거나 위치·지면 정렬,
  target count, PROP 또는 Partner roster를 바꾸지 않습니다. 공격 잠금
  중인 NPC는 모션 보호를 위해 제외하고 안내합니다.
- `ai_behavior`, `INTRO` mapping과 project schema 2는 그대로이며 attack
  lock/cooldown과 replay status는 session-only입니다.
- 후속 TODO: `AI & COMBAT / NPC 행동 / Intro replay / 전투 파라미터`를
  더 직관적인 패널로 묶는 Settings UI grouping/layout 정리.
- 실제 타격감, 대형/소형 sprite별 Hit Slice와 fallback 범위, 공격 후
  간격, 한/영 최소 창 및 deep scroll은 GUI에서 수동 확인해야 합니다.

### v0.5.7.2 NPC Combo / Intro Lock / 소환 해제 / 키 안내

- NPC 프로필에서 실제 mapping이 있는 `ComboAttack_1~N`을 숫자 순서로
  확인합니다. 1번부터 연속된 구간만 체인으로 사용하므로 1·3만 있으면
  1타만, 2만 있으면 combo 없음으로 처리합니다. `Attack`만 있는 리소스는
  1타 mapping으로 사용할 수 있고 `Attack_Intro`, `ComboAttack_Intro`,
  숫자가 아닌 suffix는 제외합니다.
- Combo 전체가 하나의 attack lock과 시작 방향을 공유합니다. 각 segment는
  자신의 애니메이션 시간 기준 35~60% active window와 1회 hit guard를
  가지며 다음 segment에서 guard가 초기화됩니다. Player가 계속 범위에
  있으면 여러 타를 맞을 수 있고, 최종 segment 뒤에만 650ms cooldown이
  시작됩니다.
- 소환 및 수동 재생 Intro 동안 NPC/PROP의 X/Y와 속도를 지면 좌표에
  고정합니다. AI 추적·공격·점프·순찰·회피와 다른 action은 Intro를
  덮어쓰지 못하며, 이미 Intro 중이면 버튼은 재시작 대신 안내합니다.
  Attack lock 중 Intro replay 차단 정책도 유지됩니다.
- `배치` action 영역에 살아 있는 NPC 전용 `소환 해제 / DESPAWN`을
  추가했습니다. 선택 인스턴스를 즉시 `ai_list`에서 제거하고 전체
  `target_ai_count`를 1 줄여 자동 보충을 막습니다. 시체·Player·PROP과
  Partner roster, profile/source에는 영향이 없습니다. 시체는 기존
  `시체 삭제`를 사용합니다.
- 하단 key guide를 sidebar content 분기 밖의 공통 HUD로 옮겼습니다.
  태그 등록, OPTIONS, 배치, 리소스에서 동일하게 보이고 현재
  ATTACK/DASH/JUMP/SWAP mapping과 언어를 반영합니다. 좁은 화면에서는
  여러 줄로 배치하며 F10 성능 overlay 중에도 안내를 유지합니다.
- 별도 input preset UI가 아직 없으므로 기존 사용자 키를 바꾸거나
  `빠른 액션 / Fast Action` 프리셋을 강제 추가하지 않았습니다. 후속:
  Action Platformer preset 선택 UI, gamepad 감지, button mapping,
  keyboard/controller 동시 guide, deadzone과 preset 저장/불러오기.
- Stub/temp 기반 대상 25개 모듈의 126개 테스트와 문법·사이드바·공백
  검사를 통과했습니다. 실제 Aseprite/SporeHeart 통합, 전체 GUI,
  패키징·커밋·태그는 실행하지 않았습니다.

### v0.5.7.3 프로그램 단축키 안내 복원 / 입력 안내 분리

- v0.5.7.2 공통 Key Guide가 새 목록을 `ATTACK/DASH/JUMP/SWAP/F5/F10`
  만으로 다시 만들면서 표시에서 누락했던 기존 프로그램 단축키 안내를
  복원했습니다. 입력 기능 자체는 삭제되지 않았으며 새 단축키는 만들지
  않았습니다.
- 하단 HUD를 `캐릭터 / Player`와 `프로그램·편집 / App·Editor` 두
  그룹으로 분리했습니다. 캐릭터 그룹은 현재 사용자 `key_map`에서
  공격, 대시, 점프, 교대, 스킬 1~3을 읽습니다. 앱 그룹은 실제 이벤트
  처리와 일치하는 `P` 일시정지, `O` 한 프레임, `[ ]` 현재 재생 속도,
  `F5` 새로고침, `F10` 성능 표시, `H` 히트박스, `R-Drag` 카메라 이동,
  `F` 카메라 복귀를 표시합니다.
- 두 그룹은 태그 등록, OPTIONS, 배치, 리소스에서 같은 공통 overlay로
  표시됩니다. 최소 폭에서는 그룹별로 자동 줄바꿈하며 sidebar scroll
  밖에 고정됩니다. F10 overlay 중에도 안내와 tooltip을 유지합니다.
- `빠른 액션 / Fast Action` 방향은 공격·대시·점프·교대 등 캐릭터
  조작 preset 후보에만 해당합니다. 앱/편집 단축키를 숨기거나 바꾸지
  않으며 현재 사용자 mapping도 덮어쓰지 않습니다.
- Controller 지원은 후속 TODO입니다: 입력 장치 감지, button mapping,
  deadzone, keyboard/controller guide 분리, preset 저장/불러오기.
- 대상 21개 모듈의 102개 테스트, 문법 검사, sidebar UI 검사와 공백
  검사를 통과했습니다. 전체 파일 독립 실행에서는 59개 모듈이
  통과했고 기존 비관련 실패 3개만 남았습니다.

### v0.5.7.4 시체 지면 정렬 / Death 상태 안정화

- NPC corpse update는 기존에 PROP이 아닌 시체의 `vy`만 0으로 만들고
  즉시 반환했습니다. 공중 피격·넉백 중 death action으로 전환되면 당시
  actor Y가 그대로 고정되는 원인이었습니다.
- Death 전환 시 현재 NPC X와 Y 아래에서 가장 가까운 플랫폼을 찾고,
  없으면 `world_ground_y`에 논리 actor 좌표를 snap합니다. X와 원래
  `spawn_y`는 유지하고 `y`, `vx/vy`, `grounded`만 안정화합니다.
  기존 pivot/visible-bottom/ground offset은 렌더 정렬에 계속 적용되므로
  SporeHeart 보정 정책과 분리됩니다.
- 과거 상태나 refresh 복원 등으로 공중에 남은 corpse는 update에서 같은
  helper로 한 번 보정합니다. 이미 올바른 지면에 있으면 위치를 다시
  움직이지 않아 death animation의 논리 기준점이 흔들리지 않습니다.
- Death는 Intro, Combo, Attack lock과 segment hit/cooldown runtime을
  정리한 뒤 최종 우선 상태가 됩니다. 반복 death 호출은 기존처럼 no-op
  이며 corpse identity/count를 중복 생성하지 않습니다.
- Delete Corpse, Delete All Corpses, corpse filter/selection, F5 위치
  snapshot, 살아 있는 NPC Despawn과 PROP 파괴 경로는 변경하지 않았습니다.
  Despawn은 여전히 corpse를 만들지 않습니다.
- Corpse fall/ragdoll 연출은 추가하지 않았습니다. 후속 작업에서는
  선택적으로 death fall animation을 도입할 수 있지만 이번 버전은
  공중 고정 제거와 안정성을 우선합니다.
- 신규 14개를 포함한 대상 27개 모듈의 135개 테스트와 문법·사이드바·
  공백 검사를 통과했습니다. 전체 파일 독립 실행에서는 61개 모듈이
  통과했고 기존 비관련 실패 3개만 남았습니다.

## 🎮 조작 방법 (기본 단축키)

- **이동:** `방향키 (Left / Right)`
- **점프:** `Space` (아래 방향키 + 점프 시 플랫폼 하강)
- **대시:** `X` (공중 대시 지원, 쿨타임 존재)
- **공격:** `Z` (연속 입력 시 콤보 발동, 방향키 아래 + Z = 파워밤)
- **교대 (Swap):** `T`
- **합격기 (Synergy):** `E` (현재 SYNERGY 키 매핑 기준)
- **살아 있는 NPC 회수:** `G`
- **일시정지 / 1프레임 진행:** `P` / `O`
- **화면 이동:** 빈 공간 `마우스 우클릭` + 드래그
- **확대/축소:** `마우스 휠`

## 📁 파일 구조
- `ase_viewer.py`: 뷰어 메인 로직 코드
- `ase_project.json`: 불러온 소스, 캐릭터 프로필, 액션 매핑, 플랫폼(지형) 데이터 저장
- `ase_settings.json`: 물리 엔진 계수, 커스텀 단축키, 카메라 줌, 다중 배경(패럴랙스) 세팅 저장
- `ase_debug.log`: 성능 모니터링 및 로드 에러 추적을 위한 디버그 로그 파일
- `tests/`: 저장 및 설정 영속화 회귀 테스트
- `MANUAL_TEST_CHECKLIST.md`: 실제 GUI와 배포본 수동 회귀 점검표
- `resources/examples/`: 내부 EX 1·EX 2용 Aseprite 소스와 배경 복사본 및 출처 기록

### v0.5.7.5 교체 가시성 / 입력 안내 / 안전한 NPC 회수

- `T` 교체 중 `Swap_Exit`을 재생하는 이전 캐릭터는 임시 연출 객체로만
  유지하고, 새 Player보다 먼저 그립니다. 겹치는 프레임에서도 조작 중인
  Player가 전면에 보이며 NPC/PROP/Partner 목록과 저장 구조는 바뀌지 않습니다.
- 캐릭터 키 가이드가 현재 `SYNERGY` 매핑을 읽어 `E 합격기 / E Synergy`
  를 표시합니다. 사용자가 키를 바꾸면 표시도 따라가며 매핑이 없으면
  임의의 기본 키를 만들어 표시하지 않습니다.
- `G` 회수는 살아 있고 표시 중인 일반 NPC만 Player 주변으로 옮깁니다.
  죽은 NPC, 시체, PROP, Partner, 임시 연출 객체는 이동하지 않으며 대상이
  없을 때도 안전하게 안내만 표시합니다.
- 앱 단축키의 `O`는 `1프레임 진행 / Step 1 frame`으로 명확히 표시하고,
  툴팁에서 일시정지 중 애니메이션 한 프레임 진행 기능임을 안내합니다.
- 이번 변경은 프로젝트/설정 스키마를 바꾸지 않습니다. 실제 GUI에서
  겹침과 툴팁을 최종 확인하는 항목은 수동 체크리스트에 남겨 두었습니다.
- Character/App 가이드 분리와 상용 게임명을 UI에 사용하지 않는 정책을
  유지했습니다. 컨트롤러 감지·매핑·듀얼 가이드는 후속 TODO입니다.
- `ase_project.json`, `ase_settings.json`, `build/`, `dist/`, 실제 리소스와
  Aseprite 원본은 수정하지 않았습니다. 대상 23개 모듈 108개 테스트,
  문법 검사, `--check`, `--check-sidebar-ui`, 헤드리스 렌더 검사를
  통과했습니다. 전체 독립 실행은 65개 모듈·367개 테스트가 통과했고
  기존 비관련 실패 3개만 남았습니다.

### v0.5.8 Settings UI/UX Reorganization

- OPTIONS 상단에 스크롤과 분리된 6개 세션 전용 섹션 탐색기를 추가했습니다:
  `빠른 설정`, `입력 / 조작`, `AI / 전투`, `배경 / 패럴랙스`,
  `보기 / 디버그`, `프로젝트 / 고급`.
- 기존 11개 accordion과 실제 편집 기능은 제거하지 않고 관련 섹션에
  정확히 한 번씩 배치했습니다. 섹션 선택은 저장하지 않으므로 기존
  settings/project schema 2와 사용자 JSON 형식이 바뀌지 않습니다.
- Quick은 현재 선택과 리소스→태그→역할→배치→AI 흐름을 요약합니다.
  Input은 실제 key map과 Character/App 가이드, Fast Action의 캐릭터
  조작 한정 범위, controller 후속 TODO를 안내합니다.
- AI / Combat에는 NPC 리소스, 행동 선택, Intro 다시 재생, ComboAttack과
  H hitbox 안내를 모았습니다. Background에는 이미지 레이어, 패럴랙스,
  X/Y offset, gizmo, 축 잠금과 undo/redo 안내를 모았습니다.
- View / Debug에는 P/O/[ ]/F10/H, 카메라와 하단 App guide 설명을,
  Advanced에는 상단 프로젝트 도구/F5 안내와 기존 PROP·물리 설정을
  배치했습니다.
- 섹션 탐색기는 OPTIONS 상단에 고정되고 본문만 별도 clipping/scroll을
  사용합니다. 섹션 전환 시 이전 scroll, key binding 대기, 숫자 입력을
  정리해 stale rect 클릭을 막습니다. 긴 한/영 안내는 두 줄로 wrap합니다.
- v0.5.7.5의 Character/App guide, Synergy, O step label, T swap front,
  G corpse 제외와 Combo/Intro/Despawn/Corpse snap, Partner, SporeHeart
  pivot, grounded dash dust, parallax history 정책을 유지합니다.
- Aseprite CLI, 실제 리소스 통합, 사용자 조작 GUI, 패키징, 릴리즈,
  커밋과 태그는 실행하지 않았습니다. 보호 대상 사용자 JSON, build/dist,
  실제 resources와 Aseprite 원본도 수정하지 않았습니다.
- 대상 31개 독립 모듈 133개 테스트와 pycompile, `--check`,
  `--check-sidebar-ui`, diff 검사가 통과했습니다. 전체 파일별 실행에서는
  총 383개 테스트를 실행했고 71개 모듈이 전부 통과했으며, 기존 비관련
  실패 모듈 3개만 남았습니다.

### v0.5.8.1 Settings Tab Consolidation / Header Order Polish

- 고정 sidebar 버튼 표시 순서를 `태그 등록 → 배치 → 리소스 → 옵션`으로
  변경했습니다. 내부 `mapping/scene/resources/settings` mode 문자열과
  동일 버튼 재클릭·exclusive mode 정책은 유지됩니다.
- OPTIONS의 6개 탭을 한 줄 3개로 통합했습니다:
  `조작·앱 / Controls & App`, `장면·전투 / Scene & Combat`,
  `화면·배경 / View & Background`. 탐색기 높이는 76px에서 42px로
  줄어 본문 공간을 늘렸습니다.
- Quick과 Advanced는 UI 탭에서 제거했습니다. LANGUAGE와 CONTROLS는
  조작·앱으로, NPCS/AI & COMBAT/PROPS/PHYSICS는 장면·전투로,
  BG IMAGE/BG COLOR/CAMERA/LAYERS/JUICE & VFX는 화면·배경으로
  이동했습니다. 기존 카테고리는 누락·중복 없이 한 탭에 한 번씩 있습니다.
- 이전 session 값은 안전하게 변환합니다: Quick/Input→조작·앱,
  AI/Advanced→장면·전투, Background/View→화면·배경. 잘못된 값은
  조작·앱으로 돌아가며 JSON에는 여전히 section을 저장하지 않습니다.
- 조작·앱은 언어, 실제 key map, Character/App guide, Synergy, 명확한 O
  문구, 캐릭터 한정 Fast Action과 controller TODO를 안내합니다.
  장면·전투는 NPC 행동, Intro, Combo, Despawn/corpse, PROP/물리를,
  화면·배경은 parallax/gizmo/history, 카메라, 레이어, VFX와 F10/H를
  함께 제공합니다.
- v0.5.8의 고정 navigator/body clipping, 전환 시 scroll·입력 초기화,
  deep-scroll tooltip 정책과 기존 전투·교대·리콜·시체·패럴랙스 기능을
  유지했습니다.
- 대상 30개 독립 모듈 125개 테스트와 pycompile, `--check`,
  확장된 `--check-sidebar-ui`, diff 검사가 통과했습니다. 전체 파일별
  실행에서는 총 391개 테스트를 실행했고 73개 모듈이 전부 통과했으며,
  기존 비관련 실패 모듈 3개만 남았습니다.

### v0.5.8.2 Settings Control Reset / Tab Semantics / UI Text Polish

- 숫자 입력이 함께 있는 모든 설정 슬라이더에 `초기화 / Reset` 버튼을
  추가했습니다. 버튼은 같은 행의 값 하나만 생성자·load fallback과
  일치하는 검증된 기본값으로 되돌리고 기존 `save_settings()` 경로를
  사용합니다. 기본값을 확인할 수 없는 항목은 안전하게 동작하지 않습니다.
- 배경 레이어 Offset X/Y 초기화는 다른 축을 보존하며 기존 parallax
  history에 기록됩니다. 따라서 Ctrl+Z/Ctrl+Y로 초기화 전후를 오갈 수
  있고, invalid active layer에서는 저장 없이 안내만 유지합니다.
- `LAYERS`와 `JUICE & VFX`를 `장면·전투`로 이동했습니다.
  `화면·배경`은 BG IMAGE/BG COLOR/CAMERA 및 패럴랙스 중심이며, 세 탭과
  상단 `태그 등록 / 배치 / 리소스 / 옵션` 순서는 그대로입니다.
- Player HUD와 메인 루프에 중복되어 있던 대시 잔여 막대 중 Player HUD
  하나만 남겼습니다. 하단 Character guide의 Dash 키, 실제 충전·소모,
  지상 대시 먼지 규칙은 변경하지 않았습니다. F10 성능 패널은 대시
  잔여수를 별도로 그리지 않습니다.
- Controls action label은 내부 key-map 키를 바꾸지 않고 한/영 표시만
  공통 번역합니다. 공격/대시/점프/교대/스킬 1~3/합격기와 프로그램
  단축키 문구를 정리했으며 키 이름은 원문 그대로 표시합니다.
- 각 탭에 작은 의미 요약을 추가하고, 배경 없음·NPC 없음·키맵 없음·
  Synergy 미지정 문구를 명확히 했습니다. Reset과 삭제 문구/색은
  구분되며 slider/numeric/reset hit rect는 서로 겹치지 않습니다.
- 프로젝트 schema 2와 session-only 탭 상태를 유지합니다. T 교대 전면,
  G의 corpse 제외, O 한 프레임, Combo/Intro/Despawn/corpse snap,
  Partner/SporeHeart/dash dust/parallax/sidebar 정책도 유지합니다.
- Aseprite CLI, 실제 리소스 통합, 전체 사용자 조작 GUI, PyInstaller,
  릴리즈/ZIP, 커밋/태그는 실행하지 않았고 사용자 JSON, build/dist,
  실제 resources와 Aseprite 원본은 수정하지 않았습니다.
- 대상 35개 독립 모듈의 146개 테스트, pycompile, `--check`,
  `--check-sidebar-ui`, diff 검사가 통과했습니다. 전체 파일별 실행은
  81개 모듈·412개 테스트 중 78개 모듈이 통과했고, 기존 비관련 실패인
  layer scroll 기대값, empty-slice reason, 누락된 SporeHeart fixture만
  남았습니다.

### v0.5.8.3 Pre-release Debug Cleanup / Icon Integration

- 누적 baseline 실패 세 건을 정리했습니다. LAYERS scroll 테스트는
  오래된 고정 `+100px` 기대를 실제 content/viewport 경계 조건으로
  교체했고, Slice export 테스트는 상태를 바꾼 mock source의 캐시와 필수
  target name을 올바르게 구성합니다. 실제 SporeHeart fixture가 없으면
  `ASE_VIEWER_SPOREHEART_FIXTURE` 안내와 함께 통합 테스트 한 건만 skip합니다.
- 전체 81개 테스트 파일의 412 tests가 통과했고 SporeHeart 실물 통합
  1건만 skip했습니다. pycompile, 소스 `--check`,
  `--check-sidebar-ui`, `git diff --check`도 통과했습니다.
- 사용자 제작 `Icon.png`를 원본 그대로 보존하면서 16/32/48/64/128/
  256px RGBA 이미지를 포함한 `Icon.ico`로 변환했습니다. PyInstaller
  spec은 상대 경로 `Icon.ico`만 EXE icon으로 사용합니다.
- 기존 `build/`와 `dist/`는 건드리지 않고 별도 icon build를 만들었으며
  PE의 RT_ICON/RT_GROUP_ICON 리소스 포함을 확인했습니다. 다만 현재 빌드
  Python의 Tcl/Tk 설치가 초기화되지 않아 PyInstaller가 `tkinter`를
  제외했고, EXE `--check`가 60초 이내 종료되지 않았습니다. 따라서 이
  산출물은 배포 후보가 아니며 release ZIP과 ZIP SHA-256은 생성하지
  않았습니다.
- 진단용 EXE:
  `dist_v0.5.8.3_icon_final/ase_viewer.exe` (25,300,425 bytes),
  SHA-256
  `B2BAD580507CE751ACFE2C2DD7316E688D96C03E7890EBE7A999D1D4FACFA2BC`.
  이 해시는 실패한 진단 산출물 식별용이며 배포 승인 해시가 아닙니다.
- 빌드 명령은 정상 Tcl/Tk가 포함된 Python 3.12 환경에서 다음과 같이
  다시 실행해야 합니다:
  `python -m PyInstaller --clean --noconfirm --workpath build_v0.5.8.3_icon --distpath dist_v0.5.8.3_icon ase_viewer.spec`.
  EXE `--check`와 `--check-sidebar-ui`가 모두 종료 코드 0일 때만 ZIP과
  배포 SHA-256을 생성합니다.

> 이 빌드는 코드 서명 인증서를 적용하지 않은 테스트/중간 배포용
> 빌드입니다. Windows에서 “알 수 없는 게시자” 또는 SmartScreen 경고가
> 표시될 수 있습니다. 배포된 ZIP의 SHA-256 값을 확인한 뒤 실행해 주세요.
>
> This is an unsigned interim/test build. Windows may show an Unknown
> Publisher or SmartScreen warning. Verify the SHA-256 hash of the distributed
> ZIP before running it.

### v0.5.8.3 Example Resources Bundled Build

- 회사 내부 배포용 `ase_viewer_v0.5.8.3_with_examples.zip`에는 EXE 옆
  `resources/examples/**`를 외부 폴더로 포함합니다. EX1, EX2, shared의
  10개 파일(필수 실행 리소스 9개와 내부 안내 1개), 총 2,790,927
  bytes입니다.
- 포함 범위는 `resources/examples`뿐입니다. 그 밖의 `resources`,
  `ase_project.json`, `ase_settings.json`, 사용자 데이터, tests, source,
  build cache, `.git`, `.gemini`는 포함하지 않습니다.
- 기존 `ase_viewer_v0.5.8.3_tkfix.zip`은 예제를 포함하지 않아 EX1/EX2
  사용 시 missing resources 안내가 발생할 수 있습니다. 새
  `with_examples` 패키지만 회사 내부 EX 기능 사용 배포 후보입니다.
- 앱은 frozen EXE 디렉터리를 기준으로 외부 리소스를 이미 지원하므로
  spec이나 앱 코드를 바꾸거나 재빌드하지 않았습니다. Tcl/Tk 8.6.12와
  `Icon.ico`가 검증된 `dist_v0.5.8.3_tkfix2/ase_viewer.exe`를 그대로
  사용했습니다.
- staging 폴더에서 EXE `--check`는 `example_resources=9/9`,
  `tkinter_tcl=8.6.12`와 종료 코드 0을 반환했습니다.
  `--check-sidebar-ui`도 종료 코드 0이며 잔류 프로세스는 없습니다.
- `tests.test_packaged_paths` 4건과 `tests.test_examples` 12건이
  통과했습니다. 실제 EX1/EX2 리소스 해시, 두 Aseprite 소스 준비,
  EX2의 6개 패럴랙스 레이어 적용·렌더와 실패 시 현재 프로젝트 보존을
  검증합니다.
- ZIP 크기는 20,612,661 bytes, SHA-256은
  `7F5D7B75014CC355D5DC7D06499429B3BE7A3342FE8514871C4CE57622DD05B8`
  입니다. ZIP 자체에 자신의 해시를 포함할 수 없으므로 외부 README와
  동반 `.sha256` 파일의 값을 기준으로 확인합니다.

> 이 빌드는 코드 서명 인증서를 적용하지 않은 테스트/중간 배포용
> 빌드입니다. Windows에서 “알 수 없는 게시자” 또는 SmartScreen 경고가
> 표시될 수 있습니다. 배포된 ZIP의 SHA-256 값을 확인한 뒤 실행해 주세요.
>
> This is an unsigned interim/test build. Windows may show an Unknown
> Publisher or SmartScreen warning. Verify the SHA-256 hash of the distributed
> ZIP before running it.

코드 서명과 SmartScreen 평판 대응은 후속 TODO입니다.

### v0.5.8.3.1 Tcl/Tk Runtime Build Fix

- 개발 환경 `C:\Dev\aitsb\Scripts\python.exe`는 Python 3.12.13 가상환경이며
  `tkinter` import, 숨긴 `Tk()` 생성, Tcl/Tk 8.6.12 초기화가 정상입니다.
  기반 Python의 `tcl\tcl8.6`, `tcl\tk8.6`, `DLLs\_tkinter.pyd`,
  `DLLs\tcl86t.dll`, `DLLs\tk86t.dll`도 확인했습니다.
- 직전 실패는 Python 설치 결함이 아니라 제한된 빌드 실행 환경에서
  PyInstaller의 Tcl 초기화가 막혀 표준 tkinter hook이 제외된 진단
  산출물이었습니다. 정상 환경의 PyInstaller 6.21.0 clean build에서는
  `hook-_tkinter.py`와 `pyi_rth__tkinter.py`가 자동 적용됐습니다.
- 별도 Tcl/Tk 경로, 수동 binaries/datas, 사용자 runtime hook은 추가하지
  않았습니다. 기존 one-file/windowed spec과 `Icon.ico` 설정을 유지했습니다.
- frozen `--check`는 파일 선택창이나 message box를 열지 않습니다. 숨긴
  Tk root로 Tcl patchlevel만 검사한 뒤 즉시 destroy하며, 배포 ZIP에서
  의도적으로 제외한 예제 9개는 외부 선택 리소스로 보고합니다. 소스
  `--check`는 기존처럼 저장소의 예제 9개를 엄격하게 확인합니다.
- 최종 후보 `dist_v0.5.8.3_tkfix2/ase_viewer.exe`는 두 smoke check 모두
  종료 코드 0이며, frozen 출력에서 `tkinter_tcl=8.6.12`를 확인했습니다.
  EXE 크기는 18,136,854 bytes, SHA-256은
  `299EF579A110C76C85A4122A6363B81E9360A41957E2D2AD7EFE001F877D0DBF`
  입니다.
- 직전 `dist_v0.5.8.3_icon_final/ase_viewer.exe`는 계속 배포 금지 진단
  산출물입니다. 새 ZIP의 승인 해시는 함께 배포되는 `.sha256` 파일과
  최신 작업 보고에서 확인해야 합니다.
- 배포 ZIP `ase_viewer_v0.5.8.3_tkfix.zip`은 17,907,557 bytes이며
  SHA-256은
  `FC40F85DF40287302DABAD77CDDF4241CF86F9C00E9D4A2A781B741BD4BB9A3D`
  입니다. ZIP 자체에 자신의 해시를 포함할 수 없으므로 이 값은 외부
  README와 동반 `.sha256` 파일을 기준으로 확인합니다.

> 이 빌드는 코드 서명 인증서를 적용하지 않은 테스트/중간 배포용
> 빌드입니다. Windows에서 “알 수 없는 게시자” 또는 SmartScreen 경고가
> 표시될 수 있습니다. 배포된 ZIP의 SHA-256 값을 확인한 뒤 실행해 주세요.
>
> This is an unsigned interim/test build. Windows may show an Unknown
> Publisher or SmartScreen warning. Verify the SHA-256 hash of the distributed
> ZIP before running it.
