# Aseprite Project Viewer v19

Aseprite 프로젝트를 실시간으로 시뮬레이션하고 멀티 캐릭터 태그 매핑을 지원하는 뷰어입니다.

## 실행 조건
1. **Python 3.x**가 설치되어 있어야 합니다.
2. **Aseprite**가 설치되어 있어야 합니다.

## 설치 및 실행 방법
1. 필수 라이브러리 설치:
   ```bash
   pip install -r requirements.txt
   ```
2. 프로그램 실행:
   ```bash
   python ase_viewer.py
   ```
3. 처음 실행 시 `Aseprite.exe` 위치를 묻는 창이 뜨면, 설치된 경로를 선택해 주세요. (이후 `config.json`에 저장됨)

## 주요 기능
- **+ SOURCE**: 현재 캐릭터 프로필에 새로운 Aseprite 파일(무기, 이펙트 등) 추가.
- **+ NPC**: 새로운 AI 캐릭터 프로필 생성.
- **Settings**: 배경 시차(Parallax), 투명도(Alpha), 물리 엔진 설정 조절.
