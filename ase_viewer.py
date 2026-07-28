import pygame
import subprocess
import json
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
import re
import random
import math
import traceback
import tempfile
import copy
import hashlib
import unicodedata
import time
from collections import OrderedDict, deque
from types import SimpleNamespace

APP_ROOT = os.path.dirname(os.path.abspath(sys.executable if getattr(sys, "frozen", False) else __file__))
RESOURCE_ROOT = getattr(sys, "_MEIPASS", APP_ROOT)
ASEPRITE_TIMEOUT_SECONDS = 120
APP_VERSION = "v0.5.8.3"
APP_TITLE = "Aseprite Action Viewer"
SIDEBAR_WIDTH = 450
TOP_UI_HEIGHT = 70
MAPPING_SLOT_TOP = TOP_UI_HEIGHT + 70
MAPPING_TAG_TOP = 475
MAPPING_SLOT_HEIGHT = MAPPING_TAG_TOP - MAPPING_SLOT_TOP - 35
SIDEBAR_MAPPING = "mapping"
SIDEBAR_SETTINGS = "settings"
SIDEBAR_SCENE = "scene"
SIDEBAR_RESOURCES = "resources"
SIDEBAR_MODES = {
    SIDEBAR_MAPPING, SIDEBAR_SETTINGS, SIDEBAR_SCENE, SIDEBAR_RESOURCES,
}
SCENE_FILTER_ALL = "all"
SCENE_FILTER_PLAYER = "player"
SCENE_FILTER_NPC = "npc"
SCENE_FILTER_PROP = "prop"
SCENE_FILTER_CORPSE = "corpse"
SCENE_OBJECT_FILTERS = (
    SCENE_FILTER_ALL,
    SCENE_FILTER_PLAYER,
    SCENE_FILTER_NPC,
    SCENE_FILTER_PROP,
    SCENE_FILTER_CORPSE,
)
DEFAULT_WINDOW_SIZE = (1350, 850)
MIN_WINDOW_SIZE = (1100, 720)
WINDOW_MARGIN = (80, 80)
_SHOWN_ERROR_KEYS = set()
_LOGGED_ERROR_KEYS = set()
LANG_KO = "ko"
LANG_EN = "en"
_CURRENT_LANGUAGE = LANG_KO
_MISSING_TRANSLATION_KEYS = set()

TRANSLATIONS = {
    LANG_KO: {
        "common.confirm": "확인",
        "common.cancel": "취소",
        "common.export": "출력",
        "common.save": "저장",
        "common.load": "불러오기",
        "common.new": "새로 만들기",
        "common.spawn": "소환",
        "common.none": "없음",
        "common.add": "추가",
        "common.remove": "삭제",
        "common.reset": "초기화",
        "common.press_key": "키 입력",
        "common.refresh": "새로고침",
        "common.clear": "지우기",
        "common.up": "위",
        "common.down": "아래",
        "ui.setup": "⚙ 옵션",
        "ui.edit_platform": "플랫폼 편집",
        "ui.add_platform": "+ 플랫폼",
        "ui.add_box": "+ 박스",
        "ui.add_source": "+ 소스",
        "ui.add_npc": "+ NPC",
        "ui.add_prop": "+ PROP",
        "ui.ranged_combo": "원거리 콤보",
        "ui.swap_target": "교대 대상:",
        "ui.roaming_target": "배회 대상:",
        "ui.shake_power": "흔들림 강도",
        "ui.debris_force": "파편 힘",
        "ui.camera_offset": "카메라 오프셋",
        "ui.show_guide": "640x360 가이드 표시",
        "ui.layers": "레이어:",
        "ui.load_image": "이미지 불러오기",
        "ui.loop_x": "가로 반복",
        "ui.dash_velocity": "대시 속도",
        "ui.jump_power": "점프 힘",
        "ui.powerbomb_speed": "파워밤 속도",
        "ui.platform_alpha": "플랫폼 투명도",
        "ui.ai_count": "AI 수",
        "ui.npc_max_hp": "NPC 최대 HP",
        "ui.npc_behavior": "NPC 행동",
        "guide.attack": "공격",
        "guide.dash": "대시",
        "guide.jump": "점프",
        "guide.swap": "교대",
        "guide.skills": "스킬",
        "guide.synergy": "합격기",
        "guide.refresh": "새로고침",
        "guide.pause": "일시정지",
        "guide.step": "1프레임 진행",
        "guide.speed": "속도 조절",
        "guide.hitbox": "히트박스",
        "guide.camera": "카메라 이동",
        "guide.performance": "성능 표시",
        "guide.camera_reset": "카메라 복귀",
        "control.skill_1": "스킬 1",
        "control.skill_2": "스킬 2",
        "control.skill_3": "스킬 3",
        "control.summon": "소환",
        "control.hit_1": "피격 1",
        "control.unavailable": "조작키 설정을 불러오지 못했습니다.",
        "guide.group.character": "캐릭터",
        "guide.group.app": "프로그램/편집",
        "tooltip.guide.step": "일시정지 중 애니메이션을 정확히 1프레임 진행합니다.",
        "status.recall_live_npcs": "살아 있는 NPC {count}개를 플레이어 주변으로 불러왔습니다.",
        "status.recall_no_live_npcs": "불러올 수 있는 살아 있는 NPC가 없습니다.",
        "ui.replay_npc_intro": "Intro 다시 재생",
        "npc_behavior.balanced": "균형",
        "npc_behavior.idle": "대기",
        "npc_behavior.follow": "추적",
        "npc_behavior.aggressive": "공격",
        "npc_behavior.guard": "경비",
        "npc_behavior.patrol": "순찰",
        "npc_behavior.flee": "회피",
        "status.npc_intro_selected": "선택 NPC의 Intro를 다시 재생했습니다.",
        "status.npc_intro_profile": "현재 프로필 NPC의 Intro를 다시 재생했습니다. ({count}개)",
        "status.npc_intro_no_target": "Intro를 재생할 NPC가 없습니다.",
        "status.npc_intro_missing": "이 프로필에는 Intro 태그가 없습니다.",
        "status.npc_intro_attack_locked": "공격 중인 NPC는 Intro를 다시 재생할 수 없습니다.",
        "status.npc_intro_already_playing": "이 NPC는 이미 Intro를 재생 중입니다.",
        "ui.attack_forward": "공격 전진",
        "ui.enable_shake": "화면 흔들림",
        "ui.enable_ghost": "잔상 효과",
        "ui.x_offset": "X 오프셋",
        "ui.y_offset": "Y 오프셋",
        "ui.scale": "크기",
        "ui.alpha": "투명도",
        "ui.parallax": "패럴랙스(Parallax)",
        "ui.parallax_gizmo": "패럴렉스 기즈모",
        "status.parallax_gizmo_on": "핸들을 드래그해 선택 레이어 오프셋을 조정하세요.",
        "status.parallax_gizmo_select": "기즈모를 사용하려면 이미지 레이어를 선택하세요.",
        "status.parallax_undo": "패럴렉스 오프셋을 되돌렸습니다.",
        "status.parallax_redo": "패럴렉스 오프셋을 다시 적용했습니다.",
        "status.parallax_nothing_undo": "되돌릴 패럴렉스 편집이 없습니다.",
        "status.parallax_nothing_redo": "다시 적용할 패럴렉스 편집이 없습니다.",
        "tooltip.parallax_gizmo": "중앙은 자유 이동, X/Y 화살표는 해당 축만 이동합니다.\nShift+중앙 드래그는 큰 이동 축을 고정하며 원본 파일은 수정하지 않습니다.",
        "selection.current": "현재 선택",
        "selection.scene": "배치된 캐릭터·오브젝트",
        "selection.resources": "리소스 라이브러리",
        "sidebar.tag_setup": "태그 등록",
        "sidebar.options": "옵션",
        "sidebar.scene": "배치",
        "sidebar.resources": "리소스",
        "mapping.title": "태그/애니메이션 등록",
        "mapping.help": "선택한 프로필의 액션에 Aseprite 태그를 연결합니다.",
        "mapping.empty.import": "먼저 리소스 탭에서 파일을 가져온 뒤 태그와 애니메이션을 확인하세요.",
        "mapping.empty.resources": "리소스 탭에서 파일을 가져오거나 + 소스 버튼을 사용하세요.",
        "mapping.empty.roles": "역할 배정 전후에 매핑을 확인할 수 있습니다. Partner는 T 교대 후보입니다.",
        "selection.scene_target": "배치 대상",
        "selection.linked_resource": "연결 리소스",
        "selection.none": "없음",
        "selection.linked": "연결됨",
        "selection.empty_scene": "아직 배치된 캐릭터나 오브젝트가 없습니다. 리소스 탭에서 Player/NPC/Prop으로 배정하세요.",
        "selection.empty_filter": "현재 필터에 표시할 배치 대상이 없습니다.",
        "selection.empty_resources": "파일을 가져온 뒤 태그 등록에서 애니메이션을 확인하고, Player/NPC/Prop 역할을 배정할 수 있습니다.",
        "selection.use_player": "PLAYER로 사용",
        "selection.spawn_npc": "NPC 소환",
        "selection.place_prop": "PROP 배치",
        "selection.assign_player": "플레이어로 사용",
        "selection.add_partner": "파트너로 추가",
        "selection.add_npc": "NPC로 추가",
        "selection.add_prop": "프롭으로 추가",
        "selection.refresh": "새로고침",
        "selection.remove": "삭제",
        "selection.export_png": "PNG 출력",
        "selection.remove_confirm": "이 리소스와 연결된 프로필을 삭제할까요?\n연결된 장면 인스턴스도 함께 정리됩니다.",
        "selection.delete_corpse": "선택 시체 삭제",
        "selection.delete_all_corpses": "시체 전체 삭제",
        "selection.despawn": "소환 해제",
        "selection.npc_despawned": "선택 NPC를 소환 해제했습니다.",
        "selection.no_npc_selected": "소환 해제할 NPC를 선택하세요.",
        "selection.corpse_use_delete": "시체는 시체 삭제 버튼을 사용하세요.",
        "selection.player_not_despawnable": "Player는 소환 해제할 수 없습니다.",
        "selection.focus_selected": "선택 대상 보기",
        "selection.corpse_deleted": "선택한 시체 오브젝트를 삭제했습니다.",
        "selection.corpses_deleted": "시체 오브젝트 {count}개를 삭제했습니다.",
        "selection.no_corpse_selected": "선택된 시체 오브젝트가 없습니다.",
        "selection.no_corpses": "장면에 시체 오브젝트가 없습니다.",
        "selection.focused": "선택 대상을 화면에 맞췄습니다.",
        "selection.no_scene_selected": "선택된 장면 오브젝트가 없습니다.",
        "selection.hidden_by_filter": "현재 선택은 필터에 의해 목록에서 숨겨져 있습니다.",
        "selection.filter.all": "전체",
        "selection.filter.player": "플레이어",
        "selection.filter.npc": "NPC",
        "selection.filter.prop": "프롭",
        "selection.filter.corpse": "시체",
        "selection.parts_count": "Parts {parts} / Particles {particles}",
        "selection.imported_choose_role": "리소스를 가져왔습니다. 역할을 선택하거나 다음으로 태그 등록에서 애니메이션을 확인하세요.",
        "selection.assigned_player": "선택 리소스를 플레이어로 사용합니다.",
        "selection.added_partner": "선택 리소스를 파트너 교대 후보에 추가했습니다. T를 눌러 교대하세요.",
        "selection.partner_roster": "파트너: {count} · 다음 파트너: {next} · T로 교대",
        "selection.added_npc": "선택 리소스를 NPC로 추가했습니다.",
        "selection.added_prop": "선택 리소스를 프롭으로 추가했습니다.",
        "selection.no_resource_selected": "선택된 리소스가 없습니다.",
        "selection.roles": "사용: {roles}",
        "tooltip.selection.current": "현재 편집 중인 배치 대상과 연결된 Aseprite 리소스를 보여줍니다.",
        "tooltip.selection.scene": "배치된 PLAYER, NPC, PROP을 선택합니다.\n선택한 대상의 태그와 설정이 편집 패널에 표시됩니다.",
        "tooltip.selection.resources": "불러온 Aseprite 파일과 감지된 Parts/Particles 정보를 관리합니다.",
        "tooltip.sidebar.tag_setup": "기존 태그/애니메이션 매핑 화면을 엽니다.",
        "tooltip.resource.use_player": "이 리소스를 플레이어 캐릭터의 애니메이션 소스로 사용합니다.",
        "tooltip.resource.spawn_npc": "이 리소스의 NPC 프로필로 새 NPC 인스턴스를 장면에 추가합니다.",
        "tooltip.resource.place_prop": "이 리소스를 파괴 가능한 PROP으로 장면에 추가합니다.",
        "tooltip.resource.assign_player": "선택 리소스를 현재 PLAYER의 애니메이션 소스로 사용합니다.\nPLAYER와 장면 오브젝트 위치는 유지합니다.",
        "tooltip.resource.add_partner": "선택 리소스를 Character Swap 대기 후보로 등록합니다.\n장면 NPC를 소환하지 않으며 T로 교대합니다.",
        "tooltip.resource.add_npc": "선택 리소스로 적 NPC 인스턴스를 추가합니다.\n기존 장면 배치는 유지합니다.",
        "tooltip.resource.add_prop": "선택 리소스로 PROP 인스턴스를 추가합니다.\n원본 리소스의 이름과 역할은 변경하지 않습니다.",
        "tooltip.resource.refresh": "Aseprite 파일을 다시 읽고 태그, 레이어, Slice 정보를 갱신합니다.",
        "tooltip.resource.remove": "리소스와 연결된 프로필을 프로젝트에서 제거합니다.\n삭제 전 영향 범위를 확인합니다.",
        "tooltip.resource.export_png": "감지된 Parts/Particles Slice를 개별 PNG 파일로 출력합니다.\n프로젝트 저장 기능이 아닙니다.",
        "tooltip.selection.delete_corpse": "선택한 NPC 시체 또는 잔여 오브젝트만 장면에서 삭제합니다.\n일반 NPC는 삭제하지 않습니다.",
        "tooltip.selection.delete_all_corpses": "장면의 NPC 시체와 잔여 오브젝트를 모두 삭제합니다.\nPLAYER, 일반 NPC, PROP은 삭제하지 않습니다.",
        "tooltip.selection.despawn": "선택한 살아 있는 NPC 인스턴스를 즉시 제거합니다.\n프로필·리소스는 유지하며 시체를 만들지 않습니다.",
        "tooltip.selection.focus_selected": "선택 대상의 위치로 카메라만 이동합니다.\n대상과 플레이어의 위치는 변경하지 않습니다.",
        "tooltip.selection.filter": "장면 목록의 표시 대상만 필터링합니다.\n오브젝트 데이터와 전체 장면 번호는 변경하지 않습니다.",
        "performance.short": "성능",
        "performance.help": "프레임 시간과 update/render 구간별 소요 시간을 표시합니다.",
        "ui.tags_from": "태그 소스: {name}",
        "ui.combo_step": "콤보 단계: {step}",
        "category.language": "언어",
        "category.props": "프랍(PROP)",
        "category.npcs": "NPC",
        "category.physics": "물리",
        "category.ai_combat": "AI 및 전투",
        "category.juice_vfx": "연출 및 VFX",
        "category.layers": "레이어(LAYERS)",
        "category.camera": "카메라",
        "category.bg_image": "배경 이미지",
        "category.bg_color": "배경색",
        "category.controls": "조작키",
        "settings.section.quick": "빠른 설정",
        "settings.section.input": "입력 / 조작",
        "settings.section.ai_combat": "AI / 전투",
        "settings.section.background": "배경 / 패럴랙스",
        "settings.section.view_debug": "보기 / 디버그",
        "settings.section.advanced": "프로젝트 / 고급",
        "settings.section.controls_app": "조작·앱",
        "settings.section.scene_combat": "장면·전투",
        "settings.section.view_background": "화면·배경",
        "settings.quick.flow": "리소스 등록 → 태그 등록 → 역할 배정 → 배치 → AI/전투 설정",
        "settings.quick.selection": "현재 선택: {actor} | {resource}",
        "settings.quick.shortcuts": "빠른 확인: F5 새로고침 · F10 성능 · H 히트박스",
        "settings.quick.guides": "하단에는 캐릭터 조작과 프로그램 단축키가 분리되어 표시됩니다.",
        "settings.input.character": "캐릭터: 공격·대시·점프·교대·스킬 1~3·합격기",
        "settings.input.app": "프로그램: P/O/[ ]/F5/F10/H/우클릭 드래그/F",
        "settings.input.fast_action": "빠른 액션은 캐릭터 조작 범위이며 현재 키를 강제로 바꾸지 않습니다.",
        "settings.input.controller_todo": "컨트롤러 감지·버튼 매핑·데드존·듀얼 가이드는 후속 작업입니다.",
        "settings.ai.behavior": "NPC 행동과 Intro 다시 재생은 선택 NPC/현재 프로필에 적용됩니다.",
        "settings.ai.combo": "ComboAttack_1부터 연속된 태그만 한 공격 체인으로 재생합니다.",
        "settings.ai.hitbox": "H로 전투 히트박스를 확인할 수 있습니다.",
        "settings.scene.lifecycle": "소환 해제와 시체 삭제는 배치 탭에서 각각 구분해 사용합니다.",
        "settings.background.guide": "레이어별 이미지·패럴랙스·X/Y 오프셋과 기즈모를 설정합니다.",
        "settings.background.history": "Shift 축 잠금 · Ctrl+Z 실행 취소 · Ctrl+Y 다시 실행",
        "settings.background.empty": "배경 레이어가 없습니다. 리소스에서 배경을 추가하세요.",
        "settings.npc.empty": "선택된 NPC가 없습니다. 배치 탭에서 NPC를 선택하세요.",
        "settings.synergy.empty": "합격기 키가 아직 설정되지 않았습니다.",
        "settings.layers.help": "캐릭터와 리소스의 표시 레이어를 관리합니다.",
        "settings.vfx.help": "타격, 잔상, 먼지와 화면 흔들림 같은 장면 연출을 조정합니다.",
        "settings.subtitle.controls_app": "언어 · 캐릭터 조작 · 프로그램 단축키 · 입력 프리셋",
        "settings.subtitle.scene_combat": "NPC / 전투 · 연출 / VFX · 레이어 · PROP / 물리 · 소환 / 시체",
        "settings.subtitle.view_background": "배경 · 패럴랙스 · 카메라 · 보기 / 디버그",
        "status.setting_reset": "{label} 값을 기본값으로 초기화했습니다.",
        "status.setting_reset_unavailable": "이 설정은 기본값을 확인할 수 없어 초기화하지 않았습니다.",
        "settings.view.shortcuts": "P 일시정지 · O 1프레임 진행 · [ ] 속도 · F10 성능 · H 히트박스",
        "settings.view.camera": "우클릭 드래그로 카메라를 이동하고 F로 Player 추적을 복원합니다.",
        "settings.view.guide": "F10 오버레이 중에도 하단 Character/App 가이드는 유지됩니다.",
        "settings.view.visual": "보기: F10 성능 · H 히트박스 · 우클릭 드래그 카메라 · F 추적",
        "settings.advanced.project": "프로젝트 새로 만들기·불러오기·저장은 화면 상단 도구를 사용합니다.",
        "settings.advanced.refresh": "F5는 소스와 레이어 정보를 새로고침하며 원본을 수정하지 않습니다.",
        "settings.advanced.todo": "실험 기능과 컨트롤러 지원은 현재 설정 스키마에 추가하지 않습니다.",
        "tooltip.settings.section.quick": "처음 사용하는 흐름과 자주 쓰는 단축키를 요약합니다.",
        "tooltip.settings.section.input": "캐릭터 키 설정과 프로그램 단축키 안내를 엽니다.",
        "tooltip.settings.section.ai_combat": "NPC 행동, Intro와 전투 관련 설정을 엽니다.",
        "tooltip.settings.section.background": "배경 이미지와 패럴랙스 설정을 엽니다.",
        "tooltip.settings.section.view_debug": "보기, 카메라와 디버그 안내를 엽니다.",
        "tooltip.settings.section.advanced": "프로젝트 안내와 고급 물리/PROP 설정을 엽니다.",
        "tooltip.settings.section.controls_app": "언어, 캐릭터 조작키와 프로그램 단축키 안내를 엽니다.",
        "tooltip.settings.section.scene_combat": "NPC, PROP, 물리, Intro와 전투 설정을 엽니다.",
        "tooltip.settings.section.view_background": "배경, 패럴랙스, 카메라와 디버그 보기 설정을 엽니다.",
        "tooltip.setting_reset": "이 값 하나만 기본값으로 되돌립니다. 삭제 기능이 아닙니다.",
        "language.ko": "한국어",
        "language.en": "English",
        "status.detected_slices": "감지된 슬라이스(Slice)",
        "status.parts": "파츠(Parts)",
        "status.particles": "파티클(Particles)",
        "status.death": "사망",
        "status.save": "저장",
        "status.available": "사용 가능",
        "status.disabled": "사용 불가",
        "status.on": "가능",
        "status.off": "불가",
        "status.last_death": "최근 사망: 시체={corpse} / 파츠={count}",
        "status.dead_loop": "사망 반복",
        "status.dead_hold": "사망 유지",
        "status.remove": "제거",
        "status.precise_parts": "정밀 파츠 {count}",
        "status.auto_alpha": "자동 알파 ~{count}",
        "status.single_image": "단일 이미지 1",
        "status.colored_fallback": "단색 폴백",
        "status.no_parts_tag": "Parts 태그 없음",
        "status.no_valid_parts": "유효한 Parts 없음",
        "status.missing_source": "소스 없음",
        "status.corpse_parts": "시체 태그가 활성화되어도 Parts는 별도로 생성됩니다.",
        "export.confirm": "파츠와 파티클 이미지를 PNG로 출력하시겠습니까?\n\n원본 Aseprite 파일은 변경되지 않습니다.\n다음 단계에서 출력 옵션과 저장 폴더를 선택할 수 있습니다.",
        "export.title": "파츠(Parts) / 파티클(Particles) 출력",
        "export.classification": "분류 방식",
        "export.auto": "자동 분류(AUTO) — 권장",
        "export.auto_desc": "Parts/Particles 태그 범위의 실제 이미지 데이터를 검사해\n유효한 슬라이스를 자동으로 구분합니다.",
        "export.name": "이름 분류(NAME) — 호환용",
        "export.name_desc": "슬라이스 이름의 Part 또는 Particle 문구를 기준으로 구분합니다.",
        "export.file_naming": "파일명 방식",
        "export.use_asset": "제작 대상 이름 사용",
        "export.use_asset_desc": "입력한 이름으로 번호가 붙은 파일을 만듭니다.",
        "export.asset_name": "제작 대상 이름:",
        "export.keep_slice": "Aseprite 슬라이스 이름 유지",
        "export.keep_slice_desc": "Aseprite에 작성된 슬라이스 이름을 파일명으로 사용합니다.",
        "export.example": "예:",
        "export.preview": "파일명 미리보기",
        "export.preview_total": "파일명 미리보기 · 총 {count}개",
        "export.preview_status": "{classification} · {naming} · 총 {total}개 · Parts {parts} · Particles {particles}",
        "export.preview_empty": "미리볼 수 있는 파일이 없습니다.\n선택한 분류 방식에서 유효한 Parts 또는 Particles Slice를 찾지 못했습니다.",
        "export.folder_collision_hint": "출력 폴더에 같은 파일명이 있으면 저장 시 _2, _3 접미사가 추가될 수 있습니다.",
        "tooltip.export.preview_list": "현재 옵션으로 출력될 모든 PNG 파일명을 보여줍니다.\n실제 저장 순서와 동일합니다.",
        "tooltip.export.collision": "이 목록은 출력 폴더 선택 전의 예정 이름입니다.\n기존 파일이 있으면 저장할 때 안전한 접미사가 추가될 수 있습니다.",
        "tooltip.export.parts_group": "Parts 태그 범위에서 감지된 파츠 이미지 파일입니다.",
        "tooltip.export.particles_group": "Particles 태그 범위에서 감지된 이펙트 이미지 파일입니다.",
        "tooltip.export.continue_disabled": "출력 가능한 파일명이 있을 때 계속할 수 있습니다.",
        "export.no_slice_preview": "저장 가능한 슬라이스 이름이 없습니다.",
        "export.independent_hint": "AUTO/NAME은 어떤 슬라이스를 출력할지 결정합니다.\n파일명 방식은 출력된 PNG의 이름만 결정합니다.",
        "export.enter_asset": "제작 대상 이름을 입력하세요.\n또는 'Aseprite 슬라이스 이름 유지'를 선택할 수 있습니다.",
        "export.continue": "계속",
        "export.completed": "출력 완료",
        "export.failed": "PNG 출력 실패",
        "export.none_saved": "저장된 PNG 파일이 없습니다.",
        "export.options_open_failed": "출력 옵션을 열 수 없음",
        "export.options_open_failed_detail": "출력 옵션 창을 열 수 없습니다.",
        "export.folder_open_failed": "출력 폴더 선택 창을 열 수 없습니다. 자세한 내용은 ase_debug.log를 확인하세요.",
        "source.removal_title": "소스 삭제 결과",
        "source.removed": "소스를 삭제했습니다.",
        "source.removed_profiles": "연결된 프로필 삭제: {count}",
        "source.removed_partners": "파트너 인스턴스 삭제: {count}",
        "source.removed_npcs": "NPC 인스턴스 삭제: {count}",
        "source.removed_props": "PROP 인스턴스 삭제: {count}",
        "source.player_disabled": "현재 플레이어 프로필이 삭제되어 플레이어 표시를 비활성화했습니다.",
        "error.ase_path_save_title": "Aseprite 경로를 저장하지 못함",
        "error.ase_path_save": "선택한 경로를 다음 파일에 저장할 수 없습니다:\n{path}\n\n쓰기 권한이 필요할 수 있습니다. 자세한 내용은 ase_debug.log를 확인하세요.",
        "error.settings_save_title": "설정을 저장하지 못함",
        "error.settings_save": "다음 파일에 쓸 수 없습니다:\n{path}\n\n이전 설정 파일은 보존되었습니다. 폴더 권한과 ase_debug.log를 확인하세요.",
        "error.settings_load_title": "설정을 불러오지 못함",
        "error.settings_load": "설정 파일이 잘못되었거나 읽을 수 없습니다:\n{path}\n\n기본값을 사용합니다. 자세한 내용은 ase_debug.log를 확인하세요.",
        "error.project_save_title": "프로젝트를 저장하지 못함",
        "error.project_save": "다음 파일에 쓸 수 없습니다:\n{path}\n\n이전 프로젝트 파일은 보존되었습니다. 폴더 권한과 ase_debug.log를 확인하세요.",
        "error.project_load_title": "프로젝트를 불러오지 못함",
        "error.project_load": "프로젝트 파일이 잘못되었거나 불완전합니다:\n{path}\n\n기존 파일은 변경하지 않았습니다. 자세한 내용은 ase_debug.log를 확인하세요.",
        "error.source_add_title": "소스를 추가하지 못함",
        "error.source_add": "다음 소스를 추가할 수 없습니다:\n{path}\n\n{error}\n\n파일과 Aseprite 경로를 확인한 뒤 다시 시도하세요.",
        "error.source_refresh_title": "소스 새로고침 실패",
        "error.source_refresh": "하나 이상의 Aseprite 소스를 새로고칠 수 없습니다. 기존 프로젝트 경로는 유지했습니다. 자세한 내용은 ase_debug.log를 확인하세요.",
        "error.layer_reload_title": "레이어 표시를 변경하지 못함",
        "error.layer_reload": "Aseprite가 이 소스를 다시 불러오지 못했습니다. 이전 표시 상태를 복원했습니다.",
        "tooltip.project.new": "새 프로젝트를 만듭니다.\n저장하지 않은 현재 배치 내용은 사라질 수 있습니다.",
        "tooltip.project.load": "저장된 프로젝트 JSON을 불러옵니다.",
        "tooltip.project.save": "현재 프로젝트 배치와 설정을 JSON으로 저장합니다.",
        "tooltip.source.add": "Aseprite 파일을 플레이어 소스로 추가합니다.",
        "tooltip.npc.add": "Aseprite 파일을 NPC 리소스로 등록하고 NPC를 소환합니다.",
        "tooltip.prop.add": "Aseprite 파일을 PROP 리소스로 등록하고 PROP을 소환합니다.",
        "tooltip.options": "언어, NPC/PROP, 물리, 연출, 레이어와 배경 옵션을 엽니다.",
        "tooltip.platform.edit": "플랫폼과 솔리드 박스의 위치 및 크기 편집을 켜거나 끕니다.",
        "tooltip.platform.add": "충돌 가능한 플랫폼을 추가합니다.",
        "tooltip.solid_box.add": "캐릭터가 통과할 수 없는 솔리드 박스를 추가합니다.",
        "tooltip.npc.spawn": "등록된 리소스를 다시 분석하지 않고 NPC 인스턴스만 추가합니다.",
        "tooltip.prop.spawn": "등록된 리소스를 다시 분석하지 않고 PROP 인스턴스만 추가합니다.",
        "tooltip.npc.save": "감지된 Parts/Particles 슬라이스를 PNG로 출력합니다.\nNPC 배치나 프로젝트 자체를 저장하는 기능은 아닙니다.",
        "tooltip.prop.save": "감지된 Parts/Particles 슬라이스를 PNG로 출력합니다.\nPROP 배치나 파괴 상태를 저장하는 기능은 아닙니다.",
        "tooltip.detected_slices": "현재 리소스에서 자동 감지된 Parts와 Particles 수를 보여줍니다.",
        "tooltip.auto": "Parts/Particles 태그 범위에서 실제 픽셀이 있는 슬라이스를 자동으로 찾습니다.\n대부분의 경우 이 옵션을 권장합니다.",
        "tooltip.name": "슬라이스 이름에 Part 또는 Particle이 포함됐는지로 분류합니다.\n기존 파일 호환용입니다.",
        "tooltip.naming.target": "직접 입력한 이름으로 Parts_01, Particle_01 형식의 파일을 만듭니다.",
        "tooltip.naming.slice": "Aseprite에서 작성한 슬라이스 이름을 PNG 파일명으로 사용합니다.",
        "tooltip.dash_velocity": "대시할 때 적용되는 수평 이동 속도입니다.",
        "tooltip.jump_power": "점프할 때 적용되는 위쪽 힘입니다.",
        "tooltip.show_guide": "게임 화면 기준이 되는 640x360 가이드를 표시합니다.",
        "tooltip.shake": "공격과 충돌 연출의 화면 흔들림을 켜거나 끕니다.",
        "tooltip.layer_visibility": "이 레이어의 표시 여부를 바꾸고 Aseprite 소스를 다시 불러옵니다.",
        "tooltip.parallax": "카메라 이동에 대한 배경 레이어의 상대 이동 비율입니다.",
        "tooltip.npc_behavior": "클릭할 때마다 NPC 행동을 변경합니다.\n균형·대기·추적·공격·경비·순찰·회피 중 선택할 수 있습니다.",
        "tooltip.replay_npc_intro": "선택한 NPC 또는 현재 NPC 프로필의 소환 Intro를 다시 재생합니다.\n공격 중인 NPC는 공격 모션을 보호하기 위해 제외됩니다.",
        "tooltip.scale": "선택한 배경 레이어의 표시 크기입니다.",
        "tooltip.x_offset": "선택한 배경 레이어의 가로 위치 보정값입니다.",
        "tooltip.y_offset": "선택한 배경 레이어의 세로 위치 보정값입니다.",
        "ui.no_resource": "선택된 리소스가 없습니다.\n리소스를 추가하면 이 옵션을 사용할 수 있습니다.",
        "tooltip.resource_required": "리소스를 먼저 추가하거나 선택해야 사용할 수 있습니다.",
        "unity.copy_button": "UNITY 설정 복사",
        "unity.dialog_title": "Unity 패럴랙스 내보내기",
        "unity.ppu": "Unity Pixels Per Unit",
        "unity.format": "출력 형식",
        "unity.detailed": "상세 설명",
        "unity.slack": "Slack 공유",
        "unity.markdown": "Jira / Notion Markdown",
        "unity.tsv": "TSV 데이터",
        "unity.compact": "Slack 공유",
        "unity.detailed_help": "좌표 변환 기준과 레이어별 값을 모두 포함합니다.",
        "unity.slack_help": "고정폭 코드 블록으로 복사합니다. 메신저에서 숫자 열을 비교하기 좋습니다.",
        "unity.markdown_help": "두 개의 Markdown 표로 복사합니다. 문서와 이슈 설명에 적합합니다.",
        "unity.tsv_help": "탭으로 구분된 표 데이터입니다. Notion 표나 스프레드시트에 붙여넣기 좋습니다.",
        "unity.include_disabled": "비활성 레이어 포함",
        "unity.copy_clipboard": "클립보드에 복사",
        "unity.preview": "미리보기",
        "unity.preview_stats": "포함 레이어: {count}개    출력 길이: {length:,}자",
        "unity.many_layers": "레이어가 많습니다. TSV 형식이 더 적합할 수 있습니다.",
        "unity.invalid_ppu": "Pixels Per Unit은 1~10000 사이의 유한한 숫자여야 합니다.",
        "unity.no_layers": "내보낼 배경 레이어가 없습니다.\n먼저 배경 레이어를 추가하세요.",
        "unity.copy_success_detailed": "상세 설명을 클립보드에 복사했습니다.\n\n레이어: {count}개\nPixels Per Unit: {ppu}",
        "unity.copy_success_slack": "Slack 공유 형식을 클립보드에 복사했습니다.\n\n레이어: {count}개\nPixels Per Unit: {ppu}",
        "unity.copy_success_markdown": "Jira / Notion Markdown을 클립보드에 복사했습니다.\n\n레이어: {count}개",
        "unity.copy_success_tsv": "TSV 데이터를 클립보드에 복사했습니다.\n\n레이어: {count}개\nOffsets: Unity units / PPU {ppu}",
        "unity.copy_failed": "Unity 설정을 클립보드에 복사하지 못했습니다.\n자세한 내용은 ase_debug.log를 확인하세요.",
        "tooltip.unity_ppu": "Unity Sprite Import Settings의 Pixels Per Unit 값입니다.\n픽셀 오프셋을 Unity 월드 단위로 변환할 때 사용합니다.",
        "tooltip.unity_copy": "현재 배경 레이어의 패럴랙스, 스케일, 오프셋을\nUnity 작업자가 읽을 수 있는 텍스트로 복사합니다.",
        "tooltip.unity_detailed": "좌표 변환 기준과 레이어별 값을 설명과 함께 출력합니다.",
        "tooltip.unity_slack": "고정폭 코드 블록과 작은 표로 복사합니다.\nSlack이나 메신저에서 빠르게 비교하기 좋습니다.",
        "tooltip.unity_markdown": "Markdown 표 두 개로 복사합니다.\nJira 또는 Notion 편집기에 따라 표 변환 방식이 다를 수 있습니다.",
        "tooltip.unity_tsv": "탭으로 구분된 원시 표 데이터입니다.\nNotion 표, Excel, Google Sheets 등에 붙여넣을 수 있습니다.",
        "tooltip.unity_compact": "구형 간단 표 설정은 Slack 공유 형식으로 열립니다.",
        "unity.handoff_title": "ASEPRITE ACTION VIEWER — UNITY PARALLAX HANDOFF",
        "unity.viewer_version": "Viewer Version",
        "unity.coordinate_basis": "좌표 기준",
        "unity.coordinate_x": "Unity X: 오른쪽이 양수",
        "unity.coordinate_y": "Unity Y: 위쪽이 양수",
        "unity.coordinate_conversion": "Viewer Y offset은 Unity 변환 시 부호를 반전합니다.",
        "unity.parallax_basis": "패럴랙스 기준",
        "unity.parallax_zero": "Viewer Parallax 0.0: 화면에 고정됨; Unity Camera Follow Ratio 1.0",
        "unity.parallax_one": "Viewer Parallax 1.0: 월드에 고정됨; Unity Camera Follow Ratio 0.0",
        "unity.formula": "Unity 등가식: layer.position = layerStart + cameraDelta * (1 - viewerParallax) + positionOffset",
        "unity.enabled": "Enabled",
        "unity.yes": "Yes",
        "unity.no": "No",
        "unity.source": "Source",
        "unity.suggested_order": "Suggested Sorting Order",
        "unity.viewer": "Viewer",
        "unity.unity": "Unity",
        "unity.not_set": "Not set",
        "unity.offset_units": "Offsets are Unity units. PPU={ppu}.",
        "summary.naming": "파일명 방식",
        "summary.target_naming": "제작 대상 이름",
        "summary.slice_naming": "Aseprite 슬라이스 이름",
        "summary.target": "제작 대상",
        "summary.classification": "분류 방식",
        "summary.parts": "파츠",
        "summary.particles": "파티클",
        "summary.skipped": "건너뜀",
        "summary.failed": "실패",
        "summary.collisions": "이름 충돌 변경",
        "summary.output_folder": "출력 폴더",
        "summary.auto": "자동 분류(AUTO)",
        "summary.name": "이름 분류(NAME)",
        "summary.count": "{count}개",
        "summary.duplicates": "태그 간 중복 가능성",
    },
    LANG_EN: {
        "common.confirm": "Confirm",
        "common.cancel": "Cancel",
        "common.export": "Export",
        "common.save": "Save",
        "common.load": "Load",
        "common.new": "New Project",
        "common.spawn": "Spawn",
        "common.none": "None",
        "common.add": "Add",
        "common.remove": "Remove",
        "common.reset": "Reset",
        "common.press_key": "PRESS KEY",
        "common.refresh": "Refresh",
        "common.clear": "Clear",
        "common.up": "Up",
        "common.down": "Down",
        "ui.setup": "⚙ Setup",
        "ui.edit_platform": "Edit Platform",
        "ui.add_platform": "+ Platform",
        "ui.add_box": "+ Box",
        "ui.add_source": "+ Source",
        "ui.add_npc": "+ NPC",
        "ui.add_prop": "+ PROP",
        "ui.ranged_combo": "Ranged Combo",
        "ui.swap_target": "Swap Target:",
        "ui.roaming_target": "Roaming Target:",
        "ui.shake_power": "Shake Power",
        "ui.debris_force": "Debris Force",
        "ui.camera_offset": "Camera Offset",
        "ui.show_guide": "Show 640x360 Guide",
        "ui.layers": "Layers:",
        "ui.load_image": "Load Image",
        "ui.loop_x": "Loop X",
        "ui.dash_velocity": "Dash Velocity",
        "ui.jump_power": "Jump Power",
        "ui.powerbomb_speed": "Powerbomb Speed",
        "ui.platform_alpha": "Platform Alpha",
        "ui.ai_count": "AI Count",
        "ui.npc_max_hp": "NPC Max HP",
        "ui.npc_behavior": "NPC Behavior",
        "guide.attack": "Attack",
        "guide.dash": "Dash",
        "guide.jump": "Jump",
        "guide.swap": "Swap",
        "guide.skills": "Skills",
        "guide.synergy": "Synergy",
        "guide.refresh": "Refresh",
        "guide.pause": "Pause",
        "guide.step": "Step 1 frame",
        "guide.speed": "Speed",
        "guide.hitbox": "Hitbox",
        "guide.camera": "Camera",
        "guide.performance": "Performance",
        "guide.camera_reset": "Camera Reset",
        "control.skill_1": "Skill 1",
        "control.skill_2": "Skill 2",
        "control.skill_3": "Skill 3",
        "control.summon": "Summon",
        "control.hit_1": "Hit 1",
        "control.unavailable": "Control mapping is unavailable.",
        "guide.group.character": "Player",
        "guide.group.app": "App / Editor",
        "tooltip.guide.step": "Advances the animation by exactly one frame while paused.",
        "status.recall_live_npcs": "Recalled {count} living NPC(s) near the Player.",
        "status.recall_no_live_npcs": "There are no living NPCs to recall.",
        "ui.replay_npc_intro": "Replay Intro",
        "npc_behavior.balanced": "Balanced",
        "npc_behavior.idle": "Idle",
        "npc_behavior.follow": "Follow",
        "npc_behavior.aggressive": "Aggressive",
        "npc_behavior.guard": "Guard",
        "npc_behavior.patrol": "Patrol",
        "npc_behavior.flee": "Flee",
        "status.npc_intro_selected": "Replayed the selected NPC intro.",
        "status.npc_intro_profile": "Replayed intro for NPCs using the current profile. ({count})",
        "status.npc_intro_no_target": "No NPC found for intro replay.",
        "status.npc_intro_missing": "This profile has no Intro tag.",
        "status.npc_intro_attack_locked": "An attacking NPC cannot replay its intro.",
        "status.npc_intro_already_playing": "This NPC is already playing its intro.",
        "ui.attack_forward": "Attack Forward",
        "ui.enable_shake": "Enable Shake",
        "ui.enable_ghost": "Enable Ghost",
        "ui.x_offset": "X Offset",
        "ui.y_offset": "Y Offset",
        "ui.scale": "Scale",
        "ui.alpha": "Alpha",
        "ui.parallax": "Parallax",
        "ui.parallax_gizmo": "Parallax Gizmo",
        "status.parallax_gizmo_on": "Drag the handle to adjust the selected layer offset.",
        "status.parallax_gizmo_select": "Select an image layer to use the gizmo.",
        "status.parallax_undo": "Undo parallax offset.",
        "status.parallax_redo": "Redo parallax offset.",
        "status.parallax_nothing_undo": "Nothing to undo.",
        "status.parallax_nothing_redo": "Nothing to redo.",
        "tooltip.parallax_gizmo": "Drag the center freely or use the X/Y arrows for one axis.\nShift+center drag locks the dominant axis and never modifies source files.",
        "selection.current": "Current Selection",
        "selection.scene": "Placed Characters & Objects",
        "selection.resources": "Resource Library",
        "sidebar.tag_setup": "Tag Setup",
        "sidebar.options": "Options",
        "sidebar.scene": "Scene",
        "sidebar.resources": "Resources",
        "mapping.title": "Tag / Animation Setup",
        "mapping.help": "Connect Aseprite tags to actions for the selected profile.",
        "mapping.empty.import": "Import a file in Resources first, then review its tags and animations.",
        "mapping.empty.resources": "Use the Resources tab or + Source to add files.",
        "mapping.empty.roles": "Review mappings before or after role assignment. Partner is a T-key swap candidate.",
        "selection.scene_target": "Placed target",
        "selection.linked_resource": "Linked resource",
        "selection.none": "None",
        "selection.linked": "Linked",
        "selection.empty_scene": "No characters or objects are placed yet. Assign a Player, NPC, or Prop role in Resources.",
        "selection.empty_filter": "No placed objects match this filter.",
        "selection.empty_resources": "Import a file, review animations in Tag Setup, then assign a Player, NPC, or Prop role.",
        "selection.use_player": "USE AS PLAYER",
        "selection.spawn_npc": "SPAWN NPC",
        "selection.place_prop": "PLACE PROP",
        "selection.assign_player": "USE AS PLAYER",
        "selection.add_partner": "ADD AS PARTNER",
        "selection.add_npc": "ADD AS NPC",
        "selection.add_prop": "ADD AS PROP",
        "selection.refresh": "REFRESH",
        "selection.remove": "REMOVE",
        "selection.export_png": "EXPORT PNG",
        "selection.remove_confirm": "Remove this resource and its linked profiles?\nLinked scene instances will also be cleaned up.",
        "selection.delete_corpse": "DELETE CORPSE",
        "selection.delete_all_corpses": "DELETE ALL CORPSES",
        "selection.despawn": "DESPAWN",
        "selection.npc_despawned": "Despawned the selected NPC.",
        "selection.no_npc_selected": "Select an NPC to despawn.",
        "selection.corpse_use_delete": "Use Delete Corpse for corpses.",
        "selection.player_not_despawnable": "Player cannot be despawned.",
        "selection.focus_selected": "FOCUS SELECTED",
        "selection.corpse_deleted": "Deleted selected corpse object.",
        "selection.corpses_deleted": "Deleted {count} corpse objects.",
        "selection.no_corpse_selected": "No corpse object selected.",
        "selection.no_corpses": "No corpse objects in scene.",
        "selection.focused": "Focused selected object.",
        "selection.no_scene_selected": "No scene object selected.",
        "selection.hidden_by_filter": "The current selection is hidden by the filter.",
        "selection.filter.all": "All",
        "selection.filter.player": "Player",
        "selection.filter.npc": "NPC",
        "selection.filter.prop": "Prop",
        "selection.filter.corpse": "Corpse",
        "selection.parts_count": "Parts {parts} / Particles {particles}",
        "selection.imported_choose_role": "Resource imported. Choose a role, or next open Tag Setup to review animations.",
        "selection.assigned_player": "Using selected resource as Player.",
        "selection.added_partner": "Added selected resource to Partner roster. Press T to swap.",
        "selection.partner_roster": "Partners: {count} · Next Partner: {next} · Press T to swap",
        "selection.added_npc": "Added selected resource as NPC.",
        "selection.added_prop": "Added selected resource as Prop.",
        "selection.no_resource_selected": "No resource selected.",
        "selection.roles": "Used by: {roles}",
        "tooltip.selection.current": "Shows the placed target currently being edited and its linked Aseprite resource.",
        "tooltip.selection.scene": "Selects placed PLAYER, NPC, and PROP objects.\nThe selected target's tags and settings appear in the editor.",
        "tooltip.selection.resources": "Manages loaded Aseprite files and detected Parts/Particles information.",
        "tooltip.sidebar.tag_setup": "Opens the existing tag and animation mapping workspace.",
        "tooltip.resource.use_player": "Uses this resource as the player character's animation source.",
        "tooltip.resource.spawn_npc": "Adds a new NPC instance to the scene using this resource's NPC profile.",
        "tooltip.resource.place_prop": "Adds this resource to the scene as a destructible PROP.",
        "tooltip.resource.assign_player": "Uses this resource as the current PLAYER animation source.\nPLAYER and scene object positions are preserved.",
        "tooltip.resource.add_partner": "Adds this resource to the Character Swap standby roster.\nIt does not spawn a scene NPC; press T to swap.",
        "tooltip.resource.add_npc": "Adds an enemy NPC instance from this resource.\nExisting scene placement is preserved.",
        "tooltip.resource.add_prop": "Adds a PROP instance from this resource.\nThe original resource name and role remain unchanged.",
        "tooltip.resource.refresh": "Reloads the Aseprite file and refreshes tags, layers, and Slice data.",
        "tooltip.resource.remove": "Removes the resource and linked profiles from the project.\nThe impact is shown before removal.",
        "tooltip.resource.export_png": "Exports detected Parts/Particles Slices as individual PNG files.\nThis does not save the project.",
        "tooltip.selection.delete_corpse": "Deletes only the selected NPC corpse or remnant object from the scene.\nLiving NPCs are never removed.",
        "tooltip.selection.delete_all_corpses": "Deletes every NPC corpse or remnant in the scene.\nPLAYER, living NPCs, and PROPs are never removed.",
        "tooltip.selection.despawn": "Immediately removes the selected living NPC instance.\nIts profile and resource remain, and no corpse is created.",
        "tooltip.selection.focus_selected": "Moves only the camera to the selected object.\nThe object and player positions are unchanged.",
        "tooltip.selection.filter": "Filters only the visible scene list.\nObject data and global scene numbering are unchanged.",
        "performance.short": "Perf",
        "performance.help": "Shows frame time and update/render timing details.",
        "ui.tags_from": "Tags from: {name}",
        "ui.combo_step": "Combo Step: {step}",
        "category.language": "Language",
        "category.props": "PROPS",
        "category.npcs": "NPCS",
        "category.physics": "PHYSICS",
        "category.ai_combat": "AI & COMBAT",
        "category.juice_vfx": "JUICE & VFX",
        "category.layers": "LAYERS",
        "category.camera": "CAMERA",
        "category.bg_image": "BG IMAGE",
        "category.bg_color": "BG COLOR",
        "category.controls": "CONTROLS",
        "settings.section.quick": "Quick",
        "settings.section.input": "Input",
        "settings.section.ai_combat": "AI / Combat",
        "settings.section.background": "Background",
        "settings.section.view_debug": "View / Debug",
        "settings.section.advanced": "Advanced",
        "settings.section.controls_app": "Controls & App",
        "settings.section.scene_combat": "Scene & Combat",
        "settings.section.view_background": "View & Background",
        "settings.quick.flow": "Import Resource → Map Tags → Assign Role → Place → Configure AI / Combat",
        "settings.quick.selection": "Current: {actor} | {resource}",
        "settings.quick.shortcuts": "Quick checks: F5 Refresh · F10 Performance · H Hitbox",
        "settings.quick.guides": "Character controls and app shortcuts remain separate in the bottom guide.",
        "settings.input.character": "Character: Attack, Dash, Jump, Swap, Skills 1–3, and Synergy",
        "settings.input.app": "App: P/O/[ ]/F5/F10/H/Right-drag/F",
        "settings.input.fast_action": "Fast Action applies only to character controls and never overwrites current keys.",
        "settings.input.controller_todo": "Controller detection, mapping, deadzone, and dual guides remain follow-up work.",
        "settings.ai.behavior": "NPC behavior and Replay Intro target the selected NPC or current profile.",
        "settings.ai.combo": "Only contiguous tags beginning with ComboAttack_1 form one attack chain.",
        "settings.ai.hitbox": "Press H to inspect combat hitboxes.",
        "settings.scene.lifecycle": "Use separate Despawn and Delete Corpse actions in the Scene tab.",
        "settings.background.guide": "Configure each layer's image, parallax, X/Y offsets, and gizmo.",
        "settings.background.history": "Shift axis lock · Ctrl+Z Undo · Ctrl+Y Redo",
        "settings.background.empty": "No background layer. Add one from Resources.",
        "settings.npc.empty": "No NPC selected. Select one in Placement.",
        "settings.synergy.empty": "Synergy key is not assigned.",
        "settings.layers.help": "Manage character and resource display layers.",
        "settings.vfx.help": "Tune scene feedback such as hits, afterimages, dust, and shake.",
        "settings.subtitle.controls_app": "Language · Character Controls · App Shortcuts · Input Presets",
        "settings.subtitle.scene_combat": "NPC / Combat · Presentation / VFX · Layers · PROP / Physics · Spawn / Corpses",
        "settings.subtitle.view_background": "Background · Parallax · Camera · View / Debug",
        "status.setting_reset": "Reset {label} to its default.",
        "status.setting_reset_unavailable": "This setting has no verified default and was not reset.",
        "settings.view.shortcuts": "P Pause · O Step 1 frame · [ ] Speed · F10 Performance · H Hitbox",
        "settings.view.camera": "Right-drag moves the camera; F restores Player follow.",
        "settings.view.guide": "The Character/App guide remains visible with the F10 overlay.",
        "settings.view.visual": "View: F10 Performance · H Hitbox · Right-drag Camera · F Follow",
        "settings.advanced.project": "Use the top toolbar to create, load, and save projects.",
        "settings.advanced.refresh": "F5 refreshes source and layer data without modifying originals.",
        "settings.advanced.todo": "Experimental and controller features are not added to the settings schema.",
        "tooltip.settings.section.quick": "Summarizes the first-use flow and common shortcuts.",
        "tooltip.settings.section.input": "Opens character key settings and app shortcut guidance.",
        "tooltip.settings.section.ai_combat": "Opens NPC behavior, Intro, and combat settings.",
        "tooltip.settings.section.background": "Opens background image and parallax settings.",
        "tooltip.settings.section.view_debug": "Opens view, camera, and debug guidance.",
        "tooltip.settings.section.advanced": "Opens project guidance and advanced physics/PROP settings.",
        "tooltip.settings.section.controls_app": "Opens language, character keys, and app shortcut guidance.",
        "tooltip.settings.section.scene_combat": "Opens NPC, PROP, physics, Intro, and combat settings.",
        "tooltip.settings.section.view_background": "Opens background, parallax, camera, and debug-view settings.",
        "tooltip.setting_reset": "Restore only this value to its default. This does not delete anything.",
        "language.ko": "한국어",
        "language.en": "English",
        "status.detected_slices": "DETECTED SLICES",
        "status.parts": "Parts",
        "status.particles": "Particles",
        "status.death": "Death",
        "status.save": "Save",
        "status.available": "Available",
        "status.disabled": "Disabled",
        "status.on": "On",
        "status.off": "Off",
        "status.last_death": "Last Death: corpse={corpse} / parts={count}",
        "status.dead_loop": "Dead Loop",
        "status.dead_hold": "Dead Hold",
        "status.remove": "Remove",
        "status.precise_parts": "Precise Parts {count}",
        "status.auto_alpha": "Auto Alpha ~{count}",
        "status.single_image": "Single Image 1",
        "status.colored_fallback": "Colored Fallback",
        "status.no_parts_tag": "No Parts tag",
        "status.no_valid_parts": "No valid Parts",
        "status.missing_source": "Missing source",
        "status.corpse_parts": "Parts spawn independently while the corpse tag is active.",
        "export.confirm": "Export Parts / Particles images as PNG files?\n\nThe original Aseprite file is not changed.\nYou can choose export options and a folder in the next step.",
        "export.title": "EXPORT PARTS / PARTICLES",
        "export.classification": "Classification",
        "export.auto": "AUTO — Recommended",
        "export.auto_desc": "Detects valid slices from actual image data inside the\nParts and Particles tag ranges.",
        "export.name": "NAME — Compatibility",
        "export.name_desc": "Classifies slices from Part or Particle text in slice names.",
        "export.file_naming": "File Naming",
        "export.use_asset": "Use asset name",
        "export.use_asset_desc": "Creates numbered files using the name entered below.",
        "export.asset_name": "Asset name:",
        "export.keep_slice": "Keep Aseprite slice names",
        "export.keep_slice_desc": "Uses the original Aseprite slice names as filenames.",
        "export.example": "Example:",
        "export.preview": "Filename Preview",
        "export.preview_total": "Filename Preview · {count} total",
        "export.preview_status": "{classification} · {naming} · {total} total · Parts {parts} · Particles {particles}",
        "export.preview_empty": "There are no filenames to preview.\nNo valid Parts or Particles slices were found with the selected classification mode.",
        "export.folder_collision_hint": "If matching files already exist in the output folder, _2 or _3 may be added when exporting.",
        "tooltip.export.preview_list": "Shows every PNG filename that will be exported with the current options.\nThe order matches the actual export.",
        "tooltip.export.collision": "This list shows planned names before an output folder is selected.\nSafe suffixes may be added when existing files are found.",
        "tooltip.export.parts_group": "Part image files detected in the Parts tag range.",
        "tooltip.export.particles_group": "Effect image files detected in the Particles tag range.",
        "tooltip.export.continue_disabled": "Continue is available when there is at least one filename to export.",
        "export.no_slice_preview": "No exportable slice names are available.",
        "export.independent_hint": "AUTO/NAME decides which slices are exported.\nFilename mode only changes the names of the PNG files.",
        "export.enter_asset": "Enter an asset name.\nYou can also select 'Keep Aseprite slice names.'",
        "export.continue": "Continue",
        "export.completed": "Export complete",
        "export.failed": "PNG export failed",
        "export.none_saved": "No PNG files were saved.",
        "export.options_open_failed": "Export options could not be opened",
        "export.options_open_failed_detail": "The export options dialog could not be opened.",
        "export.folder_open_failed": "The output folder dialog could not be opened. See ase_debug.log for details.",
        "source.removal_title": "Source removal",
        "source.removed": "Source removed.",
        "source.removed_profiles": "Connected profiles removed: {count}",
        "source.removed_partners": "Partner instances removed: {count}",
        "source.removed_npcs": "NPC instances removed: {count}",
        "source.removed_props": "PROP instances removed: {count}",
        "source.player_disabled": "The active player profile was removed, so player rendering was disabled.",
        "error.ase_path_save_title": "Aseprite path was not saved",
        "error.ase_path_save": "The selected path could not be saved to:\n{path}\n\nYou may need write permission. See ase_debug.log for details.",
        "error.settings_save_title": "Settings were not saved",
        "error.settings_save": "Could not write:\n{path}\n\nYour previous settings file was preserved. Check folder permissions and ase_debug.log.",
        "error.settings_load_title": "Settings could not be loaded",
        "error.settings_load": "The settings file is invalid or unreadable:\n{path}\n\nDefaults will be used. See ase_debug.log for details.",
        "error.project_save_title": "Project was not saved",
        "error.project_save": "Could not write:\n{path}\n\nYour previous project file was preserved. Check folder permissions and ase_debug.log.",
        "error.project_load_title": "Project could not be loaded",
        "error.project_load": "The project file is invalid or incomplete:\n{path}\n\nThe existing file was not changed. See ase_debug.log for details.",
        "error.source_add_title": "Source could not be added",
        "error.source_add": "Could not add:\n{path}\n\n{error}\n\nCheck the file and Aseprite path, then try again.",
        "error.source_refresh_title": "Source refresh failed",
        "error.source_refresh": "One or more Aseprite sources could not be refreshed. Existing project paths were kept. See ase_debug.log for details.",
        "error.layer_reload_title": "Layer visibility was not changed",
        "error.layer_reload": "Aseprite could not reload this source. The previous visibility was restored.",
        "tooltip.project.new": "Creates a new project.\nUnsaved layout changes may be lost.",
        "tooltip.project.load": "Loads the saved project JSON.",
        "tooltip.project.save": "Saves the current project layout and settings as JSON.",
        "tooltip.source.add": "Adds an Aseprite file as a player source.",
        "tooltip.npc.add": "Registers an Aseprite file as an NPC resource and spawns the NPC.",
        "tooltip.prop.add": "Registers an Aseprite file as a PROP resource and spawns the PROP.",
        "tooltip.options": "Opens language, NPC/PROP, physics, VFX, layer, and background options.",
        "tooltip.platform.edit": "Toggles position and size editing for platforms and solid boxes.",
        "tooltip.platform.add": "Adds a platform that characters can collide with.",
        "tooltip.solid_box.add": "Adds a solid box that characters cannot pass through.",
        "tooltip.npc.spawn": "Adds an NPC instance without analyzing the registered resource again.",
        "tooltip.prop.spawn": "Adds a PROP instance without analyzing the registered resource again.",
        "tooltip.npc.save": "Exports detected Parts/Particles slices as PNG files.\nThis does not save the NPC layout or project itself.",
        "tooltip.prop.save": "Exports detected Parts/Particles slices as PNG files.\nThis does not save the PROP layout or destruction state.",
        "tooltip.detected_slices": "Shows the Parts and Particles counts automatically detected in the current resource.",
        "tooltip.auto": "Detects slices containing real pixels inside the Parts and Particles tag ranges.\nRecommended for most files.",
        "tooltip.name": "Classifies slices when Part or Particle occurs in the slice name.\nFor compatibility with existing files.",
        "tooltip.naming.target": "Creates Parts_01 and Particle_01 files using the name you enter.",
        "tooltip.naming.slice": "Uses the slice names authored in Aseprite as PNG filenames.",
        "tooltip.dash_velocity": "Controls horizontal movement speed while dashing.",
        "tooltip.jump_power": "Controls the upward force applied when jumping.",
        "tooltip.show_guide": "Shows the 640x360 guide used as the game-screen reference.",
        "tooltip.shake": "Toggles screen shake for attack and impact effects.",
        "tooltip.layer_visibility": "Changes this layer's visibility and reloads the Aseprite source.",
        "tooltip.parallax": "Controls the background layer's relative movement against the camera.",
        "tooltip.npc_behavior": "Click to cycle this NPC's behavior.\nChoose Balanced, Idle, Follow, Aggressive, Guard, Patrol, or Flee.",
        "tooltip.replay_npc_intro": "Replays the spawn intro for the selected NPC or NPCs using the current profile.\nAttacking NPCs are skipped to preserve their attack animation.",
        "tooltip.scale": "Controls the displayed size of the selected background layer.",
        "tooltip.x_offset": "Adjusts the selected background layer's horizontal position.",
        "tooltip.y_offset": "Adjusts the selected background layer's vertical position.",
        "ui.no_resource": "No resource is selected.\nAdd a resource to use this option.",
        "tooltip.resource_required": "Add or select a resource before using this option.",
        "unity.copy_button": "COPY UNITY SETTINGS",
        "unity.dialog_title": "Unity Parallax Export",
        "unity.ppu": "Unity Pixels Per Unit",
        "unity.format": "Export Format",
        "unity.detailed": "Detailed",
        "unity.slack": "Slack",
        "unity.markdown": "Jira / Notion Markdown",
        "unity.tsv": "TSV Data",
        "unity.compact": "Slack",
        "unity.detailed_help": "Includes conversion rules and all values for every layer.",
        "unity.slack_help": "Copies fixed-width code-block tables for comparing values in messages.",
        "unity.markdown_help": "Copies two Markdown tables for documents and issue descriptions.",
        "unity.tsv_help": "Copies tab-separated data for Notion tables and spreadsheets.",
        "unity.include_disabled": "Include disabled layers",
        "unity.copy_clipboard": "Copy to Clipboard",
        "unity.preview": "Preview",
        "unity.preview_stats": "Included layers: {count}    Output length: {length:,} chars",
        "unity.many_layers": "There are many layers. The TSV format may be easier to use.",
        "unity.invalid_ppu": "Pixels Per Unit must be a finite number from 1 to 10000.",
        "unity.no_layers": "There are no background layers to export.\nAdd a background layer first.",
        "unity.copy_success_detailed": "Detailed handoff text was copied to the clipboard.\n\nLayers: {count}\nPixels Per Unit: {ppu}",
        "unity.copy_success_slack": "Slack sharing text was copied to the clipboard.\n\nLayers: {count}\nPixels Per Unit: {ppu}",
        "unity.copy_success_markdown": "Jira / Notion Markdown was copied to the clipboard.\n\nLayers: {count}",
        "unity.copy_success_tsv": "TSV data was copied to the clipboard.\n\nLayers: {count}\nOffsets: Unity units / PPU {ppu}",
        "unity.copy_failed": "Unity settings could not be copied to the clipboard.\nSee ase_debug.log for details.",
        "tooltip.unity_ppu": "The Pixels Per Unit value from Unity Sprite Import Settings.\nUsed to convert pixel offsets to Unity world units.",
        "tooltip.unity_copy": "Copies the current background layers' parallax, scale, and offsets\nas text that a Unity developer can use.",
        "tooltip.unity_detailed": "Exports coordinate conversion notes and per-layer values with explanations.",
        "tooltip.unity_slack": "Copies small fixed-width tables in a code block.\nUseful for quick comparisons in Slack and other messengers.",
        "tooltip.unity_markdown": "Copies two Markdown tables.\nSome Jira or Notion editors may handle table conversion differently.",
        "tooltip.unity_tsv": "Copies raw tab-separated table data.\nPaste it into Notion tables, Excel, Google Sheets, and similar tools.",
        "tooltip.unity_compact": "Legacy compact-table settings open as the Slack format.",
        "unity.handoff_title": "ASEPRITE ACTION VIEWER — UNITY PARALLAX HANDOFF",
        "unity.viewer_version": "Viewer Version",
        "unity.coordinate_basis": "Coordinate Basis",
        "unity.coordinate_x": "Unity X: positive is right",
        "unity.coordinate_y": "Unity Y: positive is up",
        "unity.coordinate_conversion": "Viewer Y offsets are sign-inverted during Unity conversion.",
        "unity.parallax_basis": "Parallax Basis",
        "unity.parallax_zero": "Viewer Parallax 0.0: screen-fixed; Unity Camera Follow Ratio 1.0",
        "unity.parallax_one": "Viewer Parallax 1.0: world-fixed; Unity Camera Follow Ratio 0.0",
        "unity.formula": "Unity equivalent: layer.position = layerStart + cameraDelta * (1 - viewerParallax) + positionOffset",
        "unity.enabled": "Enabled",
        "unity.yes": "Yes",
        "unity.no": "No",
        "unity.source": "Source",
        "unity.suggested_order": "Suggested Sorting Order",
        "unity.viewer": "Viewer",
        "unity.unity": "Unity",
        "unity.not_set": "Not set",
        "unity.offset_units": "Offsets are Unity units. PPU={ppu}.",
        "summary.naming": "File naming",
        "summary.target_naming": "Target name",
        "summary.slice_naming": "Aseprite Slice names",
        "summary.target": "Target name",
        "summary.classification": "Classification",
        "summary.parts": "Parts",
        "summary.particles": "Particles",
        "summary.skipped": "Skipped",
        "summary.failed": "Failed",
        "summary.collisions": "Collision renames",
        "summary.output_folder": "Output folder",
        "summary.auto": "AUTO",
        "summary.name": "NAME",
        "summary.count": "{count}",
        "summary.duplicates": "Possible cross-tag duplicates",
    },
}

CATEGORY_TRANSLATION_KEYS = {
    "LANGUAGE": "category.language",
    "PROPS": "category.props",
    "NPCS": "category.npcs",
    "PHYSICS": "category.physics",
    "AI & COMBAT": "category.ai_combat",
    "JUICE & VFX": "category.juice_vfx",
    "LAYERS": "category.layers",
    "CAMERA": "category.camera",
    "BG IMAGE": "category.bg_image",
    "BG COLOR": "category.bg_color",
    "CONTROLS": "category.controls",
}

SETTINGS_SECTION_QUICK = "quick"
SETTINGS_SECTION_INPUT = "input"
SETTINGS_SECTION_AI_COMBAT = "ai_combat"
SETTINGS_SECTION_BACKGROUND = "background"
SETTINGS_SECTION_VIEW_DEBUG = "view_debug"
SETTINGS_SECTION_ADVANCED = "advanced"
SETTINGS_SECTION_CONTROLS_APP = "controls_app"
SETTINGS_SECTION_SCENE_COMBAT = "scene_combat"
SETTINGS_SECTION_VIEW_BACKGROUND = "view_background"
SETTINGS_SECTION_NAV_HEIGHT = 42
SETTINGS_SECTION_INTRO_PADDING = 10
SETTINGS_SECTIONS = OrderedDict((
    (SETTINGS_SECTION_CONTROLS_APP, {
        "label": "settings.section.controls_app",
        "subtitle": "settings.subtitle.controls_app",
        "categories": ("LANGUAGE", "CONTROLS"),
        "info": (
            "settings.input.character", "settings.input.app",
            "settings.quick.guides", "settings.input.fast_action",
            "settings.input.controller_todo",
        ),
        "features": (
            "language", "character_controls", "app_shortcuts", "synergy",
            "fast_action_scope", "controller_todo",
        ),
    }),
    (SETTINGS_SECTION_SCENE_COMBAT, {
        "label": "settings.section.scene_combat",
        "subtitle": "settings.subtitle.scene_combat",
        "categories": (
            "NPCS", "AI & COMBAT", "JUICE & VFX", "LAYERS",
            "PROPS", "PHYSICS",
        ),
        "info": (
            "settings.ai.behavior", "settings.ai.combo",
            "settings.scene.lifecycle",
        ),
        "features": (
            "npc_behavior", "intro_replay", "combo_attack",
            "attack_lock", "despawn", "corpse", "props", "physics",
            "layers", "vfx",
        ),
    }),
    (SETTINGS_SECTION_VIEW_BACKGROUND, {
        "label": "settings.section.view_background",
        "subtitle": "settings.subtitle.view_background",
        "categories": ("BG IMAGE", "BG COLOR", "CAMERA"),
        "info": (
            "settings.background.guide", "settings.background.history",
            "settings.view.visual", "settings.view.guide",
        ),
        "features": (
            "background_layers", "parallax", "offsets", "gizmo",
            "axis_lock", "undo_redo", "camera", "performance", "hitbox",
            "app_guide",
        ),
    }),
))

SETTINGS_SECTION_MIGRATIONS = {
    SETTINGS_SECTION_QUICK: SETTINGS_SECTION_CONTROLS_APP,
    SETTINGS_SECTION_INPUT: SETTINGS_SECTION_CONTROLS_APP,
    SETTINGS_SECTION_AI_COMBAT: SETTINGS_SECTION_SCENE_COMBAT,
    SETTINGS_SECTION_BACKGROUND: SETTINGS_SECTION_VIEW_BACKGROUND,
    SETTINGS_SECTION_VIEW_DEBUG: SETTINGS_SECTION_VIEW_BACKGROUND,
    SETTINGS_SECTION_ADVANCED: SETTINGS_SECTION_SCENE_COMBAT,
}


def normalize_settings_section(section):
    migrated = SETTINGS_SECTION_MIGRATIONS.get(section, section)
    return (
        migrated
        if migrated in SETTINGS_SECTIONS
        else SETTINGS_SECTION_CONTROLS_APP
    )


def settings_section_model(section):
    section = normalize_settings_section(section)
    data = SETTINGS_SECTIONS[section]
    return {
        "id": section,
        "label": tr(data["label"]),
        "label_key": data["label"],
        "subtitle": tr(data["subtitle"]),
        "subtitle_key": data["subtitle"],
        "categories": tuple(data["categories"]),
        "info_keys": tuple(data["info"]),
        "features": tuple(data["features"]),
    }


def settings_section_button_rects(sidebar_width=SIDEBAR_WIDTH):
    gap = 6
    margin = 10
    columns = 3
    button_width = (
        int(sidebar_width) - margin * 2 - gap * (columns - 1)
    ) // columns
    rects = OrderedDict()
    for index, section in enumerate(SETTINGS_SECTIONS):
        row, column = divmod(index, columns)
        rects[section] = pygame.Rect(
            margin + column * (button_width + gap),
            6 + row * 32,
            button_width,
            26,
        )
    return rects


def settings_section_click_target(local_pos, sidebar_width=SIDEBAR_WIDTH):
    for section, rect in settings_section_button_rects(sidebar_width).items():
        if rect.collidepoint(local_pos):
            return section
    return None


def settings_section_transition(requested_section):
    """Build the session-only state reset applied when a settings tab changes."""
    return {
        "section": normalize_settings_section(requested_section),
        "scroll": 0,
        "binding_key": None,
        "active_input_attr": None,
    }


def valid_background_layer_index(player):
    index = getattr(player, "active_bg_layer", -1)
    backgrounds = getattr(player, "bg_layers", []) or []
    return index if isinstance(index, int) and 0 <= index < len(backgrounds) else -1


SETTINGS_SLIDER_DEFAULTS = {
    "dash_speed": 12.0,
    "jump_power": -18.0,
    "powerbomb_speed": 35.0,
    "platform_alpha": 150,
    "target_ai_count": 0,
    "npc_max_hp": 10,
    "atk_forward_v": 15.0,
    "base_shake": 0.2,
    "debris_force": 0.3,
    "cam_v_offset": -120,
}
BACKGROUND_LAYER_SLIDER_DEFAULTS = {
    "off_x": 0,
    "off_y": 0,
    "zoom": 2.0,
    "alpha": 255,
    "parallax": 1.0,
}
BACKGROUND_COLOR_DEFAULTS = (15, 15, 18)


def settings_slider_control_rects(sidebar_width, y, slider_left=110):
    """Return one consistent, non-overlapping slider/input/reset row layout."""
    reset_rect = pygame.Rect(max(0, int(sidebar_width) - 64), int(y) - 3, 54, 20)
    numeric_rect = pygame.Rect(reset_rect.x - 50, int(y) - 2, 42, 18)
    slider_right = numeric_rect.x - 12
    slider_rect = pygame.Rect(
        int(slider_left), int(y) + 5,
        max(24, slider_right - int(slider_left)), 8,
    )
    return {
        "slider": slider_rect,
        "numeric": numeric_rect,
        "reset": reset_rect,
    }


def slider_setting_value(player, attribute, default=None):
    fallback = SETTINGS_SLIDER_DEFAULTS.get(attribute, default)
    return _finite_number(getattr(player, attribute, fallback), fallback)


def reset_slider_setting(
    player, attribute, *, layer_index=None, color_index=None, persist=True,
):
    """Reset one verified slider value and preserve parallax offset history."""
    result = {
        "changed": False,
        "value": None,
        "status_key": "status.setting_reset_unavailable",
    }
    if player is None:
        return result

    if layer_index is not None:
        layers = getattr(player, "bg_layers", None)
        if (
            attribute not in BACKGROUND_LAYER_SLIDER_DEFAULTS
            or not isinstance(layers, list)
            or not isinstance(layer_index, int)
            or not 0 <= layer_index < len(layers)
            or not isinstance(layers[layer_index], dict)
        ):
            return result
        layer = layers[layer_index]
        default = BACKGROUND_LAYER_SLIDER_DEFAULTS[attribute]
        before = get_parallax_layer_offset(layer)
        if attribute in {"off_x", "off_y"}:
            commit_parallax_offset_edit(player)
            after = (
                default if attribute == "off_x" else before[0],
                default if attribute == "off_y" else before[1],
            )
            set_parallax_layer_offset(layer, *after)
            result["changed"] = push_parallax_offset_history(
                player, layer, before, after, f"reset_{attribute}",
            )
        else:
            previous = layer.get(attribute, default)
            layer[attribute] = default
            layer["needs_update"] = True
            result["changed"] = previous != default
        result["value"] = default
    elif color_index is not None:
        colors = getattr(player, "bg_color", None)
        if (
            not isinstance(colors, list)
            or not isinstance(color_index, int)
            or not 0 <= color_index < len(BACKGROUND_COLOR_DEFAULTS)
            or color_index >= len(colors)
        ):
            return result
        default = BACKGROUND_COLOR_DEFAULTS[color_index]
        result["changed"] = colors[color_index] != default
        colors[color_index] = default
        result["value"] = default
    else:
        if attribute not in SETTINGS_SLIDER_DEFAULTS:
            return result
        default = SETTINGS_SLIDER_DEFAULTS[attribute]
        previous = getattr(player, attribute, default)
        setattr(player, attribute, default)
        result["changed"] = previous != default
        result["value"] = default

    result["status_key"] = "status.setting_reset"
    player.settings_status_message = tr(
        result["status_key"], label=str(attribute).replace("_", " "),
    )
    if persist and hasattr(player, "save_settings"):
        player.save_settings()
    return result


def draw_slider_reset_button(surface, font, rect, enabled=True):
    pygame.draw.rect(
        surface, (70, 82, 104) if enabled else (48, 48, 54),
        rect, border_radius=4,
    )
    draw_centered_label(
        surface, font, tr("common.reset"), rect,
        (235, 240, 250) if enabled else (125, 125, 132),
    )


def settings_section_intro_height(section):
    info_count = len(settings_section_model(section)["info_keys"])
    return 36 + info_count * 42 + SETTINGS_SECTION_INTRO_PADDING


def draw_settings_section_navigation(
    surface, section, font, tooltip_regions=None, origin=(0, 0),
):
    section = normalize_settings_section(section)
    rects = settings_section_button_rects(surface.get_width())
    pygame.draw.rect(
        surface, (25, 25, 30),
        (0, 0, surface.get_width(), SETTINGS_SECTION_NAV_HEIGHT),
    )
    for section_id, rect in rects.items():
        selected = section_id == section
        pygame.draw.rect(
            surface,
            (59, 130, 246) if selected else (55, 58, 68),
            rect,
            border_radius=5,
        )
        draw_centered_label(
            surface, font, tr(SETTINGS_SECTIONS[section_id]["label"]), rect,
            (255, 255, 255) if selected else (195, 200, 212),
        )
        if tooltip_regions is not None:
            register_tooltip(
                tooltip_regions,
                rect.move(origin),
                f"tooltip.settings.section.{section_id}",
            )
    pygame.draw.line(
        surface, (59, 130, 246),
        (10, SETTINGS_SECTION_NAV_HEIGHT - 2),
        (surface.get_width() - 10, SETTINGS_SECTION_NAV_HEIGHT - 2),
        1,
    )
    return rects


def draw_settings_section_intro(surface, section, top, font, player=None):
    model = settings_section_model(section)
    height = settings_section_intro_height(section)
    panel = pygame.Rect(10, top, surface.get_width() - 20, height - 8)
    pygame.draw.rect(surface, (38, 42, 51), panel, border_radius=6)
    surface.blit(
        font.render(model["label"], True, (120, 190, 255)),
        (panel.x + 10, panel.y + 8),
    )
    subtitle = ellipsize_ui_text(model["subtitle"], font, panel.w - 20)
    surface.blit(
        font.render(subtitle, True, (155, 165, 185)),
        (panel.x + 10, panel.y + 26),
    )
    y = panel.y + 46
    for key in model["info_keys"]:
        if key == "settings.quick.selection":
            summary = (
                current_selection_summary(player)
                if player is not None
                else {"actor_text": "—", "resource_text": "—"}
            )
            text = tr(
                key,
                actor=summary["actor_text"],
                resource=summary["resource_text"],
            )
        else:
            text = tr(key)
        lines = wrap_ui_text(f"• {text}", font, panel.w - 20)
        for line_index, line in enumerate(lines[:2]):
            surface.blit(
                font.render(line, True, (190, 198, 214)),
                (panel.x + 10, y + line_index * 16),
            )
        y += 42
    return top + height


def normalize_language(language):
    return language if language in {LANG_KO, LANG_EN} else LANG_KO


def set_current_language(language):
    global _CURRENT_LANGUAGE
    selected = normalize_language(language)
    if selected != _CURRENT_LANGUAGE:
        _CURRENT_LANGUAGE = selected
        clear_ui_caches = globals().get("clear_ui_caches")
        if clear_ui_caches is not None:
            clear_ui_caches()
    else:
        _CURRENT_LANGUAGE = selected
    return _CURRENT_LANGUAGE


def tr(key, language=None, **kwargs):
    selected = normalize_language(language if language is not None else _CURRENT_LANGUAGE)
    text = TRANSLATIONS.get(selected, {}).get(key)
    if text is None:
        text = TRANSLATIONS[LANG_EN].get(key)
    if text is None:
        if key not in _MISSING_TRANSLATION_KEYS:
            _MISSING_TRANSLATION_KEYS.add(key)
            try:
                log_debug(f"[WARN] Missing translation key: {key}")
            except NameError:
                pass
        text = key
    try:
        return text.format(**kwargs)
    except (KeyError, ValueError):
        return text


def validate_unity_pixels_per_unit(value, language=None):
    try:
        pixels_per_unit = float(value)
    except (TypeError, ValueError):
        raise ValueError(tr("unity.invalid_ppu", language=language)) from None
    if not math.isfinite(pixels_per_unit) or not 1 <= pixels_per_unit <= 10000:
        raise ValueError(tr("unity.invalid_ppu", language=language))
    return pixels_per_unit


def _finite_number(value, default):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return float(default)
    return number if math.isfinite(number) else float(default)


def _normalized_zero(value):
    return 0.0 if abs(value) < 0.0000005 else value


def _format_export_number(value):
    value = _normalized_zero(float(value))
    text = f"{value:.4f}".rstrip("0").rstrip(".")
    return "0" if text in {"", "-0"} else text


UNITY_PARALLAX_EXPORT_FORMATS = {"detailed", "slack", "markdown", "tsv"}


def normalize_unity_parallax_export_format(value):
    if value == "compact":
        return "slack"
    return value if value in UNITY_PARALLAX_EXPORT_FORMATS else "detailed"


def display_width(text):
    width = 0
    for character in str(text):
        if unicodedata.combining(character):
            continue
        width += 2 if unicodedata.east_asian_width(character) in {"W", "F"} else 1
    return width


def _truncate_display_text(text, max_width=24):
    text = str(text)
    if display_width(text) <= max_width:
        return text
    target_width = max(0, max_width - 1)
    result = []
    current_width = 0
    for character in text:
        character_width = display_width(character)
        if current_width + character_width > target_width:
            break
        result.append(character)
        current_width += character_width
    return "".join(result).rstrip() + "…"


def _display_pad(text, width, right=False):
    text = str(text)
    padding = " " * max(0, width - display_width(text))
    return padding + text if right else text + padding


def _fixed_width_table(headers, rows, right_columns=()):
    widths = [
        max(display_width(header), *(display_width(row[index]) for row in rows))
        for index, header in enumerate(headers)
    ]
    return [
        "  ".join(_display_pad(value, widths[index], index in right_columns)
                   for index, value in enumerate(row))
        for row in [headers] + rows
    ]


def _markdown_cell(value):
    text = str(value).replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\\", "\\\\").replace("|", "\\|")
    return text.replace("\n", " ").replace("\t", " ").strip()


def _tsv_cell(value):
    text = str(value).replace("\r\n", "\n").replace("\r", "\n")
    return text.replace("\t", " ").replace("\n", " ").strip()


def _parallax_axes_are_independent(item):
    return (
        item["viewer_parallax_x"] != item["viewer_parallax_y"]
        or item["unity_camera_follow_x"] != item["unity_camera_follow_y"]
    )


def convert_layer_to_unity_parallax(layer, pixels_per_unit, order):
    ppu = validate_unity_pixels_per_unit(pixels_per_unit)
    layer = layer if isinstance(layer, dict) else {}
    viewer_parallax = _finite_number(layer.get("parallax", 1.0), 1.0)
    viewer_offset_x = _finite_number(layer.get("off_x", 0.0), 0.0)
    viewer_offset_y = _finite_number(layer.get("off_y", 0.0), 0.0)
    viewer_scale = _finite_number(layer.get("zoom", 2.0), 2.0)
    unity_scale = _normalized_zero(viewer_scale * 0.5)
    path = str(layer.get("path", "") or "")
    source_name = os.path.basename(path) if path else ""
    display_name = str(layer.get("name", "") or os.path.splitext(source_name)[0] or f"Layer {order + 1:02d}")
    image = layer.get("img")
    alpha = int(max(0, min(255, _finite_number(layer.get("alpha", 255), 255))))
    original_size = None
    try:
        if image is not None:
            original_size = (int(image.get_width()), int(image.get_height()))
    except (AttributeError, TypeError, ValueError, pygame.error):
        original_size = None
    current_size = (
        (max(1, int(original_size[0] * unity_scale)), max(1, int(original_size[1] * unity_scale)))
        if original_size is not None else None
    )
    return {
        "order": int(order),
        "name": display_name,
        "path": path,
        "source": source_name,
        "enabled": bool(layer.get("enabled", alpha > 0)),
        "alpha": alpha,
        "loop_x": bool(layer.get("loop_x", False)),
        "viewer_parallax_x": viewer_parallax,
        "viewer_parallax_y": viewer_parallax,
        "unity_camera_follow_x": _normalized_zero(1.0 - viewer_parallax),
        "unity_camera_follow_y": _normalized_zero(1.0 - viewer_parallax),
        "viewer_offset_x": viewer_offset_x,
        "viewer_offset_y": viewer_offset_y,
        "unity_offset_x": _normalized_zero(viewer_offset_x / ppu),
        "unity_offset_y": _normalized_zero(-viewer_offset_y / ppu),
        "viewer_scale_x": viewer_scale,
        "viewer_scale_y": viewer_scale,
        "unity_scale_x": unity_scale,
        "unity_scale_y": unity_scale,
        "original_size": original_size,
        "current_size": current_size,
    }


def viewer_layer_center_offset(layer, camera_delta_x, camera_delta_y):
    parallax = _finite_number(layer.get("parallax", 1.0), 1.0)
    return (
        -camera_delta_x * parallax + _finite_number(layer.get("off_x", 0.0), 0.0),
        -camera_delta_y * parallax + _finite_number(layer.get("off_y", 0.0), 0.0),
    )


def unity_layer_screen_offset(converted_layer, camera_delta_x, camera_delta_y):
    return (
        camera_delta_x * (converted_layer["unity_camera_follow_x"] - 1.0) + converted_layer["unity_offset_x"],
        camera_delta_y * (converted_layer["unity_camera_follow_y"] - 1.0) + converted_layer["unity_offset_y"],
    )


def build_detailed_unity_parallax_export(converted, ppu, language=None):
    ppu_text = _format_export_number(ppu)
    header = [
        tr("unity.handoff_title", language=language),
        f"{tr('unity.viewer_version', language=language)}: {APP_VERSION}",
        f"Pixels Per Unit: {ppu_text}",
        "",
    ]
    if not converted:
        return "\n".join(header + [tr("unity.no_layers", language=language)])
    lines = header + [
        tr("unity.coordinate_basis", language=language),
        f"- {tr('unity.coordinate_x', language=language)}",
        f"- {tr('unity.coordinate_y', language=language)}",
        f"- {tr('unity.coordinate_conversion', language=language)}",
        "",
        tr("unity.parallax_basis", language=language),
        f"- {tr('unity.parallax_zero', language=language)}",
        f"- {tr('unity.parallax_one', language=language)}",
        f"- {tr('unity.formula', language=language)}",
    ]
    for item in converted:
        size_text = (
            f"{item['original_size'][0]}x{item['original_size'][1]} px"
            if item["original_size"] else tr("unity.not_set", language=language)
        )
        current_size_text = (
            f"{item['current_size'][0]}x{item['current_size'][1]} px"
            if item["current_size"] else tr("unity.not_set", language=language)
        )
        lines.extend([
            "",
            f"[Layer {item['order'] + 1:02d}]",
            f"Name: {item['name']}",
            f"{tr('unity.source', language=language)}: {item['source'] or tr('unity.not_set', language=language)}",
            f"Path: {item['path'] or tr('unity.not_set', language=language)}",
            f"{tr('unity.enabled', language=language)}: {tr('unity.yes' if item['enabled'] else 'unity.no', language=language)}",
            f"{tr('unity.suggested_order', language=language)}: {item['order']}",
            f"Original Size: {size_text}",
            f"Viewer Size at Camera Zoom 1.0: {current_size_text}",
            "",
            tr("unity.viewer", language=language),
            f"- Parallax X: {_format_export_number(item['viewer_parallax_x'])}",
            f"- Parallax Y: {_format_export_number(item['viewer_parallax_y'])}",
            f"- Offset X: {_format_export_number(item['viewer_offset_x'])} px",
            f"- Offset Y: {_format_export_number(item['viewer_offset_y'])} px",
            f"- Scale Setting X: {_format_export_number(item['viewer_scale_x'])}",
            f"- Scale Setting Y: {_format_export_number(item['viewer_scale_y'])}",
            f"- Alpha: {item['alpha']}",
            f"- Loop X: {tr('unity.yes' if item['loop_x'] else 'unity.no', language=language)}",
            "",
            tr("unity.unity", language=language),
            f"- Camera Follow Ratio X: {_format_export_number(item['unity_camera_follow_x'])}",
            f"- Camera Follow Ratio Y: {_format_export_number(item['unity_camera_follow_y'])}",
            f"- Position Offset X: {_format_export_number(item['unity_offset_x'])} units",
            f"- Position Offset Y: {_format_export_number(item['unity_offset_y'])} units",
            f"- Local Scale X: {_format_export_number(item['unity_scale_x'])}",
            f"- Local Scale Y: {_format_export_number(item['unity_scale_y'])}",
        ])
    return "\n".join(lines)


def _slack_fence(text):
    longest = max((len(match.group(0)) for match in re.finditer(r"`+", text)), default=0)
    return "`" * max(3, longest + 1)


def build_slack_unity_parallax_export(converted, ppu, language=None, max_width=88):
    ppu_text = _format_export_number(ppu)
    if not converted:
        return build_detailed_unity_parallax_export(converted, ppu, language=language)
    names = [_truncate_display_text(item["name"], 24) for item in converted]
    mappings = [
        (short_name, item["name"])
        for item, short_name in zip(converted, names)
        if short_name != item["name"]
    ]
    parallax_rows = [
        [
            name, str(item["order"]), "Y" if item["enabled"] else "N",
            _format_export_number(item["viewer_parallax_x"]),
            _format_export_number(item["unity_camera_follow_x"]),
        ]
        for item, name in zip(converted, names)
    ]
    transform_rows = [
        [
            name,
            f"{_format_export_number(item['unity_offset_x'])} / {_format_export_number(item['unity_offset_y'])}",
            f"{_format_export_number(item['unity_scale_x'])} / {_format_export_number(item['unity_scale_y'])}",
        ]
        for item, name in zip(converted, names)
    ]
    parallax_table = _fixed_width_table(
        ["LAYER", "ORDER", "ON", "P", "FOLLOW"], parallax_rows, {1, 3, 4},
    )
    transform_table = _fixed_width_table(
        ["LAYER", "OFFSET X/Y", "SCALE X/Y"], transform_rows, {1, 2},
    )
    table_width = max(display_width(line) for line in parallax_table + transform_table)
    use_cards = (
        table_width > max_width
        or any(display_width(item["name"]) > 48 for item in converted)
        or any(_parallax_axes_are_independent(item) for item in converted)
    )
    if use_cards:
        body_lines = []
        for index, item in enumerate(converted, 1):
            if _parallax_axes_are_independent(item):
                parallax_line = (
                    f"P X/Y {_format_export_number(item['viewer_parallax_x'])}, "
                    f"{_format_export_number(item['viewer_parallax_y'])}"
                    f" → Follow X/Y {_format_export_number(item['unity_camera_follow_x'])}, "
                    f"{_format_export_number(item['unity_camera_follow_y'])}"
                )
            else:
                parallax_line = (
                    f"P {_format_export_number(item['viewer_parallax_x'])}"
                    f" → Follow {_format_export_number(item['unity_camera_follow_x'])}"
                )
            body_lines.extend([
                f"[{index:02d}] {item['name']} — {'ON' if item['enabled'] else 'OFF'}",
                parallax_line,
                (
                    f"Offset {_format_export_number(item['unity_offset_x'])}, "
                    f"{_format_export_number(item['unity_offset_y'])}"
                ),
                (
                    f"Scale {_format_export_number(item['unity_scale_x'])}, "
                    f"{_format_export_number(item['unity_scale_y'])}"
                ),
                "",
            ])
        if body_lines:
            body_lines.pop()
    else:
        body_lines = parallax_table + [""] + transform_table
        body_lines.extend([
            "",
            "Offset: Unity units",
            "Follow = 1 - Viewer Parallax",
        ])
        if mappings:
            body_lines.extend(["", "Names"])
            body_lines.extend(f"- {short_name} = {full_name}" for short_name, full_name in mappings)
    body = "\n".join(body_lines)
    fence = _slack_fence(body)
    return "\n".join([
        f"*Unity Parallax — PPU {ppu_text}*",
        f"Viewer {APP_VERSION}",
        "",
        fence,
        body,
        fence,
    ])


def build_markdown_unity_parallax_export(converted, ppu, language=None):
    ppu_text = _format_export_number(ppu)
    yes = tr("unity.yes", language=language)
    no = tr("unity.no", language=language)
    lines = [
        "## Unity Parallax Handoff",
        "",
        f"- Viewer: `{APP_VERSION}`",
        f"- Pixels Per Unit: `{ppu_text}`",
        "- Offset unit: Unity units",
        "- Unity Follow: `1 - Viewer Parallax`",
        "",
        "### Parallax",
        "",
        "| Layer | Order | Enabled | Viewer P | Unity Follow |",
        "|---|---:|:---:|---:|---:|",
    ]
    for item in converted:
        lines.append(
            f"| {_markdown_cell(item['name'])} | {item['order']} | "
            f"{yes if item['enabled'] else no} | "
            f"{_format_export_number(item['viewer_parallax_x'])} | "
            f"{_format_export_number(item['unity_camera_follow_x'])} |"
        )
    lines.extend([
        "",
        "### Transform",
        "",
        "| Layer | Offset X | Offset Y | Scale X | Scale Y |",
        "|---|---:|---:|---:|---:|",
    ])
    for item in converted:
        lines.append(
            f"| {_markdown_cell(item['name'])} | "
            f"{_format_export_number(item['unity_offset_x'])} | "
            f"{_format_export_number(item['unity_offset_y'])} | "
            f"{_format_export_number(item['unity_scale_x'])} | "
            f"{_format_export_number(item['unity_scale_y'])} |"
        )
    sources = [item for item in converted if item["path"] or item["source"]]
    if sources:
        lines.extend(["", "### Sources", ""])
        for item in sources:
            source = item["path"] or item["source"]
            lines.append(f"- **{_markdown_cell(item['name'])}**: {_markdown_cell(source)}")
    return "\n".join(lines)


def build_tsv_unity_parallax_export(converted, ppu, language=None):
    rows = [[
        "Layer", "Order", "Enabled", "Viewer Parallax", "Unity Follow",
        "Offset X", "Offset Y", "Scale X", "Scale Y",
    ]]
    for item in converted:
        rows.append([
            _tsv_cell(item["name"]),
            str(item["order"]),
            tr("unity.yes" if item["enabled"] else "unity.no", language=language),
            _format_export_number(item["viewer_parallax_x"]),
            _format_export_number(item["unity_camera_follow_x"]),
            _format_export_number(item["unity_offset_x"]),
            _format_export_number(item["unity_offset_y"]),
            _format_export_number(item["unity_scale_x"]),
            _format_export_number(item["unity_scale_y"]),
        ])
    return "\n".join("\t".join(row) for row in rows)


def build_unity_parallax_export(layers, pixels_per_unit, output_format="detailed", include_disabled=True, language=None):
    ppu = validate_unity_pixels_per_unit(pixels_per_unit, language=language)
    output_format = normalize_unity_parallax_export_format(output_format)
    converted = [
        convert_layer_to_unity_parallax(layer, ppu, order)
        for order, layer in enumerate(layers or [])
    ]
    if not include_disabled:
        converted = [layer for layer in converted if layer["enabled"]]
    formatters = {
        "detailed": build_detailed_unity_parallax_export,
        "slack": build_slack_unity_parallax_export,
        "markdown": build_markdown_unity_parallax_export,
        "tsv": build_tsv_unity_parallax_export,
    }
    return formatters[output_format](converted, ppu, language=language)


def copy_text_to_clipboard(text, tk_factory=tk.Tk):
    root = None
    try:
        root = tk_factory()
        root.withdraw()
        root.clipboard_clear()
        root.clipboard_append(text)
        root.update()
        return True, ""
    except (tk.TclError, OSError, RuntimeError) as error:
        log_debug(f"[ERROR] Unity clipboard copy failed: {error}\n{traceback.format_exc()}")
        return False, str(error)
    finally:
        if root is not None:
            try:
                root.destroy()
            except tk.TclError:
                pass


def perform_unity_parallax_clipboard_export(
    layers, pixels_per_unit, output_format="detailed", include_disabled=True,
    language=None, clipboard_writer=copy_text_to_clipboard,
):
    try:
        ppu = validate_unity_pixels_per_unit(pixels_per_unit, language=language)
        output_format = normalize_unity_parallax_export_format(output_format)
        selected_layers = [
            layer for layer in (layers or [])
            if include_disabled or convert_layer_to_unity_parallax(layer, ppu, 0)["enabled"]
        ]
        if not selected_layers:
            return {"success": False, "error": tr("unity.no_layers", language=language), "text": "", "count": 0}
        text = build_unity_parallax_export(
            selected_layers, ppu, output_format=output_format,
            include_disabled=True, language=language,
        )
        success, error = clipboard_writer(text)
        return {
            "success": bool(success), "error": error or "", "text": text,
            "count": len(selected_layers), "pixels_per_unit": ppu,
            "output_format": output_format,
        }
    except (TypeError, ValueError) as error:
        return {"success": False, "error": str(error), "text": "", "count": 0}


class AsepriteError(RuntimeError):
    pass


def calculate_initial_window_size(
    desktop_size,
    zoom=3.0,
    target_size=(640, 360),
    saved_size=None,
):
    desktop_w, desktop_h = max(1, int(desktop_size[0])), max(1, int(desktop_size[1]))
    max_w, max_h = max(1, int(desktop_w * 0.9)), max(1, int(desktop_h * 0.9))
    if (
        isinstance(saved_size, (list, tuple))
        and len(saved_size) >= 2
        and all(isinstance(value, (int, float)) and value > 0 for value in saved_size[:2])
    ):
        requested_w, requested_h = int(saved_size[0]), int(saved_size[1])
    else:
        requested_w = max(
            DEFAULT_WINDOW_SIZE[0],
            SIDEBAR_WIDTH + math.ceil(target_size[0] * zoom) + WINDOW_MARGIN[0],
        )
        requested_h = max(
            DEFAULT_WINDOW_SIZE[1],
            TOP_UI_HEIGHT + math.ceil(target_size[1] * zoom) + WINDOW_MARGIN[1],
        )
    minimum_w, minimum_h = min(MIN_WINDOW_SIZE[0], max_w), min(MIN_WINDOW_SIZE[1], max_h)
    return (
        max(minimum_w, min(requested_w, max_w)),
        max(minimum_h, min(requested_h, max_h)),
    )


def current_desktop_size():
    try:
        sizes = pygame.display.get_desktop_sizes()
        if sizes:
            return sizes[0]
    except pygame.error:
        pass
    info = pygame.display.Info()
    return max(1, info.current_w), max(1, info.current_h)


def app_window_title():
    return f"{APP_TITLE} {APP_VERSION}"


def application_check_success_message(
    example_count, expected_example_count=None, tk_patchlevel=None,
):
    message = (
        f"CHECK OK: {app_window_title()}; pygame {pygame.version.ver}; "
        f"app_root={APP_ROOT}; example_resources={example_count}"
    )
    if expected_example_count is not None:
        message += f"/{expected_example_count}"
        if example_count < expected_example_count:
            message += "; external_example_resources_required=true"
    if tk_patchlevel:
        message += f"; tkinter_tcl={tk_patchlevel}"
    return message


def check_tk_runtime():
    """Verify the packaged Tcl/Tk runtime without opening a persistent dialog."""
    root = tk.Tk()
    try:
        root.withdraw()
        return str(root.tk.call("info", "patchlevel"))
    finally:
        root.destroy()


def log_boot():
    log_debug(
        f"[BOOT] version={APP_VERSION} entry={os.path.abspath(__file__)} "
        f"python={sys.executable} cwd={os.getcwd()}"
    )


def app_resource_path(relative_path):
    for root in (RESOURCE_ROOT, APP_ROOT):
        candidate = os.path.abspath(os.path.join(root, relative_path))
        if os.path.exists(candidate):
            return candidate
    return os.path.abspath(os.path.join(APP_ROOT, relative_path))


def portable_path(path, reference_file):
    absolute_path = os.path.abspath(path)
    reference_dir = os.path.dirname(os.path.abspath(reference_file))
    try:
        return os.path.relpath(absolute_path, reference_dir).replace("\\", "/")
    except ValueError:
        return absolute_path


def resolve_stored_path(stored_path, reference_file, app_root=APP_ROOT):
    if not stored_path or not isinstance(stored_path, str):
        return None, []
    reference_dir = os.path.dirname(os.path.abspath(reference_file))
    candidates = []
    if os.path.isabs(stored_path):
        candidates.append(stored_path)
    else:
        candidates.extend((os.path.join(reference_dir, stored_path), os.path.join(app_root, stored_path)))
    basename = os.path.basename(stored_path)
    candidates.extend((os.path.join(reference_dir, basename), os.path.join(reference_dir, "Testfiles", basename), os.path.join(app_root, basename)))
    checked = []
    for candidate in candidates:
        normalized = os.path.abspath(candidate)
        if normalized in checked:
            continue
        checked.append(normalized)
        if os.path.isfile(normalized):
            return normalized, checked
    return None, checked


def file_sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as source_file:
        for chunk in iter(lambda: source_file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest().upper()


def _historical_example_profiles():
    return [
        {
            "name": "PLAYER",
            "source_idx": 0,
            "kind": "player",
            "mappings": {
                "IDLE": [[0, "Idle_(Loop)"]],
                "WALK": [[0, "Walk_(Loop)"]],
                "JUMP": [[0, "Jump_(Loop)"]],
                "FALL": [[0, "Fall_Ready"], [0, "Fall_(Loop)"]],
                "ComboAttack_1": [[0, "ComboAttack_1_Ready"], [0, "ComboAttack_1"]],
                "ComboAttack_2": [[0, "ComboAttack_2_Ready"], [0, "ComboAttack_2"]],
                "ComboAttack_3": [[0, "ComboAttack_3_Ready"], [0, "ComboAttack_3"]],
                "ComboAttack_4": [],
                "JUMPATTACK": [[0, "JumpAttack_Ready"], [0, "JumpAttack"]],
                "POWERBOMB": [[0, "PowerBomb_Ready"], [0, "PowerBomb_(Loop)"], [0, "PowerBomb_End"]],
                "DASH": [[0, "Dash"]],
                "SKILL 1": [],
                "SKILL 2": [],
                "SKILL 3": [],
                "HIT_1": [],
                "HIT_2": [],
                "Swap_Enter": [[0, "Swap_Enter"]],
                "Swap_Exit": [[0, "Swap_Exit_Ready"], [0, "Swap_Exit"]],
            },
        },
        {
            "name": "NPC_1",
            "source_idx": 1,
            "kind": "partner",
            "mappings": {
                "IDLE": [[1, "Idle_(Loop)"]],
                "WALK": [[1, "Walk_(Loop)"]],
                "JUMP": [[1, "Jump(Loop)"]],
                "FALL": [[1, "Fall_Ready"], [1, "Fall_(Loop)"]],
                "ComboAttack_1": [[1, "ComboAttack_1_Ready"], [1, "ComboAttack_1"]],
                "ComboAttack_2": [[1, "ComboAttack_2"]],
                "ComboAttack_3": [[1, "ComboAttack_3_Ready"], [1, "ComboAttack_3"]],
                "ComboAttack_4": [[1, "ComboAttack_4_Ready"], [1, "ComboAttack_4"]],
                "JUMPATTACK": [[1, "JumpAttack_Ready"], [1, "JumpAttack"]],
                "POWERBOMB": [[1, "PowerBomb"], [1, "PowerBomb_(Loop)"], [1, "PowerBomb_End"]],
                "DASH": [[1, "Dash"]],
                "SKILL 1": [],
                "SKILL 2": [],
                "SKILL 3": [],
                "HIT_1": [],
                "HIT_2": [],
                "Swap_Enter": [[1, "Swap_Enter"]],
                "Swap_Exit": [[1, "Swap_Exit_Ready"], [1, "Swap_Exit"]],
            },
        },
    ]


_EXAMPLE_SOURCES = [
    {
        "path": "resources/examples/shared/sources/Cailin_00_Public.aseprite",
        "sha256": "184D011939C82AAD384F2F2BC561654C7E2105F236BB1EB768B99F5534FE1A99",
    },
    {
        "path": "resources/examples/shared/sources/Nisariel_00_Public_02.aseprite",
        "sha256": "FFA591D664F3323458B09CEF9B5515CCC02B84375307EC5D73F7FD88FAB26D01",
    },
]


def example_preset(variant):
    common = {
        "sources": _EXAMPLE_SOURCES,
        "profiles": _historical_example_profiles(),
        "ai_count": 0,
        "platforms": [[262, 372, 200, 20], [500, 200, 200, 20], [-146, 248, 300, 20], [900, 300, 400, 20], [-1027, 207, 927, 51], [-164, 69, 254, 25]],
        "solid_boxes": [[-628, 254, 349, 275], [-739, -287, 614, 208]],
        "physics": {"dash_speed": 12.0, "jump_power": -18.0, "powerbomb_speed": 35.0},
        "combat": {"atk_forward_v": 15.0, "is_ranged_combo": False},
        "vfx": {"shake_enabled": True, "vfx_enabled": True, "base_shake": 0.2, "debris_force": 0.3},
        "viewport": {"show_viewport": True, "target_w": 640, "target_h": 360},
        "npc_max_hp": 10,
    }
    if variant == 1:
        common.update({
            "name": "EX 1",
            "purpose": "Single-layer lobby environment",
            "bg_color": [17, 15, 18],
            "cam_v_offset": -120,
            "platform_alpha": 5.275862068965517,
            "bg_layers": [{
                "path": "resources/examples/ex1/backgrounds/로비 컨셉94 (1).png",
                "sha256": "5CDB08AF1D823E629316AF19AB7B3511A861F03AFA29FD9A33AA42D1979B144F",
                "off_x": 0, "off_y": -130.0, "zoom": 2.0, "alpha": 255,
                "parallax": 0.9862068965517241, "loop_x": False,
            }],
        })
    elif variant == 2:
        common.update({
            "name": "EX 2",
            "purpose": "Six-layer parallax environment",
            "bg_color": [15, 15, 18],
            "cam_v_offset": -100.0,
            "platform_alpha": 150,
            "bg_layers": [
                {"path": "resources/examples/ex2/parallax/00.png", "sha256": "7E7B8B6BAAAA4EB83D87F23FB71CE3EAA5751F69D8081F741F72F1FB74017497", "off_x": 0, "off_y": -13, "zoom": 2.0, "alpha": 255, "parallax": 0.0, "loop_x": False},
                {"path": "resources/examples/ex2/parallax/01.png", "sha256": "0E464F568C8BD22FC9327E9690EA7EAEB85F848C36AB41434FBF58910DB629EC", "off_x": 0, "off_y": -27, "zoom": 2.0, "alpha": 255, "parallax": 0.05, "loop_x": False},
                {"path": "resources/examples/ex2/parallax/# 2번_완성본.png", "sha256": "8679AF1C841547DCE829A53299BE7B1905DDF4983CBABCBFF530B60D6D5B50BB", "off_x": 0, "off_y": -137, "zoom": 2.0, "alpha": 125, "parallax": 0.06, "loop_x": False},
                {"path": "resources/examples/ex2/parallax/# 3번_완성본.png", "sha256": "DBA6908BED67A33A514B38D2CFA45CFBA4B79AE194184EEF5F3365B457B13C22", "off_x": 0, "off_y": -220, "zoom": 2.0, "alpha": 255, "parallax": 0.5344827586206895, "loop_x": True},
                {"path": "resources/examples/ex2/parallax/# 4번_완성본.png", "sha256": "3B87B5EFB69929F18F092C5A8D736219AB8B525019811813BA5B2C7034A4B030", "off_x": 0, "off_y": -234, "zoom": 2.0, "alpha": 255, "parallax": 0.703448275862069, "loop_x": True},
                {"path": "resources/examples/ex2/parallax/레이어 3.png", "sha256": "F5200A638007A255A027D907746BC644EFB3A5F5331F82C04B539CB137586345", "off_x": 0, "off_y": 137, "zoom": 2.0, "alpha": 255, "parallax": 1.0, "loop_x": True},
            ],
        })
    else:
        raise ValueError(f"Unknown example variant: {variant}")
    return copy.deepcopy(common)

# Comprehensive Log Function
def log_debug(msg):
    try:
        with open(os.path.join(APP_ROOT, "ase_debug.log"), "a", encoding="utf-8") as f:
            f.write(f"{msg}\n")
    except OSError:
        pass
    print(msg)


def log_debug_once(key, msg):
    if key in _LOGGED_ERROR_KEYS:
        return
    _LOGGED_ERROR_KEYS.add(key)
    log_debug(msg)


def show_user_error(title, message, key=None):
    if key and key in _SHOWN_ERROR_KEYS:
        return
    if key:
        _SHOWN_ERROR_KEYS.add(key)
    log_debug(f"[USER ERROR] {title}: {message}")
    try:
        root = tk.Tk(); root.withdraw(); root.attributes("-topmost", True)
        messagebox.showerror(title, message, parent=root); root.destroy()
    except Exception as e:
        log_debug(f"[ERROR] Could not display error dialog: {e}")

def show_user_info(title, message):
    log_debug(f"[USER INFO] {title}: {message}")
    root = None
    try:
        root = tk.Tk(); root.withdraw(); root.attributes("-topmost", True)
        messagebox.showinfo(title, message, parent=root)
    except Exception as e:
        log_debug(f"[ERROR] Could not display information dialog: {e}")
    finally:
        if root is not None:
            try: root.destroy()
            except tk.TclError: pass


def profile_kind(profile, profile_index=None):
    kind = getattr(profile, "kind", None)
    if kind in {"player", "partner", "npc", "prop"}:
        return kind
    if getattr(profile, "is_prop_profile", False):
        return "prop"
    return "player" if profile_index == 0 else "npc"


def source_kind(source):
    kind = getattr(source, "kind", None)
    if kind in {"generic", "npc", "prop"}:
        return kind
    return "prop" if getattr(source, "is_prop_source", False) else "generic"


def _safe_slice_stem(slice_name, fallback_index):
    name = str(slice_name or "").strip()
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "", name)
    name = name.rstrip(" .")
    reserved_base = name.split(".", 1)[0].upper()
    if reserved_base in {
        "CON", "PRN", "AUX", "NUL",
        "COM1", "COM2", "COM3", "COM4", "COM5", "COM6", "COM7", "COM8", "COM9",
        "LPT1", "LPT2", "LPT3", "LPT4", "LPT5", "LPT6", "LPT7", "LPT8", "LPT9",
    }:
        name = f"{name}_slice"
    return name or f"slice_{fallback_index:03d}"


def safe_original_slice_stem(slice_name, fallback_index):
    safe = _safe_slice_stem(slice_name, fallback_index)
    if safe == f"slice_{fallback_index:03d}":
        return f"Slice_{fallback_index:03d}"
    return safe


def suggested_export_target_name(source):
    source_name = getattr(source, "name", "") or getattr(source, "file_path", "")
    return os.path.splitext(os.path.basename(str(source_name)))[0].strip()


def validate_slice_export_options(options):
    if not isinstance(options, dict):
        return None, "Export options are missing."
    classification = str(options.get("classification", "auto")).lower()
    naming_mode = str(options.get("naming_mode", "target")).lower()
    if classification not in {"auto", "name"}:
        return None, "Classification must be AUTO or NAME."
    if naming_mode not in {"target", "slice"}:
        return None, "File naming must use a target name or Aseprite Slice names."
    target_name = str(options.get("target_name", "")).strip()
    if naming_mode == "target" and not target_name:
        return None, "Enter a target name or select 'Keep Aseprite Slice names'."
    return {
        "classification": classification,
        "naming_mode": naming_mode,
        "target_name": target_name,
    }, ""


def build_slice_export_plan(source, options):
    validated, error = validate_slice_export_options(options)
    if error:
        return {"entries": [], "error": error, "parts": 0, "particles": 0}
    try:
        classified = classify_export_slices(source, mode=validated["classification"])
    except (KeyError, IndexError, TypeError, ValueError, pygame.error) as exception:
        return {"entries": [], "error": str(exception), "parts": 0, "particles": 0}
    owner_stem = (
        _safe_slice_stem(validated["target_name"], 1)
        if validated["naming_mode"] == "target" else ""
    )
    group_numbers = {"Parts": 0, "Particles": 0}
    reserved_names = set()
    entries = []
    for item_index, item in enumerate(classified["items"], 1):
        group = item["group"]
        group_numbers[group] += 1
        if validated["naming_mode"] == "target":
            label = "Parts" if group == "Parts" else "Particle"
            standard_stem = f"{owner_stem}_{label}_{group_numbers[group]:02d}"
        else:
            standard_stem = safe_original_slice_stem(item["slice_name"], item_index)
        filename = f"{standard_stem}.png"
        suffix = 2
        while filename.casefold() in reserved_names:
            filename = f"{standard_stem}_{suffix}.png"
            suffix += 1
        reserved_names.add(filename.casefold())
        entries.append({
            "group": group,
            "slice_name": item["slice_name"],
            "frame": item["frame"],
            "bounds": dict(item["bounds"]),
            "image": item["image"],
            "standard_stem": standard_stem,
            "filename": filename,
            "possible_duplicate": item.get("possible_duplicate", False),
        })
    return {
        "entries": entries,
        "error": "",
        "parts": group_numbers["Parts"],
        "particles": group_numbers["Particles"],
        "classification": validated["classification"],
        "naming_mode": validated["naming_mode"],
        "target_name": validated["target_name"],
        "skipped": list(classified.get("skipped", [])),
    }


def slice_export_filename_preview(source, options, language=None):
    plan = build_slice_export_plan(source, options)
    if plan["error"]:
        return [tr("export.enter_asset", language=language)]
    return [
        entry["filename"] for entry in plan["entries"]
    ] or [tr("export.no_slice_preview", language=language)]


def _unique_png_path(output_directory, stem, reserved_names):
    suffix = 1
    while True:
        filename = f"{stem}.png" if suffix == 1 else f"{stem}_{suffix}.png"
        candidate = os.path.join(output_directory, filename)
        if filename.casefold() not in reserved_names and not os.path.exists(candidate):
            reserved_names.add(filename.casefold())
            return candidate
        suffix += 1


def find_source_tag(source, expected_name):
    normalized = expected_name.casefold()
    return next((name for name in getattr(source, "tags", {}) if name.casefold() == normalized), None)


def active_slice_key(slice_keys, frame_index):
    return max(
        (
            key for key in slice_keys
            if isinstance(key, dict) and isinstance(key.get("frame"), int) and key["frame"] <= frame_index
        ),
        key=lambda key: key["frame"],
        default=None,
    )


def crop_source_slice(source, frame_index, bounds, facing_right=True):
    width, height = int(bounds["w"]), int(bounds["h"])
    if width <= 0 or height <= 0 or not 0 <= frame_index < len(source.frames):
        return None
    frame_image = source.get_frame(frame_index, 1.0, True)
    if frame_image is None:
        return None
    frame_info = source.frames[frame_index]
    crop_x = int(bounds["x"]) - int(source.orig_w) // 2 - int(frame_info["ox"])
    crop_y = int(bounds["y"]) - int(source.orig_h) // 2 - int(frame_info["oy"])
    cropped = pygame.Surface((width, height), pygame.SRCALPHA)
    cropped.blit(frame_image, (-crop_x, -crop_y))
    if not facing_right:
        cropped = pygame.transform.flip(cropped, True, False)
    return cropped


def representative_slice_image(source, tag_name, slice_keys, require_pixels=True):
    tag_range = getattr(source, "tags", {}).get(tag_name)
    if not isinstance(tag_range, (list, tuple)) or len(tag_range) < 2:
        return None
    start, end = tag_range[0], tag_range[1]
    if not isinstance(start, int) or not isinstance(end, int):
        return None
    for frame_index in range(max(0, start), min(end, len(source.frames) - 1) + 1):
        key = active_slice_key(slice_keys, frame_index)
        if key is None or not isinstance(key.get("bounds"), dict):
            continue
        image = crop_source_slice(source, frame_index, key["bounds"])
        if image is None:
            continue
        if require_pixels and not image.get_bounding_rect().width:
            continue
        return {
            "frame": frame_index,
            "bounds": dict(key["bounds"]),
            "image": image,
        }
    return None


def _classify_export_slices_uncached(source, mode="auto"):
    mode = str(mode or "auto").lower()
    if mode not in {"auto", "name"}:
        raise ValueError(f"Unknown Slice classification mode: {mode}")
    parts_tag = find_source_tag(source, "Parts")
    particles_tag = find_source_tag(source, "Particles")
    items = []
    skipped = []
    if parts_tag is None:
        skipped.append("Parts tag was not found.")
    if particles_tag is None:
        skipped.append("Particles tag was not found.")

    for definition_index, (slice_name, slice_keys) in enumerate(getattr(source, "slices", {}).items()):
        try:
            name_lower = str(slice_name).casefold()
            has_particle_hint = "particle" in name_lower
            has_part_hint = "part" in name_lower and not has_particle_hint
            candidates = {}
            if mode == "name":
                if parts_tag and not has_particle_hint:
                    candidates["Parts"] = representative_slice_image(source, parts_tag, slice_keys, require_pixels=False)
                if particles_tag and has_particle_hint:
                    candidates["Particles"] = representative_slice_image(source, particles_tag, slice_keys, require_pixels=False)
            else:
                if parts_tag:
                    candidates["Parts"] = representative_slice_image(source, parts_tag, slice_keys, require_pixels=True)
                if particles_tag:
                    candidates["Particles"] = representative_slice_image(source, particles_tag, slice_keys, require_pixels=True)
        except (KeyError, IndexError, TypeError, ValueError, pygame.error) as e:
            skipped.append(f"{slice_name}: Slice analysis failed.")
            log_debug(f"[WARN] Slice analysis skipped {slice_name!r}: {e}")
            continue

        valid_groups = [group for group, representative in candidates.items() if representative is not None]
        if mode == "auto" and len(valid_groups) == 2:
            if has_particle_hint:
                valid_groups = ["Particles"]
            elif has_part_hint:
                valid_groups = ["Parts"]
        if not valid_groups:
            skipped.append(f"{slice_name}: no non-empty image in the selected tag frames.")
            continue
        duplicate = False
        if mode == "auto" and len(valid_groups) == 2:
            left, right = candidates["Parts"], candidates["Particles"]
            duplicate = left["bounds"] == right["bounds"] and pygame.image.tostring(left["image"], "RGBA") == pygame.image.tostring(right["image"], "RGBA")
        for group in valid_groups:
            representative = candidates[group]
            items.append({
                "group": group,
                "slice_name": str(slice_name),
                "frame": representative["frame"],
                "bounds": representative["bounds"],
                "image": representative["image"],
                "empty_image": False,
                "definition_index": definition_index,
                "possible_duplicate": duplicate,
            })
    items.sort(key=lambda item: (
        0 if item["group"] == "Parts" else 1,
        item["definition_index"],
        int(item["bounds"].get("y", 0)),
        int(item["bounds"].get("x", 0)),
        item["slice_name"].casefold(),
    ))
    return {"mode": mode, "items": items, "skipped": skipped}


def _slice_analysis_is_current(source, analysis):
    return (
        isinstance(analysis, dict)
        and hasattr(source, "source_revision")
        and getattr(source, "slice_analysis_revision", None) == source.source_revision
        and analysis.get("revision") == source.source_revision
    )


def build_source_slice_analysis(source, revision=None):
    classified = _classify_export_slices_uncached(source, mode="auto")
    parts_tag = find_source_tag(source, "Parts")
    particles_tag = find_source_tag(source, "Particles")
    valid_parts = [item for item in classified["items"] if item["group"] == "Parts"]
    valid_particles = [item for item in classified["items"] if item["group"] == "Particles"]
    if parts_tag is None:
        reason = "Parts tag was not found."
    elif not valid_parts:
        reason = "Parts has no non-empty Slice image."
    else:
        reason = ""
    analysis_failures = [entry for entry in classified["skipped"] if entry.endswith("Slice analysis failed.")]
    return {
        "revision": revision,
        "mode": "auto",
        "parts_tag": parts_tag,
        "particles_tag": particles_tag,
        "parts_range": getattr(source, "tags", {}).get(parts_tag) if parts_tag else None,
        "particles_range": getattr(source, "tags", {}).get(particles_tag) if particles_tag else None,
        "valid_parts_slices": valid_parts,
        "valid_particle_slices": valid_particles,
        "has_valid_parts": bool(valid_parts),
        "has_valid_particles": bool(valid_particles),
        "save_enabled": bool(valid_parts),
        "reason": reason,
        "analysis_failed": bool(analysis_failures),
        "analysis_failure_reason": "; ".join(analysis_failures),
        "skipped": list(classified["skipped"]),
    }


def ensure_source_slice_analysis(source):
    if source is None:
        return None
    analysis = getattr(source, "slice_export_analysis", None)
    if _slice_analysis_is_current(source, analysis):
        return analysis
    revision = getattr(source, "source_revision", 0)
    analysis = build_source_slice_analysis(source, revision=revision)
    source.slice_export_analysis = analysis
    source.slice_analysis_revision = revision
    source.export_status = {"enabled": analysis["save_enabled"], "reason": analysis["reason"]}
    return analysis


def classify_export_slices(source, mode="auto"):
    mode = str(mode or "auto").lower()
    revision = getattr(source, "source_revision", None)
    cache = getattr(source, "_classification_mode_cache", None)
    if not isinstance(cache, dict):
        cache = {}
        source._classification_mode_cache = cache
    cache_key = (revision, mode)
    if cache_key in cache:
        return cache[cache_key]
    if mode == "auto":
        analysis = getattr(source, "slice_export_analysis", None)
        if _slice_analysis_is_current(source, analysis):
            result = {
                "mode": "auto",
                "items": analysis["valid_parts_slices"] + analysis["valid_particle_slices"],
                "skipped": list(analysis["skipped"]),
            }
            cache[cache_key] = result
            return result
    result = _classify_export_slices_uncached(source, mode=mode)
    cache.clear()
    cache[cache_key] = result
    return result


def evaluate_slice_export(source):
    if source is None:
        return {"enabled": False, "reason": "Source is missing."}
    analysis = ensure_source_slice_analysis(source)
    return {"enabled": analysis["save_enabled"], "reason": analysis["reason"]}


def export_source_slices(
    source,
    output_directory,
    export_parts=True,
    export_particles=True,
    mode="auto",
    owner_name=None,
    owner_kind="Source",
    naming_mode="target",
    target_name=None,
):
    result = {
        "saved": [],
        "skipped": [],
        "failed": [],
        "entries": [],
        "mode": str(mode or "auto").lower(),
        "naming_mode": str(naming_mode or "target").lower(),
        "target_name": str(target_name if target_name is not None else owner_name or "").strip(),
        "renamed_collisions": 0,
        "output_directory": os.path.abspath(output_directory) if output_directory else "",
    }
    if source is None:
        result["failed"].append("Source is missing.")
        return result
    if not output_directory or not os.path.isdir(output_directory):
        result["failed"].append("Output directory does not exist.")
        return result

    if not isinstance(getattr(source, "tags", None), dict) or not isinstance(getattr(source, "slices", None), dict) or not isinstance(getattr(source, "frames", None), list):
        result["failed"].append("Source metadata is invalid.")
        return result
    naming_mode = result["naming_mode"]
    if naming_mode not in {"target", "slice"}:
        result["failed"].append("Unknown file naming mode.")
        return result
    target_name = result["target_name"]
    if naming_mode == "target" and not target_name:
        result["failed"].append("Target name is required.")
        return result
    plan = build_slice_export_plan(source, {
        "classification": mode,
        "naming_mode": naming_mode,
        "target_name": target_name,
    })
    if plan["error"]:
        result["failed"].append("Slice classification failed.")
        return result
    result["skipped"].extend(plan.get("skipped", []))
    selected_items = [
        item for item in plan["entries"]
        if (export_parts and item["group"] == "Parts")
        or (export_particles and item["group"] == "Particles")
    ]

    reserved_names = set()
    try:
        reserved_names.update(entry.name.casefold() for entry in os.scandir(output_directory) if entry.is_file())
    except OSError as e:
        result["failed"].append("Output directory could not be read.")
        log_debug(f"[ERROR] Slice export directory scan failed for {output_directory}: {e}\n{traceback.format_exc()}")
        return result

    for item in selected_items:
        group = item["group"]
        standard_stem = item["standard_stem"]
        final_path = _unique_png_path(output_directory, standard_stem, reserved_names)
        if os.path.basename(final_path).casefold() != f"{standard_stem}.png".casefold():
            result["renamed_collisions"] += 1
        entry = {
            "group": group,
            "slice_name": item["slice_name"],
            "frame": item["frame"],
            "bounds": dict(item["bounds"]),
            "filename": os.path.basename(final_path),
            "saved": False,
            "reason": "",
            "possible_duplicate": item.get("possible_duplicate", False),
        }
        result["entries"].append(entry)
        try:
            fd, temp_path = tempfile.mkstemp(prefix=f".{os.path.basename(final_path)}.", suffix=".tmp.png", dir=output_directory)
            os.close(fd)
            try:
                pygame.image.save(item["image"], temp_path)
                if not os.path.isfile(temp_path) or os.path.getsize(temp_path) <= 0:
                    raise OSError("pygame did not create a non-empty PNG.")
                os.replace(temp_path, final_path)
            finally:
                if os.path.exists(temp_path):
                    try: os.remove(temp_path)
                    except OSError: pass
            entry["saved"] = True
            result["saved"].append(final_path)
            log_debug(f"[EXPORT] {entry['filename']} <- {entry['slice_name']} ({group}, frame {entry['frame']})")
            if entry["possible_duplicate"]:
                log_debug(f"[WARN] Slice may be duplicated across Parts and Particles: {entry['slice_name']}")
        except (OSError, KeyError, TypeError, ValueError, pygame.error) as e:
            entry["reason"] = "PNG could not be saved."
            result["failed"].append(f"{item['slice_name']}: PNG could not be saved.")
            log_debug(f"[ERROR] Slice export failed for {item['slice_name']!r} from {group}: {e}\n{traceback.format_exc()}")
    return result


def summarize_slice_export(result):
    saved = len(result["saved"])
    skipped = len(result["skipped"])
    failed = len(result["failed"])
    parts = sum(1 for entry in result.get("entries", []) if entry["saved"] and entry["group"] == "Parts")
    particles = sum(1 for entry in result.get("entries", []) if entry["saved"] and entry["group"] == "Particles")
    duplicates = sum(1 for entry in result.get("entries", []) if entry.get("possible_duplicate"))
    naming_mode = result.get("naming_mode", "target")
    naming_label = tr("summary.target_naming") if naming_mode == "target" else tr("summary.slice_naming")
    lines = [
        tr("export.completed"),
        "",
        f"{tr('summary.naming')}: {naming_label}",
    ]
    if naming_mode == "target":
        lines.append(f"{tr('summary.target')}: {result.get('target_name', '')}")
    lines.extend([
        f"{tr('summary.classification')}: {tr('summary.auto') if result.get('mode', 'auto') == 'auto' else tr('summary.name')}",
        "",
        f"{tr('summary.parts')}: {tr('summary.count', count=parts)}",
        f"{tr('summary.particles')}: {tr('summary.count', count=particles)}",
        f"{tr('summary.skipped')}: {tr('summary.count', count=skipped)}",
        f"{tr('summary.failed')}: {tr('summary.count', count=failed)}",
    ])
    if naming_mode == "slice":
        lines.append(f"{tr('summary.collisions')}: {tr('summary.count', count=result.get('renamed_collisions', 0))}")
    if duplicates:
        lines.append(f"{tr('summary.duplicates')}: {tr('summary.count', count=duplicates)}")
    lines.extend(["", f"{tr('summary.output_folder')}:\n{result['output_directory']}"])
    if not saved:
        reasons = result["skipped"] + result["failed"]
        lines.extend(["", tr("export.none_saved")])
        if reasons:
            lines.extend(f"- {reason}" for reason in reasons[:6])
    return "\n".join(lines)


_SLICE_EXPORT_DIALOG_ACTIVE = False


class TkHoverTooltip:
    def __init__(self, widget, text, delay_ms=400, wraplength=360):
        self.widget = widget
        self.text = text
        self.delay_ms = int(delay_ms)
        self.wraplength = int(wraplength)
        self.after_id = None
        self.window = None
        widget.bind("<Enter>", self._enter, add="+")
        widget.bind("<Leave>", self._leave, add="+")
        widget.bind("<Destroy>", self._leave, add="+")

    def _enter(self, _event=None):
        self._cancel_after()
        self.after_id = self.widget.after(self.delay_ms, self._show)

    def _leave(self, _event=None):
        self._cancel_after()
        if self.window is not None:
            try:
                self.window.destroy()
            except tk.TclError:
                pass
            self.window = None

    def _cancel_after(self):
        if self.after_id is not None:
            try:
                self.widget.after_cancel(self.after_id)
            except tk.TclError:
                pass
            self.after_id = None

    def _show(self):
        self.after_id = None
        if self.window is not None or not self.widget.winfo_exists():
            return
        self.window = tk.Toplevel(self.widget)
        self.window.wm_overrideredirect(True)
        label = tk.Label(
            self.window, text=self.text, justify="left", wraplength=self.wraplength,
            background="#181a20", foreground="#f5f5f8", relief="solid",
            borderwidth=1, padx=8, pady=6,
        )
        label.pack()
        self.window.update_idletasks()
        pointer_x = self.widget.winfo_pointerx()
        pointer_y = self.widget.winfo_pointery()
        width = self.window.winfo_reqwidth()
        height = self.window.winfo_reqheight()
        screen_width = self.widget.winfo_screenwidth()
        screen_height = self.widget.winfo_screenheight()
        rect = calculate_tooltip_rect(
            (pointer_x, pointer_y), (width, height), (screen_width, screen_height),
        )
        self.window.wm_geometry(f"+{rect.x}+{rect.y}")


def attach_tk_tooltip(widget, translation_key, language):
    return TkHoverTooltip(widget, tr(translation_key, language=language))


def prompt_unity_parallax_export(player):
    language = _CURRENT_LANGUAGE
    if not getattr(player, "bg_layers", None):
        show_user_error(tr("unity.dialog_title", language=language), tr("unity.no_layers", language=language))
        return False
    root = None
    copied = False
    try:
        root = tk.Tk()
        root.title(tr("unity.dialog_title", language=language))
        root.geometry("980x720")
        root.minsize(780, 600)
        root.attributes("-topmost", True)
        ppu_var = tk.StringVar(value=_format_export_number(getattr(player, "unity_pixels_per_unit", 100)))
        format_var = tk.StringVar(value=normalize_unity_parallax_export_format(
            getattr(player, "unity_parallax_export_format", "detailed"),
        ))
        include_var = tk.BooleanVar(value=getattr(player, "unity_parallax_include_disabled", True))
        error_var = tk.StringVar(value="")
        format_help_var = tk.StringVar(value="")
        stats_var = tk.StringVar(value="")

        top = tk.Frame(root)
        top.pack(fill="x", padx=12, pady=(12, 6))
        tk.Label(top, text=f"{tr('unity.ppu', language=language)}:").grid(row=0, column=0, sticky="w")
        ppu_entry = tk.Entry(top, textvariable=ppu_var, width=12)
        ppu_entry.grid(row=0, column=1, sticky="w", padx=(6, 18))
        attach_tk_tooltip(ppu_entry, "tooltip.unity_ppu", language)
        tk.Label(top, text=tr("unity.format", language=language)).grid(row=0, column=2, sticky="w")
        format_widgets = []
        format_options = [
            ("detailed", "unity.detailed", "tooltip.unity_detailed"),
            ("slack", "unity.slack", "tooltip.unity_slack"),
            ("markdown", "unity.markdown", "tooltip.unity_markdown"),
            ("tsv", "unity.tsv", "tooltip.unity_tsv"),
        ]
        for column, (value, label_key, tooltip_key) in enumerate(format_options, 3):
            radio = tk.Radiobutton(
                top, text=tr(label_key, language=language),
                variable=format_var, value=value,
            )
            radio.grid(row=0, column=column, sticky="w", padx=(6, 0))
            attach_tk_tooltip(radio, tooltip_key, language)
            format_widgets.append(radio)
        include_check = tk.Checkbutton(
            top, text=tr("unity.include_disabled", language=language), variable=include_var,
        )
        include_check.grid(row=1, column=0, columnspan=7, sticky="w", pady=(8, 0))
        tk.Label(
            top, textvariable=format_help_var, fg="#555555", justify="left",
        ).grid(row=2, column=0, columnspan=7, sticky="w", pady=(6, 0))

        tk.Label(root, text=tr("unity.preview", language=language), font=("TkDefaultFont", 10, "bold")).pack(
            anchor="w", padx=12, pady=(6, 2),
        )
        tk.Label(root, textvariable=stats_var, fg="#555555", anchor="w").pack(
            fill="x", padx=12, pady=(0, 2),
        )
        preview_frame = tk.Frame(root)
        preview_frame.pack(fill="both", expand=True, padx=12, pady=(0, 6))
        preview = tk.Text(preview_frame, wrap="word", height=30, font=("Consolas", 10))
        vertical_scroll = tk.Scrollbar(preview_frame, orient="vertical", command=preview.yview)
        horizontal_scroll = tk.Scrollbar(preview_frame, orient="horizontal", command=preview.xview)
        preview.configure(
            yscrollcommand=vertical_scroll.set,
            xscrollcommand=horizontal_scroll.set,
        )
        preview.grid(row=0, column=0, sticky="nsew")
        vertical_scroll.grid(row=0, column=1, sticky="ns")
        horizontal_scroll.grid(row=1, column=0, sticky="ew")
        preview_frame.grid_rowconfigure(0, weight=1)
        preview_frame.grid_columnconfigure(0, weight=1)
        error_label = tk.Label(root, textvariable=error_var, fg="#b91c1c")
        error_label.pack(fill="x", padx=12)

        def refresh_preview(*_args):
            selected_format = normalize_unity_parallax_export_format(format_var.get())
            format_help_var.set(tr(f"unity.{selected_format}_help", language=language))
            preview.configure(wrap="word" if selected_format == "detailed" else "none")
            try:
                ppu = validate_unity_pixels_per_unit(ppu_var.get())
                text = build_unity_parallax_export(
                    player.bg_layers,
                    ppu,
                    output_format=selected_format,
                    include_disabled=include_var.get(),
                    language=language,
                )
                included_count = sum(
                    1 for layer in player.bg_layers
                    if include_var.get() or convert_layer_to_unity_parallax(layer, ppu, 0)["enabled"]
                )
                stats = tr(
                    "unity.preview_stats", language=language,
                    count=included_count, length=len(text),
                )
                if included_count > 50:
                    stats += f"\n{tr('unity.many_layers', language=language)}"
                stats_var.set(stats)
                error_var.set("")
            except (TypeError, ValueError) as error:
                text = ""
                stats_var.set("")
                error_var.set(str(error))
            preview.configure(state="normal")
            preview.delete("1.0", "end")
            preview.insert("1.0", text)
            preview.configure(state="disabled")

        def clipboard_writer(text):
            try:
                root.clipboard_clear()
                root.clipboard_append(text)
                root.update()
                return True, ""
            except (tk.TclError, OSError, RuntimeError) as error:
                log_debug(f"[ERROR] Unity clipboard copy failed: {error}\n{traceback.format_exc()}")
                return False, str(error)

        def copy_preview():
            nonlocal copied
            result = perform_unity_parallax_clipboard_export(
                player.bg_layers, ppu_var.get(), output_format=format_var.get(),
                include_disabled=include_var.get(), language=language,
                clipboard_writer=clipboard_writer,
            )
            if not result["success"]:
                error_var.set(result["error"] or tr("unity.copy_failed", language=language))
                return
            player.unity_pixels_per_unit = result["pixels_per_unit"]
            player.unity_parallax_export_format = result["output_format"]
            player.unity_parallax_include_disabled = include_var.get()
            player.save_settings()
            copied = True
            messagebox.showinfo(
                tr("unity.dialog_title", language=language),
                tr(
                    f"unity.copy_success_{result['output_format']}",
                    language=language, count=result["count"],
                    ppu=_format_export_number(result["pixels_per_unit"]),
                ),
                parent=root,
            )
            root.destroy()

        buttons = tk.Frame(root)
        buttons.pack(pady=(4, 12))
        copy_button = tk.Button(
            buttons, text=tr("unity.copy_clipboard", language=language),
            width=18, command=copy_preview,
        )
        copy_button.pack(side="left", padx=4)
        attach_tk_tooltip(copy_button, "tooltip.unity_copy", language)
        tk.Button(
            buttons, text=tr("common.cancel", language=language),
            width=14, command=root.destroy,
        ).pack(side="left", padx=4)
        ppu_var.trace_add("write", refresh_preview)
        format_var.trace_add("write", refresh_preview)
        include_var.trace_add("write", refresh_preview)
        refresh_preview()
        root.grab_set()
        root.mainloop()
        return copied
    except (tk.TclError, OSError) as error:
        log_debug(f"[ERROR] Unity parallax dialog failed: {error}\n{traceback.format_exc()}")
        show_user_error(tr("unity.dialog_title", language=language), tr("unity.copy_failed", language=language))
        return False
    finally:
        if root is not None:
            try:
                if root.winfo_exists():
                    root.destroy()
            except tk.TclError:
                pass


def prompt_slice_export_options(source):
    global _SLICE_EXPORT_DIALOG_ACTIVE
    if _SLICE_EXPORT_DIALOG_ACTIVE:
        return None
    _SLICE_EXPORT_DIALOG_ACTIVE = True
    root = None
    result = None
    language = _CURRENT_LANGUAGE
    try:
        root = tk.Tk()
        root.title(tr("export.title", language=language))
        root.geometry("720x780")
        root.resizable(True, True)
        root.minsize(620, 680)
        root.attributes("-topmost", True)
        classification = tk.StringVar(value="auto")
        naming_mode = tk.StringVar(value="target")
        target_name = tk.StringVar(value=suggested_export_target_name(source))
        error_text = tk.StringVar(value="")
        preview_title_text = tk.StringVar(value="")
        preview_status_text = tk.StringVar(value="")

        tk.Label(root, text=tr("export.classification", language=language), font=("TkDefaultFont", 10, "bold")).grid(
            row=0, column=0, columnspan=2, sticky="w", padx=12, pady=(12, 2),
        )
        auto_radio = tk.Radiobutton(root, text=tr("export.auto", language=language), variable=classification, value="auto")
        auto_radio.grid(row=1, column=0, columnspan=2, sticky="w", padx=18)
        attach_tk_tooltip(auto_radio, "tooltip.auto", language)
        tk.Label(
            root, text=tr("export.auto_desc", language=language), justify="left",
            wraplength=570, fg="#4b5563",
        ).grid(row=2, column=0, columnspan=2, sticky="w", padx=38)
        name_radio = tk.Radiobutton(root, text=tr("export.name", language=language), variable=classification, value="name")
        name_radio.grid(row=3, column=0, columnspan=2, sticky="w", padx=18, pady=(6, 0))
        attach_tk_tooltip(name_radio, "tooltip.name", language)
        tk.Label(
            root, text=tr("export.name_desc", language=language), justify="left",
            wraplength=570, fg="#4b5563",
        ).grid(row=4, column=0, columnspan=2, sticky="w", padx=38)
        tk.Label(root, text=tr("export.file_naming", language=language), font=("TkDefaultFont", 10, "bold")).grid(
            row=5, column=0, columnspan=2, sticky="w", padx=12, pady=(14, 2),
        )
        target_radio = tk.Radiobutton(
            root, text=tr("export.use_asset", language=language), variable=naming_mode, value="target",
        )
        target_radio.grid(row=6, column=0, columnspan=2, sticky="w", padx=18)
        attach_tk_tooltip(target_radio, "tooltip.naming.target", language)
        tk.Label(
            root, text=tr("export.use_asset_desc", language=language), justify="left",
            wraplength=570, fg="#4b5563",
        ).grid(row=7, column=0, columnspan=2, sticky="w", padx=38)
        tk.Label(root, text=tr("export.asset_name", language=language)).grid(
            row=8, column=0, sticky="e", padx=(18, 4), pady=4,
        )
        name_entry = tk.Entry(root, textvariable=target_name, width=30)
        name_entry.grid(row=8, column=1, sticky="w", padx=(0, 12), pady=4)
        slice_radio = tk.Radiobutton(
            root, text=tr("export.keep_slice", language=language), variable=naming_mode, value="slice",
        )
        slice_radio.grid(row=9, column=0, columnspan=2, sticky="w", padx=18, pady=(6, 0))
        attach_tk_tooltip(slice_radio, "tooltip.naming.slice", language)
        tk.Label(
            root, text=tr("export.keep_slice_desc", language=language), justify="left",
            wraplength=570, fg="#4b5563",
        ).grid(row=10, column=0, columnspan=2, sticky="w", padx=38)
        preview_title_label = tk.Label(root, textvariable=preview_title_text, font=("TkDefaultFont", 10, "bold"))
        preview_title_label.grid(
            row=11, column=0, columnspan=2, sticky="w", padx=12, pady=(14, 2),
        )
        preview_frame = tk.Frame(root, relief="groove", borderwidth=1)
        preview_frame.grid(row=12, column=0, columnspan=2, sticky="nsew", padx=12)
        preview_group_help = tk.Frame(preview_frame)
        preview_group_help.grid(row=0, column=0, columnspan=2, sticky="w", padx=4, pady=(3, 0))
        parts_help = tk.Label(preview_group_help, text="Parts", fg="#374151")
        parts_help.pack(side="left", padx=(0, 12))
        particles_help = tk.Label(preview_group_help, text="Particles", fg="#374151")
        particles_help.pack(side="left")
        attach_tk_tooltip(parts_help, "tooltip.export.parts_group", language)
        attach_tk_tooltip(particles_help, "tooltip.export.particles_group", language)
        preview_list = tk.Listbox(
            preview_frame, height=10, font=("Consolas", 10),
            activestyle="none", exportselection=False,
        )
        preview_y_scroll = tk.Scrollbar(preview_frame, orient="vertical", command=preview_list.yview)
        preview_x_scroll = tk.Scrollbar(preview_frame, orient="horizontal", command=preview_list.xview)
        preview_list.configure(
            yscrollcommand=preview_y_scroll.set,
            xscrollcommand=preview_x_scroll.set,
        )
        preview_list.grid(row=1, column=0, sticky="nsew")
        preview_y_scroll.grid(row=1, column=1, sticky="ns")
        preview_x_scroll.grid(row=2, column=0, sticky="ew")
        preview_frame.grid_rowconfigure(1, weight=1)
        preview_frame.grid_columnconfigure(0, weight=1)
        attach_tk_tooltip(preview_list, "tooltip.export.preview_list", language)
        tk.Label(
            root, textvariable=preview_status_text, justify="left", anchor="w",
            fg="#374151",
        ).grid(row=13, column=0, columnspan=2, sticky="w", padx=12, pady=(5, 0))
        collision_label = tk.Label(
            root, text=tr("export.folder_collision_hint", language=language),
            justify="left", wraplength=660, fg="#4b5563",
        )
        collision_label.grid(row=14, column=0, columnspan=2, sticky="w", padx=12, pady=(5, 0))
        attach_tk_tooltip(collision_label, "tooltip.export.collision", language)
        tk.Label(
            root, text=tr("export.independent_hint", language=language), justify="left",
            wraplength=570, fg="#374151",
        ).grid(row=15, column=0, columnspan=2, sticky="w", padx=12, pady=(10, 0))
        tk.Label(root, textvariable=error_text, fg="#b91c1c").grid(
            row=16, column=0, columnspan=2, padx=12, pady=(6, 0),
        )

        def update_preview(*_args):
            is_target = naming_mode.get() == "target"
            name_entry.configure(state="normal" if is_target else "disabled")
            options = {
                "classification": classification.get(),
                "naming_mode": naming_mode.get(),
                "target_name": target_name.get(),
            }
            plan = build_slice_export_plan(source, options)
            preview_list.delete(0, "end")
            if plan["entries"]:
                preview_title_text.set(tr(
                    "export.preview_total", language=language,
                    count=len(plan["entries"]),
                ))
                for group, count, tooltip_key in (
                    ("Parts", plan["parts"], "tooltip.export.parts_group"),
                    ("Particles", plan["particles"], "tooltip.export.particles_group"),
                ):
                    if count:
                        preview_list.insert("end", f"{group} · {count}")
                        group_entries = [
                            entry for entry in plan["entries"] if entry["group"] == group
                        ]
                        for index, entry in enumerate(group_entries, 1):
                            preview_list.insert("end", f"{index:02d}  {entry['filename']}")
                        preview_list.insert("end", "")
                naming_label = tr(
                    "summary.target_naming" if naming_mode.get() == "target" else "summary.slice_naming",
                    language=language,
                )
                preview_status_text.set(tr(
                    "export.preview_status", language=language,
                    classification=classification.get().upper(),
                    naming=naming_label,
                    total=len(plan["entries"]),
                    parts=plan["parts"],
                    particles=plan["particles"],
                ))
                continue_button.configure(state="normal")
                error_text.set("")
            else:
                preview_title_text.set(tr("export.preview", language=language))
                preview_status_text.set("")
                preview_list.insert(
                    "end",
                    tr(
                        "export.enter_asset" if plan["error"] and is_target
                        else "export.preview_empty",
                        language=language,
                    ),
                )
                continue_button.configure(state="disabled")

        def continue_export():
            nonlocal result
            validated, error = validate_slice_export_options({
                "classification": classification.get(),
                "naming_mode": naming_mode.get(),
                "target_name": target_name.get(),
            })
            if error:
                error_text.set(tr("export.enter_asset", language=language) if naming_mode.get() == "target" else error)
                name_entry.focus_set()
                return
            result = validated
            root.destroy()

        def cancel_export():
            root.destroy()

        buttons = tk.Frame(root)
        buttons.grid(row=17, column=0, columnspan=2, pady=12)
        continue_button = tk.Button(buttons, text=tr("export.continue", language=language), width=14, command=continue_export)
        continue_button.pack(side="left", padx=4)
        attach_tk_tooltip(continue_button, "tooltip.export.continue_disabled", language)
        tk.Button(buttons, text=tr("common.cancel", language=language), width=14, command=cancel_export).pack(side="left", padx=4)
        root.protocol("WM_DELETE_WINDOW", cancel_export)
        classification.trace_add("write", update_preview)
        naming_mode.trace_add("write", update_preview)
        target_name.trace_add("write", update_preview)
        root.grid_rowconfigure(12, weight=1)
        root.grid_columnconfigure(1, weight=1)
        update_preview()
        root.grab_set()
        name_entry.focus_set()
        root.mainloop()
        return result
    except (tk.TclError, OSError) as e:
        log_debug(f"[ERROR] Slice export options dialog failed: {e}\n{traceback.format_exc()}")
        show_user_error(tr("export.options_open_failed"), tr("export.options_open_failed_detail"))
        return None
    finally:
        _SLICE_EXPORT_DIALOG_ACTIVE = False
        if root is not None:
            try:
                if root.winfo_exists():
                    root.destroy()
            except tk.TclError:
                pass


def prompt_slice_export_directory():
    root = None
    try:
        root = tk.Tk()
        root.withdraw()
        root.attributes("-topmost", True)
        return filedialog.askdirectory(parent=root)
    except (tk.TclError, OSError) as e:
        log_debug(f"[ERROR] Slice export directory selection failed: {e}\n{traceback.format_exc()}")
        show_user_error(tr("export.failed"), tr("export.folder_open_failed"))
        return None
    finally:
        if root is not None:
            try:
                root.destroy()
            except tk.TclError:
                pass


def run_slice_export_workflow(
    source,
    owner_kind,
    confirm,
    options_prompt=prompt_slice_export_options,
    folder_prompt=prompt_slice_export_directory,
    exporter=export_source_slices,
):
    if not confirm():
        return None
    options = options_prompt(source)
    if options is None:
        return None
    options, error = validate_slice_export_options(options)
    if error:
        localized_error = tr("export.enter_asset") if options and options.get("naming_mode") == "target" else error
        show_user_error(tr("export.failed"), localized_error)
        return None
    folder = folder_prompt()
    if not folder:
        return None
    result = exporter(
        source,
        folder,
        mode=options["classification"],
        owner_kind=owner_kind,
        naming_mode=options["naming_mode"],
        target_name=options["target_name"],
    )
    summary = summarize_slice_export(result)
    if result["saved"]:
        show_user_info(tr("export.completed"), summary)
    else:
        show_user_error(tr("export.none_saved"), summary)
    return result


def request_slice_export(source, owner_kind="Source"):
    return run_slice_export_workflow(
        source,
        owner_kind,
        confirm=lambda: True,
    )


def slice_export_availability(source):
    if source is None:
        return {"enabled": False, "reason": "Source is missing."}
    analysis = ensure_source_slice_analysis(source)
    status = {"enabled": analysis["save_enabled"], "reason": analysis["reason"]}
    if not getattr(source, "frames", None):
        return {"enabled": False, "reason": "Source image data is not loaded."}
    return status


def source_slice_status_text(source):
    analysis = ensure_source_slice_analysis(source)
    if analysis is None:
        return f"P:0 / FX:0 / {tr('status.save')}:{tr('status.off')}"
    return (
        f"P:{len(analysis['valid_parts_slices'])} / "
        f"FX:{len(analysis['valid_particle_slices'])} / "
        f"{tr('status.save')}:{tr('status.on') if analysis['save_enabled'] else tr('status.off')}"
    )


NPC_SLICE_STATUS_PANEL_HEIGHT = 142


def profile_has_valid_death_mapping(profile, sources, slots=("DEAD_LOOP", "DEAD")):
    if profile is None:
        return False
    for slot in slots:
        for mapping in getattr(profile, "mappings", {}).get(slot, []):
            if not isinstance(mapping, (list, tuple)) or len(mapping) < 2:
                continue
            source_index, tag_name = mapping[0], mapping[1]
            if not isinstance(source_index, int) or not 0 <= source_index < len(sources):
                continue
            source = sources[source_index]
            tag_range = getattr(source, "tags", {}).get(tag_name)
            if not isinstance(tag_range, (list, tuple)) or len(tag_range) < 2:
                continue
            start, end = tag_range[0], tag_range[1]
            frames = getattr(source, "frames", [])
            if isinstance(start, int) and isinstance(end, int) and 0 <= start <= end < len(frames):
                if isinstance(frames[start], dict) and frames[start].get("img") is not None:
                    return True
    return False


def _alpha_pixel_count(surface):
    return pygame.mask.from_surface(surface, 1).count()


def _auto_parts_grid_size(width, height):
    largest = max(width, height)
    if largest <= 16:
        target_cell = 12
    elif largest <= 48:
        target_cell = 12
    elif largest <= 96:
        target_cell = 16
    else:
        target_cell = 24
    columns = max(1, math.ceil(width / target_cell))
    rows = max(1, math.ceil(height / target_cell))
    while columns * rows > 24:
        target_cell += 1
        columns = max(1, math.ceil(width / target_cell))
        rows = max(1, math.ceil(height / target_cell))
    return columns, rows


def build_auto_alpha_parts(source, frame_index):
    frames = getattr(source, "frames", [])
    if not frames:
        return {"mode": "colored_fallback", "pieces": [], "frame": 0, "opaque_bounds": None, "grid": (0, 0)}
    frame_index = min(max(0, int(frame_index)), len(frames) - 1)
    revision = getattr(source, "source_revision", 0)
    cache = getattr(source, "auto_parts_cache", None)
    if not isinstance(cache, dict):
        cache = {}
        source.auto_parts_cache = cache
    cache_key = (revision, frame_index)
    if cache_key in cache:
        return cache[cache_key]

    frame_info = frames[frame_index]
    full_frame = frame_info.get("img") if isinstance(frame_info, dict) else None
    if full_frame is None:
        result = {"mode": "colored_fallback", "pieces": [], "frame": frame_index, "opaque_bounds": None, "grid": (0, 0)}
        cache[cache_key] = result
        return result
    opaque_bounds = full_frame.get_bounding_rect(min_alpha=1)
    if opaque_bounds.width <= 0 or opaque_bounds.height <= 0:
        result = {"mode": "colored_fallback", "pieces": [], "frame": frame_index, "opaque_bounds": None, "grid": (0, 0)}
        cache[cache_key] = result
        return result

    columns, rows = _auto_parts_grid_size(opaque_bounds.width, opaque_bounds.height)
    total_alpha = _alpha_pixel_count(full_frame.subsurface(opaque_bounds))
    minimum_alpha = 1 if total_alpha <= 8 else max(2, int(total_alpha * 0.0015))
    pieces = []
    for row in range(rows):
        cell_top = opaque_bounds.top + (opaque_bounds.height * row) // rows
        cell_bottom = opaque_bounds.top + (opaque_bounds.height * (row + 1)) // rows
        for column in range(columns):
            cell_left = opaque_bounds.left + (opaque_bounds.width * column) // columns
            cell_right = opaque_bounds.left + (opaque_bounds.width * (column + 1)) // columns
            cell_rect = pygame.Rect(cell_left, cell_top, cell_right - cell_left, cell_bottom - cell_top)
            if cell_rect.width <= 0 or cell_rect.height <= 0:
                continue
            cell = full_frame.subsurface(cell_rect)
            local_bounds = cell.get_bounding_rect(min_alpha=1)
            if local_bounds.width <= 0 or local_bounds.height <= 0:
                continue
            cropped = cell.subsurface(local_bounds).copy()
            alpha_pixels = _alpha_pixel_count(cropped)
            if alpha_pixels < minimum_alpha:
                continue
            local_x = cell_rect.x + local_bounds.x
            local_y = cell_rect.y + local_bounds.y
            pieces.append({
                "image": cropped,
                "alpha_pixels": alpha_pixels,
                "local_x": local_x,
                "local_y": local_y,
                "bounds": {
                    "x": frame_info["ox"] + source.orig_w // 2 + local_x,
                    "y": frame_info["oy"] + source.orig_h // 2 + local_y,
                    "w": cropped.get_width(),
                    "h": cropped.get_height(),
                },
            })

    mode = "auto_alpha"
    if not pieces:
        cropped = full_frame.subsurface(opaque_bounds).copy()
        pieces = [{
            "image": cropped,
            "alpha_pixels": total_alpha,
            "local_x": opaque_bounds.x,
            "local_y": opaque_bounds.y,
            "bounds": {
                "x": frame_info["ox"] + source.orig_w // 2 + opaque_bounds.x,
                "y": frame_info["oy"] + source.orig_h // 2 + opaque_bounds.y,
                "w": cropped.get_width(),
                "h": cropped.get_height(),
            },
        }]
        mode = "single_image_fallback"
    result = {
        "mode": mode,
        "pieces": pieces,
        "frame": frame_index,
        "opaque_bounds": opaque_bounds.copy(),
        "grid": (columns, rows),
    }
    cache[cache_key] = result
    return result


def resolve_npc_death_parts_mode(source, frame_index=0):
    analysis = ensure_source_slice_analysis(source)
    valid_parts = analysis["valid_parts_slices"]
    if valid_parts:
        return {
            "mode": "precise",
            "expected": len(valid_parts),
            "analysis": analysis,
            "plan": None,
        }
    plan = build_auto_alpha_parts(source, frame_index)
    return {
        "mode": plan["mode"],
        "expected": len(plan["pieces"]),
        "analysis": analysis,
        "plan": plan,
    }


def profile_representative_frame(profile, source):
    for slot in ("IDLE", "WALK"):
        for mapping in getattr(profile, "mappings", {}).get(slot, []):
            if not isinstance(mapping, (list, tuple)) or len(mapping) < 2:
                continue
            if mapping[0] != getattr(profile, "source_idx", -1):
                continue
            tag_range = getattr(source, "tags", {}).get(mapping[1])
            if isinstance(tag_range, (list, tuple)) and tag_range:
                return int(tag_range[0])
    return 0


def profile_corpse_mode(profile, sources):
    if profile is None:
        return "remove"
    for slot, mode in (("DEAD_LOOP", "dead_loop"), ("DEAD", "dead_hold")):
        for mapping in getattr(profile, "mappings", {}).get(slot, []):
            if not isinstance(mapping, (list, tuple)) or len(mapping) < 2:
                continue
            source_index, tag_name = mapping[0], mapping[1]
            if not isinstance(source_index, int) or not 0 <= source_index < len(sources):
                continue
            tag_range = getattr(sources[source_index], "tags", {}).get(tag_name)
            if isinstance(tag_range, (list, tuple)) and len(tag_range) >= 2:
                return mode
    return "remove"


def npc_death_prediction_text(profile, sources, resolution):
    corpse_labels = {"dead_loop": "Dead Loop", "dead_hold": "Dead Hold", "remove": "Remove"}
    part_labels = {
        "precise": f"Precise Parts {resolution['expected']}",
        "auto_alpha": f"Auto Alpha ~{resolution['expected']}",
        "single_image_fallback": "Single Image 1",
        "colored_fallback": "Colored Fallback",
    }
    return f"{corpse_labels[profile_corpse_mode(profile, sources)]} + {part_labels[resolution['mode']]}"


def npc_slice_status_data(profile, sources, last_death=None):
    result = {
        "parts": 0,
        "particles": 0,
        "death": "Auto Alpha — 0 expected",
        "save_enabled": False,
        "save": "Disabled",
        "reason": "No NPC profile selected.",
        "runtime": "",
        "corpse_mode": "remove",
        "parts_mode": "auto_alpha",
        "expected": 0,
    }
    if profile is None:
        return result
    source_index = getattr(profile, "source_idx", -1)
    if not isinstance(source_index, int) or not 0 <= source_index < len(sources):
        result["reason"] = "NPC source is missing."
        return result
    analysis = ensure_source_slice_analysis(sources[source_index])
    result["parts"] = len(analysis["valid_parts_slices"])
    result["particles"] = len(analysis["valid_particle_slices"])
    result["save_enabled"] = analysis["save_enabled"]
    if analysis["save_enabled"]:
        result["save"] = "Available"
    elif analysis["parts_tag"] is None:
        result["save"] = "Disabled — No Parts tag"
    else:
        result["save"] = "Disabled — No valid Parts"
    resolution = resolve_npc_death_parts_mode(
        sources[source_index], profile_representative_frame(profile, sources[source_index]),
    )
    result["death"] = npc_death_prediction_text(profile, sources, resolution)
    result["corpse_mode"] = profile_corpse_mode(profile, sources)
    result["parts_mode"] = resolution["mode"]
    result["expected"] = resolution["expected"]
    if (
        isinstance(last_death, dict)
        and last_death.get("profile") is profile
    ):
        corpse_label = {"dead_loop": "Dead Loop", "dead_hold": "Dead Hold", "remove": "Remove"}.get(
            last_death.get("corpse_mode"), str(last_death.get("corpse_mode", "Unknown")),
        )
        result["runtime"] = f"Last Death: corpse={corpse_label} / parts={last_death.get('created', 0)}"
        result["last_corpse_mode"] = last_death.get("corpse_mode", "remove")
        result["last_created"] = last_death.get("created", 0)
    if analysis.get("analysis_failure_reason"):
        result["reason"] = analysis["analysis_failure_reason"]
    elif not analysis["save_enabled"]:
        result["reason"] = analysis["reason"]
    elif profile_has_valid_death_mapping(profile, sources):
        result["reason"] = "Corpse tag active; Parts spawn independently."
    else:
        result["reason"] = ""
    return result


def localized_slice_export_reason(reason):
    if reason == "Parts tag was not found.":
        return tr("status.no_parts_tag")
    if reason == "Parts has no non-empty Slice image.":
        return tr("status.no_valid_parts")
    if "source" in str(reason).casefold() and "missing" in str(reason).casefold():
        return tr("status.missing_source")
    return reason


def localized_npc_status(status):
    corpse = tr({
        "dead_loop": "status.dead_loop",
        "dead_hold": "status.dead_hold",
        "remove": "status.remove",
    }.get(status.get("corpse_mode"), "status.remove"))
    parts_key = {
        "precise": "status.precise_parts",
        "auto_alpha": "status.auto_alpha",
        "single_image_fallback": "status.single_image",
        "colored_fallback": "status.colored_fallback",
    }.get(status.get("parts_mode"), "status.colored_fallback")
    parts = tr(parts_key, count=status.get("expected", 0))
    runtime = ""
    if status.get("runtime"):
        runtime = tr(
            "status.last_death",
            corpse=tr({
                "dead_loop": "status.dead_loop",
                "dead_hold": "status.dead_hold",
                "remove": "status.remove",
            }.get(status.get("last_corpse_mode", status.get("corpse_mode")), "status.remove")),
            count=status.get("last_created", status.get("expected", 0)),
        )
    if status.get("save_enabled"):
        save = tr("status.available")
    elif "No Parts tag" in status.get("save", ""):
        save = f"{tr('status.disabled')} — {tr('status.no_parts_tag')}"
    else:
        save = f"{tr('status.disabled')} — {tr('status.no_valid_parts')}"
    return {
        "death": f"{corpse} + {parts}",
        "runtime": runtime,
        "save": save,
        "reason": localized_slice_export_reason(status.get("reason", "")),
    }


def layer_list_height(layer_count):
    return max(0, int(layer_count)) * 28 + 10


def clamp_settings_scroll(scroll, content_height, viewport_height):
    return max(min(0, int(scroll)), -max(0, int(content_height) - int(viewport_height)))


def set_sidebar_mode(current_mode, requested_mode):
    requested_mode = requested_mode if requested_mode in SIDEBAR_MODES else SIDEBAR_MAPPING
    return requested_mode


CONTROL_ACTION_LABEL_KEYS = OrderedDict((
    ("ATTACK", "guide.attack"),
    ("DASH", "guide.dash"),
    ("JUMP", "guide.jump"),
    ("SWAP", "guide.swap"),
    ("SKILL1", "control.skill_1"),
    ("SKILL2", "control.skill_2"),
    ("SKILL3", "control.skill_3"),
    ("SYNERGY", "guide.synergy"),
    ("SUMMON", "control.summon"),
    ("HIT_1", "control.hit_1"),
))


def control_action_label(action, language=None):
    label_key = CONTROL_ACTION_LABEL_KEYS.get(str(action))
    return tr(label_key, language=language) if label_key else str(action)


def character_key_guide_items(player):
    key_map = getattr(player, "key_map", {}) or {}
    actions = (
        ("ATTACK", "guide.attack"),
        ("DASH", "guide.dash"),
        ("JUMP", "guide.jump"),
        ("SWAP", "guide.swap"),
    )
    items = []
    for action, label_key in actions:
        key = key_map.get(action)
        if key is None:
            continue
        items.append((pygame.key.name(key).upper(), tr(label_key), None))
    skill_keys = [
        pygame.key.name(key_map[action]).upper()
        for action in ("SKILL1", "SKILL2", "SKILL3")
        if action in key_map
    ]
    if skill_keys:
        items.append(("/".join(skill_keys), tr("guide.skills"), None))
    synergy_key = key_map.get("SYNERGY")
    if synergy_key is not None:
        items.append((
            pygame.key.name(synergy_key).upper(),
            tr("guide.synergy"),
            None,
        ))
    return items


def app_shortcut_guide_items(player=None):
    """Shortcuts already handled by the application event loop."""
    playback_speed = _finite_number(
        getattr(player, "playback_speed", 1.0), 1.0,
    )
    return [
        ("P", tr("guide.pause"), None),
        ("O", tr("guide.step"), "tooltip.guide.step"),
        ("[ ]", f"{tr('guide.speed')} {playback_speed:.1f}x", None),
        ("F5", tr("guide.refresh"), None),
        ("F10", tr("guide.performance"), "performance.help"),
        ("H", tr("guide.hitbox"), None),
        ("R-Drag", tr("guide.camera"), None),
        ("F", tr("guide.camera_reset"), None),
    ]


def bottom_key_guide_groups(player):
    return [
        {
            "id": "character",
            "title": tr("guide.group.character"),
            "items": character_key_guide_items(player),
        },
        {
            "id": "app",
            "title": tr("guide.group.app"),
            "items": app_shortcut_guide_items(player),
        },
    ]


def bottom_key_guide_items(player):
    """Compatibility flat view; layout and drawing retain group identity."""
    return [
        item
        for group in bottom_key_guide_groups(player)
        for item in group["items"]
    ]


def dash_charge_hud_rects(hud_y, max_charges=2):
    """The single normal-play dash remaining indicator."""
    return [
        pygame.Rect(20 + index * 40, int(hud_y) + 25, 35, 10)
        for index in range(max(0, int(max_charges)))
    ]


def split_actor_render_layers(player):
    """Keep swap-departure visuals below Player without reordering scene actors."""
    temp_actors = list(getattr(player, "temp_ai_list", []) or [])
    below_player = [
        actor for actor in temp_actors
        if bool(getattr(actor, "render_below_player", False))
    ]
    foreground = (
        list(getattr(player, "ai_list", []) or [])
        + list(getattr(player, "prop_list", []) or [])
        + [
            actor for actor in temp_actors
            if not bool(getattr(actor, "render_below_player", False))
        ]
    )
    return below_player, foreground


def bottom_key_guide_layout(player, sidebar_mode, play_width, screen_height, font):
    del sidebar_mode  # The common HUD intentionally has identical mode policy.
    gap = 8
    rows = []
    for group in bottom_key_guide_groups(player):
        if not group["items"]:
            continue
        title_width = font.size(group["title"])[0] + 18
        row = [{
            "kind": "title", "group": group["id"],
            "text": group["title"],
            "rect": pygame.Rect(15, 0, title_width, 24),
        }]
        row_width = 15 + title_width + gap
        for key, label, tooltip_key in group["items"]:
            width = font.size(key)[0] + font.size(label)[0] + 25
            if len(row) > 1 and row_width + width > max(80, play_width - 10):
                rows.append(row)
                row = []
                row_width = 15
            rect = pygame.Rect(row_width, 0, width, 24)
            row.append({
                "kind": "item", "group": group["id"], "rect": rect,
                "key": key, "label": label, "tooltip_key": tooltip_key,
            })
            row_width += width + gap
        rows.append(row)
    if not rows:
        return {
            "background": pygame.Rect(0, screen_height, play_width, 0),
            "groups": [], "items": [],
        }
    guide_height = max(40, 8 + len(rows) * 28)
    top = screen_height - guide_height
    laid_out = []
    titles = []
    for row_index, row in enumerate(rows):
        for entry in row:
            positioned = dict(entry)
            positioned["rect"] = entry["rect"].move(
                0, top + 6 + row_index * 28,
            )
            if entry["kind"] == "title":
                titles.append(positioned)
            else:
                laid_out.append(positioned)
    return {
        "background": pygame.Rect(0, top, play_width, guide_height),
        "groups": titles,
        "items": laid_out,
    }


def draw_bottom_key_guide(
    surface, player, sidebar_mode, play_width, font, tooltip_regions,
):
    model = bottom_key_guide_layout(
        player, sidebar_mode, play_width, surface.get_height(), font,
    )
    pygame.draw.rect(surface, (30, 30, 35), model["background"])
    for group in model["groups"]:
        pygame.draw.rect(
            surface, (67, 73, 87), group["rect"], border_radius=4,
        )
        draw_centered_label(
            surface, font, group["text"], group["rect"], (220, 225, 235),
        )
    for item in model["items"]:
        pygame.draw.rect(surface, (45, 45, 50), item["rect"], border_radius=4)
        x = item["rect"].x + 5
        surface.blit(
            font.render(item["key"], True, (59, 130, 246)),
            (x, item["rect"].y + 5),
        )
        surface.blit(
            font.render(f": {item['label']}", True, (255, 255, 255)),
            (x + font.size(item["key"])[0], item["rect"].y + 5),
        )
        if item["tooltip_key"]:
            register_tooltip(
                tooltip_regions, item["rect"], item["tooltip_key"],
            )
    return model


def sidebar_rects(play_width, window_height, sidebar_width=SIDEBAR_WIDTH):
    header = pygame.Rect(int(play_width), 0, int(sidebar_width), TOP_UI_HEIGHT)
    content = pygame.Rect(
        int(play_width), TOP_UI_HEIGHT, int(sidebar_width),
        max(0, int(window_height) - TOP_UI_HEIGHT),
    )
    return header, content


def sidebar_navigation_button_rects(play_width, sidebar_width=SIDEBAR_WIDTH):
    gap = 5
    left = int(play_width) + 10
    available = int(sidebar_width) - 20 - gap * 3
    base_width, remainder = divmod(available, 4)
    rects = []
    x = left
    for index in range(4):
        width = base_width + (1 if index < remainder else 0)
        rects.append(pygame.Rect(x, 5, width, 28))
        x += width + gap
    return tuple(rects)


def sidebar_selection_button_rects(play_width, sidebar_width=SIDEBAR_WIDTH):
    _mapping, scene, resources, _settings = sidebar_navigation_button_rects(
        play_width, sidebar_width,
    )
    return scene, resources


def sidebar_header_click_target(
    mouse_pos, mapping_button, scene_button, resource_button, settings_button,
):
    if pygame.Rect(mapping_button).collidepoint(mouse_pos):
        return SIDEBAR_MAPPING
    if pygame.Rect(scene_button).collidepoint(mouse_pos):
        return SIDEBAR_SCENE
    if pygame.Rect(resource_button).collidepoint(mouse_pos):
        return SIDEBAR_RESOURCES
    if pygame.Rect(settings_button).collidepoint(mouse_pos):
        return SIDEBAR_SETTINGS
    return None


def draw_sidebar_header(
    surface, player, sidebar_mode, mapping_button, scene_button,
    resource_button, settings_button,
    fonts, tooltip_regions, header_rect,
):
    font_small, _font_bold = fonts
    pygame.draw.rect(surface, (25, 25, 30), header_rect)
    for mode, rect, label_key, tooltip_key in (
        (SIDEBAR_MAPPING, mapping_button, "sidebar.tag_setup", "tooltip.sidebar.tag_setup"),
        (SIDEBAR_SCENE, scene_button, "sidebar.scene", "tooltip.selection.scene"),
        (SIDEBAR_RESOURCES, resource_button, "sidebar.resources", "tooltip.selection.resources"),
        (SIDEBAR_SETTINGS, settings_button, "sidebar.options", "tooltip.options"),
    ):
        pygame.draw.rect(
            surface, (59, 130, 246) if sidebar_mode == mode else (60, 60, 70),
            rect, border_radius=5,
        )
        draw_centered_label(surface, font_small, tr(label_key), rect)
        register_tooltip(tooltip_regions, rect, tooltip_key)
    summary = current_selection_summary(player)
    summary_rect = pygame.Rect(
        header_rect.x + 15, 40, max(0, header_rect.w - 30), 22,
    )
    summary_text = f"{summary['actor_text']}  |  {summary['resource_text']}"
    summary_text = ellipsize_path(summary_text, font_small, summary_rect.w)
    surface.blit(
        font_small.render(summary_text, True, (190, 202, 220)),
        summary_rect.topleft,
    )
    register_tooltip(tooltip_regions, summary_rect, "tooltip.selection.current")
    return {
        "mapping_button": pygame.Rect(mapping_button),
        "settings_button": pygame.Rect(settings_button),
        "scene_button": pygame.Rect(scene_button),
        "resource_button": pygame.Rect(resource_button),
        "summary": summary_rect,
    }


def clipped_global_rect(local_rect, origin, viewport):
    global_rect = pygame.Rect(local_rect).move(origin)
    clipped = global_rect.clip(pygame.Rect(viewport))
    return clipped if clipped.w > 0 and clipped.h > 0 else None


def register_clipped_tooltip(regions, local_rect, translation_key, origin, viewport):
    clipped = clipped_global_rect(local_rect, origin, viewport)
    if clipped is not None:
        register_tooltip(regions, clipped, translation_key)
    return clipped


def sidebar_control_hit(local_rect, mouse_pos, origin, viewport):
    clipped = clipped_global_rect(local_rect, origin, viewport)
    return bool(clipped and clipped.collidepoint(mouse_pos))


def mapping_workspace_copy(player):
    has_resources = bool(getattr(player, "sources", []))
    has_profiles = bool(getattr(player, "profiles", []))
    lines = [tr("mapping.help")]
    if not has_resources:
        lines = [
            tr("mapping.empty.import"),
            tr("mapping.empty.resources"),
            tr("mapping.empty.roles"),
        ]
    elif not has_profiles:
        lines.extend([
            tr("selection.imported_choose_role"),
            tr("mapping.empty.roles"),
        ])
    return {
        "title": tr("mapping.title"),
        "lines": lines,
        "empty": not has_profiles,
    }


def draw_mapping_workspace_intro(surface, player, fonts, viewport_rect):
    font_small, font_bold = fonts
    viewport = pygame.Rect(viewport_rect)
    copy_data = mapping_workspace_copy(player)
    pygame.draw.rect(surface, (25, 27, 34), viewport)
    title_rect = pygame.Rect(
        viewport.x + 15, viewport.y + 10, viewport.w - 30, 24,
    )
    surface.blit(
        font_bold.render(copy_data["title"], True, (245, 245, 248)),
        title_rect.topleft,
    )
    y = title_rect.bottom + 7
    for message in copy_data["lines"]:
        for line in wrap_ui_text(message, font_small, viewport.w - 36):
            surface.blit(
                font_small.render(line, True, (170, 184, 205)),
                (viewport.x + 18, y),
            )
            y += 18
        y += 3
    return {
        "title_rect": title_rect,
        "content_bottom": y,
        **copy_data,
    }


def layer_inventory_summary(layers):
    keys = [layer.get("key") for layer in layers]
    return {
        "total": len(layers),
        "groups": sum(1 for layer in layers if layer.get("is_group")),
        "renderable": sum(1 for layer in layers if layer.get("is_image") or layer.get("is_tilemap") or layer.get("is_reference")),
        "duplicate_keys": len(keys) - len(set(keys)),
        "order": [layer.get("path", layer.get("name", "")) for layer in layers],
    }


def begin_slice_export(player, source, owner_kind):
    status = slice_export_availability(source)
    if not status["enabled"]:
        show_user_error(
            f"{tr('common.save')} — {tr('status.disabled')}",
            localized_slice_export_reason(status["reason"]),
        )
        return False
    player.popup = {
        "msg": tr("export.confirm"),
        "confirm_label": tr("common.export"),
        "cancel_label": tr("common.cancel"),
        "cb": lambda: run_slice_export_workflow(
            source,
            owner_kind,
            confirm=lambda: True,
        ),
        "no_cb": None,
    }
    return True


def show_source_removal_result(result):
    if not result or not result.get("removed"):
        return
    message = "\n".join([
        tr("source.removed"),
        tr("source.removed_profiles", count=result["profiles"]),
        tr("source.removed_partners", count=result.get("partners", 0)),
        tr("source.removed_npcs", count=result["npcs"]),
        tr("source.removed_props", count=result["props"]),
    ])
    if result.get("player_disabled"):
        message += f"\n{tr('source.player_disabled')}"
    show_user_info(tr("source.removal_title"), message)


def save_json(path, data):
    directory = os.path.dirname(os.path.abspath(path))
    fd, temp_path = tempfile.mkstemp(prefix=f".{os.path.basename(path)}.", suffix=".tmp", dir=directory)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        os.replace(temp_path, path)
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

# Crash Catcher
def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    log_debug("[CRITICAL ERROR]")
    err_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    log_debug(err_msg)

sys.excepthook = handle_exception


class LimitedLRU:
    def __init__(self, max_size=512):
        self.max_size = max(1, int(max_size))
        self._items = OrderedDict()

    def get(self, key, default=None):
        try:
            value = self._items.pop(key)
        except KeyError:
            return default
        self._items[key] = value
        return value

    def put(self, key, value):
        if key in self._items:
            self._items.pop(key)
        self._items[key] = value
        while len(self._items) > self.max_size:
            self._items.popitem(last=False)
        return value

    def clear(self):
        self._items.clear()

    def __contains__(self, key):
        return key in self._items

    def __len__(self):
        return len(self._items)


PERFORMANCE_SECTIONS = (
    "events",
    "update",
    "background_update",
    "actor_update",
    "particle_update",
    "world_render",
    "background_render",
    "actor_render",
    "particle_render",
    "ui_render",
    "tooltip_render",
    "display",
    "frame_limiter",
)


def _performance_percentile(values, percentile):
    if not values:
        return 0.0
    ordered = sorted(values)
    index = min(len(ordered) - 1, max(0, int((len(ordered) - 1) * percentile)))
    return float(ordered[index])


class PerformanceMonitor:
    def __init__(self, enabled=False, window_size=600):
        self.enabled = bool(enabled)
        self.window_size = max(1, int(window_size))
        self.frame_times = deque(maxlen=self.window_size)
        self.section_times = {
            name: deque(maxlen=self.window_size) for name in PERFORMANCE_SECTIONS
        }
        self.object_counts = {}
        self.total_frames = 0
        self.total_frame_ms = 0.0
        self.total_spikes_over_25ms = 0
        self.total_max_ms = 0.0
        self._current_sections = {}
        self._overlay_lines = []
        self._overlay_surfaces = []
        self._overlay_updated_at = -1000
        self._last_profile_report_at = 0

    def set_enabled(self, enabled, clear=False):
        self.enabled = bool(enabled)
        if clear:
            self.clear()

    def clear(self):
        self.frame_times.clear()
        for values in self.section_times.values():
            values.clear()
        self.object_counts = {}
        self.total_frames = 0
        self.total_frame_ms = 0.0
        self.total_spikes_over_25ms = 0
        self.total_max_ms = 0.0
        self._current_sections = {}
        self._overlay_lines = []
        self._overlay_surfaces = []
        self._overlay_updated_at = -1000
        self._last_profile_report_at = 0

    def begin_frame(self):
        if self.enabled:
            self._current_sections = {}
            return time.perf_counter_ns()
        return None

    def record(self, section, elapsed_ms):
        if not self.enabled or section not in self.section_times:
            return
        value = max(0.0, float(elapsed_ms))
        self._current_sections[section] = self._current_sections.get(section, 0.0) + value

    def record_since(self, section, started_ns):
        if self.enabled and started_ns is not None:
            self.record(section, (time.perf_counter_ns() - started_ns) / 1_000_000.0)

    def end_frame(self, started_ns, object_counts=None, total_ms=None):
        if not self.enabled:
            return
        if total_ms is None:
            total_ms = (
                (time.perf_counter_ns() - started_ns) / 1_000_000.0
                if started_ns is not None else sum(self._current_sections.values())
            )
        total_ms = max(0.0, float(total_ms))
        self.frame_times.append(total_ms)
        for section, values in self.section_times.items():
            values.append(self._current_sections.get(section, 0.0))
        self.object_counts = dict(object_counts or {})
        self.total_frames += 1
        self.total_frame_ms += total_ms
        self.total_max_ms = max(self.total_max_ms, total_ms)
        if total_ms > 25.0:
            self.total_spikes_over_25ms += 1
        self._current_sections = {}

    def snapshot(self):
        frames = list(self.frame_times)
        frame_avg = sum(frames) / len(frames) if frames else 0.0
        sections = {}
        for name, values in self.section_times.items():
            section_values = list(values)
            sections[name] = {
                "avg_ms": sum(section_values) / len(section_values) if section_values else 0.0,
                "max_ms": max(section_values, default=0.0),
            }
        return {
            "frames": len(frames),
            "fps": 1000.0 / frame_avg if frame_avg > 0 else 0.0,
            "frame_avg_ms": frame_avg,
            "frame_median_ms": _performance_percentile(frames, 0.5),
            "frame_p95_ms": _performance_percentile(frames, 0.95),
            "frame_p99_ms": _performance_percentile(frames, 0.99),
            "frame_max_ms": max(frames, default=0.0),
            "frames_over_16_67ms": sum(value > 16.67 for value in frames),
            "spikes_over_25ms": sum(value > 25.0 for value in frames),
            "sections": sections,
            "objects": dict(self.object_counts),
        }

    def final_summary(self):
        snapshot = self.snapshot()
        snapshot["frames"] = self.total_frames
        snapshot["fps"] = (
            1000.0 / (self.total_frame_ms / self.total_frames)
            if self.total_frames and self.total_frame_ms > 0 else 0.0
        )
        snapshot["frame_avg_ms"] = (
            self.total_frame_ms / self.total_frames if self.total_frames else 0.0
        )
        snapshot["frame_max_ms"] = self.total_max_ms
        snapshot["spikes_over_25ms"] = self.total_spikes_over_25ms
        return snapshot

    def overlay_surfaces(self, font, now_ms, cache_usage=0, cache_limit=512):
        if not self.enabled:
            return []
        if now_ms - self._overlay_updated_at >= 250 or not self._overlay_surfaces:
            data = self.snapshot()
            sections = data["sections"]
            objects = data["objects"]
            self._overlay_lines = [
                f"FPS {data['fps']:.1f}",
                (
                    f"Frame avg {data['frame_avg_ms']:.2f} ms / "
                    f"p95 {data['frame_p95_ms']:.2f} / max {data['frame_max_ms']:.2f}"
                ),
                (
                    f"Update {sections['update']['avg_ms']:.2f}  "
                    f"BG {sections['background_render']['avg_ms']:.2f}  "
                    f"Actors {sections['actor_render']['avg_ms']:.2f}"
                ),
                (
                    f"Particles {sections['particle_render']['avg_ms']:.2f}  "
                    f"UI {sections['ui_render']['avg_ms']:.2f}  "
                    f"Display {sections['display']['avg_ms']:.2f}"
                ),
                (
                    f"NPC {objects.get('npc', 0)} / PROP {objects.get('prop', 0)} / "
                    f"IMG PARTS {objects.get('image_particles', 0)} / "
                    f"FX {objects.get('color_particles', 0)}"
                ),
                (
                    f"BG {objects.get('backgrounds', 0)} / "
                    f"Tooltips {objects.get('tooltips', 0)} / "
                    f"Text cache {cache_usage}/{cache_limit}"
                ),
            ]
            self._overlay_surfaces = [
                font.render(line, True, (235, 241, 248)) for line in self._overlay_lines
            ]
            self._overlay_updated_at = int(now_ms)
        return self._overlay_surfaces


class CachedFont:
    def __init__(self, font, max_cache_size=512):
        self.font = font
        self.cache = LimitedLRU(max_cache_size)
    def render(self, text, antialias, color):
        key = (str(text), bool(antialias), tuple(color))
        cached = self.cache.get(key)
        if cached is None:
            cached = self.cache.put(key, self.font.render(str(text), antialias, color))
        return cached
    def size(self, text):
        return self.font.size(text)
    def clear_cache(self):
        self.cache.clear()


_UI_FONT_CACHE = {}
_UI_FONT_NAME = None
_UI_LAYOUT_CACHE = LimitedLRU(512)
_UI_LAYOUT_WINDOW_SIZE = None


def clear_ui_caches():
    _UI_LAYOUT_CACHE.clear()
    for font in _UI_FONT_CACHE.values():
        font.clear_cache()


def invalidate_ui_layout_for_window_size(window_size):
    global _UI_LAYOUT_WINDOW_SIZE
    normalized = tuple(int(value) for value in window_size)
    if normalized != _UI_LAYOUT_WINDOW_SIZE:
        _UI_LAYOUT_WINDOW_SIZE = normalized
        _UI_LAYOUT_CACHE.clear()
        return True
    return False


def ui_text_cache_usage():
    return sum(len(font.cache) for font in _UI_FONT_CACHE.values())


def selected_ui_font_name():
    global _UI_FONT_NAME
    if _UI_FONT_NAME is None:
        candidates = ["Malgun Gothic", "맑은 고딕", "Noto Sans CJK KR", "Arial Unicode MS", "Arial"]
        _UI_FONT_NAME = next(
            (name for name in candidates if pygame.font.match_font(name)),
            pygame.font.get_default_font(),
        )
    return _UI_FONT_NAME


def create_ui_font(size, bold=False):
    key = (int(size), bool(bold))
    if key not in _UI_FONT_CACHE:
        try:
            font = pygame.font.SysFont(selected_ui_font_name(), key[0], bold=key[1])
        except (pygame.error, TypeError):
            font = pygame.font.Font(None, key[0])
            font.set_bold(key[1])
        _UI_FONT_CACHE[key] = CachedFont(font)
    return _UI_FONT_CACHE[key]


def measure_ui_text(text, font):
    value = str(text or "")
    key = ("measure", id(font), value)
    cached = _UI_LAYOUT_CACHE.get(key)
    if cached is None:
        cached = _UI_LAYOUT_CACHE.put(key, font.size(value))
    return cached


def calculate_button_width(label, font, minimum_width, horizontal_padding=14, icon_width=0, maximum_width=None):
    text_width, _ = measure_ui_text(label, font)
    width = max(int(minimum_width), text_width + int(horizontal_padding) * 2 + int(icon_width))
    if maximum_width is not None:
        width = min(width, int(maximum_width))
    return width


def layout_button_row(specs, font, start_x, y, height=28, gap=5, horizontal_padding=14):
    key = (
        "button-row", tuple(tuple(spec) for spec in specs), id(font),
        int(start_x), int(y), int(height), int(gap), int(horizontal_padding),
    )
    cached = _UI_LAYOUT_CACHE.get(key)
    if cached is not None:
        return [pygame.Rect(rect) for rect in cached]
    rects = []
    x = int(start_x)
    for label, minimum_width, maximum_width in specs:
        width = calculate_button_width(
            label, font, minimum_width, horizontal_padding=horizontal_padding,
            maximum_width=maximum_width,
        )
        rects.append(pygame.Rect(x, int(y), width, int(height)))
        x += width + int(gap)
    _UI_LAYOUT_CACHE.put(key, tuple(pygame.Rect(rect) for rect in rects))
    return rects


def calculate_options_button_rect(play_width, font):
    del font
    return sidebar_navigation_button_rects(play_width)[3]


def toggle_options_panel(current_value, button_rect, mouse_pos):
    return not current_value if pygame.Rect(button_rect).collidepoint(mouse_pos) else current_value


def should_render_sidebar(show_settings, profiles):
    return bool(show_settings or profiles)


def options_availability(player):
    sources = getattr(player, "sources", [])
    profiles = getattr(player, "profiles", [])
    backgrounds = getattr(player, "bg_layers", [])
    return {
        "global": True,
        "layers": bool(sources),
        "source": bool(sources),
        "profile": bool(profiles),
        "slice_status": any(
            profile_kind(profile, index) in {"partner", "npc", "prop"}
            for index, profile in enumerate(profiles)
        ),
        "background": bool(backgrounds),
    }


SELECTION_WORKSPACE_CONTROLS = {
    "selection.current": {"tooltip_key": "tooltip.selection.current"},
    "selection.scene": {"tooltip_key": "tooltip.selection.scene"},
    "selection.resources": {"tooltip_key": "tooltip.selection.resources"},
    "selection.delete_corpse": {"tooltip_key": "tooltip.selection.delete_corpse"},
    "selection.delete_all_corpses": {"tooltip_key": "tooltip.selection.delete_all_corpses"},
    "selection.despawn": {"tooltip_key": "tooltip.selection.despawn"},
    "selection.focus_selected": {"tooltip_key": "tooltip.selection.focus_selected"},
    "selection.filter": {"tooltip_key": "tooltip.selection.filter"},
    "resource.use_player": {"tooltip_key": "tooltip.resource.use_player"},
    "resource.spawn_npc": {"tooltip_key": "tooltip.resource.spawn_npc"},
    "resource.place_prop": {"tooltip_key": "tooltip.resource.place_prop"},
    "resource.assign_player": {"tooltip_key": "tooltip.resource.assign_player"},
    "resource.add_partner": {"tooltip_key": "tooltip.resource.add_partner"},
    "resource.add_npc": {"tooltip_key": "tooltip.resource.add_npc"},
    "resource.add_prop": {"tooltip_key": "tooltip.resource.add_prop"},
    "resource.refresh": {"tooltip_key": "tooltip.resource.refresh"},
    "resource.remove": {"tooltip_key": "tooltip.resource.remove"},
    "resource.export_png": {"tooltip_key": "tooltip.resource.export_png"},
}


def visible_row_range(total_rows, scroll_offset, viewport_height, row_height, overscan=1):
    total_rows = max(0, int(total_rows))
    row_height = max(1, int(row_height))
    viewport_height = max(0, int(viewport_height))
    maximum_scroll = max(0, total_rows * row_height - viewport_height)
    scroll_offset = max(0, min(int(scroll_offset), maximum_scroll))
    start = max(0, scroll_offset // row_height - max(0, int(overscan)))
    visible_count = (viewport_height + row_height - 1) // row_height
    end = min(total_rows, start + visible_count + max(0, int(overscan)) * 2)
    return start, end, scroll_offset, maximum_scroll


def _profile_index_by_identity(player, profile):
    return next(
        (index for index, candidate in enumerate(player.profiles) if candidate is profile),
        None,
    )


def _friendly_profile_name(player, profile, profile_index, kind):
    profile_name = str(getattr(profile, "display_name", "") or getattr(profile, "name", "") or "").strip()
    generated_name = re.fullmatch(
        r"(?:PLAYER|PARTNER|NPC|PROP)(?:[_ -]?\d+)?",
        profile_name,
        re.IGNORECASE,
    )
    source_index = getattr(profile, "source_idx", -1)
    source = player.sources[source_index] if 0 <= source_index < len(player.sources) else None
    source_name = os.path.splitext(os.path.basename(str(getattr(source, "name", "") or "")))[0]
    if profile_name and not generated_name:
        return profile_name
    if source_name:
        return source_name
    return {
        "player": "Player", "partner": "Partner",
        "npc": "NPC", "prop": "PROP",
    }.get(kind, "Actor")


_SCENE_OBJECT_STATE_ATTRS = (
    "x", "y", "spawn_x", "spawn_y", "vx", "vy", "grounded",
    "facing_right", "visible", "frame_idx", "anim_timer",
    "active_tag_info", "active_action_slot", "action_queue",
    "action_end_frame", "decision", "swap_timer", "is_dead",
    "is_corpse", "corpse_looping", "corpse_anim_step",
    "scale", "zoom", "offset_x", "offset_y", "rotation",
)


def scene_object_stable_key(entity, kind, ordinal):
    if kind == "player":
        return "player", "singleton"
    for attribute in ("scene_object_id", "object_id", "persistent_id", "uid"):
        value = getattr(entity, attribute, None)
        if value not in (None, ""):
            return kind, attribute, str(value)
    profile = getattr(entity, "profile", None)
    return kind, "profile-instance", id(profile), int(ordinal)


def snapshot_scene_object_states(player):
    snapshot = {}
    for kind, entities in (
        ("player", [player]),
        ("npc", getattr(player, "ai_list", [])),
        ("prop", getattr(player, "prop_list", [])),
    ):
        for ordinal, entity in enumerate(entities):
            state = {
                attribute: copy.deepcopy(getattr(entity, attribute))
                for attribute in _SCENE_OBJECT_STATE_ATTRS
                if hasattr(entity, attribute)
            }
            snapshot[scene_object_stable_key(entity, kind, ordinal)] = state
    return snapshot


def restore_scene_object_states(player, snapshot):
    restored = 0
    for kind, entities in (
        ("player", [player]),
        ("npc", getattr(player, "ai_list", [])),
        ("prop", getattr(player, "prop_list", [])),
    ):
        for ordinal, entity in enumerate(entities):
            state = snapshot.get(scene_object_stable_key(entity, kind, ordinal))
            if state is None:
                continue
            for attribute, value in state.items():
                setattr(entity, attribute, copy.deepcopy(value))
            restored += 1
    return restored


def run_scene_preserving_mutation(player, mutation):
    snapshot = snapshot_scene_object_states(player)
    selected_key = getattr(player, "selected_scene_actor_key", None)
    try:
        return mutation()
    finally:
        restore_scene_object_states(player, snapshot)
        if selected_key is not None:
            remaining_keys = {
                row["key"] for row in build_scene_actor_rows(player)
            }
            if selected_key in remaining_keys:
                player.selected_scene_actor_key = selected_key


def _is_scene_object_corpse(entity):
    if entity is None:
        return False
    if bool(getattr(entity, "is_corpse", False)):
        return True
    explicit_values = [
        getattr(entity, attribute, None)
        for attribute in ("object_type", "state", "status", "decision")
    ]
    corpse_states = {
        "corpse", "dead", "death", "dead_loop", "dead_hold", "remnant",
    }
    if any(str(value).strip().casefold() in corpse_states for value in explicit_values):
        return True
    if bool(getattr(entity, "is_dead", False)):
        return True
    if any(value not in (None, "") for value in explicit_values):
        return False
    fallback_name = str(
        getattr(entity, "display_name", "")
        or getattr(entity, "name", "")
    ).casefold()
    return any(token in fallback_name for token in ("corpse", "remnant"))


def build_scene_actor_rows(player):
    raw_rows = []
    if (
        player.profiles
        and profile_kind(player.profiles[0], 0) == "player"
    ):
        profile = player.profiles[0]
        raw_rows.append({
            "kind": "player",
            "entity": player,
            "profile": profile,
            "profile_index": 0,
            "source_index": getattr(profile, "source_idx", -1),
            "key": ("player", id(player)),
            "status": "hidden" if not getattr(player, "visible", True) else "active",
        })
    for kind, entities in (
        ("npc", getattr(player, "ai_list", [])),
        ("prop", getattr(player, "prop_list", [])),
    ):
        for entity in entities:
            if bool(getattr(entity, "is_partner", False)):
                continue
            profile = getattr(entity, "profile", None)
            profile_index = _profile_index_by_identity(player, profile)
            is_corpse = kind == "npc" and _is_scene_object_corpse(entity)
            raw_rows.append({
                "kind": kind,
                "entity": entity,
                "profile": profile,
                "profile_index": profile_index,
                "source_index": getattr(profile, "source_idx", -1) if profile else -1,
                "key": (kind, id(entity)),
                "is_corpse": is_corpse,
                "status": (
                    "corpse" if is_corpse
                    else "hidden" if not getattr(entity, "visible", True)
                    else "active"
                ),
            })
    name_counts = {}
    kind_counts = {"npc": 0, "prop": 0}
    for row in raw_rows:
        base_name = _friendly_profile_name(
            player, row["profile"], row["profile_index"], row["kind"],
        ) if row["profile"] is not None else row["kind"].upper()
        row["base_name"] = base_name
        if row["kind"] != "player":
            kind_counts[row["kind"]] += 1
            row["scene_number"] = kind_counts[row["kind"]]
            count_key = (row["kind"], base_name.casefold())
            name_counts[count_key] = name_counts.get(count_key, 0) + 1
            row["instance_number"] = name_counts[count_key]
            row["display_name"] = f"{base_name} #{row['instance_number']}"
            corpse_suffix = " · CORPSE" if row.get("is_corpse") else ""
            row["badge_text"] = (
                f"{row['kind'].upper()} {row['scene_number']:02d}{corpse_suffix}"
            )
        else:
            row["instance_number"] = None
            row["scene_number"] = None
            row["display_name"] = base_name
            row["badge_text"] = "PLAYER"
        source_index = row["source_index"]
        row["source_name"] = (
            player.sources[source_index].name
            if 0 <= source_index < len(player.sources) else ""
        )
        row["source_missing"] = not bool(row["source_name"])
    return raw_rows


def normalize_scene_object_filter(value):
    normalized = str(value or SCENE_FILTER_ALL).strip().casefold()
    return normalized if normalized in SCENE_OBJECT_FILTERS else SCENE_FILTER_ALL


def filter_scene_actor_rows(rows, filter_name):
    normalized = normalize_scene_object_filter(filter_name)
    if normalized == SCENE_FILTER_ALL:
        return list(rows)
    if normalized == SCENE_FILTER_PLAYER:
        return [row for row in rows if row["kind"] == "player"]
    if normalized == SCENE_FILTER_NPC:
        return [
            row for row in rows
            if row["kind"] == "npc" and not row.get("is_corpse")
        ]
    if normalized == SCENE_FILTER_PROP:
        return [row for row in rows if row["kind"] == "prop"]
    return [row for row in rows if row.get("is_corpse")]


def scene_rows_for_current_filter(player, rows=None):
    if rows is None:
        rows = selection_workspace_model(player)["scene_rows"]
    return filter_scene_actor_rows(
        rows, getattr(player, "scene_object_filter", SCENE_FILTER_ALL),
    )


def set_scene_object_filter(player, filter_name):
    player.scene_object_filter = normalize_scene_object_filter(filter_name)
    selected_key = getattr(player, "selected_scene_actor_key", None)
    all_rows = selection_workspace_model(player)["scene_rows"]
    visible_keys = {
        row["key"] for row in scene_rows_for_current_filter(player, all_rows)
    }
    if selected_key is not None and selected_key not in visible_keys:
        player.scene_status_message = tr("selection.hidden_by_filter")
    else:
        player.scene_status_message = ""
    return player.scene_object_filter


def build_resource_library_rows(player):
    rows = []
    for source_index, source in enumerate(player.sources):
        linked_profiles = [
            (index, profile)
            for index, profile in enumerate(player.profiles)
            if getattr(profile, "source_idx", -1) == source_index
        ]
        roles = sorted({
            profile_kind(profile, index).upper() for index, profile in linked_profiles
        })
        npc_instances = sum(
            getattr(entity, "profile", None) is profile
            for _, profile in linked_profiles
            for entity in getattr(player, "ai_list", [])
        )
        partner_profiles = sum(
            profile_kind(profile, profile_index) == "partner"
            for profile_index, profile in linked_profiles
        )
        prop_instances = sum(
            getattr(entity, "profile", None) is profile
            for _, profile in linked_profiles
            for entity in getattr(player, "prop_list", [])
        )
        analysis = getattr(source, "slice_export_analysis", None)
        if not _slice_analysis_is_current(source, analysis):
            analysis = None
        parts = len(analysis["valid_parts_slices"]) if analysis else 0
        particles = len(analysis["valid_particle_slices"]) if analysis else 0
        rows.append({
            "key": ("source", id(source)),
            "source": source,
            "source_index": source_index,
            "filename": os.path.basename(str(getattr(source, "name", "") or getattr(source, "file_path", ""))),
            "path": str(getattr(source, "file_path", "") or ""),
            "roles": roles,
            "profile_count": len(linked_profiles),
            "npc_instances": npc_instances,
            "partner_profiles": partner_profiles,
            "prop_instances": prop_instances,
            "parts": parts,
            "particles": particles,
            "can_use_player": any(profile_kind(profile, index) == "player" for index, profile in linked_profiles),
            "can_spawn_npc": any(profile_kind(profile, index) == "npc" for index, profile in linked_profiles),
            "can_place_prop": any(profile_kind(profile, index) == "prop" for index, profile in linked_profiles),
            "can_assign_player": True,
            "can_add_partner": True,
            "can_add_npc": True,
            "can_add_prop": True,
            "can_export_png": bool(parts or particles),
        })
    return rows


def selection_workspace_model(player):
    signature = (
        tuple((id(source), getattr(source, "source_revision", 0)) for source in player.sources),
        tuple(
            (
                id(profile), getattr(profile, "source_idx", -1),
                getattr(profile, "name", ""),
                profile_kind(profile, index),
            )
            for index, profile in enumerate(player.profiles)
        ),
        tuple(
            (
                id(entity), getattr(entity, "visible", True),
                getattr(entity, "is_corpse", False),
                getattr(entity, "is_dead", False),
                getattr(entity, "decision", None),
            )
            for entity in getattr(player, "ai_list", [])
        ),
        tuple(id(profile) for profile in partner_roster_profiles(player)),
        tuple(
            (id(entity), getattr(entity, "visible", True), getattr(entity, "is_corpse", False))
            for entity in getattr(player, "prop_list", [])
        ),
        normalize_language(getattr(player, "language", _CURRENT_LANGUAGE)),
    )
    cached = getattr(player, "_selection_workspace_model", None)
    if cached and cached["signature"] == signature:
        return cached
    model = {
        "signature": signature,
        "scene_rows": build_scene_actor_rows(player),
        "resource_rows": build_resource_library_rows(player),
    }
    player._selection_workspace_model = model
    return model


def select_scene_actor(player, actor_key):
    rows = selection_workspace_model(player)["scene_rows"]
    row = next((candidate for candidate in rows if candidate["key"] == actor_key), None)
    if row is None or row["profile_index"] is None:
        return False
    player.cur_profile_idx = row["profile_index"]
    if 0 <= row["source_index"] < len(player.sources):
        player.cur_source_idx = row["source_index"]
    player.selected_scene_actor_key = row["key"]
    return True


def select_resource_row(player, source_index):
    if not 0 <= int(source_index) < len(player.sources):
        return False
    player.cur_source_idx = int(source_index)
    return True


def workspace_selected_row_index(player, tab):
    model = selection_workspace_model(player)
    if tab == "resources":
        source_index = getattr(player, "cur_source_idx", -1)
        return next(
            (index for index, row in enumerate(model["resource_rows"])
             if row["source_index"] == source_index),
            0,
        )
    scene_rows = scene_rows_for_current_filter(player, model["scene_rows"])
    selected_key = getattr(player, "selected_scene_actor_key", None)
    index = next(
        (index for index, row in enumerate(scene_rows)
         if row["key"] == selected_key),
        None,
    )
    if index is not None:
        return index
    profile_index = getattr(player, "cur_profile_idx", -1)
    return next(
        (index for index, row in enumerate(scene_rows)
         if row["profile_index"] == profile_index),
        0,
    )


def current_selection_summary(player):
    model = selection_workspace_model(player)
    selected_key = getattr(player, "selected_scene_actor_key", None)
    selected = next(
        (row for row in model["scene_rows"] if row["key"] == selected_key),
        None,
    )
    if selected is None:
        selected = next(
            (
                row for row in model["scene_rows"]
                if row["profile_index"] == getattr(player, "cur_profile_idx", -1)
            ),
            model["scene_rows"][0] if model["scene_rows"] else None,
        )
    source = (
        player.sources[player.cur_source_idx]
        if player.sources and 0 <= player.cur_source_idx < len(player.sources) else None
    )
    return {
        "actor": selected,
        "actor_text": (
            f"{selected['kind'].upper()} · {selected['display_name']}"
            if selected else tr("selection.none")
        ),
        "resource_text": (
            os.path.basename(str(getattr(source, "name", "") or getattr(source, "file_path", "")))
            if source else tr("selection.none")
        ),
        "linked_source_index": selected["source_index"] if selected else None,
    }


def _select_scene_removal_fallback(player, old_rows, removed_keys, preferred_key):
    if preferred_key is None:
        player.selected_scene_actor_key = None
        return None
    if preferred_key not in removed_keys:
        remaining_keys = {
            row["key"] for row in selection_workspace_model(player)["scene_rows"]
        }
        if preferred_key in remaining_keys:
            player.selected_scene_actor_key = preferred_key
            return preferred_key

    old_visible_rows = scene_rows_for_current_filter(player, old_rows)
    old_index = next(
        (
            index for index, row in enumerate(old_visible_rows)
            if row["key"] == preferred_key
        ),
        0,
    )
    refreshed_rows = scene_rows_for_current_filter(player)
    if refreshed_rows:
        fallback = refreshed_rows[min(old_index, len(refreshed_rows) - 1)]
        if select_scene_actor(player, fallback["key"]):
            return fallback["key"]
    player.selected_scene_actor_key = None
    if not selection_workspace_model(player)["scene_rows"]:
        player.cur_profile_idx = 0
        player.cur_source_idx = 0
    return None


def delete_selected_corpse(player):
    model = selection_workspace_model(player)
    corpse_rows = [
        row for row in model["scene_rows"]
        if row["kind"] == "npc" and row.get("is_corpse")
    ]
    if not corpse_rows:
        status_key = "selection.no_corpses"
        player.scene_status_message = tr(status_key)
        return {"deleted": False, "status_key": status_key, "entity": None}

    selected_key = getattr(player, "selected_scene_actor_key", None)
    selected_row = next(
        (row for row in model["scene_rows"] if row["key"] == selected_key),
        None,
    )
    if selected_row is None:
        selected_row = current_selection_summary(player)["actor"]
    if (
        selected_row is None
        or selected_row["kind"] != "npc"
        or not selected_row.get("is_corpse")
    ):
        status_key = "selection.no_corpse_selected"
        player.scene_status_message = tr(status_key)
        return {"deleted": False, "status_key": status_key, "entity": None}

    entity = selected_row["entity"]
    player.ai_list = [
        candidate for candidate in getattr(player, "ai_list", [])
        if candidate is not entity
    ]
    _select_scene_removal_fallback(
        player, model["scene_rows"], {selected_row["key"]}, selected_row["key"],
    )
    status_key = "selection.corpse_deleted"
    player.scene_status_message = tr(status_key)
    return {"deleted": True, "status_key": status_key, "entity": entity}


def despawn_selected_npc(player):
    model = selection_workspace_model(player)
    selected_key = getattr(player, "selected_scene_actor_key", None)
    selected_row = next(
        (row for row in model["scene_rows"] if row["key"] == selected_key),
        None,
    )
    if selected_row is None:
        status_key = "selection.no_npc_selected"
    elif selected_row["kind"] == "player":
        status_key = "selection.player_not_despawnable"
    elif selected_row["kind"] != "npc":
        status_key = "selection.no_npc_selected"
    elif selected_row.get("is_corpse"):
        status_key = "selection.corpse_use_delete"
    else:
        entity = selected_row["entity"]
        player.ai_list = [
            candidate for candidate in getattr(player, "ai_list", [])
            if candidate is not entity
        ]
        player.target_ai_count = max(
            0, int(getattr(player, "target_ai_count", 0)) - 1,
        )
        _select_scene_removal_fallback(
            player, model["scene_rows"], {selected_row["key"]},
            selected_row["key"],
        )
        status_key = "selection.npc_despawned"
        player.scene_status_message = tr(status_key)
        return {
            "despawned": True, "status_key": status_key, "entity": entity,
        }
    player.scene_status_message = tr(status_key)
    return {"despawned": False, "status_key": status_key, "entity": None}


def delete_all_corpses(player):
    model = selection_workspace_model(player)
    corpse_rows = [
        row for row in model["scene_rows"]
        if row["kind"] == "npc" and row.get("is_corpse")
    ]
    if not corpse_rows:
        status_key = "selection.no_corpses"
        player.scene_status_message = tr(status_key)
        return {"deleted": 0, "status_key": status_key, "entities": []}

    removed_entities = [row["entity"] for row in corpse_rows]
    removed_ids = {id(entity) for entity in removed_entities}
    removed_keys = {row["key"] for row in corpse_rows}
    selected_key = getattr(player, "selected_scene_actor_key", None)
    player.ai_list = [
        candidate for candidate in getattr(player, "ai_list", [])
        if id(candidate) not in removed_ids
    ]
    _select_scene_removal_fallback(
        player, model["scene_rows"], removed_keys, selected_key,
    )
    status_key = "selection.corpses_deleted"
    player.scene_status_message = tr(status_key, count=len(removed_entities))
    return {
        "deleted": len(removed_entities),
        "status_key": status_key,
        "entities": removed_entities,
    }


def focus_selected_scene_object(player):
    selected_key = getattr(player, "selected_scene_actor_key", None)
    selected_row = next(
        (
            row for row in selection_workspace_model(player)["scene_rows"]
            if row["key"] == selected_key
        ),
        None,
    )
    entity = selected_row["entity"] if selected_row is not None else None
    x = getattr(entity, "x", None)
    y = getattr(entity, "y", None)
    if (
        entity is None
        or not isinstance(x, (int, float))
        or not isinstance(y, (int, float))
        or not math.isfinite(x)
        or not math.isfinite(y)
    ):
        status_key = "selection.no_scene_selected"
        player.scene_status_message = tr(status_key)
        return False
    player.cam_x = float(x)
    player.cam_y = float(y)
    player.cam_follow = False
    status_key = "selection.focused"
    player.scene_status_message = tr(status_key)
    return True


def draw_selection_workspace(
    surface, player, tab, scroll_offset, fonts, tooltip_regions,
    viewport_rect=None, origin_x=0,
):
    font_small, font_bold = fonts
    width, height = surface.get_size()
    panel = (
        pygame.Rect(viewport_rect)
        if viewport_rect is not None
        else pygame.Rect(origin_x, TOP_UI_HEIGHT, width - origin_x, height - TOP_UI_HEIGHT)
    )
    pygame.draw.rect(surface, (25, 27, 34), panel)
    summary = current_selection_summary(player)
    controls = []

    title_rect = pygame.Rect(panel.x + 12, panel.y + 10, panel.w - 24, 22)
    surface.blit(font_bold.render(tr("selection.current"), True, (245, 245, 248)), title_rect.topleft)
    register_tooltip(tooltip_regions, title_rect, "tooltip.selection.current")
    surface.blit(
        font_small.render(
            f"{tr('selection.scene_target')}: {summary['actor_text']}",
            True, (215, 220, 230),
        ),
        (panel.x + 18, panel.y + 36),
    )
    surface.blit(
        font_small.render(
            f"{tr('selection.linked_resource')}: {summary['resource_text']}",
            True, (160, 188, 230),
        ),
        (panel.x + 18, panel.y + 56),
    )

    if tab == SIDEBAR_SCENE:
        filter_name = normalize_scene_object_filter(
            getattr(player, "scene_object_filter", SCENE_FILTER_ALL),
        )
        filter_gap = 4
        filter_width = max(
            36, (panel.w - 24 - filter_gap * (len(SCENE_OBJECT_FILTERS) - 1))
            // len(SCENE_OBJECT_FILTERS),
        )
        for index, filter_value in enumerate(SCENE_OBJECT_FILTERS):
            filter_rect = pygame.Rect(
                panel.x + 12 + index * (filter_width + filter_gap),
                panel.y + 84,
                filter_width,
                26,
            )
            active = filter_value == filter_name
            pygame.draw.rect(
                surface, (59, 130, 246) if active else (50, 53, 62),
                filter_rect, border_radius=4,
            )
            draw_centered_label(
                surface, font_small,
                tr(f"selection.filter.{filter_value}"), filter_rect,
                (248, 250, 255) if active else (170, 176, 188),
            )
            register_tooltip(
                tooltip_regions, filter_rect, "tooltip.selection.filter",
            )
            controls.append({
                "rect": filter_rect,
                "action": "scene_filter",
                "value": filter_value,
                "enabled": True,
            })
        section_y = panel.y + 118
    else:
        roster = partner_roster_profiles(player)
        selected_partner = (
            player.profiles[getattr(player, "swap_target_idx", -1)]
            if 0 <= getattr(player, "swap_target_idx", -1) < len(player.profiles)
            and player.profiles[getattr(player, "swap_target_idx", -1)] in roster
            else (roster[0] if roster else None)
        )
        next_name = (
            _friendly_profile_name(
                player, selected_partner,
                _profile_index_by_identity(player, selected_partner),
                "partner",
            )
            if selected_partner is not None else "-"
        )
        roster_text = tr(
            "selection.partner_roster", count=len(roster), next=next_name,
        )
        surface.blit(
            font_small.render(roster_text, True, (166, 188, 225)),
            (panel.x + 18, panel.y + 82),
        )
        section_y = panel.y + 108

    section_rect = pygame.Rect(panel.x + 12, section_y, panel.w - 24, 22)
    section_key = "selection.scene" if tab == SIDEBAR_SCENE else "selection.resources"
    section_tooltip = (
        "tooltip.selection.scene"
        if tab == SIDEBAR_SCENE else "tooltip.selection.resources"
    )
    surface.blit(font_bold.render(tr(section_key), True, (225, 230, 240)), section_rect.topleft)
    register_tooltip(tooltip_regions, section_rect, section_tooltip)
    pygame.draw.line(
        surface, (65, 70, 82),
        (section_rect.x, section_rect.bottom + 2),
        (section_rect.right, section_rect.bottom + 2),
    )

    model = selection_workspace_model(player)
    rows = (
        scene_rows_for_current_filter(player, model["scene_rows"])
        if tab == SIDEBAR_SCENE else model["resource_rows"]
    )
    row_height = 42 if tab == SIDEBAR_SCENE else 58
    actions_height = (
        138 if tab == SIDEBAR_RESOURCES and rows
        else 100 if tab == SIDEBAR_SCENE
        else 10
    )
    viewport = pygame.Rect(
        panel.x + 12, section_rect.bottom + 8, panel.w - 24,
        max(40, panel.bottom - (section_rect.bottom + 8) - actions_height - 12),
    )
    pygame.draw.rect(surface, (18, 20, 26), viewport, border_radius=4)
    start, end, scroll_offset, maximum_scroll = visible_row_range(
        len(rows), scroll_offset, viewport.h, row_height, overscan=1,
    )
    surface.set_clip(viewport)
    for row_index in range(start, end):
        row = rows[row_index]
        y = viewport.y + row_index * row_height - scroll_offset
        row_rect = pygame.Rect(viewport.x + 4, y + 2, viewport.w - 8, row_height - 4)
        if row_rect.bottom < viewport.top or row_rect.top > viewport.bottom:
            continue
        if tab == SIDEBAR_SCENE:
            selected = summary["actor"] is not None and summary["actor"]["key"] == row["key"]
            pygame.draw.rect(
                surface, (54, 90, 148) if selected else (43, 46, 56),
                row_rect, border_radius=4,
            )
            badge_surface = font_bold.render(
                f"[{row['badge_text']}]", True,
                (245, 166, 35) if row.get("is_corpse") else (130, 190, 255),
            )
            surface.blit(badge_surface, (row_rect.x + 8, row_rect.y + 6))
            name_x = row_rect.x + 16 + badge_surface.get_width()
            available_name_width = max(20, row_rect.right - name_x - 20)
            display_name = ellipsize_path(
                row["display_name"], font_small, available_name_width,
            )
            surface.blit(font_small.render(display_name, True, (245, 245, 248)), (name_x, row_rect.y + 7))
            if row["source_missing"]:
                surface.blit(font_small.render("!", True, (248, 113, 113)), (row_rect.right - 18, row_rect.y + 7))
            controls.append({"rect": row_rect, "action": "select_actor", "value": row["key"], "enabled": True})
            register_tooltip(tooltip_regions, row_rect, "tooltip.selection.scene")
        else:
            selected = row["source_index"] == getattr(player, "cur_source_idx", -1)
            linked = row["source_index"] == summary["linked_source_index"]
            pygame.draw.rect(
                surface, (58, 67, 86) if selected else (43, 46, 56),
                row_rect, border_radius=4,
            )
            if linked:
                pygame.draw.rect(surface, (96, 165, 250), row_rect, 1, border_radius=4)
            filename = ellipsize_path(row["filename"], font_bold, row_rect.w - 20)
            surface.blit(font_bold.render(filename, True, (245, 245, 248)), (row_rect.x + 8, row_rect.y + 5))
            roles = " / ".join(row["roles"]) or "-"
            detail = (
                f"{roles} · PARTNER {row['partner_profiles']} / "
                f"NPC {row['npc_instances']} / PROP {row['prop_instances']} · "
                f"{tr('selection.parts_count', parts=row['parts'], particles=row['particles'])}"
            )
            detail = ellipsize_path(detail, font_small, row_rect.w - 16)
            surface.blit(font_small.render(detail, True, (166, 178, 198)), (row_rect.x + 8, row_rect.y + 29))
            controls.append({"rect": row_rect, "action": "select_resource", "value": row["source_index"], "enabled": True})
            register_tooltip(tooltip_regions, row_rect, "tooltip.selection.resources")
    surface.set_clip(None)

    if not rows:
        if tab == SIDEBAR_SCENE:
            empty_key = (
                "selection.empty_filter"
                if model["scene_rows"] else "selection.empty_scene"
            )
        else:
            empty_key = "selection.empty_resources"
        empty_lines = wrap_ui_text(tr(empty_key), font_small, viewport.w - 24)
        for index, line in enumerate(empty_lines[:3]):
            surface.blit(font_small.render(line, True, (145, 150, 162)), (viewport.x + 12, viewport.y + 14 + index * 18))

    if tab == SIDEBAR_SCENE:
        selected_key = getattr(player, "selected_scene_actor_key", None)
        selected_actor = next(
            (
                row for row in model["scene_rows"]
                if row["key"] == selected_key
            ),
            None,
        )
        selected_visible = bool(
            selected_actor
            and any(row["key"] == selected_actor["key"] for row in rows)
        )
        can_delete_corpse = bool(
            selected_visible
            and selected_actor["kind"] == "npc"
            and selected_actor.get("is_corpse")
        )
        can_despawn = bool(
            selected_visible
            and selected_actor["kind"] == "npc"
            and not selected_actor.get("is_corpse")
        )
        can_delete_all = any(
            row["kind"] == "npc" and row.get("is_corpse")
            for row in model["scene_rows"]
        )
        can_focus = selected_actor is not None
        status_text = str(getattr(player, "scene_status_message", "") or "")
        if status_text:
            status_text = ellipsize_path(status_text, font_small, panel.w - 24)
            surface.blit(
                font_small.render(status_text, True, (176, 186, 204)),
                (panel.x + 12, panel.bottom - 94),
            )
        scene_actions = (
            (
                "focus_selected", "selection.focus_selected",
                "tooltip.selection.focus_selected", can_focus, (58, 105, 168),
            ),
            (
                "despawn_selected", "selection.despawn",
                "tooltip.selection.despawn", can_despawn, (190, 98, 38),
            ),
            (
                "delete_corpse", "selection.delete_corpse",
                "tooltip.selection.delete_corpse", can_delete_corpse, (174, 48, 48),
            ),
            (
                "delete_all_corpses", "selection.delete_all_corpses",
                "tooltip.selection.delete_all_corpses", can_delete_all, (145, 52, 52),
            ),
        )
        action_gap = 5
        action_width = (panel.w - 24 - action_gap) // 2
        for index, (action, label_key, tooltip_key, enabled, active_color) in enumerate(scene_actions):
            action_rect = pygame.Rect(
                panel.x + 12 + (index % 2) * (action_width + action_gap),
                panel.bottom - 70 + (index // 2) * 32,
                action_width,
                28,
            )
            pygame.draw.rect(
                surface, active_color if enabled else (55, 57, 63),
                action_rect, border_radius=4,
            )
            draw_centered_label(
                surface, font_small, tr(label_key), action_rect,
                (255, 255, 255) if enabled else (125, 128, 136),
            )
            register_tooltip(tooltip_regions, action_rect, tooltip_key)
            controls.append({
                "rect": action_rect,
                "action": action,
                "value": None,
                "enabled": enabled,
            })

    if tab == SIDEBAR_RESOURCES and rows:
        selected_row = next(
            (row for row in rows if row["source_index"] == getattr(player, "cur_source_idx", -1)),
            rows[0],
        )
        status_text = str(getattr(player, "resource_status_message", "") or "")
        if status_text:
            status_text = ellipsize_path(status_text, font_small, panel.w - 24)
            surface.blit(
                font_small.render(status_text, True, (176, 186, 204)),
                (panel.x + 12, panel.bottom - 130),
            )
        action_specs = [
            ("assign_player", "selection.assign_player", selected_row["can_assign_player"]),
            ("add_partner", "selection.add_partner", selected_row["can_add_partner"]),
            ("add_npc", "selection.add_npc", selected_row["can_add_npc"]),
            ("add_prop", "selection.add_prop", selected_row["can_add_prop"]),
            ("refresh", "selection.refresh", True),
            ("remove", "selection.remove", True),
            ("export_png", "selection.export_png", selected_row["can_export_png"]),
        ]
        button_width = (panel.w - 34) // 3
        for index, (action, label_key, enabled) in enumerate(action_specs):
            rect = pygame.Rect(
                panel.x + 12 + (index % 3) * (button_width + 5),
                panel.bottom - 106 + (index // 3) * 34,
                button_width, 28,
            )
            pygame.draw.rect(
                surface, (58, 105, 168) if enabled else (55, 57, 63),
                rect, border_radius=4,
            )
            draw_centered_label(
                surface, font_small, tr(label_key), rect,
                (245, 245, 248) if enabled else (125, 128, 136),
            )
            tooltip_key = f"tooltip.resource.{action}"
            register_tooltip(tooltip_regions, rect, tooltip_key)
            controls.append({
                "rect": rect,
                "action": action,
                "value": selected_row["source_index"],
                "enabled": enabled,
            })
    return {
        "controls": controls,
        "scroll_offset": scroll_offset,
        "maximum_scroll": maximum_scroll,
        "visible_rows": end - start,
        "total_rows": len(rows),
        "viewport": viewport,
    }


def _role_profile_for_source(player, source_index, role):
    return next(
        (
            profile for profile_index, profile in enumerate(player.profiles)
            if getattr(profile, "source_idx", -1) == source_index
            and profile_kind(profile, profile_index) == role
        ),
        None,
    )


def _create_role_profile(player, source_index, role):
    prefix = {
        "partner": "PARTNER", "npc": "NPC", "prop": "PROP",
    }.get(role, role.upper())
    profile = AseProfile(
        f"{prefix}_{len(player.profiles)}", source_index, kind=role,
    )
    profile.is_prop_profile = role == "prop"
    player.profiles.append(profile)
    player.auto_map_profile(profile)
    if not any(
        profile_kind(candidate, index) == "player"
        for index, candidate in enumerate(player.profiles)
    ):
        player.visible = False
    return profile


def partner_roster_profiles(player):
    """Return standby swap profiles and absorb v0.5.5 runtime partner actors."""
    profiles = []
    known_profiles = list(getattr(player, "profiles", []))
    for profile_index, profile in enumerate(known_profiles):
        if profile_index > 0 and profile_kind(profile, profile_index) == "partner":
            profiles.append(profile)
    for profile in getattr(player, "partner_profiles", []):
        if profile in known_profiles and profile not in profiles:
            profiles.append(profile)
    for legacy_actor in getattr(player, "partner_list", []):
        profile = getattr(legacy_actor, "profile", None)
        if profile in known_profiles and profile not in profiles:
            profile.kind = "partner"
            profile.is_prop_profile = False
            profiles.append(profile)
    player.partner_profiles = profiles
    # v0.5.5 kept AseAI objects here. They are roster data now, never actors.
    player.partner_list = []
    return profiles


def swap_candidate_profile_indices(player, include_legacy=True):
    partner_roster_profiles(player)
    partners = [
        index for index, profile in enumerate(getattr(player, "profiles", []))
        if index > 0 and profile_kind(profile, index) == "partner"
    ]
    if partners or not include_legacy:
        return partners
    return [
        index for index, profile in enumerate(getattr(player, "profiles", []))
        if index > 0 and profile_kind(profile, index) != "prop"
    ]


def assign_resource_role(player, source_index, role):
    if (
        player is None
        or not isinstance(source_index, int)
        or not 0 <= source_index < len(getattr(player, "sources", []))
    ):
        if player is not None:
            player.resource_status_message = tr("selection.no_resource_selected")
        return {
            "assigned": False, "role": role, "profile": None, "instance": None,
        }
    if role not in {"player", "partner", "npc", "prop"}:
        return {
            "assigned": False, "role": role, "profile": None, "instance": None,
        }

    result = {"assigned": False, "role": role, "profile": None, "instance": None}

    def mutate_role():
        if role == "player":
            player_entry = next(
                (
                    (index, profile)
                    for index, profile in enumerate(player.profiles)
                    if profile_kind(profile, index) == "player"
                ),
                None,
            )
            if player_entry is not None:
                player_index, profile = player_entry
                if player_index != 0:
                    player.profiles.pop(player_index)
                    player.profiles.insert(0, profile)
                    if getattr(player, "swap_target_idx", -1) < player_index:
                        player.swap_target_idx += 1
                    if getattr(player, "roaming_npc_idx", -1) < player_index:
                        player.roaming_npc_idx += 1
                profile.source_idx = source_index
                profile.kind = "player"
                profile.is_prop_profile = False
            else:
                profile = AseProfile("PLAYER", source_index, kind="player")
                player.profiles.insert(0, profile)
                if hasattr(player, "swap_target_idx"):
                    player.swap_target_idx += 1
                if hasattr(player, "roaming_npc_idx"):
                    player.roaming_npc_idx += 1
            player.auto_map_profile(profile)
            player.visible = True
            player.cur_profile_idx = 0
            player.cur_source_idx = source_index
            result.update(
                assigned=True, profile=profile, instance=player,
            )
            return

        profile = _role_profile_for_source(player, source_index, role)
        if profile is None:
            profile = _create_role_profile(player, source_index, role)
        profile_index = player.profiles.index(profile)
        if role == "partner":
            roster = partner_roster_profiles(player)
            if profile not in roster:
                roster.append(profile)
            player.partner_profiles = roster
            instance = None
            candidates = swap_candidate_profile_indices(player, include_legacy=False)
            if getattr(player, "swap_target_idx", -1) not in candidates:
                player.swap_target_idx = profile_index
        elif role == "npc":
            instance = player.spawn_npc_profile(profile_index, increase_target=True)
        else:
            instance = AseAI(player, profile, is_prop=True, hp=3)
            player.prop_list.append(instance)
        result.update(
            assigned=(role == "partner" or instance is not None),
            profile=profile,
            instance=instance,
        )

    run_scene_preserving_mutation(player, mutate_role)
    status_key = {
        "player": "selection.assigned_player",
        "partner": "selection.added_partner",
        "npc": "selection.added_npc",
        "prop": "selection.added_prop",
    }[role]
    if result["assigned"]:
        player.resource_status_message = tr(status_key)
    return result


def activate_resource_action(player, action, source_index):
    if not 0 <= source_index < len(player.sources):
        return False
    source = player.sources[source_index]
    linked = [
        (index, profile)
        for index, profile in enumerate(player.profiles)
        if getattr(profile, "source_idx", -1) == source_index
    ]
    role_actions = {
        "assign_player": "player",
        "add_partner": "partner",
        "add_npc": "npc",
        "add_prop": "prop",
    }
    if action in role_actions:
        return bool(
            assign_resource_role(player, source_index, role_actions[action])["assigned"]
        )
    if action == "use_player":
        player_profile = next(
            ((index, profile) for index, profile in linked if profile_kind(profile, index) == "player"),
            None,
        )
        return select_scene_actor(player, ("player", id(player))) if player_profile else False
    if action == "spawn_npc":
        profile_entry = next(
            ((index, profile) for index, profile in linked if profile_kind(profile, index) == "npc"),
            None,
        )
        return bool(
            profile_entry
            and run_scene_preserving_mutation(
                player, lambda: player.spawn_npc_profile(profile_entry[0]),
            )
        )
    if action == "place_prop":
        profile_entry = next(
            ((index, profile) for index, profile in linked if profile_kind(profile, index) == "prop"),
            None,
        )
        if not profile_entry:
            return False
        run_scene_preserving_mutation(
            player,
            lambda: player.prop_list.append(
                AseAI(player, profile_entry[1], is_prop=True, hp=3),
            ),
        )
        return True
    if action == "refresh":
        def refresh_source():
            refreshed_result = source.export_and_load()
            if refreshed_result:
                for _, profile in linked:
                    player.auto_map_profile(profile)
            return refreshed_result
        refreshed = run_scene_preserving_mutation(player, refresh_source)
        return bool(refreshed)
    if action == "remove":
        def remove_confirmed(index=source_index):
            show_source_removal_result(player.remove_source_by_index(index))
        player.popup = {"msg": tr("selection.remove_confirm"), "cb": remove_confirmed}
        return True
    if action == "export_png":
        return begin_slice_export(player, source, "Source")
    return False


def refresh_all_sources_preserving_scene(player):
    def refresh_all_sources():
        reload_results = [
            source.export_and_load() for source in getattr(player, "sources", [])
        ]
        reload_ok = all(reload_results)
        if reload_ok:
            for profile in getattr(player, "profiles", []):
                player.auto_map_profile(profile)
        return reload_ok

    reload_ok = bool(run_scene_preserving_mutation(player, refresh_all_sources))
    if reload_ok:
        for source in getattr(player, "sources", []):
            source.clear_cache()
    return reload_ok


PARALLAX_GIZMO_SIZE = 18
PARALLAX_AXIS_HANDLE_SIZE = 18
PARALLAX_AXIS_HANDLE_OFFSET = 34
PARALLAX_HISTORY_LIMIT = 100


def selected_parallax_layer(player):
    layers = getattr(player, "bg_layers", None)
    index = getattr(player, "active_bg_layer", -1)
    if not isinstance(layers, list) or not isinstance(index, int):
        return None
    if index < 0 or index >= len(layers):
        return None
    layer = layers[index]
    if not isinstance(layer, dict):
        return None
    if layer.get("visible", True) is False or layer.get("enabled", True) is False:
        return None
    return layer


def get_parallax_layer_offset(layer):
    if not isinstance(layer, dict):
        return 0.0, 0.0
    return (
        _finite_number(layer.get("off_x", 0.0), 0.0),
        _finite_number(layer.get("off_y", 0.0), 0.0),
    )


def set_parallax_layer_offset(layer, x, y):
    if not isinstance(layer, dict):
        return False
    layer["off_x"] = _finite_number(x, 0.0)
    layer["off_y"] = _finite_number(y, 0.0)
    layer["needs_update"] = True
    return True


def parallax_offsets_equal(first, second):
    return (
        abs(first[0] - second[0]) < 0.0001
        and abs(first[1] - second[1]) < 0.0001
    )


def ensure_parallax_history_state(player):
    if not isinstance(getattr(player, "parallax_offset_history", None), list):
        player.parallax_offset_history = []
    if not isinstance(getattr(player, "parallax_offset_redo_stack", None), list):
        player.parallax_offset_redo_stack = []
    if not hasattr(player, "parallax_offset_edit"):
        player.parallax_offset_edit = None


def resolve_parallax_history_layer(player, command):
    layers = getattr(player, "bg_layers", [])
    layer_ref = command.get("layer_ref") if isinstance(command, dict) else None
    if not isinstance(layers, list) or not isinstance(layer_ref, dict):
        return None
    return next((layer for layer in layers if layer is layer_ref), None)


def push_parallax_offset_history(player, layer, before, after, reason):
    if not isinstance(layer, dict) or parallax_offsets_equal(before, after):
        return False
    ensure_parallax_history_state(player)
    command = {
        "layer_ref": layer,
        "layer_index": next(
            (index for index, candidate in enumerate(player.bg_layers)
             if candidate is layer),
            -1,
        ),
        "path": layer.get("path", ""),
        "before": tuple(before),
        "after": tuple(after),
        "reason": str(reason),
    }
    player.parallax_offset_history.append(command)
    del player.parallax_offset_history[:-PARALLAX_HISTORY_LIMIT]
    player.parallax_offset_redo_stack.clear()
    player.parallax_history_status_key = ""
    return True


def begin_parallax_offset_edit(player, layer, reason):
    if not isinstance(layer, dict):
        return False
    ensure_parallax_history_state(player)
    current = player.parallax_offset_edit
    if current and current.get("layer_ref") is layer:
        return True
    if current:
        commit_parallax_offset_edit(player)
    player.parallax_offset_edit = {
        "layer_ref": layer,
        "before": get_parallax_layer_offset(layer),
        "reason": str(reason),
    }
    return True


def commit_parallax_offset_edit(player):
    ensure_parallax_history_state(player)
    edit = player.parallax_offset_edit
    player.parallax_offset_edit = None
    if not isinstance(edit, dict):
        return False
    layer = edit.get("layer_ref")
    if not any(candidate is layer for candidate in getattr(player, "bg_layers", [])):
        return False
    return push_parallax_offset_history(
        player,
        layer,
        edit["before"],
        get_parallax_layer_offset(layer),
        edit["reason"],
    )


def cancel_parallax_offset_edit(player, restore=False):
    ensure_parallax_history_state(player)
    edit = player.parallax_offset_edit
    player.parallax_offset_edit = None
    if not isinstance(edit, dict):
        return False
    layer = edit.get("layer_ref")
    if restore and any(candidate is layer for candidate in getattr(player, "bg_layers", [])):
        set_parallax_layer_offset(layer, *edit["before"])
    return True


def undo_parallax_offset(player):
    ensure_parallax_history_state(player)
    while player.parallax_offset_history:
        command = player.parallax_offset_history.pop()
        layer = resolve_parallax_history_layer(player, command)
        if layer is None:
            continue
        set_parallax_layer_offset(layer, *command["before"])
        player.parallax_offset_redo_stack.append(command)
        player.parallax_history_status_key = "status.parallax_undo"
        return True
    player.parallax_history_status_key = "status.parallax_nothing_undo"
    return False


def redo_parallax_offset(player):
    ensure_parallax_history_state(player)
    while player.parallax_offset_redo_stack:
        command = player.parallax_offset_redo_stack.pop()
        layer = resolve_parallax_history_layer(player, command)
        if layer is None:
            continue
        set_parallax_layer_offset(layer, *command["after"])
        player.parallax_offset_history.append(command)
        del player.parallax_offset_history[:-PARALLAX_HISTORY_LIMIT]
        player.parallax_history_status_key = "status.parallax_redo"
        return True
    player.parallax_history_status_key = "status.parallax_nothing_redo"
    return False


def handle_parallax_history_shortcut(player, key, modifiers):
    if not modifiers & pygame.KMOD_CTRL:
        return None
    is_redo = key == pygame.K_y or (
        key == pygame.K_z and modifiers & pygame.KMOD_SHIFT
    )
    is_undo = key == pygame.K_z and not modifiers & pygame.KMOD_SHIFT
    if not is_redo and not is_undo:
        return None
    end_parallax_gizmo_drag(player)
    commit_parallax_offset_edit(player)
    if is_redo:
        return "redo", redo_parallax_offset(player)
    if is_undo:
        return "undo", undo_parallax_offset(player)


def parallax_offset_delta_from_screen(dx, dy, zoom):
    safe_zoom = abs(_finite_number(zoom, 1.0))
    if safe_zoom < 0.001:
        safe_zoom = 1.0
    return dx / safe_zoom, dy / safe_zoom


def parallax_layer_origin_screen(player, layer, play_w, play_h):
    if not isinstance(layer, dict):
        return None
    zoom = _finite_number(getattr(player, "zoom", 1.0), 1.0)
    parallax = _finite_number(layer.get("parallax", 1.0), 1.0)
    off_x, off_y = get_parallax_layer_offset(layer)
    cx, cy = play_w / 2.0, play_h / 2.0
    x = (
        cx
        + (_finite_number(getattr(player, "spawn_x", 0.0), 0.0)
           - _finite_number(getattr(player, "cam_x", 0.0), 0.0))
        * parallax * zoom
        + off_x * zoom
    )
    y = (
        cy
        + (_finite_number(getattr(player, "spawn_y", 0.0), 0.0)
           - _finite_number(getattr(player, "cam_y", 0.0), 0.0))
        * parallax * zoom
        + off_y * zoom
    )
    return int(round(x)), int(round(y))


def parallax_gizmo_handle_rects(player, play_w, play_h):
    if not getattr(player, "parallax_gizmo_enabled", False):
        return {}
    layer = selected_parallax_layer(player)
    if layer is None or not (layer.get("img") or layer.get("cached_bg")):
        return {}
    origin = parallax_layer_origin_screen(player, layer, play_w, play_h)
    if origin is None:
        return {}
    free_rect = pygame.Rect(0, 0, PARALLAX_GIZMO_SIZE, PARALLAX_GIZMO_SIZE)
    free_rect.center = origin
    x_rect = pygame.Rect(0, 0, PARALLAX_AXIS_HANDLE_SIZE, PARALLAX_AXIS_HANDLE_SIZE)
    x_rect.center = (origin[0] + PARALLAX_AXIS_HANDLE_OFFSET, origin[1])
    y_rect = pygame.Rect(0, 0, PARALLAX_AXIS_HANDLE_SIZE, PARALLAX_AXIS_HANDLE_SIZE)
    y_rect.center = (origin[0], origin[1] + PARALLAX_AXIS_HANDLE_OFFSET)
    viewport = pygame.Rect(0, TOP_UI_HEIGHT, max(0, play_w), max(0, play_h))
    if not viewport.contains(free_rect):
        return {}
    return {
        axis: rect
        for axis, rect in (("free", free_rect), ("x", x_rect), ("y", y_rect))
        if viewport.contains(rect)
    }


def build_parallax_gizmo_rect(player, play_w, play_h):
    return parallax_gizmo_handle_rects(player, play_w, play_h).get("free")


def parallax_gizmo_hit_axis(player, mouse_pos, play_w, play_h):
    handles = parallax_gizmo_handle_rects(player, play_w, play_h)
    return next(
        (axis for axis in ("x", "y", "free")
         if axis in handles and handles[axis].collidepoint(mouse_pos)),
        None,
    )


def set_parallax_gizmo_enabled(player, enabled):
    player.parallax_gizmo_enabled = bool(enabled)
    if not player.parallax_gizmo_enabled:
        cancel_parallax_gizmo_drag(player, restore=True)
    return player.parallax_gizmo_enabled


def begin_parallax_gizmo_drag(player, mouse_pos, play_w, play_h):
    axis = parallax_gizmo_hit_axis(player, mouse_pos, play_w, play_h)
    layer = selected_parallax_layer(player)
    if axis is None or layer is None:
        return False
    player.parallax_gizmo_dragging = True
    player.parallax_gizmo_drag_layer = getattr(player, "active_bg_layer", -1)
    player.parallax_gizmo_drag_layer_ref = layer
    player.parallax_gizmo_drag_axis = axis
    player.parallax_gizmo_drag_start = tuple(mouse_pos)
    player.parallax_gizmo_drag_before = get_parallax_layer_offset(layer)
    player.parallax_gizmo_drag_dirty = False
    return True


def update_parallax_gizmo_drag(player, mouse_pos, shift_pressed=False):
    if not getattr(player, "parallax_gizmo_dragging", False):
        return False
    if not getattr(player, "parallax_gizmo_enabled", False):
        cancel_parallax_gizmo_drag(player, restore=True)
        return True
    layer = getattr(player, "parallax_gizmo_drag_layer_ref", None)
    if not any(candidate is layer for candidate in getattr(player, "bg_layers", [])):
        cancel_parallax_gizmo_drag(player, restore=True)
        return True
    if layer is not selected_parallax_layer(player):
        cancel_parallax_gizmo_drag(player, restore=True)
        return True
    start_pos = getattr(player, "parallax_gizmo_drag_start", None)
    before = getattr(player, "parallax_gizmo_drag_before", None)
    if start_pos is None or before is None:
        cancel_parallax_gizmo_drag(player, restore=True)
        return True
    dx, dy = mouse_pos[0] - start_pos[0], mouse_pos[1] - start_pos[1]
    delta_x, delta_y = parallax_offset_delta_from_screen(dx, dy, getattr(player, "zoom", 1.0))
    axis = getattr(player, "parallax_gizmo_drag_axis", "free")
    effective_axis = axis
    if axis == "free" and shift_pressed:
        effective_axis = "x" if abs(dx) >= abs(dy) else "y"
    target_x = before[0] + (delta_x if effective_axis in {"free", "x"} else 0.0)
    target_y = before[1] + (delta_y if effective_axis in {"free", "y"} else 0.0)
    if not set_parallax_layer_offset(layer, target_x, target_y):
        return False
    player.parallax_gizmo_drag_dirty = not parallax_offsets_equal(
        before, get_parallax_layer_offset(layer),
    )
    return True


def end_parallax_gizmo_drag(player):
    was_dragging = bool(getattr(player, "parallax_gizmo_dragging", False))
    layer = getattr(player, "parallax_gizmo_drag_layer_ref", None)
    before = getattr(player, "parallax_gizmo_drag_before", None)
    axis = getattr(player, "parallax_gizmo_drag_axis", "free")
    changed = (
        was_dragging
        and isinstance(layer, dict)
        and before is not None
        and any(candidate is layer for candidate in getattr(player, "bg_layers", []))
        and push_parallax_offset_history(
            player, layer, before, get_parallax_layer_offset(layer),
            f"gizmo_{axis}_drag",
        )
    )
    player.parallax_gizmo_dragging = False
    player.parallax_gizmo_drag_layer = None
    player.parallax_gizmo_drag_layer_ref = None
    player.parallax_gizmo_drag_axis = None
    player.parallax_gizmo_drag_start = None
    player.parallax_gizmo_drag_before = None
    player.parallax_gizmo_drag_dirty = False
    return bool(changed)


def cancel_parallax_gizmo_drag(player, restore=False):
    if not getattr(player, "parallax_gizmo_dragging", False):
        return False
    layer = getattr(player, "parallax_gizmo_drag_layer_ref", None)
    before = getattr(player, "parallax_gizmo_drag_before", None)
    if (
        restore
        and isinstance(layer, dict)
        and before is not None
        and any(candidate is layer for candidate in getattr(player, "bg_layers", []))
    ):
        set_parallax_layer_offset(layer, *before)
    player.parallax_gizmo_dragging = False
    player.parallax_gizmo_drag_layer = None
    player.parallax_gizmo_drag_layer_ref = None
    player.parallax_gizmo_drag_axis = None
    player.parallax_gizmo_drag_start = None
    player.parallax_gizmo_drag_before = None
    player.parallax_gizmo_drag_dirty = False
    return True


def draw_parallax_offset_gizmo(surface, player, play_w, play_h, font=None):
    handles = parallax_gizmo_handle_rects(player, play_w, play_h)
    rect = handles.get("free")
    if rect is None:
        return None
    center = rect.center
    pygame.draw.rect(surface, (245, 158, 11), rect, 3, border_radius=3)
    if "x" in handles:
        pygame.draw.line(surface, (239, 68, 68), center, handles["x"].center, 3)
        pygame.draw.rect(surface, (239, 68, 68), handles["x"], 2, border_radius=4)
        if font is not None:
            draw_centered_label(surface, font, "X", handles["x"], (255,255,255))
    if "y" in handles:
        pygame.draw.line(surface, (34, 197, 94), center, handles["y"].center, 3)
        pygame.draw.rect(surface, (34, 197, 94), handles["y"], 2, border_radius=4)
        if font is not None:
            draw_centered_label(surface, font, "Y", handles["y"], (255,255,255))
    if font is not None:
        label = font.render(tr("ui.parallax_gizmo"), True, (255, 220, 140))
        rightmost = max(handle.right for handle in handles.values())
        label_pos = (min(play_w - label.get_width() - 4, rightmost + 6), rect.top - 1)
        surface.blit(label, label_pos)
    return rect


def npc_profile_entries(player):
    return [
        (index, profile)
        for index, profile in enumerate(getattr(player, "profiles", []))
        if profile_kind(profile, index) == "npc"
    ]


def replay_npc_intro(player):
    """Replay Intro without spawning, moving, or changing any roster membership."""
    result = {"status_key": "status.npc_intro_no_target", "count": 0}
    if player is None:
        return result

    selected_key = getattr(player, "selected_scene_actor_key", None)
    selected_row = next(
        (
            row for row in build_scene_actor_rows(player)
            if row["key"] == selected_key and row["kind"] == "npc"
        ),
        None,
    )
    if selected_row is not None:
        npc = selected_row["entity"]
        if _is_npc_attack_locked(npc):
            result["status_key"] = "status.npc_intro_attack_locked"
        elif _is_intro_locked(npc):
            result["status_key"] = "status.npc_intro_already_playing"
        elif not getattr(getattr(npc, "profile", None), "mappings", {}).get("INTRO"):
            result["status_key"] = "status.npc_intro_missing"
        elif not bool(getattr(npc, "is_dead", False)) and not bool(getattr(npc, "is_corpse", False)):
            before_position = (getattr(npc, "x", None), getattr(npc, "y", None))
            if npc.trigger_action("INTRO"):
                _start_intro_lock(npc)
                npc.x, npc.y = before_position
                result = {"status_key": "status.npc_intro_selected", "count": 1}
        player.npc_intro_replay_status = tr(
            result["status_key"], count=result["count"],
        )
        return result

    profile_index = getattr(player, "cur_profile_idx", -1)
    profiles = getattr(player, "profiles", [])
    if not 0 <= profile_index < len(profiles):
        player.npc_intro_replay_status = tr(result["status_key"])
        return result
    profile = profiles[profile_index]
    if profile_kind(profile, profile_index) != "npc":
        player.npc_intro_replay_status = tr(result["status_key"])
        return result
    if not getattr(profile, "mappings", {}).get("INTRO"):
        result["status_key"] = "status.npc_intro_missing"
        player.npc_intro_replay_status = tr(result["status_key"])
        return result

    live_targets = [
        npc for npc in getattr(player, "ai_list", [])
        if getattr(npc, "profile", None) is profile
        and not bool(getattr(npc, "is_dead", False))
        and not bool(getattr(npc, "is_corpse", False))
    ]
    unlocked_targets = [
        npc for npc in live_targets
        if not _is_npc_attack_locked(npc) and not _is_intro_locked(npc)
    ]
    if live_targets and not unlocked_targets:
        result["status_key"] = (
            "status.npc_intro_attack_locked"
            if any(_is_npc_attack_locked(npc) for npc in live_targets)
            else "status.npc_intro_already_playing"
        )
    elif unlocked_targets:
        for npc in unlocked_targets:
            before_position = (getattr(npc, "x", None), getattr(npc, "y", None))
            if npc.trigger_action("INTRO"):
                _start_intro_lock(npc)
                npc.x, npc.y = before_position
                result["count"] += 1
        if result["count"]:
            result["status_key"] = "status.npc_intro_profile"
    player.npc_intro_replay_status = tr(
        result["status_key"], count=result["count"],
    )
    return result


def ai_combat_content_height(player):
    profile_count = len(getattr(player, "profiles", []))
    existing_height = 245 + max(0, ((profile_count - 2) // 4) * 30) * 2
    npc_count = len(npc_profile_entries(player))
    return existing_height + 100 + npc_count * 32 + (22 if npc_count == 0 else 0)


def settings_content_height(player, folds, section=None):
    section = normalize_settings_section(section) if section is not None else None
    categories = (
        settings_section_model(section)["categories"]
        if section is not None
        else tuple(folds.keys())
    )
    height = (
        settings_section_intro_height(section)
        if section is not None
        else 10
    )
    sources = getattr(player, "sources", [])
    profiles = getattr(player, "profiles", [])
    backgrounds = getattr(player, "bg_layers", [])
    for category in categories:
        opened = bool(folds.get(category, True))
        height += 35
        if not opened:
            continue
        if category == "LANGUAGE":
            height += 45
        elif category == "PROPS":
            height += len([source for source in sources if getattr(source, "is_prop_source", False)]) * 35 + 10
        elif category == "NPCS":
            height += len([
                profile for index, profile in enumerate(profiles)
                if profile_kind(profile, index) == "npc"
            ]) * 35 + NPC_SLICE_STATUS_PANEL_HEIGHT
        elif category == "PHYSICS":
            height += 185
        elif category == "AI & COMBAT":
            height += ai_combat_content_height(player)
        elif category == "JUICE & VFX":
            height += 195
        elif category == "LAYERS":
            height += (layer_list_height(len(sources[min(getattr(player, "cur_source_idx", 0), len(sources)-1)].layers)) if sources else 55) + 20
        elif category == "CAMERA":
            height += 85
        elif category == "BG IMAGE":
            active = valid_background_layer_index(player)
            height += 85 + 25 + max(1, ((len(backgrounds)-1)//5 + 1)) * 30 + 10 + (270 if active >= 0 else 35)
        elif category == "BG COLOR":
            height += 170
        elif category == "CONTROLS":
            height += max(1, len(getattr(player, "key_map", {}) or {})) * 30 + 34
    return max(60, height)


def draw_resource_required_notice(surface, font, rect):
    panel = pygame.Rect(rect)
    pygame.draw.rect(surface, (42, 44, 52), panel, border_radius=5)
    lines = wrap_ui_text(tr("ui.no_resource"), font, panel.w - 20)
    line_height = max(16, measure_ui_text("가Ag", font)[1] + 3)
    for index, line in enumerate(lines[:2]):
        surface.blit(font.render(line, True, (155, 160, 172)), (panel.x + 10, panel.y + 8 + index * line_height))
    return panel


def sidebar_action_rects(sidebar_width, y, font):
    export_width = calculate_button_width(tr("common.save"), font, 45, horizontal_padding=9, maximum_width=70)
    spawn_width = calculate_button_width(tr("common.spawn"), font, 50, horizontal_padding=9, maximum_width=75)
    export_rect = pygame.Rect(sidebar_width - export_width - 10, int(y), export_width, 24)
    spawn_rect = pygame.Rect(export_rect.x - spawn_width - 5, int(y), spawn_width, 24)
    return spawn_rect, export_rect


def wrap_ui_text(text, font, max_width):
    if not text:
        return [""]
    max_width = max(1, int(max_width))
    cache_key = ("wrap", id(font), str(text), max_width)
    cached = _UI_LAYOUT_CACHE.get(cache_key)
    if cached is not None:
        return list(cached)
    wrapped = []
    for paragraph in str(text).splitlines():
        if not paragraph:
            wrapped.append("")
            continue
        current = ""
        for word in paragraph.split(" "):
            candidate = word if not current else f"{current} {word}"
            if measure_ui_text(candidate, font)[0] <= max_width:
                current = candidate
                continue
            if current:
                wrapped.append(current)
                current = ""
            if measure_ui_text(word, font)[0] <= max_width:
                current = word
                continue
            chunk = ""
            for character in word:
                candidate = f"{chunk}{character}"
                if chunk and measure_ui_text(candidate, font)[0] > max_width:
                    wrapped.append(chunk)
                    chunk = character
                else:
                    chunk = candidate
            current = chunk
        if current:
            wrapped.append(current)
    result = wrapped or [""]
    _UI_LAYOUT_CACHE.put(cache_key, tuple(result))
    return result


def ellipsize_path(path, font, max_width):
    text = str(path or "")
    cache_key = ("path", id(font), text, int(max_width))
    cached = _UI_LAYOUT_CACHE.get(cache_key)
    if cached is not None:
        return cached
    if measure_ui_text(text, font)[0] <= max_width:
        return _UI_LAYOUT_CACHE.put(cache_key, text)
    suffix = os.path.basename(text)
    prefix = f"...{os.sep}"
    while suffix and measure_ui_text(prefix + suffix, font)[0] > max_width:
        suffix = suffix[1:]
    return _UI_LAYOUT_CACHE.put(cache_key, prefix + suffix if suffix else "...")


def ellipsize_ui_text(text, font, max_width):
    value = str(text or "")
    cache_key = ("ellipsis", id(font), value, int(max_width))
    cached = _UI_LAYOUT_CACHE.get(cache_key)
    if cached is not None:
        return cached
    if measure_ui_text(value, font)[0] <= max_width:
        return _UI_LAYOUT_CACHE.put(cache_key, value)
    while value and measure_ui_text(f"{value}…", font)[0] > max_width:
        value = value[:-1]
    return _UI_LAYOUT_CACHE.put(cache_key, f"{value}…" if value else "…")


def calculate_tooltip_rect(mouse_pos, tooltip_size, screen_size, offset=(12, 16), margin=8):
    mouse_x, mouse_y = mouse_pos
    width, height = tooltip_size
    screen_width, screen_height = screen_size
    x = mouse_x + offset[0]
    y = mouse_y + offset[1]
    if x + width + margin > screen_width:
        x = mouse_x - width - offset[0]
    if y + height + margin > screen_height:
        y = mouse_y - height - offset[1]
    x = max(margin, min(x, screen_width - width - margin))
    y = max(margin, min(y, screen_height - height - margin))
    return pygame.Rect(int(x), int(y), int(width), int(height))


class TooltipController:
    def __init__(self, delay_ms=400):
        self.delay_ms = int(delay_ms)
        self.hovered_key = None
        self.hover_started_at = 0

    def reset(self):
        self.hovered_key = None
        self.hover_started_at = 0

    def update(self, regions, mouse_pos, now_ms, blocked=False):
        if blocked:
            self.reset()
            return None
        hovered_key = next(
            (key for rect, key in reversed(regions) if pygame.Rect(rect).collidepoint(mouse_pos)),
            None,
        )
        if hovered_key is None:
            self.reset()
            return None
        if hovered_key != self.hovered_key:
            self.hovered_key = hovered_key
            self.hover_started_at = int(now_ms)
            return None
        if int(now_ms) - self.hover_started_at < self.delay_ms:
            return None
        return hovered_key


def register_tooltip(regions, rect, translation_key):
    if translation_key:
        regions.append((pygame.Rect(rect), translation_key))


def render_tooltip(surface, font, text, mouse_pos, max_width=360, max_lines=4):
    lines = wrap_ui_text(text, font, max_width)
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        tail = lines[-1]
        while tail and measure_ui_text(f"{tail}…", font)[0] > max_width:
            tail = tail[:-1]
        lines[-1] = f"{tail}…"
    line_height = max(16, measure_ui_text("가Ag", font)[1] + 3)
    text_width = max((measure_ui_text(line, font)[0] for line in lines), default=0)
    box_size = (text_width + 20, line_height * len(lines) + 16)
    rect = calculate_tooltip_rect(mouse_pos, box_size, surface.get_size())
    pygame.draw.rect(surface, (24, 26, 32), rect, border_radius=6)
    pygame.draw.rect(surface, (118, 129, 151), rect, 1, border_radius=6)
    for index, line in enumerate(lines):
        surface.blit(font.render(line, True, (245, 245, 248)), (rect.x + 10, rect.y + 8 + index * line_height))
    return rect


def draw_centered_label(surface, font, text, rect, color=(255, 255, 255)):
    rendered = font.render(text, True, color)
    surface.blit(rendered, (
        rect.x + max(0, (rect.w - rendered.get_width()) // 2),
        rect.y + max(0, (rect.h - rendered.get_height()) // 2),
    ))


class AsePathManager:
    def __init__(self, config_path=None):
        self.config_path = config_path or os.path.join(APP_ROOT, "config.json")
        self.invalid_config_path = None
        self.invalid_path_warning_shown = False
        self.path = self.load_config()
        if self.path and not os.path.isfile(self.path):
            self.invalid_config_path = self.path
            log_debug(f"[ERROR] Configured Aseprite executable does not exist: {self.path}")
            self.path = None
        if not self.path:
            self.path = self.find_aseprite()
    def load_config(self):
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                return data.get("aseprite_path") if isinstance(data, dict) else None
            except (OSError, json.JSONDecodeError, AttributeError) as e:
                log_debug(f"[ERROR] Aseprite config load failed: {e}")
        return None
    def save_config(self, path):
        try:
            save_json(self.config_path, {"aseprite_path": path})
        except (OSError, TypeError, ValueError) as e:
            log_debug(f"[ERROR] Config save failed: {e}")
            show_user_error(tr("error.ase_path_save_title"), tr("error.ase_path_save", path=self.config_path), key=f"config-save:{self.config_path}:{type(e).__name__}")
    def find_aseprite(self):
        candidates = [r"C:\Program Files (x86)\Steam\steamapps\common\Aseprite\Aseprite.exe", r"C:\Program Files\Steam\steamapps\common\Aseprite\Aseprite.exe", r"C:\Program Files\Aseprite\Aseprite.exe", r"D:\SteamLibrary\steamapps\common\Aseprite\Aseprite.exe"]
        for c in candidates:
            if os.path.isfile(c): return c
        return None
    def get_path(self, allow_prompt=True):
        if self.path and os.path.isfile(self.path):
            if self.invalid_config_path and not self.invalid_path_warning_shown:
                self.invalid_path_warning_shown = True
                show_user_error("Aseprite path was updated", f"The configured Aseprite path no longer exists:\n{self.invalid_config_path}\n\nUsing the detected installation instead:\n{self.path}")
            return self.path
        self.path = self.find_aseprite()
        if self.path: return self.path
        if allow_prompt:
            root = tk.Tk(); root.withdraw(); root.attributes("-topmost", True)
            selected = filedialog.askopenfilename(title="Select Aseprite.exe", filetypes=[("Aseprite", "Aseprite.exe"), ("Executable", "*.exe")]); root.destroy()
            if selected and os.path.isfile(selected):
                self.path = selected; self.save_config(selected); return selected
        detail = f"Configured path: {self.invalid_config_path}" if self.invalid_config_path else "No configured or automatically detected executable."
        raise AsepriteError(f"Aseprite.exe could not be found. {detail} Select it when adding a source file.")

ase_manager = AsePathManager()


def run_aseprite(arguments, executable=None, expected_files=(), timeout=ASEPRITE_TIMEOUT_SECONDS):
    exe = executable or ase_manager.get_path()
    if not exe or not os.path.isfile(exe):
        raise AsepriteError(f"Aseprite executable does not exist: {exe or '(not configured)'}")
    startupinfo = None
    if os.name == "nt":
        startupinfo = subprocess.STARTUPINFO(); startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    command = [exe, *arguments]
    try:
        if os.name == "nt":
            with tempfile.TemporaryDirectory(prefix="aseprite_cli_appdata_") as cli_appdata:
                process_env = os.environ.copy(); process_env["APPDATA"] = cli_appdata
                result = subprocess.run(command, capture_output=True, text=True, startupinfo=startupinfo, timeout=timeout, env=process_env)
        else:
            result = subprocess.run(command, capture_output=True, text=True, startupinfo=startupinfo, timeout=timeout)
    except subprocess.TimeoutExpired as e:
        log_debug(f"[ERROR] Aseprite timed out after {timeout}s: {command}")
        raise AsepriteError(f"Aseprite did not finish within {timeout} seconds. Try a smaller file or check Aseprite.") from e
    except OSError as e:
        log_debug(f"[ERROR] Aseprite process start failed: {e}")
        raise AsepriteError(f"Aseprite could not be started: {os.path.basename(exe)}") from e
    if result.returncode != 0:
        detail = (result.stderr or result.stdout or "No process output").strip()
        log_debug(f"[ERROR] Aseprite exited with code {result.returncode}: {detail}")
        raise AsepriteError(f"Aseprite failed with exit code {result.returncode}. Check ase_debug.log for details.")
    missing = [path for path in expected_files if not os.path.isfile(path)]
    if missing:
        log_debug(f"[ERROR] Aseprite did not create expected files: {missing}")
        raise AsepriteError(f"Aseprite finished but did not create {', '.join(os.path.basename(p) for p in missing)}.")
    return result


def export_aseprite(source_path, png_path, json_path, visible_layers=None, executable=None, layer_visibility=None, inventory_path=None):
    if not os.path.isfile(source_path):
        raise AsepriteError(f"Source file does not exist: {source_path}")
    arguments = ["-b", source_path]
    for layer in visible_layers or []:
        arguments.extend(["--layer", layer])
    script_path = None
    if inventory_path:
        fd, script_path = tempfile.mkstemp(prefix="ase_viewer_layers_", suffix=".lua")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as script_file:
                script_file.write(
                    "local sprite = app.activeSprite\n"
                    "if sprite then\n"
                    "  local inventory = {}\n"
                    "  local flat = {}\n"
                    "  local function visit(layers, parentPath, depth)\n"
                    "    for _, layer in ipairs(layers) do\n"
                    "      local path = parentPath == '' and layer.name or (parentPath .. '/' .. layer.name)\n"
                    "      local uuid = layer.uuid and tostring(layer.uuid) or ''\n"
                    "      local entry = {\n"
                    "        uuid=uuid, name=layer.name, path=path, depth=depth,\n"
                    "        stackIndex=layer.stackIndex, visible=layer.isVisible,\n"
                    "        isGroup=layer.isGroup, isImage=layer.isImage,\n"
                    "        isTilemap=layer.isTilemap, isReference=layer.isReference\n"
                    "      }\n"
                    "      table.insert(inventory, entry)\n"
                    "      table.insert(flat, { layer=layer, uuid=uuid, path=path })\n"
                    "      if layer.isGroup then visit(layer.layers, path, depth + 1) end\n"
                    "    end\n"
                    "  end\n"
                    "  visit(sprite.layers, '', 0)\n"
                    "  local choices = json.decode(app.params['layer_visibility'] or '{}')\n"
                    "  for index, item in ipairs(flat) do\n"
                    "    local fallbackKey = 'stack:' .. (index - 1) .. ':' .. item.path\n"
                    "    local key = item.uuid ~= '' and ('uuid:' .. item.uuid) or fallbackKey\n"
                    "    local desired = choices[key]\n"
                    "    if desired == nil then desired = choices[fallbackKey] end\n"
                    "    if desired ~= nil then item.layer.isVisible = desired end\n"
                    "    inventory[index].appliedVisible = item.layer.isVisible\n"
                    "  end\n"
                    "  local output = assert(io.open(app.params['layer_inventory'], 'w'))\n"
                    "  output:write(json.encode(inventory))\n"
                    "  output:close()\n"
                    "  app.command.ExportSpriteSheet {\n"
                    "    ui=false, recent=false, askOverwrite=false,\n"
                    "    type=SpriteSheetType.HORIZONTAL,\n"
                    "    textureFilename=app.params['sheet_output'],\n"
                    "    dataFilename=app.params['data_output'],\n"
                    "    dataFormat=SpriteSheetDataFormat.JSON_ARRAY,\n"
                    "    trim=true, openGenerated=false,\n"
                    "    listLayers=true, listTags=true, listSlices=true\n"
                    "  }\n"
                    "end\n"
                )
            visibility_json = json.dumps(layer_visibility or {}, ensure_ascii=False, separators=(",", ":"))
            arguments.extend([
                "--script-param", f"layer_inventory={inventory_path}",
                "--script-param", f"layer_visibility={visibility_json}",
                "--script-param", f"sheet_output={png_path}",
                "--script-param", f"data_output={json_path}",
                "--script", script_path,
            ])
        except Exception:
            if script_path and os.path.exists(script_path):
                os.remove(script_path)
            raise
    if not inventory_path:
        arguments.extend(["--trim", "--sheet", png_path, "--data", json_path, "--format", "json-array", "--list-layer-hierarchy", "--list-tags", "--list-slices"])
    try:
        expected_files = (png_path, json_path, inventory_path) if inventory_path else (png_path, json_path)
        run_aseprite(arguments, executable=executable, expected_files=expected_files)
    finally:
        if script_path and os.path.exists(script_path):
            try: os.remove(script_path)
            except OSError: pass
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        raise AsepriteError(f"Aseprite metadata could not be read: {os.path.basename(json_path)}") from e
    if not isinstance(data, dict) or not isinstance(data.get("frames"), list) or not data["frames"]:
        raise AsepriteError("Aseprite metadata is missing a non-empty 'frames' list.")
    return data

def select_file(ftypes):
    root = None
    try:
        root = tk.Tk(); root.withdraw(); root.attributes("-topmost", True)
        return filedialog.askopenfilename(filetypes=ftypes)
    except (tk.TclError, OSError) as e:
        log_debug(f"[ERROR] File selection dialog failed: {e}"); return None
    finally:
        if root is not None:
            try: root.destroy()
            except tk.TclError: pass

class AseSource:
    def __init__(self, file_path, source_id, kind="generic"):
        self.id = source_id; self.file_path = os.path.abspath(file_path); self.name = os.path.basename(file_path)
        self.kind = kind if kind in {"generic", "npc", "prop"} else "generic"
        self.is_prop_source = self.kind == "prop"
        if not os.path.isfile(self.file_path):
            raise AsepriteError(f"Source file does not exist: {self.file_path}")
        self.frames = []; self.tags = {}; self.tag_list = []; self.tag_metadata = {}; self.slices = {}; self.orig_w = self.orig_h = 0
        self.layers = []; self.visible_layer_keys = set(); self.visible_layers = set(); self.export_status = {"enabled": False, "reason": "Source is not loaded."}; self.source_revision = 0; self.slice_analysis_revision = -1; self.slice_export_analysis = None; self.auto_parts_cache = {}; self.last_mtime = os.path.getmtime(self.file_path); self.cache = LimitedLRU(256)
        if not self.export_and_load():
            raise AsepriteError(f"Aseprite could not export {self.name}.")
    def clear_cache(self): self.cache.clear()
    def get_frame(self, f_idx, zoom, facing_right):
        key = (self.source_revision, f_idx, zoom, facing_right)
        cached = self.cache.get(key)
        if cached is not None: return cached
        if not self.frames: return None
        f = self.frames[min(max(0, f_idx), len(self.frames)-1)]; img = f['img']; scaled = pygame.transform.scale(img, (int(img.get_width()*zoom), int(img.get_height()*zoom)))
        if not facing_right: scaled = pygame.transform.flip(scaled, True, False)
        return self.cache.put(key, scaled)
    @staticmethod
    def _normalize_layer_inventory(layer_data):
        normalized = []
        for index, layer in enumerate(layer_data or []):
            if not isinstance(layer, dict):
                continue
            name = str(layer.get("name", "Layer"))
            path = str(layer.get("path") or name)
            uuid = str(layer.get("uuid") or "")
            key = f"uuid:{uuid}" if uuid else f"stack:{index}:{path}"
            normalized.append({
                "key": key,
                "index": index,
                "name": name,
                "path": path,
                "depth": max(0, int(layer.get("depth", 0))),
                "stack_index": int(layer.get("stackIndex", index + 1)),
                "is_group": bool(layer.get("isGroup", False)),
                "is_image": bool(layer.get("isImage", False)),
                "is_tilemap": bool(layer.get("isTilemap", False)),
                "is_reference": bool(layer.get("isReference", False)),
                "original_visible": bool(layer.get("visible", True)),
                "applied_visible": bool(layer.get("appliedVisible", layer.get("visible", True))),
            })
        return normalized
    def _apply_layer_inventory(self, layer_data):
        self._apply_normalized_layer_inventory(self._normalize_layer_inventory(layer_data))
    def _apply_normalized_layer_inventory(self, new_layers):
        previous_layers = list(self.layers)
        previous_visible = set(self.visible_layer_keys)
        legacy_visible_names = set(self.visible_layers)
        if previous_layers:
            visible = {layer["key"] for layer in new_layers if layer["key"] in previous_visible}
            previous_by_fallback = {(layer["index"], layer["path"]): layer["key"] in previous_visible for layer in previous_layers}
            previous_keys = {layer["key"] for layer in previous_layers}
            for layer in new_layers:
                if layer["key"] not in previous_keys and previous_by_fallback.get((layer["index"], layer["path"]), layer["original_visible"]):
                    visible.add(layer["key"])
        elif legacy_visible_names:
            counts = {}
            for layer in new_layers: counts[layer["name"]] = counts.get(layer["name"], 0) + 1
            visible = set()
            for layer in new_layers:
                if counts[layer["name"]] == 1:
                    if layer["name"] in legacy_visible_names: visible.add(layer["key"])
                else:
                    visible.add(layer["key"])
                    if layer["name"] not in legacy_visible_names:
                        log_debug_once(f"ambiguous-layer:{self.file_path}:{layer['name']}", f"[WARN] Ambiguous legacy layer visibility ignored for duplicate name: {layer['name']}")
        else:
            visible = {layer["key"] for layer in new_layers if layer["original_visible"]}
        self.layers = new_layers
        self.visible_layer_keys = visible
        self.visible_layers = {layer["name"] for layer in new_layers if layer["key"] in visible}
    def set_layer_visibility(self, layer_key, visible):
        valid_keys = {layer["key"] for layer in self.layers}
        if layer_key not in valid_keys:
            return False
        if visible: self.visible_layer_keys.add(layer_key)
        else: self.visible_layer_keys.discard(layer_key)
        self.visible_layers = {layer["name"] for layer in self.layers if layer["key"] in self.visible_layer_keys}
        return True
    def check_for_reload(self):
        try:
            current_mtime = os.path.getmtime(self.file_path)
            if current_mtime > self.last_mtime:
                if self.export_and_load():
                    self.last_mtime = current_mtime; self.clear_cache(); return True
        except OSError as e: log_debug(f"[ERROR] Reload check failed for {self.file_path}: {e}")
        return False
    def export_and_load(self):
        try:
            with tempfile.TemporaryDirectory(prefix="ase_viewer_export_") as temp_dir:
                png_p = os.path.join(temp_dir, "sheet.png"); json_p = os.path.join(temp_dir, "data.json"); inventory_p = os.path.join(temp_dir, "layers.json")
                layer_visibility = {}
                for layer in self.layers:
                    desired = layer["key"] in self.visible_layer_keys
                    layer_visibility[layer["key"]] = desired
                    layer_visibility[f"stack:{layer['index']}:{layer['path']}"] = desired
                data = export_aseprite(self.file_path, png_p, json_p, layer_visibility=layer_visibility, inventory_path=inventory_p)
                try:
                    sheet = pygame.image.load(png_p).convert_alpha()
                except (OSError, pygame.error) as e:
                    raise AsepriteError(f"Exported image could not be loaded: {os.path.basename(png_p)}") from e
                try:
                    with open(inventory_p, "r", encoding="utf-8") as inventory_file:
                        layer_inventory = json.load(inventory_file)
                except (OSError, json.JSONDecodeError) as e:
                    raise AsepriteError("Aseprite layer inventory could not be read.") from e
                if not isinstance(layer_inventory, list) or not layer_inventory:
                    raise AsepriteError("Aseprite layer inventory is empty or invalid.")
                normalized_inventory = self._normalize_layer_inventory(layer_inventory)
                if len(normalized_inventory) != len(layer_inventory):
                    raise AsepriteError("Aseprite layer inventory contains invalid entries.")
            new_orig_w, new_orig_h = data['frames'][0]['sourceSize']['w'], data['frames'][0]['sourceSize']['h']
            new_frames = []
            for f in data['frames']:
                r, s = f['frame'], f['spriteSourceSize']; surf = pygame.Surface((r['w'], r['h']), pygame.SRCALPHA); surf.blit(sheet, (0, 0), (r['x'], r['y'], r['w'], r['h']))
                new_frames.append({'img': surf, 'ox': s['x'] - new_orig_w // 2, 'oy': s['y'] - new_orig_h // 2, 'duration': f.get('duration', 100)})
            new_tags = {}; new_tag_metadata = {}; new_slices = {}
            if 'meta' in data:
                if 'frameTags' in data['meta']:
                    for t in data['meta']['frameTags']:
                        new_tags[t['name']] = (t['from'], t['to']); new_tag_metadata[t['name']] = dict(t)
                if 'slices' in data['meta']:
                    for s in data['meta']['slices']: new_slices[s['name']] = s['keys']
            analysis_source = copy.copy(self)
            analysis_source.orig_w, analysis_source.orig_h = new_orig_w, new_orig_h
            analysis_source.frames, analysis_source.tags, analysis_source.slices = new_frames, new_tags, new_slices
            new_revision = getattr(self, "source_revision", 0) + 1
            new_analysis = build_source_slice_analysis(analysis_source, revision=new_revision)
            self.orig_w, self.orig_h = new_orig_w, new_orig_h
            self.frames, self.tags, self.tag_metadata, self.slices = new_frames, new_tags, new_tag_metadata, new_slices
            self.ground_offset_y = source_ground_alignment_offset(self)
            self._apply_normalized_layer_inventory(normalized_inventory)
            self.source_revision = new_revision
            self.slice_analysis_revision = new_revision
            self.slice_export_analysis = new_analysis
            self.auto_parts_cache = {}
            self.export_status = {"enabled": new_analysis["save_enabled"], "reason": new_analysis["reason"]}
            self.tag_list = sorted(list(self.tags.keys())); log_debug(f"[LOAD] {self.name} Success.")
            return True
        except (AsepriteError, KeyError, TypeError, ValueError, IndexError) as e:
            log_debug(f"[ERROR] Source load failed for {self.file_path}: {e}")
            return False

NPC_BEHAVIORS = (
    "balanced", "idle", "follow", "aggressive", "guard", "patrol", "flee",
)


def normalize_npc_behavior(value):
    normalized = str(value or "").strip().casefold()
    return normalized if normalized in NPC_BEHAVIORS else "balanced"


def cycle_npc_behavior(profile):
    current = normalize_npc_behavior(getattr(profile, "ai_behavior", "balanced"))
    next_index = (NPC_BEHAVIORS.index(current) + 1) % len(NPC_BEHAVIORS)
    profile.ai_behavior = NPC_BEHAVIORS[next_index]
    return profile.ai_behavior


def spawn_intro_tags(source):
    aliases = {
        "intro", "spawn", "spawnintro", "summon", "summonintro",
        "emerge", "emergence", "appear", "appearance", "entrance",
    }
    return [
        tag for tag in getattr(source, "tag_list", [])
        if re.sub(r"[^a-z]", "", str(tag).casefold()) in aliases
    ]


class AseProfile:
    def __init__(self, name, source_idx, kind=None):
        self.name = name; self.source_idx = source_idx; self.kind = kind
        self.is_prop_profile = kind == "prop"
        self.ai_behavior = "balanced"
        self.ground_offset_y = 0
        self.mappings = { "INTRO": [], "IDLE": [], "WALK": [], "JUMP": [], "FALL": [], "ComboAttack_1": [], "ComboAttack_2": [], "ComboAttack_3": [], "ComboAttack_4": [], "JUMPATTACK": [], "POWERBOMB": [], "DASH": [], "SKILL 1": [], "SKILL 2": [], "SKILL 3": [], "HIT_1": [], "HIT_2": [], "Swap_Enter": [], "Swap_Exit": [], "DEAD_LOOP": [], "DEAD": [], "Break1": [], "Break2": [] }


def source_ground_alignment_offset(source, frame_index=0):
    """Offset a trimmed frame so its authored pivot/bottom meets world ground."""
    explicit = getattr(source, "ground_offset_y", None)
    if isinstance(explicit, (int, float)) and math.isfinite(explicit):
        return float(explicit)
    for slice_name, keys in getattr(source, "slices", {}).items():
        normalized = re.sub(r"[^a-z]", "", str(slice_name).casefold())
        if not any(token in normalized for token in ("pivot", "anchor", "foot", "feet", "ground")):
            continue
        for key in keys or []:
            pivot = key.get("pivot") if isinstance(key, dict) else None
            bounds = key.get("bounds", {}) if isinstance(key, dict) else {}
            if isinstance(pivot, dict) and isinstance(pivot.get("y"), (int, float)):
                pivot_y = float(bounds.get("y", 0)) + float(pivot["y"])
                return float(getattr(source, "orig_h", 0)) / 2.0 - pivot_y
    frames = getattr(source, "frames", [])
    if not frames:
        return 0.0
    frame = frames[min(max(0, int(frame_index)), len(frames) - 1)]
    image = frame.get("img")
    if image is None or not hasattr(image, "get_height"):
        return 0.0
    # ox/oy are relative to the old canvas-center origin. Moving by the
    # negative visible bottom converts that origin to a stable ground point.
    return -float(frame.get("oy", 0) + image.get_height())


def update_profile_ground_alignment(player, profile):
    source_index = getattr(profile, "source_idx", -1)
    if not 0 <= source_index < len(getattr(player, "sources", [])):
        profile.ground_offset_y = 0.0
        return profile.ground_offset_y
    source = player.sources[source_index]
    frame_index = 0
    idle_mapping = getattr(profile, "mappings", {}).get("IDLE", [])
    if idle_mapping:
        mapping_source, tag_name = idle_mapping[0]
        if mapping_source == source_index:
            tag_range = getattr(source, "tags", {}).get(tag_name)
            if tag_range:
                frame_index = tag_range[0]
    profile.ground_offset_y = source_ground_alignment_offset(source, frame_index)
    return profile.ground_offset_y


def entity_ground_alignment_offset(player, entity, source_index):
    profile = (
        getattr(entity, "profile", None)
        if entity is not player
        else (player.profiles[0] if getattr(player, "profiles", []) else None)
    )
    if profile is not None and getattr(profile, "source_idx", -1) == source_index:
        return float(getattr(profile, "ground_offset_y", 0.0))
    if 0 <= source_index < len(getattr(player, "sources", [])):
        return source_ground_alignment_offset(player.sources[source_index])
    return 0.0


class Projectile:
    def __init__(self, master, x, y, vx, vy, source_idx, anim_tag):
        self.master = master; self.x = x; self.y = y; self.vx = vx; self.vy = vy
        self.source_idx = source_idx; self.facing_right = vx > 0
        self.anim_tag = anim_tag
        if source_idx is not None and source_idx >= 0 and source_idx < len(master.sources):
            src = master.sources[source_idx]
            self.frame_idx, self.end_frame = src.tags.get(anim_tag, (0, 0))
        else:
            self.frame_idx, self.end_frame = 0, 0
        self.anim_timer = 0; self.lifetime = 2000; self.active = True
    def update(self, dt):
        self.x += self.vx * (dt/16.6); self.y += self.vy * (dt/16.6)
        self.lifetime -= dt
        if self.source_idx is not None and self.source_idx >= 0 and self.source_idx < len(self.master.sources):
            src = self.master.sources[self.source_idx]
            self.anim_timer += dt
            if self.anim_timer > src.frames[self.frame_idx]['duration']:
                self.anim_timer -= src.frames[self.frame_idx]['duration']
                self.frame_idx += 1
                if self.frame_idx > self.end_frame: 
                    tr = src.tags.get(self.anim_tag, (0,0))
                    self.frame_idx = tr[0]

class Spark:
    def __init__(self, x, y, angle, speed, color, length, width, lifetime):
        self.x = x; self.y = y; self.angle = angle; self.speed = speed
        self.color = color; self.length = length; self.width = width
        self.lifetime = lifetime; self.max_life = lifetime
    def update(self, dt):
        self.x += math.cos(self.angle) * self.speed * (dt/16.6)
        self.y += math.sin(self.angle) * self.speed * (dt/16.6)
        self.speed *= 0.85 # Friction/drag
        self.lifetime -= dt
        self.length *= 0.9 # Shrink over time

def is_actor_grounded_for_dash_dust(actor):
    return getattr(actor, "grounded", False) is True


def can_emit_ground_dash_dust(actor):
    grounded = is_actor_grounded_for_dash_dust(actor)
    started_grounded = getattr(actor, "dash_started_grounded", grounded)
    return (
        grounded
        and started_grounded is True
        and _finite_number(getattr(actor, "dash_timer", 0), 0) > 0
    )


def emit_ground_dash_dust(actor, chance_value=None):
    if not can_emit_ground_dash_dust(actor):
        return False
    roll = random.random() if chance_value is None else chance_value
    if roll >= 0.5:
        return False
    particles = getattr(actor, "particles", None)
    if not isinstance(particles, list):
        return False
    particles.append(Particle(
        actor.x + random.uniform(-10, 10),
        actor.y,
        random.uniform(-3, 3),
        random.uniform(-6, -2),
        (180, 180, 180),
        random.uniform(2, 6),
        400,
    ))
    return True


class Particle:
    def __init__(self, x, y, vx, vy, color, size, lifetime, image=None):
        self.x = x; self.y = y; self.vx = vx; self.vy = vy
        self.color = color; self.size = size; self.lifetime = lifetime; self.max_life = lifetime
        self.image = image
        self.rotation = random.uniform(0, 360) if image else 0
        self.rot_speed = random.uniform(-10, 10) if image else 0
        self.cached_surface = None; self.cached_zoom = -1; self.cached_rotation = -1
        self.cached_scaled_surface = None; self.cached_scaled_zoom = -1
    def update(self, dt, gravity, ground_y, platforms):
        self.lifetime -= dt
        # Optimization: Skip expensive physics and collision logic if particle is at rest
        if abs(self.vx) < 0.1 and abs(self.vy) < 0.1 and self.y >= ground_y - 10:
            return

        self.vy += gravity * (dt/16.6); self.x += self.vx * (dt/16.6); self.y += self.vy * (dt/16.6)
        if self.image: self.rotation += self.rot_speed * (dt/16.6)
        # Simple floor/platform collision for bounce
        hit_ground = False
        if self.y >= ground_y:
            self.y = ground_y; hit_ground = True

        # Only check platform collisions if falling down
        if self.vy > 0 and not hit_ground:
            for p in platforms:
                if p.collidepoint(self.x, self.y):
                    self.y = p.top; hit_ground = True; break

        if hit_ground:
            if abs(self.vy) < 2.0:
                self.vy = 0; self.rot_speed = 0; self.vx *= 0.5
            else:
                self.vy *= -0.5; self.vx *= 0.8


def spawn_ground_y(master, spawn_x):
    world_ground = _finite_number(
        getattr(master, "world_ground_y", 500.0), 500.0,
    )
    current_y = _finite_number(getattr(master, "y", world_ground), world_ground)
    candidates = [world_ground]
    for platform in getattr(master, "platforms", []):
        if (
            hasattr(platform, "left")
            and platform.left <= spawn_x < platform.right
            and platform.top >= current_y - 10
        ):
            candidates.append(float(platform.top))
    return min(candidates)


def _find_ground_y_below_actor(actor, world_ground_y=None):
    master = getattr(actor, "master", None)
    fallback_ground = _finite_number(
        world_ground_y,
        _finite_number(getattr(master, "world_ground_y", 500.0), 500.0),
    )
    actor_x = _finite_number(getattr(actor, "x", 0.0), 0.0)
    actor_y = _finite_number(getattr(actor, "y", fallback_ground), fallback_ground)
    candidates = [fallback_ground]
    for platform in getattr(master, "platforms", []) or []:
        try:
            if (
                platform.left <= actor_x < platform.right
                and platform.top >= actor_y - 10
            ):
                candidates.append(float(platform.top))
        except (AttributeError, TypeError, ValueError):
            continue
    return min(candidates)


def _snap_npc_corpse_to_ground(npc, world_ground_y=None):
    if npc is None or bool(getattr(npc, "is_prop", False)):
        return False
    target_y = _find_ground_y_below_actor(npc, world_ground_y)
    npc.y = target_y
    npc.vx = 0
    npc.vy = 0
    npc.grounded = True
    npc.corpse_ground_y = target_y
    return True


def _stabilize_corpse_grounding(npc, world_ground_y=None):
    if (
        npc is None
        or not bool(getattr(npc, "is_corpse", False))
        or bool(getattr(npc, "is_prop", False))
    ):
        return False
    target_y = _find_ground_y_below_actor(npc, world_ground_y)
    current_y = _finite_number(getattr(npc, "y", target_y), target_y)
    needs_snap = (
        not bool(getattr(npc, "grounded", False))
        or abs(current_y - target_y) > 0.5
        or abs(_finite_number(getattr(npc, "vy", 0.0), 0.0)) > 0.01
    )
    if needs_snap:
        return _snap_npc_corpse_to_ground(npc, target_y)
    npc.vx = 0
    npc.vy = 0
    npc.grounded = True
    npc.corpse_ground_y = target_y
    return False


def is_recallable_npc(actor):
    """Return whether G recall may reposition this living scene NPC."""
    if actor is None:
        return False
    if (
        bool(getattr(actor, "is_prop", False))
        or bool(getattr(actor, "is_partner", False))
        or bool(getattr(actor, "is_temp", False))
        or _is_scene_object_corpse(actor)
        or not bool(getattr(actor, "visible", True))
    ):
        return False
    try:
        return float(getattr(actor, "hp", 1)) > 0
    except (TypeError, ValueError):
        return False


def recall_live_npcs(player, direction_picker=random.choice):
    """Recall only living NPCs, preserving corpse and non-NPC scene objects."""
    if player is None:
        return 0
    recalled = 0
    for actor in getattr(player, "ai_list", []) or []:
        if not is_recallable_npc(actor):
            continue
        recalled += 1
        offset = direction_picker((-80, 80)) * recalled
        actor.x, actor.y = player.x + offset, player.y
        trigger_action = getattr(actor, "trigger_action", None)
        if callable(trigger_action):
            trigger_action("Swap_Enter")
    status_key = (
        "status.recall_live_npcs"
        if recalled
        else "status.recall_no_live_npcs"
    )
    player.scene_status_message = tr(status_key, count=recalled)
    return recalled


def _clear_npc_death_runtime_state(npc):
    npc.npc_attack_locked = False
    npc.npc_attack_slot = None
    npc.npc_attack_elapsed = 0.0
    npc.npc_attack_duration = 0.0
    npc.npc_attack_has_hit = False
    npc.npc_attack_cooldown = 0.0
    npc.npc_combo_actions = []
    npc.npc_combo_index = 0
    npc.intro_locked = False
    npc.intro_elapsed = 0.0
    npc.intro_duration = 0.0
    npc.hit_cooldown = 0
    npc.pending_execution = 0
    npc.vx = 0
    npc.vy = 0


_COMBO_ACTION_RE = re.compile(r"^ComboAttack_(\d+)$", re.IGNORECASE)
_COMBO_TAG_RE = re.compile(
    r"^ComboAttack_(\d+)(?:_(?:Ready|Loop|End))?$", re.IGNORECASE,
)


def _combo_attack_number(name, allow_tag_suffix=False):
    pattern = _COMBO_TAG_RE if allow_tag_suffix else _COMBO_ACTION_RE
    match = pattern.fullmatch(str(name or "").strip())
    return int(match.group(1)) if match else None


def _detect_npc_combo_actions(profile_or_source):
    mappings = getattr(profile_or_source, "mappings", None)
    if isinstance(mappings, dict):
        numbers = {
            number for action, tags in mappings.items()
            if tags and (number := _combo_attack_number(action)) is not None
        }
    else:
        numbers = {
            number for tag in getattr(profile_or_source, "tag_list", [])
            if (number := _combo_attack_number(tag, allow_tag_suffix=True)) is not None
        }
    chain = []
    number = 1
    while number in numbers:
        chain.append(f"ComboAttack_{number}")
        number += 1
    return chain


def _get_npc_combo_chain(profile):
    return _detect_npc_combo_actions(profile)


NPC_ATTACK_ACTIVE_START = 0.35
NPC_ATTACK_ACTIVE_END = 0.60
NPC_ATTACK_RECOVERY_MS = 650.0
NPC_ATTACK_FALLBACK_DURATION_MS = 450.0
NPC_ATTACK_FALLBACK_GRACE_MS = 250.0


def _is_npc_attack_locked(npc):
    return bool(getattr(npc, "npc_attack_locked", False))


def _npc_attack_slots(npc):
    return _get_npc_combo_chain(getattr(npc, "profile", None))


def _npc_action_duration_ms(npc, slot):
    total = 0.0
    master = getattr(npc, "master", None)
    sources = getattr(master, "sources", [])
    mappings = getattr(getattr(npc, "profile", None), "mappings", {})
    for source_index, tag_name in mappings.get(slot, []):
        if not 0 <= source_index < len(sources):
            continue
        source = sources[source_index]
        tag_range = getattr(source, "tags", {}).get(tag_name)
        frames = getattr(source, "frames", [])
        if not tag_range or not frames:
            continue
        start, end = tag_range
        for frame_index in range(max(0, start), min(end, len(frames) - 1) + 1):
            total += max(1.0, _finite_number(frames[frame_index].get("duration"), 100.0))
    return total if total > 0 else NPC_ATTACK_FALLBACK_DURATION_MS


def _can_npc_start_attack(npc):
    return (
        npc is not None
        and not _is_npc_attack_locked(npc)
        and _finite_number(getattr(npc, "npc_attack_cooldown", 0.0), 0.0) <= 0
        and not bool(getattr(npc, "is_dead", False))
        and not bool(getattr(npc, "is_corpse", False))
        and bool(_npc_attack_slots(npc))
    )


def _start_npc_attack(npc, target_delta):
    if not _can_npc_start_attack(npc):
        return False
    slots = _npc_attack_slots(npc)
    slot = slots[0]
    npc.facing_right = target_delta >= 0
    if not npc.trigger_action(slot):
        return False
    npc.npc_attack_locked = True
    npc.npc_combo_actions = list(slots)
    npc.npc_combo_index = 0
    npc.npc_attack_slot = slot
    npc.npc_attack_facing_right = bool(npc.facing_right)
    npc.npc_attack_elapsed = 0.0
    npc.npc_attack_duration = _npc_action_duration_ms(npc, slot)
    npc.npc_attack_has_hit = False
    npc.npc_attack_instance_id = getattr(npc, "npc_attack_instance_id", 0) + 1
    npc.decision = "ATTACK"
    npc.vx = 0
    return True


def _advance_npc_combo_segment(npc):
    actions = list(getattr(npc, "npc_combo_actions", []) or [])
    next_index = int(getattr(npc, "npc_combo_index", 0)) + 1
    if next_index >= len(actions):
        return False
    slot = actions[next_index]
    if not npc.trigger_action(slot, allow_attack_chain=True):
        return False
    npc.npc_combo_index = next_index
    npc.npc_attack_slot = slot
    npc.npc_attack_elapsed = 0.0
    npc.npc_attack_duration = _npc_action_duration_ms(npc, slot)
    npc.npc_attack_has_hit = False
    return True


def _finish_npc_attack(npc):
    if not _is_npc_attack_locked(npc):
        return False
    npc.npc_attack_locked = False
    npc.npc_attack_slot = None
    npc.npc_combo_actions = []
    npc.npc_combo_index = 0
    npc.npc_attack_elapsed = 0.0
    npc.npc_attack_duration = 0.0
    npc.npc_attack_cooldown = NPC_ATTACK_RECOVERY_MS
    npc.decision = "IDLE"
    return True


def npc_attack_hitbox(npc):
    """Return the authored active hit slice, or a conservative front-facing fallback."""
    facing_right = bool(getattr(npc, "npc_attack_facing_right", getattr(npc, "facing_right", True)))
    active_info = getattr(npc, "active_tag_info", None)
    master = getattr(npc, "master", None)
    sources = getattr(master, "sources", [])
    if active_info and 0 <= active_info[0] < len(sources):
        source = sources[active_info[0]]
        active_slices = []
        for name, keys in getattr(source, "slices", {}).items():
            if "hit" not in str(name).casefold():
                continue
            key = None
            for candidate in keys:
                if candidate.get("frame", 0) <= getattr(npc, "frame_idx", 0):
                    if key is None or candidate.get("frame", 0) > key.get("frame", 0):
                        key = candidate
            if key and isinstance(key.get("bounds"), dict):
                active_slices.append(key["bounds"])
        if active_slices:
            bounds = active_slices[0]
            orig_w = getattr(source, "orig_w", 0)
            orig_h = getattr(source, "orig_h", 0)
            offset_x = (
                bounds["x"] - orig_w // 2
                if facing_right
                else -(bounds["x"] - orig_w // 2 + bounds["w"])
            )
            return pygame.Rect(
                getattr(npc, "x", 0) + offset_x,
                getattr(npc, "y", 0) + bounds["y"] - orig_h // 2,
                bounds["w"], bounds["h"],
            )
    width, height = 125, 80
    offset_x = 8 if facing_right else -8 - width
    return pygame.Rect(
        getattr(npc, "x", 0) + offset_x,
        getattr(npc, "y", 0) - height,
        width, height,
    )


def player_hurtbox(player):
    if player is None or not bool(getattr(player, "visible", True)):
        return None
    return pygame.Rect(
        getattr(player, "x", 0) - 20,
        getattr(player, "y", 0) - 70,
        40, 70,
    )


def _apply_npc_attack_hit(npc):
    if getattr(npc, "npc_attack_has_hit", False):
        return False
    player = getattr(npc, "master", None)
    hurtbox = player_hurtbox(player)
    if hurtbox is None or not npc_attack_hitbox(npc).colliderect(hurtbox):
        return False
    if not hasattr(player, "hp") or getattr(player, "hp", 0) <= 0:
        return False
    damage = 5
    player.hp = max(0, player.hp - damage)
    npc.npc_attack_has_hit = True
    if hasattr(player, "damage_numbers"):
        player.damage_numbers.append({
            "val": damage, "x": player.x, "y": player.y - 60,
            "lifetime": 1000, "max_life": 1000, "vy": -2,
        })
    if getattr(player, "shake_enabled", False):
        player.shake_timer = 8
        player.shake_intensity = 3
    if hasattr(player, "play_sound"):
        player.play_sound("hit")
    if hasattr(player, "trigger_action") and getattr(player, "profiles", None):
        player.trigger_action("HIT_1")
    return True


def _update_npc_attack_state(npc, dt):
    elapsed_dt = max(0.0, _finite_number(dt, 0.0))
    if not _is_npc_attack_locked(npc):
        npc.npc_attack_cooldown = max(
            0.0,
            _finite_number(getattr(npc, "npc_attack_cooldown", 0.0), 0.0) - elapsed_dt,
        )
        return False
    previous = _finite_number(getattr(npc, "npc_attack_elapsed", 0.0), 0.0)
    duration = max(
        1.0,
        _finite_number(getattr(npc, "npc_attack_duration", 0.0), NPC_ATTACK_FALLBACK_DURATION_MS),
    )
    current = previous + elapsed_dt
    npc.npc_attack_elapsed = current
    active_start = duration * NPC_ATTACK_ACTIVE_START
    active_end = duration * NPC_ATTACK_ACTIVE_END
    if previous <= active_end and current >= active_start:
        _apply_npc_attack_hit(npc)
    action_is_active = (
        getattr(npc, "active_action_slot", None) == getattr(npc, "npc_attack_slot", None)
        and getattr(npc, "active_tag_info", None) is not None
    )
    if not action_is_active:
        if not _advance_npc_combo_segment(npc):
            _finish_npc_attack(npc)
    elif current >= duration + NPC_ATTACK_FALLBACK_GRACE_MS:
        if not _advance_npc_combo_segment(npc):
            npc.active_tag_info = None
            npc.active_action_slot = None
            _finish_npc_attack(npc)
    return True


def _is_intro_locked(actor):
    return bool(getattr(actor, "intro_locked", False))


def _start_intro_lock(actor):
    if (
        actor is None
        or _is_npc_attack_locked(actor)
        or getattr(actor, "active_action_slot", None) != "INTRO"
    ):
        return False
    actor.intro_locked = True
    actor.intro_lock_x = _finite_number(getattr(actor, "x", 0.0), 0.0)
    actor.intro_lock_y = _finite_number(getattr(actor, "y", 0.0), 0.0)
    actor.intro_elapsed = 0.0
    actor.intro_duration = _npc_action_duration_ms(actor, "INTRO")
    actor.vx = 0
    actor.vy = 0
    actor.grounded = True
    return True


def _finish_intro_lock(actor):
    if not _is_intro_locked(actor):
        return False
    actor.intro_locked = False
    actor.intro_elapsed = 0.0
    actor.intro_duration = 0.0
    actor.vx = 0
    actor.vy = 0
    actor.grounded = True
    if getattr(actor, "decision", None) != "DEAD":
        actor.decision = "IDLE"
    return True


def _update_intro_lock(actor, dt):
    if not _is_intro_locked(actor):
        return False
    actor.x = getattr(actor, "intro_lock_x", getattr(actor, "x", 0.0))
    actor.y = getattr(actor, "intro_lock_y", getattr(actor, "y", 0.0))
    actor.vx = 0
    actor.vy = 0
    actor.grounded = True
    actor.intro_elapsed = (
        _finite_number(getattr(actor, "intro_elapsed", 0.0), 0.0)
        + max(0.0, _finite_number(dt, 0.0))
    )
    duration = max(
        1.0,
        _finite_number(
            getattr(actor, "intro_duration", 0.0),
            NPC_ATTACK_FALLBACK_DURATION_MS,
        ),
    )
    action_active = (
        getattr(actor, "active_action_slot", None) == "INTRO"
        and getattr(actor, "active_tag_info", None) is not None
    )
    if (
        not action_active
        or actor.intro_elapsed >= duration + NPC_ATTACK_FALLBACK_GRACE_MS
    ):
        if getattr(actor, "active_action_slot", None) == "INTRO":
            actor.active_action_slot = None
            actor.active_tag_info = None
            actor.action_queue = []
        _finish_intro_lock(actor)
    return True


def update_npc_behavior(ai, dist_p, dt):
    behavior = normalize_npc_behavior(
        getattr(getattr(ai, "profile", None), "ai_behavior", "balanced"),
    )
    if _is_intro_locked(ai):
        ai.decision = "IDLE"
        ai.vx = 0
        return behavior
    if _is_npc_attack_locked(ai):
        ai.decision = "ATTACK"
        ai.vx = 0
        return behavior
    ai.ai_timer -= dt / 16.6
    distance = abs(dist_p)
    timer_ready = ai.ai_timer <= 0

    if behavior == "idle":
        ai.decision = "IDLE"
        if timer_ready:
            ai.ai_timer = 90
        return behavior

    if behavior == "follow":
        ai.decision = "CHASE" if distance > 120 else "IDLE"
        if timer_ready:
            ai.ai_timer = 60
        return behavior

    if behavior == "aggressive":
        if distance > 150:
            ai.decision = "CHASE"
        elif timer_ready:
            if _start_npc_attack(ai, dist_p):
                ai.ai_timer = random.randint(45, 90)
            else:
                ai.decision = "IDLE"
        elif not ai.active_tag_info:
            ai.decision = "IDLE"
        return behavior

    if behavior == "guard":
        home_delta = ai.spawn_x - ai.x
        if distance <= 220:
            if distance <= 110 and timer_ready:
                if _start_npc_attack(ai, dist_p):
                    ai.ai_timer = random.randint(60, 110)
                else:
                    ai.decision = "IDLE"
            elif distance > 110:
                ai.decision = "CHASE"
            elif not ai.active_tag_info:
                ai.decision = "IDLE"
        elif abs(home_delta) > 30:
            ai.decision = "WALK_R" if home_delta > 0 else "WALK_L"
        else:
            ai.decision = "IDLE"
        return behavior

    if behavior == "patrol":
        patrol_radius = 220
        home_delta = ai.x - ai.spawn_x
        if home_delta >= patrol_radius:
            ai.decision = "WALK_L"
            ai.ai_timer = random.randint(90, 160)
        elif home_delta <= -patrol_radius:
            ai.decision = "WALK_R"
            ai.ai_timer = random.randint(90, 160)
        elif timer_ready:
            ai.decision = random.choice(["WALK_L", "WALK_R", "IDLE"])
            ai.ai_timer = random.randint(90, 180)
        return behavior

    if behavior == "flee":
        if distance < 280:
            ai.decision = "WALK_L" if dist_p > 0 else "WALK_R"
        else:
            ai.decision = "IDLE"
        if timer_ready:
            ai.ai_timer = 60
        return behavior

    if timer_ready:
        choices = (
            ["IDLE", "CHASE", "ATTACK", "DASH", "JUMP", "SWAP"]
            if distance < 600
            else ["IDLE", "WALK_L", "WALK_R"]
        )
        ai.decision = random.choice(choices)
        ai.ai_timer = random.randint(40, 120)
        if ai.decision == "SWAP":
            ai.trigger_action("Swap_Exit")
        elif ai.decision == "ATTACK" and distance < 200:
            if not _start_npc_attack(ai, dist_p):
                ai.decision = "IDLE"
        elif ai.decision == "DASH":
            ai.facing_right = dist_p > 0
            ai.trigger_action("DASH")
        elif ai.decision == "JUMP" and ai.grounded:
            ai.vy = ai.master.jump_power
            ai.grounded = False
    return behavior


class AseAI:
    def __init__(self, master, profile, is_temp=False, is_prop=False, hp=1, is_partner=False):
        self.master = master; self.profile = profile
        if 0 <= profile.source_idx < len(getattr(master, "sources", [])):
            ensure_source_slice_analysis(master.sources[profile.source_idx])
        self.spawn_x = master.x + (100 if master.facing_right else -100)
        self.spawn_y = spawn_ground_y(master, self.spawn_x)
        self.x, self.y = self.spawn_x, self.spawn_y; self.vx = self.vy = 0; self.grounded = True; self.facing_right = random.choice([True, False]); self.frame_idx = 0; self.anim_timer = 0; self.active_tag_info = None; self.action_queue = []; self.action_end_frame = -1; self.ai_timer = random.randint(30, 90); self.decision = "IDLE"; self.swap_timer = 0; self.visible = True; self.active_action_slot = None
        self.is_temp = is_temp; self.is_partner = bool(is_partner); self.attack_buffer = 0; self.combo_step = 0
        self.is_prop = is_prop; self.hit_cooldown = 0; self.is_dead = False; self.is_corpse = False; self.corpse_looping = False; self.corpse_anim_step = 1; self.last_hit_frame_idx = -1; self.pending_execution = 0
        self.npc_attack_locked = False; self.npc_attack_cooldown = 0.0; self.npc_attack_slot = None; self.npc_attack_facing_right = self.facing_right; self.npc_attack_elapsed = 0.0; self.npc_attack_duration = 0.0; self.npc_attack_has_hit = False; self.npc_attack_instance_id = 0; self.npc_combo_actions = []; self.npc_combo_index = 0
        self.intro_locked = False; self.intro_lock_x = self.x; self.intro_lock_y = self.y; self.intro_elapsed = 0.0; self.intro_duration = 0.0
        if is_prop:
            self.prop_state = 0 # 0: IDLE, 1: Break1, 2: Break2
            self.stage_hp = 3
            self.hp = 999 # Use stage_hp instead
        else:
            self.hp = getattr(master, 'npc_max_hp', 10) if hp == 1 else hp
            self.max_hp = self.hp
        self.spawned_with_intro = bool(profile.mappings.get("INTRO"))
        if self.spawned_with_intro:
            if self.trigger_action("INTRO"):
                _start_intro_lock(self)
    def update(self, ground_y, dt):
        if self.is_partner:
            return
        if self.is_corpse:
            self.vx = 0; self.decision = "DEAD"
            if not self.is_prop:
                _stabilize_corpse_grounding(self, ground_y)
            elif not self.grounded:
                previous_y = self.y
                self.vy += self.master.gravity * (dt / 16.6)
                self.y += self.vy * (dt / 16.6)
                if self.y >= ground_y:
                    self.y = ground_y; self.vy = 0; self.grounded = True
                elif self.vy >= 0:
                    for platform in self.master.platforms:
                        if platform.collidepoint(self.x, self.y) and previous_y <= platform.top + 10:
                            self.y = platform.top; self.vy = 0; self.grounded = True
                            break
            else:
                self.vy = 0
            if not self.active_tag_info or not 0 <= self.active_tag_info[0] < len(self.master.sources):
                return
            source = self.master.sources[self.active_tag_info[0]]
            tag_name = self.active_tag_info[1]
            tag_range = source.tags.get(tag_name)
            if not tag_range or not source.frames:
                return
            start, end = tag_range
            metadata = getattr(source, "tag_metadata", {}).get(tag_name, {})
            direction = str(metadata.get("direction", "forward")).lower()
            if not self.master.is_paused:
                self.anim_timer += dt
                duration = source.frames[min(max(self.frame_idx, start), end)]["duration"]
                if self.anim_timer >= duration:
                    self.anim_timer -= duration
                    if not self.corpse_looping:
                        self.frame_idx = min(end, self.frame_idx + 1)
                    elif direction == "reverse":
                        self.frame_idx -= 1
                        if self.frame_idx < start: self.frame_idx = end
                    elif direction in {"pingpong", "pingpong_reverse"}:
                        self.frame_idx += self.corpse_anim_step
                        if self.frame_idx > end or self.frame_idx < start:
                            self.corpse_anim_step *= -1
                            self.frame_idx = max(start, min(end, self.frame_idx + self.corpse_anim_step * 2))
                    else:
                        self.frame_idx += 1
                        if self.frame_idx > end: self.frame_idx = start
            return
        if getattr(self, 'pending_execution', 0) > 0:
            self.pending_execution -= dt
        if self.hit_cooldown > 0: self.hit_cooldown -= dt
        _update_intro_lock(self, 0 if self.master.is_paused else dt)
        _update_npc_attack_state(self, 0 if self.master.is_paused else dt)
        if self.swap_timer > 0:
            self.swap_timer -= dt
            if self.swap_timer <= 0: self.x, self.y = self.spawn_x, self.spawn_y; self.visible = True; self.trigger_action("Swap_Enter")
            return
        if _is_intro_locked(self):
            self.x = self.intro_lock_x; self.y = self.intro_lock_y
            self.vx = 0; self.vy = 0; self.grounded = True; self.decision = "IDLE"
        elif self.is_prop:
            self.vx *= 0.85
        elif not self.is_temp:
            dist_p = self.master.x - self.x
            update_npc_behavior(self, dist_p, dt)
            self.vx *= 0.85
            if not self.active_tag_info:
                if self.decision == "WALK_R": self.vx = 2.6; self.facing_right = True
                elif self.decision == "WALK_L": self.vx = -2.6; self.facing_right = False
                elif self.decision == "CHASE": self.vx = 3.6 if dist_p > 0 else -3.6; self.facing_right = dist_p > 0
                if self.decision == "CHASE" and abs(dist_p) < 100:
                    self.decision = "IDLE"
        else:
            self.vx *= 0.85
        if _is_intro_locked(self):
            self.x = self.intro_lock_x; self.y = self.intro_lock_y
        else:
            if self.active_tag_info and self.active_tag_info[1] == "DASH": self.vy = 0
            else: self.vy += self.master.gravity
            self.x += self.vx * (dt/16.6); self.y += self.vy * (dt/16.6)
        if self.y >= ground_y: self.y = ground_y; self.vy = 0; self.grounded = True
        if not _is_intro_locked(self) and self.vy >= 0:
            for plat in self.master.platforms:
                if plat.collidepoint(self.x, self.y) and self.y - (self.vy * (dt/16.6)) <= plat.top + 10: self.y = plat.top; self.vy = 0; self.grounded = True
        target_info = None
        if not self.active_tag_info:
            if self.is_temp:
                self.trigger_action("Swap_Exit")
                if not self.active_tag_info: self.visible = False; return
                target_info = self.active_tag_info
            else:
                if self.is_prop:
                    state = "IDLE" if getattr(self, 'prop_state', 0) == 0 else (f"Break{getattr(self, 'prop_state', 0)}")
                else:
                    state = "WALK" if self.grounded and abs(self.vx) > 0.5 else ("IDLE" if self.grounded else ("JUMP" if self.vy < 0 else "FALL"))
                
                m = self.profile.mappings.get(state, []) if self.profile else []
                # Fallback to IDLE if Break1/Break2 mappings aren't found
                if not m and self.is_prop and state != "IDLE": m = self.profile.mappings.get("IDLE", [])
                target_info = m[0] if m else None
        else: target_info = self.active_tag_info
        if target_info and target_info[0] >= 0 and target_info[0] < len(self.master.sources):
            src = self.master.sources[target_info[0]]; tr = src.tags.get(target_info[1], (0,0))
            if self.frame_idx < tr[0] or self.frame_idx > tr[1]: self.frame_idx = tr[0]; self.anim_timer = 0
            if not self.master.is_paused:
                self.anim_timer += dt
                if self.frame_idx < len(src.frames):
                    dur = src.frames[self.frame_idx]['duration']
                    if self.anim_timer >= dur:
                        self.frame_idx += 1; self.anim_timer = 0
                        if self.active_tag_info and self.frame_idx > self.action_end_frame:
                            if target_info[1] == "Swap_Exit" and not self.action_queue: self.visible = False; self.swap_timer = 500; self.active_tag_info = None; self.active_action_slot = None; return
                            if "(loop)" in target_info[1].lower(): 
                                if self.active_action_slot in ["HIT_1", "HIT_2"] and not self.action_queue:
                                    self.active_tag_info = None; self.active_action_slot = None; self.decision = "IDLE"
                                else:
                                    self.frame_idx = tr[0]
                            elif self.is_temp and not self.action_queue:
                                if getattr(self, 'attack_buffer', 0) > 0:
                                    self.attack_buffer -= 1
                                    self.combo_step = (getattr(self, 'combo_step', 0) % 4) + 1
                                    self.trigger_action(f"ComboAttack_{self.combo_step}")
                                else:
                                    self.trigger_action("Swap_Exit")
                                    if not self.active_tag_info: self.visible = False
                                return
                            elif self.action_queue:
                                self.active_tag_info = self.action_queue.pop(0)
                                if self.active_tag_info[0] >= 0 and self.active_tag_info[0] < len(self.master.sources):
                                    s = self.master.sources[self.active_tag_info[0]]; self.frame_idx, self.action_end_frame = s.tags.get(self.active_tag_info[1], (0,0))
                                else:
                                    self.active_tag_info = None; self.active_action_slot = None
                            else:
                                if (
                                    _is_npc_attack_locked(self)
                                    and _advance_npc_combo_segment(self)
                                ):
                                    pass
                                else:
                                    self.active_tag_info = None
                                    self.active_action_slot = None
                        elif self.frame_idx > tr[1]: self.frame_idx = tr[0]
                else: self.frame_idx = tr[0]
        if _is_npc_attack_locked(self) and self.active_tag_info is None:
            _finish_npc_attack(self)
        if _is_intro_locked(self) and self.active_tag_info is None:
            _finish_intro_lock(self)
    def trigger_action(self, slot, allow_attack_chain=False):
        if _is_intro_locked(self):
            return False
        if _is_npc_attack_locked(self) and not allow_attack_chain:
            return False
        tags = self.profile.mappings.get(slot, [])
        if tags:
            log_debug(f"[AI] Triggering {slot} -> Tags: {tags}")
            self.active_action_slot = slot; self.action_queue = list(tags); self.active_tag_info = self.action_queue.pop(0)
            if self.active_tag_info[0] >= 0 and self.active_tag_info[0] < len(self.master.sources):
                src = self.master.sources[self.active_tag_info[0]]; self.frame_idx, self.action_end_frame = src.tags.get(self.active_tag_info[1], (0,0)); self.anim_timer = 0
                if slot == "DASH": 
                    self.vx = 8 if self.facing_right else -8
                    self.master.play_sound('dash')
                elif slot == "JUMP" or slot == "JUMPATTACK":
                    self.master.play_sound('jump')
            else:
                self.active_tag_info = None; self.active_action_slot = None; self.action_queue = []
                return False
            return True
        return False

class AsepritePlayer:
    def __init__(self, initial_path=None, project_path=None, settings_path=None):
        self.project_path = os.path.abspath(project_path or os.path.join(APP_ROOT, "ase_project.json"))
        self.project_file_available = os.path.exists(self.project_path)
        self.settings_path = os.path.abspath(settings_path or os.path.join(APP_ROOT, "ase_settings.json"))
        self.language = set_current_language(LANG_KO)
        self.unity_pixels_per_unit = 100.0
        self.unity_parallax_export_format = "detailed"
        self.unity_parallax_include_disabled = True
        self.sources = []; self.profiles = []; self.cur_profile_idx = 0; self.cur_source_idx = 0; self.spawn_x, self.spawn_y = 400, 500; self.world_ground_y = 500.0; self.x, self.y = self.spawn_x, self.spawn_y; self.vx = self.vy = 0; self.grounded = False; self.jumps_left = 2; self.facing_right = True; self.zoom = 3.0; self.dash_speed = 12.0; self.jump_power = -18.0; self.gravity = 1.0; self.atk_forward_v = 15.0; self.powerbomb_speed = 35.0; self.cam_v_offset = -120; self.pbomb_pause_timer = 0; self.loop_counter = 0; self.cam_x, self.cam_y = 400, 300; self.cam_follow = True; self.platforms = [pygame.Rect(200, 350, 200, 20), pygame.Rect(500, 200, 200, 20), pygame.Rect(-200, 250, 300, 20), pygame.Rect(900, 300, 400, 20)]
        self.bg_layers = []; self.active_bg_layer = 0; self.bg_color = [15, 15, 18]; self.grid_color = [40, 40, 50]
        self.parallax_gizmo_enabled = False
        self.parallax_gizmo_dragging = False
        self.parallax_gizmo_drag_layer = None
        self.parallax_gizmo_drag_layer_ref = None
        self.parallax_gizmo_drag_axis = None
        self.parallax_gizmo_drag_start = None
        self.parallax_gizmo_drag_before = None
        self.parallax_gizmo_drag_dirty = False
        self.parallax_offset_history = []
        self.parallax_offset_redo_stack = []
        self.parallax_offset_edit = None
        self.parallax_history_status_key = ""
        self.performance_monitor = None
        self.selected_scene_actor_key = None
        self.scene_object_filter = SCENE_FILTER_ALL
        self.scene_status_message = ""
        self.resource_status_message = ""
        self.npc_intro_replay_status = ""
        self.solid_boxes = []
        self.frame_idx = 0; self.anim_timer = 0; self.combo_step = 0; self.combo_reset_timer = 0; self.attack_buffer = 0; self.active_action_slot = None; self.active_tag_info = None; self.action_queue = []; self.action_end_frame = -1; self.dash_charges = 2; self.dash_cooldowns = [0, 0]; self.dash_timer = 0; self.dash_started_grounded = False; self.attack_move_timer = 0; self.ai_list = []; self.partner_profiles = []; self.partner_list = []; self.temp_ai_list = []; self.prop_list = []; self.target_ai_count = 0; self.npc_max_hp = 10; self.last_npc_death_result = None; self.swap_timer = 0; self.visible = True; self.playback_speed = 1.0; self.is_paused = False; self.step_forward = False; self.show_hitboxes = True; self.target_w, self.target_h = 640, 360; self.show_viewport = True; self.shake_timer = 0; self.shake_intensity = 0; self.shake_enabled = True; self.base_shake = 0.2; self.debris_force = 0.3; self.afterimages = []; self.particles = []; self.sparks = []; self.projectiles = []; self.last_shot_frame = -1; self.hitstop_timer = 0; self.damage_numbers = []; self.vfx_enabled = True; self.is_ranged_combo = False; self.ghost_timer = 0; self.platform_alpha = 150; self.edit_platforms = False; self.selected_plat = None; self.drag_offset = (0,0); self.drop_through_timer = 0
        self.hp = 100; self.max_hp = 100; self.skill_cooldowns = [0, 0, 0]
        if pygame.font.get_init():
            self.font_10 = create_ui_font(10)
            self.font_12 = create_ui_font(12)
            self.font_b = create_ui_font(14, bold=True)
            self.font_dmg = create_ui_font(28, bold=True)
        else:
            self.font_10 = None; self.font_12 = None; self.font_b = None; self.font_dmg = None
        self.key_map = {"ATTACK": pygame.K_z, "DASH": pygame.K_x, "JUMP": pygame.K_SPACE, "SKILL1": pygame.K_c, "SKILL2": pygame.K_b, "SKILL3": pygame.K_n, "SUMMON": pygame.K_g, "SWAP": pygame.K_t, "SYNERGY": pygame.K_e, "HIT_1": pygame.K_v}
        self.popup = None
        self.sounds = {}
        if pygame.mixer.get_init():
            for snd in ['hit', 'jump', 'dash']:
                p = app_resource_path(os.path.join("sounds", f"{snd}.wav"))
                if os.path.exists(p): self.sounds[snd] = pygame.mixer.Sound(p)
        if initial_path:
            source_idx = self.add_source(initial_path)
            if source_idx is not None: self.add_profile("PLAYER", source_idx)
        
    def play_sound(self, name):
        if name in self.sounds and self.sounds[name]:
            self.sounds[name].set_volume(0.3)
            self.sounds[name].play()
    def update_bg_cache(self):
        zoom_changed = getattr(self, '_last_bg_zoom', None) != self.zoom
        if zoom_changed: self._last_bg_zoom = self.zoom
        
        for bg in self.bg_layers:
            if zoom_changed or bg.get('needs_update', True) or bg.get('cached_bg') is None:
                if bg.get('img'):
                    bw, bh = int(bg['img'].get_width()*bg['zoom']*self.zoom*0.5), int(bg['img'].get_height()*bg['zoom']*self.zoom*0.5)
                    bg['cached_bg'] = pygame.transform.scale(bg['img'], (max(1, bw), max(1, bh)))
                    if bg['alpha'] < 255: bg['cached_bg'].set_alpha(bg['alpha'])
                bg['needs_update'] = False
    def save_settings(self):
        bg_layers_data = []
        for bg in self.bg_layers:
            path = bg.get('path', '')
            bg_layers_data.append({"path": portable_path(path, self.settings_path) if path else "", "off_x": bg.get('off_x', 0), "off_y": bg.get('off_y', 0), "zoom": bg.get('zoom', 2.0), "alpha": bg.get('alpha', 255), "parallax": bg.get('parallax', 1.0), "loop_x": bg.get('loop_x', False)})
        try:
            unity_ppu = validate_unity_pixels_per_unit(self.unity_pixels_per_unit)
        except ValueError:
            unity_ppu = 100.0
        data = {"language": normalize_language(self.language), "unity_pixels_per_unit": unity_ppu, "unity_parallax_export_format": normalize_unity_parallax_export_format(self.unity_parallax_export_format), "unity_parallax_include_disabled": bool(self.unity_parallax_include_disabled), "physics": {"dash_speed": self.dash_speed, "jump_power": self.jump_power, "powerbomb_speed": self.powerbomb_speed, "cam_v_offset": self.cam_v_offset}, "combat": {"atk_forward_v": self.atk_forward_v, "is_ranged_combo": getattr(self, 'is_ranged_combo', False)}, "vfx": {"shake_enabled": self.shake_enabled, "vfx_enabled": self.vfx_enabled, "base_shake": self.base_shake, "debris_force": self.debris_force}, "viewport": {"show_viewport": self.show_viewport, "target_w": self.target_w, "target_h": self.target_h}, "bg": {"bg_color": self.bg_color, "layers": bg_layers_data}, "ai": {"target_ai_count": self.target_ai_count, "npc_max_hp": getattr(self, 'npc_max_hp', 10)}, "platforms": {"alpha": self.platform_alpha}, "controls": self.key_map}
        try:
            save_json(self.settings_path, data)
        except (OSError, TypeError, ValueError) as e:
            log_debug(f"[ERROR] Settings save failed: {e}")
            show_user_error(tr("error.settings_save_title"), tr("error.settings_save", path=self.settings_path), key=f"settings-save:{self.settings_path}:{type(e).__name__}")
    def load_settings(self, notify_missing_assets=True):
        if not hasattr(self, "key_map"):
            self.key_map = {"ATTACK": pygame.K_z, "DASH": pygame.K_x, "JUMP": pygame.K_SPACE, "SKILL1": pygame.K_c, "SKILL2": pygame.K_b, "SKILL3": pygame.K_n, "SUMMON": pygame.K_g, "SWAP": pygame.K_t, "SYNERGY": pygame.K_e, "HIT_1": pygame.K_v}
        self.popup = None # {'msg': str, 'cb': func}
        if os.path.exists(self.settings_path):
            try:
                missing_assets = []
                with open(self.settings_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if not isinstance(data, dict): raise ValueError("Settings root must be a JSON object.")
                    self.language = set_current_language(data.get("language", LANG_KO))
                    try:
                        self.unity_pixels_per_unit = validate_unity_pixels_per_unit(data.get("unity_pixels_per_unit", 100))
                    except ValueError:
                        self.unity_pixels_per_unit = 100.0
                    export_format = data.get("unity_parallax_export_format", "detailed")
                    self.unity_parallax_export_format = normalize_unity_parallax_export_format(export_format)
                    self.unity_parallax_include_disabled = bool(data.get("unity_parallax_include_disabled", True))
                    for cat_name, cat in data.items():
                        if isinstance(cat, dict):
                            if cat_name == "bg":
                                if "bg_color" in cat: self.bg_color = cat["bg_color"]
                                if "layers" in cat:
                                    self.bg_layers = []
                                    for l_data in cat["layers"]:
                                        stored_path = l_data.get("path", "")
                                        path, checked = resolve_stored_path(stored_path, self.settings_path)
                                        path = path or ""
                                        if stored_path and not path:
                                            log_debug(f"[ERROR] Background image not found: {stored_path}; checked={checked}"); missing_assets.append((stored_path, checked))
                                        layer = {"path": path, "off_x": l_data.get("off_x", 0), "off_y": l_data.get("off_y", 0), "zoom": l_data.get("zoom", 2.0), "alpha": l_data.get("alpha", 255), "parallax": l_data.get("parallax", 1.0), "loop_x": l_data.get("loop_x", False), "img": None, "cached_bg": None, "needs_update": True, "last_mtime": 0}
                                        if os.path.exists(path):
                                            layer["img"] = pygame.image.load(path).convert_alpha()
                                            layer["last_mtime"] = os.path.getmtime(path)
                                        self.bg_layers.append(layer)
                                elif "bg_path" in cat: # Legacy support
                                    stored_path = cat["bg_path"]
                                    path, checked = resolve_stored_path(stored_path, self.settings_path)
                                    path = path or ""
                                    if stored_path and not path:
                                        log_debug(f"[ERROR] Legacy background image not found: {stored_path}; checked={checked}"); missing_assets.append((stored_path, checked))
                                    layer = {"path": path, "off_x": cat.get("bg_off_x", 0), "off_y": cat.get("bg_off_y", 0), "zoom": cat.get("bg_zoom", 2.0), "alpha": cat.get("bg_alpha", 255), "parallax": cat.get("bg_parallax", 1.0), "loop_x": False, "img": None, "cached_bg": None, "needs_update": True, "last_mtime": 0}
                                    if os.path.exists(path):
                                        layer["img"] = pygame.image.load(path).convert_alpha()
                                        layer["last_mtime"] = os.path.getmtime(path)
                                    self.bg_layers = [layer]
                            else:
                                for k, v in cat.items():
                                    if k == "alpha" and "platforms" in data: self.platform_alpha = v
                                    elif hasattr(self, k): setattr(self, k, v)
                    if "controls" in data:
                        if not isinstance(data["controls"], dict): raise ValueError("'controls' must be a JSON object.")
                        self.key_map = data["controls"]
                        if "JUMP" not in self.key_map: self.key_map["JUMP"] = pygame.K_SPACE
                if missing_assets and notify_missing_assets:
                    names = "\n".join(f"- {stored}" for stored, _ in missing_assets)
                    show_user_error("Background files not found", f"These background files could not be restored:\n{names}\n\nUse SETUP > BG IMAGE to select them again. Details are in ase_debug.log.")
                return True
            except (OSError, json.JSONDecodeError, TypeError, ValueError, pygame.error) as e:
                log_debug(f"[ERROR] Settings load failed for {self.settings_path}: {e}")
                show_user_error(tr("error.settings_load_title"), tr("error.settings_load", path=self.settings_path))
                return False
        return True
    def save_project(self):
        try:
            invalid_profiles = [p.name for p in self.profiles if not isinstance(p.source_idx, int) or not 0 <= p.source_idx < len(self.sources)]
            if invalid_profiles:
                raise ValueError(f"Profiles reference missing sources: {', '.join(invalid_profiles)}")
            project = {
                "schema_version": 2,
                "sources": [portable_path(s.file_path, self.project_path) for s in self.sources],
                "source_kinds": [source_kind(s) for s in self.sources],
                "profiles": [
                    {
                        "name": p.name,
                        "source_idx": p.source_idx,
                        "kind": profile_kind(p, index),
                        "ai_behavior": normalize_npc_behavior(
                            getattr(p, "ai_behavior", "balanced"),
                        ),
                        "mappings": p.mappings,
                    }
                    for index, p in enumerate(self.profiles)
                ],
                "ai_count": self.target_ai_count,
                "platforms": [[p.x, p.y, p.w, p.h] for p in self.platforms],
                "solid_boxes": [[b.x, b.y, b.w, b.h] for b in self.solid_boxes],
            }
            save_json(self.project_path, project)
            self.project_file_available = True
        except (OSError, TypeError, ValueError, AttributeError) as e:
            log_debug(f"[ERROR] Project save failed: {e}")
            show_user_error(tr("error.project_save_title"), tr("error.project_save", path=self.project_path), key=f"project-save:{self.project_path}:{type(e).__name__}")
    def load_project(self):
        if os.path.exists(self.project_path):
            try:
                with open(self.project_path, "r", encoding="utf-8") as f:
                    p = json.load(f)
                if not isinstance(p, dict) or not isinstance(p.get("sources"), list) or not isinstance(p.get("profiles"), list):
                    raise ValueError("Required 'sources' and 'profiles' lists are missing.")
                resolved_sources = [None] * len(p["sources"])
                missing_sources = []
                for source_index, stored_path in enumerate(p["sources"]):
                    resolved, checked = resolve_stored_path(stored_path, self.project_path)
                    if resolved: resolved_sources[source_index] = resolved
                    else:
                        log_debug(f"[ERROR] Project source not found: {stored_path}; checked={checked}")
                        missing_sources.append((source_index, stored_path, checked))
                if missing_sources:
                    names = "\n".join(f"- {stored_path}" for _, stored_path, _ in missing_sources)
                    show_user_error("Project sources not found", f"These source files could not be restored:\n{names}\n\nSelect a replacement for each file. Canceling any selection cancels the entire load and keeps the current project unchanged.")
                    replacement_cache = {}
                    for source_index, stored_path, _ in missing_sources:
                        if stored_path not in replacement_cache:
                            replacement_cache[stored_path] = select_file([("Aseprite", "*.aseprite *.ase")])
                        replacement = replacement_cache[stored_path]
                        if not replacement:
                            log_debug(f"[LOAD] Project source replacement canceled: {stored_path}")
                            return False
                        resolved_sources[source_index] = replacement
                source_kinds = p.get("source_kinds", [])
                if source_kinds and (not isinstance(source_kinds, list) or len(source_kinds) != len(resolved_sources)):
                    raise ValueError("source_kinds must match the sources list.")
                prepared_sources = []
                try:
                    for source_index, resolved in enumerate(resolved_sources):
                        kind = source_kinds[source_index] if source_index < len(source_kinds) else "generic"
                        if kind not in {"generic", "npc", "prop"}:
                            raise ValueError(f"Unknown source kind: {kind}")
                        prepared_source = self._create_source(resolved, source_index)
                        prepared_source.kind = kind
                        prepared_source.is_prop_source = kind == "prop"
                        prepared_sources.append(prepared_source)
                except (AsepriteError, OSError, pygame.error) as e:
                    log_debug(f"[ERROR] Project source preparation failed: {e}")
                    show_user_error("Project sources could not be loaded", f"A source failed validation or Aseprite export.\n\n{e}\n\nThe current project was kept unchanged. See ase_debug.log for details.")
                    return False
                for prof_data in p["profiles"]:
                    if not isinstance(prof_data, dict) or not all(k in prof_data for k in ("name", "source_idx", "mappings")):
                        raise ValueError("A profile is missing name, source_idx, or mappings.")
                    if not isinstance(prof_data["source_idx"], int) or not 0 <= prof_data["source_idx"] < len(prepared_sources):
                        raise ValueError(f"Profile source_idx is out of range: {prof_data['source_idx']}")
                prepared_profiles = []
                for profile_index, prof_data in enumerate(p["profiles"]):
                    if not isinstance(prof_data["mappings"], dict): raise ValueError("Profile mappings must be a JSON object.")
                    kind = prof_data.get("kind")
                    if kind is None:
                        source_is_prop = source_kind(prepared_sources[prof_data["source_idx"]]) == "prop"
                        kind = "prop" if source_is_prop else ("player" if profile_index == 0 else "npc")
                    if kind not in {"player", "partner", "npc", "prop"}:
                        raise ValueError(f"Unknown profile kind: {kind}")
                    new_prof = AseProfile(prof_data["name"], prof_data["source_idx"], kind=kind)
                    new_prof.ai_behavior = normalize_npc_behavior(
                        prof_data.get("ai_behavior", "balanced"),
                    )
                    new_prof.mappings.update(prof_data["mappings"]); prepared_profiles.append(new_prof)
                    update_profile_ground_alignment(
                        type("_PreparedPlayer", (), {"sources": prepared_sources})(),
                        new_prof,
                    )
                    if kind == "prop":
                        prepared_sources[new_prof.source_idx].kind = "prop"
                        prepared_sources[new_prof.source_idx].is_prop_source = True
                prepared_platforms = [pygame.Rect(*data) for data in p.get("platforms", [])]
                prepared_boxes = [pygame.Rect(*data) for data in p.get("solid_boxes", [])]
                prepared_ai_count = p.get("ai_count", self.target_ai_count)
                if not isinstance(prepared_ai_count, int) or prepared_ai_count < 0: raise ValueError("ai_count must be a non-negative integer.")
                self.sources = prepared_sources; self.profiles = prepared_profiles; self.ai_list = []; self.partner_profiles = []; self.partner_list = []; self.temp_ai_list = []; self.prop_list = []
                self.visible = bool(
                    prepared_profiles
                    and profile_kind(prepared_profiles[0], 0) == "player"
                )
                if not self.profiles and self.sources: self.add_profile("PLAYER", 0)
                partner_roster_profiles(self)
                self.target_ai_count = prepared_ai_count; self.platforms = prepared_platforms; self.solid_boxes = prepared_boxes
                return True
            except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError, IndexError) as e:
                log_debug(f"[ERROR] Project load failed for {self.project_path}: {e}")
                show_user_error(tr("error.project_load_title"), tr("error.project_load", path=self.project_path))
                return False
        else: self.solid_boxes = []
        return False

    def _prepare_example(self, variant, source_factory=None, source_paths=None):
        preset = example_preset(variant)
        required = preset["sources"] + preset["bg_layers"]
        resolved = {}
        missing = []
        for resource in required:
            stored_path = resource["path"]
            resource_path = app_resource_path(stored_path)
            if not os.path.isfile(resource_path):
                missing.append(stored_path)
                continue
            actual_hash = file_sha256(resource_path)
            if actual_hash != resource["sha256"]:
                raise ValueError(f"Example resource checksum mismatch: {stored_path}")
            resolved[stored_path] = resource_path
        if missing:
            raise FileNotFoundError("Missing required example resources:\n" + "\n".join(missing))

        if source_paths is None:
            source_paths = [resolved[source["path"]] for source in preset["sources"]]
        if len(source_paths) != len(preset["sources"]):
            raise ValueError(f"{preset['name']} requires {len(preset['sources'])} Aseprite sources.")
        factory = source_factory or self._create_source
        prepared_sources = []
        for source_index, source_path in enumerate(source_paths):
            source = factory(source_path, source_index)
            source.id = source_index; source.kind = "generic"; source.is_prop_source = False
            prepared_sources.append(source)

        prepared_profiles = []
        for profile_data in preset["profiles"]:
            source_idx = profile_data["source_idx"]
            if not 0 <= source_idx < len(prepared_sources):
                raise ValueError(f"Profile source_idx is out of range: {source_idx}")
            mappings = profile_data["mappings"]
            if not isinstance(mappings, dict):
                raise ValueError(f"Mappings for {profile_data['name']} must be an object.")
            for entries in mappings.values():
                for mapping_source_idx, tag_name in entries:
                    if not 0 <= mapping_source_idx < len(prepared_sources):
                        raise ValueError(f"Mapping source_idx is out of range: {mapping_source_idx}")
                    if tag_name not in prepared_sources[mapping_source_idx].tags:
                        raise ValueError(f"Tag '{tag_name}' is missing from {prepared_sources[mapping_source_idx].name}.")
            profile = AseProfile(profile_data["name"], source_idx, kind=profile_data["kind"])
            profile.mappings.update(copy.deepcopy(mappings))
            profile.is_prop_profile = profile_data["kind"] == "prop"
            prepared_profiles.append(profile)

        prepared_layers = []
        for layer_data in preset["bg_layers"]:
            path = resolved[layer_data["path"]]
            image = pygame.image.load(path).convert_alpha()
            layer = {key: value for key, value in layer_data.items() if key not in ("sha256",)}
            layer.update({"path": path, "img": image, "cached_bg": None, "needs_update": True, "last_mtime": os.path.getmtime(path)})
            prepared_layers.append(layer)

        return {
            "preset": preset,
            "sources": prepared_sources,
            "profiles": prepared_profiles,
            "bg_layers": prepared_layers,
            "platforms": [pygame.Rect(*data) for data in preset["platforms"]],
            "solid_boxes": [pygame.Rect(*data) for data in preset["solid_boxes"]],
        }

    def _apply_prepared_example(self, prepared, persist=True):
        preset = prepared["preset"]
        self.sources = prepared["sources"]; self.profiles = prepared["profiles"]
        self.temp_ai_list = []; self.prop_list = []; self.ai_list = []; self.partner_profiles = []; self.partner_list = []
        self.cur_source_idx = 0; self.cur_profile_idx = 0
        self.bg_color = list(preset["bg_color"]); self.cam_v_offset = preset["cam_v_offset"]
        self.bg_layers = prepared["bg_layers"]; self.active_bg_layer = 0
        self.platforms = prepared["platforms"]; self.solid_boxes = prepared["solid_boxes"]
        for key, value in preset["physics"].items(): setattr(self, key, value)
        for key, value in preset["combat"].items(): setattr(self, key, value)
        for key, value in preset["vfx"].items(): setattr(self, key, value)
        for key, value in preset["viewport"].items(): setattr(self, key, value)
        self.target_ai_count = preset["ai_count"]; self.npc_max_hp = preset["npc_max_hp"]
        self.platform_alpha = preset["platform_alpha"]
        self.x, self.y = self.spawn_x, self.spawn_y; self.vx, self.vy = 0, 0
        self.cam_x, self.cam_y = self.x, self.y
        for profile, profile_data in zip(self.profiles, preset["profiles"]):
            if profile_data["kind"] == "partner": self.partner_profiles.append(profile)
            elif profile_data["kind"] == "npc": self.ai_list.append(AseAI(self, profile))
            elif profile_data["kind"] == "prop": self.prop_list.append(AseAI(self, profile, is_prop=True, hp=3))
        if persist: self.save_settings(); self.save_project()
        return True

    def _load_example(self, variant, persist=True, source_factory=None, source_paths=None):
        try:
            prepared = self._prepare_example(variant, source_factory=source_factory, source_paths=source_paths)
        except (AsepriteError, OSError, ValueError, TypeError, KeyError, IndexError, pygame.error) as e:
            log_debug(f"[ERROR] Example {variant} preparation failed: {e}")
            show_user_error("Example could not be loaded", f"{e}\n\nThe current project was kept unchanged. Required example resources are under resources/examples.")
            return False
        return self._apply_prepared_example(prepared, persist=persist)

    def load_example(self):
        return self._load_example(1)

    def load_example2(self):
        return self._load_example(2)
    def _create_source(self, path, source_id, is_prop_source=False, kind=None):
        resolved_kind = kind or ("prop" if is_prop_source else "generic")
        new_source = AseSource(path, source_id, kind=resolved_kind)
        new_source.is_prop_source = resolved_kind == "prop"
        return new_source
    def add_source(self, path, is_prop_source=False, kind=None):
        scene_snapshot = snapshot_scene_object_states(self)
        try:
            new_source = self._create_source(path, len(self.sources), is_prop_source, kind)
            self.sources.append(new_source); self.cur_source_idx = new_source.id; return new_source.id
        except (AsepriteError, OSError, pygame.error) as e:
            log_debug(f"[ERROR] Add source failed for {path}: {e}")
            show_user_error(tr("error.source_add_title"), tr("error.source_add", path=path, error=e))
            return None
        finally:
            restore_scene_object_states(self, scene_snapshot)

    def register_npc_source(self, path, profile_name=None):
        scene_snapshot = snapshot_scene_object_states(self)
        selected_key = getattr(self, "selected_scene_actor_key", None)
        try:
            source_index = self.add_source(path, kind="npc")
            if source_index is None:
                return None
            profile = self.add_profile(
                profile_name or f"NPC_{len(self.profiles)}", source_index, is_npc=True,
            )
            if profile is None:
                return None
            return {
                "source": self.sources[source_index],
                "source_idx": source_index,
                "profile": profile,
                "profile_idx": self.profiles.index(profile),
                "instance": self.ai_list[-1],
            }
        finally:
            restore_scene_object_states(self, scene_snapshot)
            if selected_key is not None:
                self.selected_scene_actor_key = selected_key

    def register_prop_source(self, path, profile_name=None):
        scene_snapshot = snapshot_scene_object_states(self)
        selected_key = getattr(self, "selected_scene_actor_key", None)
        try:
            source_index = self.add_source(path, is_prop_source=True, kind="prop")
            if source_index is None:
                return None
            profile = AseProfile(
                profile_name or f"PROP_{len(self.profiles)}",
                source_index, kind="prop",
            )
            profile.is_prop_profile = True
            self.profiles.append(profile)
            if not any(
                profile_kind(candidate, index) == "player"
                for index, candidate in enumerate(self.profiles)
            ):
                self.visible = False
            self.auto_map_profile(profile)
            instance = AseAI(self, profile, is_prop=True, hp=3)
            self.prop_list.append(instance)
            return {
                "source": self.sources[source_index],
                "source_idx": source_index,
                "profile": profile,
                "profile_idx": self.profiles.index(profile),
                "instance": instance,
            }
        finally:
            restore_scene_object_states(self, scene_snapshot)
            if selected_key is not None:
                self.selected_scene_actor_key = selected_key

    def spawn_npc_profile(self, profile_index, increase_target=True):
        if not isinstance(profile_index, int) or not 0 <= profile_index < len(self.profiles):
            return None
        profile = self.profiles[profile_index]
        if profile_kind(profile, profile_index) != "npc":
            return None
        instance = AseAI(self, profile)
        self.ai_list.append(instance)
        if increase_target:
            self.target_ai_count += 1
        return instance

    def remove_source_by_index(self, i):
        if i < 0 or i >= len(self.sources):
            return {"removed": False, "profiles": 0, "partners": 0, "npcs": 0, "props": 0, "player_disabled": False}

        removed_profiles = [profile for profile in self.profiles if profile.source_idx == i]
        removed_profile_ids = {id(profile) for profile in removed_profiles}
        active_player_removed = bool(
            self.profiles
            and profile_kind(self.profiles[0], 0) == "player"
            and id(self.profiles[0]) in removed_profile_ids
        )
        removed_npcs = sum(1 for ai in self.ai_list + self.temp_ai_list if id(ai.profile) in removed_profile_ids)
        removed_partners = sum(
            1 for profile in partner_roster_profiles(self)
            if id(profile) in removed_profile_ids
        )
        removed_props = sum(1 for prop in self.prop_list if id(prop.profile) in removed_profile_ids)

        self.sources.pop(i)
        for idx, s in enumerate(self.sources):
            s.id = idx

        self.profiles = [profile for profile in self.profiles if id(profile) not in removed_profile_ids]
        self.ai_list = [ai for ai in self.ai_list if id(ai.profile) not in removed_profile_ids]
        self.partner_profiles = [
            profile for profile in self.partner_profiles
            if id(profile) not in removed_profile_ids
        ]
        self.partner_list = []
        self.temp_ai_list = [ai for ai in self.temp_ai_list if id(ai.profile) not in removed_profile_ids]
        self.prop_list = [prop for prop in self.prop_list if id(prop.profile) not in removed_profile_ids]

        if self.cur_source_idx > i: self.cur_source_idx -= 1
        elif self.cur_source_idx >= len(self.sources): self.cur_source_idx = max(0, len(self.sources)-1)
        self.cur_profile_idx = min(self.cur_profile_idx, max(0, len(self.profiles) - 1))
        if active_player_removed:
            self.visible = False
            self.active_tag_info = None
            self.active_action_slot = None
            self.action_queue = []

        for prof in self.profiles:
            if prof.source_idx > i: prof.source_idx -= 1
            for slot, mappings in prof.mappings.items():
                prof.mappings[slot] = [m for m in mappings if m[0] != i]
                for mapping in prof.mappings[slot]:
                    if mapping[0] > i: mapping[0] -= 1

        for ent in [self] + self.ai_list + self.temp_ai_list + getattr(self, 'prop_list', []):
            if ent.active_tag_info and ent.active_tag_info[0] == i:
                ent.active_tag_info = None; ent.active_action_slot = None
            elif ent.active_tag_info and ent.active_tag_info[0] > i:
                ent.active_tag_info = [ent.active_tag_info[0] - 1, ent.active_tag_info[1]]
            ent.action_queue = [act for act in ent.action_queue if act[0] != i]
            for act in ent.action_queue:
                if act[0] > i: act[0] -= 1
        self.projectiles = [projectile for projectile in self.projectiles if projectile.source_idx != i]
        for projectile in self.projectiles:
            if projectile.source_idx is not None and projectile.source_idx > i:
                projectile.source_idx -= 1
        self.afterimages = [image for image in self.afterimages if image.get("s") != i]
        for image in self.afterimages:
            if image.get("s", -1) > i:
                image["s"] -= 1

        npc_indices = [index for index, profile in enumerate(self.profiles) if profile_kind(profile, index) == "npc"]
        if not npc_indices:
            self.target_ai_count = 0
            self.ai_list = []
            self.temp_ai_list = []
            self.roaming_npc_idx = 0
        else:
            if getattr(self, "roaming_npc_idx", -1) not in npc_indices:
                self.roaming_npc_idx = npc_indices[0]
        swap_candidates = swap_candidate_profile_indices(self)
        self.swap_target_idx = (
            getattr(self, "swap_target_idx", swap_candidates[0])
            if getattr(self, "swap_target_idx", -1) in swap_candidates
            else (swap_candidates[0] if swap_candidates else 0)
        )

        result = {
            "removed": True,
            "profiles": len(removed_profiles),
            "partners": removed_partners,
            "npcs": removed_npcs,
            "props": removed_props,
            "player_disabled": active_player_removed,
        }
        log_debug(
            f"[SOURCE] Removed source {i}; profiles={result['profiles']}, "
            f"partners={result['partners']}, npcs={result['npcs']}, props={result['props']}"
        )
        return result

    def add_profile(self, name, source_idx, is_npc=False):
        kind = "npc" if is_npc else ("player" if not any(profile_kind(p, idx) == "player" for idx, p in enumerate(self.profiles)) else "npc")
        if 0 <= source_idx < len(self.sources):
            ensure_source_slice_analysis(self.sources[source_idx])
        new_profile = AseProfile(name, source_idx, kind=kind); self.profiles.append(new_profile); self.auto_map_profile(new_profile)
        if 0 <= source_idx < len(self.sources) and kind == "npc" and source_kind(self.sources[source_idx]) == "generic":
            self.sources[source_idx].kind = "npc"
        if kind == "player":
            self.visible = True
        elif not any(
            profile_kind(candidate, index) == "player"
            for index, candidate in enumerate(self.profiles)
        ):
            self.visible = False
        if is_npc:
            profile_index = self.profiles.index(new_profile)
            instance = self.spawn_npc_profile(profile_index, increase_target=True)
            analysis = ensure_source_slice_analysis(self.sources[source_idx])
            log_debug(
                f"[NPC REGISTER] profile={new_profile.name} profile_index={profile_index} "
                f"kind={new_profile.kind} source_idx={source_idx} "
                f"source_path={self.sources[source_idx].file_path} "
                f"source_revision={getattr(self.sources[source_idx], 'source_revision', None)} "
                f"parts_valid={len(analysis['valid_parts_slices'])} "
                f"particles_valid={len(analysis['valid_particle_slices'])} "
                f"dead={new_profile.mappings.get('DEAD', [])} "
                f"dead_loop={new_profile.mappings.get('DEAD_LOOP', [])}"
            )
            if instance is None:
                return None
        return new_profile
    def auto_map_profile(self, profile):
        if profile.source_idx >= len(self.sources): return
        source = self.sources[profile.source_idx]
        for action in _detect_npc_combo_actions(source):
            profile.mappings.setdefault(action, [])
        if "INTRO" not in profile.mappings:
            profile.mappings["INTRO"] = []
        if not profile.mappings["INTRO"]:
            profile.mappings["INTRO"] = [
                [profile.source_idx, tag] for tag in spawn_intro_tags(source)
            ]
        if "DEAD_LOOP" not in profile.mappings:
            profile.mappings["DEAD_LOOP"] = []
        if not profile.mappings["DEAD_LOOP"]:
            dead_loop_tag = next(
                (
                    tag for tag in source.tag_list
                    if re.sub(r"[^a-z]", "", tag.casefold()) in {"deadloop", "deathloop"}
                ),
                None,
            )
            if dead_loop_tag:
                profile.mappings["DEAD_LOOP"] = [[profile.source_idx, dead_loop_tag]]
        if "DEAD" not in profile.mappings:
            profile.mappings["DEAD"] = []
        if not profile.mappings["DEAD"]:
            dead_tag = next(
                (
                    tag for tag in source.tag_list
                    if re.sub(r"[^a-z]", "", tag.casefold()) in {"dead", "death"}
                ),
                None,
            )
            if dead_tag:
                profile.mappings["DEAD"] = [[profile.source_idx, dead_tag]]
        suffix = re.compile(r"(_|\s)?\(?(ready|intro|loop|end)\)?", re.IGNORECASE)
        for slot in list(profile.mappings.keys()):
            if slot in {"INTRO", "DEAD_LOOP", "DEAD"}:
                continue
            base_slot = slot.lower().replace("ComboAttack_", "attack").replace(" ", "").replace("_", "")
            matches = []
            for t in source.tag_list:
                clean_t = suffix.sub("", t).lower().replace(" ", "").replace("_", "")
                is_match = False
                
                if clean_t == base_slot:
                    is_match = True
                elif (
                    base_slot in {"attack1", "comboattack1"}
                    and re.sub(r"[^a-z]", "", t.casefold()) == "attack"
                ):
                    is_match = True
                elif base_slot == "walk" and clean_t == "move":
                    is_match = True
                elif base_slot == "hit1":
                    if clean_t in ["hit", "hurt", "hita", "hit1", "hurta", "hurt1"]: is_match = True
                elif base_slot == "hit2":
                    if clean_t in ["hitb", "hit2", "hurtb", "hurt2"]: is_match = True
                    
                if is_match:
                    matches.append([profile.source_idx, t])
                    
            def sort_key(item): 
                tl = item[1].lower()
                if "ready" in tl or "intro" in tl: return 0
                if "end" in tl: return 2
                return 1
            profile.mappings[slot] = sorted(matches, key=sort_key)
        update_profile_ground_alignment(self, profile)
    def handle_attack(self, keys):
        if self.swap_timer > 0: return
        if not self.grounded:
            if keys[pygame.K_DOWN]: self.trigger_action("POWERBOMB", keys)
            else: self.trigger_action("JUMPATTACK", keys)
        elif self.profiles:
            # Check current attack slot and buffering
            if self.active_action_slot and "ComboAttack" in str(self.active_action_slot):
                if self.attack_buffer < 1: self.attack_buffer += 1
            else:
                # If reset timer expired, start from 1
                if self.combo_reset_timer <= 0: self.combo_step = 0
                slot = f"ComboAttack_{self.combo_step + 1}"
                # Check if this slot exists and has tags
                p = self.profiles[0]
                if not p.mappings.get(slot, []):
                    self.combo_step = 0
                    slot = "ComboAttack_1"
                self.trigger_action(slot, keys)

    def trigger_action(self, slot, keys=None):
        if self.swap_timer > 0 or not self.profiles: return
        
        if "SKILL" in slot:
            try:
                s_idx = int(slot[-1]) - 1
                if self.skill_cooldowns[s_idx] > 0: return
                self.skill_cooldowns[s_idx] = 3000 # 3 seconds CD
            except (ValueError, IndexError):
                log_debug_once(f"invalid-skill-slot:{slot}", f"[ERROR] Invalid skill slot ignored: {slot}")
                return

        # Dash can interrupt everything
        if slot == "DASH":
            if self.dash_charges > 0:
                log_debug(f"[ACTION] DASH triggered")
                self.dash_started_grounded = is_actor_grounded_for_dash_dust(self)
                self.dash_charges -= 1; self.dash_timer = 200; self.vx = self.dash_speed if self.facing_right else -self.dash_speed; self.vy = 0; self.active_action_slot = "DASH"; self.action_queue = list(self.profiles[0].mappings.get(slot, [])); self.play_next_in_queue()
                for i in range(2): 
                    if self.dash_cooldowns[i] <= 0: self.dash_cooldowns[i] = 1500; break
            return
        
        # Don't restart the same action unless it's a specific one
        if self.active_action_slot == slot and slot not in ["JUMP"]: return
        if self.active_action_slot and "ComboAttack" in str(self.active_action_slot) and "ComboAttack" not in slot: return
        
        profile = self.profiles[0]
        tags = profile.mappings.get(slot, [])
        
        if not tags and slot == "Swap_Exit":
             self.visible = False; return
             
        if not tags and slot == "FALL": # Fallback for Fall if no mapping
             self.active_action_slot = None; self.active_tag_info = None; return

        if tags:
            log_debug(f"[ACTION] Triggering {slot}")
            self.active_action_slot = slot; self.action_queue = list(tags); self.loop_counter = 0; self.anim_timer = 0; self.last_shot_frame = -1
            if "ComboAttack" in slot:
                # Update combo step
                self.combo_step = int(slot.split("_")[-1])
                self.combo_reset_timer = 1000 # 1 second window
                curr_keys = keys if keys is not None else pygame.key.get_pressed()
                if curr_keys[pygame.K_RIGHT] or curr_keys[pygame.K_LEFT]: 
                    self.attack_move_timer = 200; self.facing_right = curr_keys[pygame.K_RIGHT]; mv = self.atk_forward_v * 0.5
                    self.vx = mv if self.facing_right else -mv
                else: self.attack_move_timer = 0; self.vx = 0
            elif slot == "POWERBOMB": self.pbomb_pause_timer = 250; self.vy = 0; self.vx = 0
            elif slot == "FALL":
                # Explicit Sequence for Fall: Try to find Fall_Ready then Fall_Loop
                ready_tags = [t for t in tags if "ready" in t[1].lower()]
                loop_tags = [t for t in tags if "loop" in t[1].lower()]
                if ready_tags and loop_tags:
                    if getattr(self, "drop_through_timer", 0) > 0:
                        log_debug(f"[FALL] Drop Through Sequence: Loop({loop_tags[0][1]})")
                        self.action_queue = list(loop_tags)
                    else:
                        log_debug(f"[FALL] Sequence: Ready({ready_tags[0][1]}) -> Loop({loop_tags[0][1]})")
                        self.action_queue = list(ready_tags + loop_tags)
                elif tags:
                    log_debug(f"[FALL] Tags: {[t[1] for t in tags]}")
                    self.action_queue = list(tags)
            self.play_next_in_queue()

    def transition_to_passive_animation(self):
        previous_action = self.active_action_slot
        self.active_action_slot = None
        self.active_tag_info = None
        self.action_queue = []
        state = "WALK" if self.grounded and abs(self.vx) > 0.5 else (
            "IDLE" if self.grounded else ("JUMP" if self.vy < -4.0 else "FALL")
        )
        mappings = self.profiles[0].mappings.get(state, []) if self.profiles else []
        if mappings:
            source_index, tag_name = mappings[0]
            if 0 <= source_index < len(self.sources) and tag_name in self.sources[source_index].tags:
                self.frame_idx, self.action_end_frame = self.sources[source_index].tags[tag_name]
                self.anim_timer = 0
                if previous_action:
                    log_debug(f"[ACTION] {previous_action} complete -> {state} frame {self.frame_idx}")

    def play_next_in_queue(self):
        if self.action_queue:
            self.active_tag_info = self.action_queue.pop(0)
            if not self.active_tag_info or self.active_tag_info[0] < 0 or self.active_tag_info[0] >= len(self.sources):
                self.transition_to_passive_animation()
                return
            src = self.sources[self.active_tag_info[0]]
            if self.active_tag_info[1] in src.tags: 
                self.frame_idx, self.action_end_frame = src.tags[self.active_tag_info[1]]
                log_debug(f"  [QUEUE] Start Tag: {self.active_tag_info[1]} (Frames {self.frame_idx}-{self.action_end_frame})")
                self.loop_counter = 0; self.anim_timer = 0; self.last_shot_frame = -1
            else: self.play_next_in_queue()
        else:
            log_debug(f"  [QUEUE] Empty for {self.active_action_slot}")
            if self.attack_buffer > 0:
                self.attack_buffer -= 1
                next_step = self.combo_step + 1
                if next_step > 4: next_step = 1
                slot = f"ComboAttack_{next_step}"
                # If next combo doesn't exist, stop
                if not self.profiles[0].mappings.get(slot, []):
                    self.transition_to_passive_animation(); self.attack_buffer = 0
                else:
                    self.active_action_slot = None; self.trigger_action(slot)
                return
            self.transition_to_passive_animation(); self.attack_buffer = 0
            if getattr(self, 'pending_swap', False): self.execute_swap()

    def execute_swap(self):
        candidates = swap_candidate_profile_indices(self)
        if not candidates:
            return
        target_idx = getattr(self, 'swap_target_idx', 0)
        if target_idx not in candidates:
            target_idx = candidates[0]
            
        self.pending_swap = False
        old_player_profile = self.profiles[0]
        target_p = self.profiles[target_idx]
        partner_swap = profile_kind(target_p, target_idx) == "partner"
        player_position = (self.x, self.y)
        
        # Old Player -> Temporary AI for Exit
        temp_ai = AseAI(self, self.profiles[0], is_temp=True)
        # This transient Swap_Exit visual must stay behind the incoming Player.
        temp_ai.render_below_player = True
        temp_ai.is_swap_departure = True
        temp_ai.x, temp_ai.y = self.x, self.y
        temp_ai.vx, temp_ai.vy = self.vx, self.vy
        temp_ai.facing_right = self.facing_right
        
        # Inherit current action and attack buffer
        temp_ai.active_tag_info = self.active_tag_info
        temp_ai.action_queue = list(self.action_queue)
        temp_ai.active_action_slot = self.active_action_slot
        temp_ai.attack_buffer = getattr(self, 'attack_buffer', 0)
        temp_ai.combo_step = getattr(self, 'combo_step', 0)
        temp_ai.frame_idx = self.frame_idx
        temp_ai.anim_timer = self.anim_timer
        
        if not temp_ai.active_action_slot or "attack" not in temp_ai.active_action_slot.lower():
            temp_ai.trigger_action("Swap_Exit")
            
        self.temp_ai_list.append(temp_ai)
        
        # Swap profiles array
        self.profiles[0], self.profiles[target_idx] = target_p, self.profiles[0]
        if partner_swap:
            target_p.kind = "player"
            target_p.is_prop_profile = False
            old_player_profile.kind = "partner"
            old_player_profile.is_prop_profile = False
        
        # Keep roaming target assigned to the exact same profile if it was swapped
        roam_idx = getattr(self, 'roaming_npc_idx', 1 if len(self.profiles) > 1 else 0)
        if roam_idx == target_idx:
            self.roaming_npc_idx = 0
        elif roam_idx == 0:
            self.roaming_npc_idx = target_idx
        
        # The Player object owns scene placement; profiles only rotate through it.
        self.x, self.y = player_position
        self.facing_right = temp_ai.facing_right
        
        if partner_swap:
            self.partner_profiles = [
                profile for profile in partner_roster_profiles(self)
                if profile is not target_p
            ]
            if old_player_profile not in self.partner_profiles:
                self.partner_profiles.append(old_player_profile)
            self.partner_list = []
            selected_key = getattr(self, "selected_scene_actor_key", None)
            if selected_key and selected_key[0] == "partner":
                self.selected_scene_actor_key = ("player", id(self))
            self.swap_target_idx = target_idx
        else:
            # Legacy projects used an NPC profile as their swap candidate.
            target_ai = next((ai for ai in self.ai_list if ai.profile == target_p), None)
            if target_ai:
                self.ai_list.remove(target_ai)
            
        self.vx, self.vy = 0, 0
        self.active_tag_info = None; self.action_queue = []; self.active_action_slot = None
        self.combo_step = 0; self.combo_reset_timer = 0; self.attack_buffer = 0
        self.trigger_action("Swap_Enter")
        self.swap_vfx_timer = 400
        self.swap_vfx_max_timer = 400
        self.visible = True

    def valid_death_mapping(self, ai, slot):
        for mapping in ai.profile.mappings.get(slot, []):
            if not isinstance(mapping, (list, tuple)) or len(mapping) < 2:
                continue
            source_index, tag_name = mapping[0], mapping[1]
            if not isinstance(source_index, int) or not 0 <= source_index < len(self.sources):
                continue
            source = self.sources[source_index]
            tag_range = source.tags.get(tag_name)
            if not isinstance(tag_range, (list, tuple)) or len(tag_range) < 2:
                continue
            start, end = tag_range
            if not isinstance(start, int) or not isinstance(end, int) or not 0 <= start <= end < len(source.frames):
                continue
            try:
                if source.get_frame(start, 1.0, ai.facing_right) is not None:
                    return source_index, tag_name, start, end
            except (IndexError, TypeError, ValueError, pygame.error):
                continue
        return None

    def valid_dead_loop_mapping(self, ai):
        return self.valid_death_mapping(ai, "DEAD_LOOP")

    def activate_corpse(self, ai, mapping, slot):
        source_index, tag_name, start, end = mapping
        source = self.sources[source_index]
        metadata = getattr(source, "tag_metadata", {}).get(tag_name, {})
        direction = str(metadata.get("direction", "forward")).lower()
        _clear_npc_death_runtime_state(ai)
        ai.is_dead = True; ai.is_corpse = True; ai.vx = 0; ai.decision = "DEAD"
        if ai.is_prop:
            ai.grounded = False
        else:
            _snap_npc_corpse_to_ground(ai)
        ai.active_action_slot = slot; ai.active_tag_info = [source_index, tag_name]; ai.action_queue = []
        ai.action_end_frame = end; ai.anim_timer = 0
        ai.corpse_looping = (
            slot == "DEAD_LOOP"
            or "loop" in re.sub(r"[^a-z]", "", tag_name.casefold())
            or "repeat" in metadata
        )
        ai.corpse_anim_step = -1 if direction in {"reverse", "pingpong_reverse"} else 1
        ai.frame_idx = end if direction == "reverse" and ai.corpse_looping else start

    def create_precise_parts_from_analysis(self, source, analysis, world_x, world_y, facing_right, lifetime, outward=False):
        if analysis is None or not analysis.get("has_valid_parts"):
            return 0
        created = 0
        for item in analysis["valid_parts_slices"]:
            try:
                bounds = item["bounds"]
                image = item["image"] if facing_right else pygame.transform.flip(item["image"], True, False)
                if not image.get_bounding_rect().width:
                    continue
                if facing_right:
                    px = world_x + (bounds["x"] - source.orig_w // 2) + bounds["w"] / 2
                else:
                    px = world_x - (bounds["x"] - source.orig_w // 2 + bounds["w"]) + bounds["w"] / 2
                py = world_y + (bounds["y"] - source.orig_h // 2) + bounds["h"] / 2
                velocity_x = random.uniform(-15, 15) * self.debris_force
                if outward:
                    direction = 1 if px > world_x else (-1 if px < world_x else (1 if created % 2 == 0 else -1))
                    velocity_x = direction * random.uniform(8, 15) * self.debris_force
                self.particles.append(Particle(
                    px, py,
                    velocity_x,
                    random.uniform(-20, -5) * self.debris_force,
                    (255, 255, 255), 10, lifetime, image=image,
                ))
                created += 1
            except (KeyError, TypeError, ValueError, pygame.error) as e:
                log_debug(f"[WARN] Precise Parts item was skipped: {e}")
        return created

    def create_image_debris_from_tag_slices(self, source, tag_name, world_x, world_y, facing_right, lifetime):
        try:
            analysis = ensure_source_slice_analysis(source)
        except (KeyError, IndexError, TypeError, ValueError, pygame.error) as e:
            log_debug(f"[ERROR] Precise debris classification failed: {e}")
            return 0
        if analysis is None or not tag_name or tag_name != analysis["parts_tag"]:
            return 0
        return self.create_precise_parts_from_analysis(
            source, analysis, world_x, world_y, facing_right, lifetime,
        )

    def create_custom_hit_particles(self, source, world_x, world_y):
        try:
            analysis = ensure_source_slice_analysis(source)
        except (KeyError, IndexError, TypeError, ValueError, pygame.error) as e:
            log_debug_once("hit-slice-analysis", f"[ERROR] Hit Slice analysis failed; using fallback particles: {e}")
            return 0
        if analysis is None:
            return 0
        created = 0
        for item in analysis["valid_particle_slices"]:
            image = item["image"]
            if not image.get_bounding_rect().width:
                continue
            self.particles.append(Particle(
                world_x + random.uniform(-15, 15),
                world_y - 30 + random.uniform(-10, 10),
                random.uniform(-10, 10) * self.debris_force,
                random.uniform(-15, -5) * self.debris_force,
                (255, 255, 255), 10, random.randint(600, 1000), image=image,
            ))
            created += 1
        return created

    def create_grid_debris(self, source, frame_index, world_x, world_y, facing_right, lifetime):
        full_frame = source.get_frame(frame_index, 1.0, facing_right)
        if full_frame is None or not 0 <= frame_index < len(source.frames):
            return 0
        width, height = full_frame.get_size()
        cell_w, cell_h = width // 3, height // 3
        if cell_w <= 0 or cell_h <= 0:
            return 0
        frame_info = source.frames[frame_index]
        start_x = world_x + frame_info["ox"] if facing_right else world_x - frame_info["ox"] - width
        start_y = world_y + frame_info["oy"]
        created = 0
        for row in range(3):
            for column in range(3):
                cropped = pygame.Surface((cell_w, cell_h), pygame.SRCALPHA)
                cropped.blit(full_frame, (-column * cell_w, -row * cell_h))
                if not cropped.get_bounding_rect().width:
                    continue
                px = start_x + column * cell_w + cell_w // 2
                py = start_y + row * cell_h + cell_h // 2
                self.particles.append(Particle(
                    px, py,
                    random.uniform(-15, 15) * self.debris_force,
                    random.uniform(-20, -5) * self.debris_force,
                    (255, 255, 255), max(cell_w, cell_h), lifetime, image=cropped,
                ))
                created += 1
        return created

    def create_auto_alpha_debris(self, source, plan, world_x, world_y, facing_right, lifetime):
        if not plan or plan.get("mode") == "colored_fallback":
            return 0
        frame_index = plan["frame"]
        if not 0 <= frame_index < len(source.frames):
            return 0
        frame_info = source.frames[frame_index]
        created = 0
        for item in plan["pieces"]:
            try:
                original = item["image"]
                if original.get_width() < 1 or original.get_height() < 1 or _alpha_pixel_count(original) < 1:
                    continue
                image = original if facing_right else pygame.transform.flip(original, True, False)
                center_x = frame_info["ox"] + item["local_x"] + original.get_width() / 2
                px = world_x + center_x if facing_right else world_x - center_x
                py = world_y + frame_info["oy"] + item["local_y"] + original.get_height() / 2
                self.particles.append(Particle(
                    px, py,
                    random.uniform(-15, 15) * self.debris_force,
                    random.uniform(-20, -5) * self.debris_force,
                    (255, 255, 255), max(image.get_size()), lifetime, image=image,
                ))
                created += 1
            except (KeyError, TypeError, ValueError, pygame.error) as e:
                log_debug(f"[WARN] Auto Alpha part was skipped: {e}")
        return created

    def resolve_npc_corpse_mode(self, ai):
        dead_loop = self.valid_dead_loop_mapping(ai)
        if dead_loop:
            return {"mode": "dead_loop", "mapping": dead_loop, "slot": "DEAD_LOOP"}
        dead = self.valid_death_mapping(ai, "DEAD")
        if dead:
            return {"mode": "dead_hold", "mapping": dead, "slot": "DEAD"}
        return {"mode": "remove", "mapping": None, "slot": None}

    def spawn_npc_death_parts(self, ai, source, resolution):
        analysis = resolution["analysis"]
        requested = len(analysis["valid_parts_slices"])
        created = 0
        mode = resolution["mode"]
        if mode == "precise":
            created = self.create_precise_parts_from_analysis(
                source, analysis, ai.x, ai.y, ai.facing_right, 5000, outward=True,
            )
        if not created:
            plan = resolution["plan"] or build_auto_alpha_parts(source, ai.frame_idx)
            created = self.create_auto_alpha_debris(
                source, plan, ai.x, ai.y, ai.facing_right, 5000,
            )
            mode = plan["mode"]
        if not created:
            mode = "colored_fallback"
            for _ in range(10):
                self.particles.append(Particle(
                    ai.x, ai.y - 20,
                    random.uniform(-15, 15) * self.debris_force,
                    random.uniform(-20, -5) * self.debris_force,
                    (220, 38, 38), random.uniform(4, 8), 5000,
                ))
        return {"mode": mode, "requested": requested, "created": created}

    def trigger_npc_death(self, ai):
        if ai.is_dead: return None
        _clear_npc_death_runtime_state(ai)
        _snap_npc_corpse_to_ground(ai)
        profile = ai.profile
        profile_index = next((index for index, item in enumerate(self.profiles) if item is profile), -1)
        source_index = getattr(profile, "source_idx", -1)
        corpse = self.resolve_npc_corpse_mode(ai)
        source = self.sources[source_index] if 0 <= source_index < len(self.sources) else None
        analysis = ensure_source_slice_analysis(source) if source is not None else None
        resolution = resolve_npc_death_parts_mode(source, ai.frame_idx) if source is not None else None
        parts_valid = len(analysis["valid_parts_slices"]) if analysis else 0
        particles_before = len(self.particles)
        dead_tag = profile.mappings.get("DEAD", [])
        dead_loop_tag = profile.mappings.get("DEAD_LOOP", [])
        log_debug(
            f"[NPC DEATH BEGIN] instance_id={id(ai)} profile_index={profile_index} "
            f"profile_name={getattr(profile, 'name', 'NPC')} source_idx={source_index} "
            f"hp={getattr(ai, 'hp', None)} is_dead={ai.is_dead} "
            f"dead_tag={dead_tag} dead_loop_tag={dead_loop_tag} "
            f"parts_valid={parts_valid} particles_before={particles_before}"
        )
        if getattr(ai, "pending_execution", 0) > 0:
            if self.shake_enabled:
                self.shake_timer = 30; self.shake_intensity = 15
            for _ in range(15):
                self.particles.append(Particle(ai.x, ai.y - 30, random.uniform(-15, 15)*self.debris_force, random.uniform(-20, -5)*self.debris_force, (255, 255, 0), random.uniform(4, 10), 1000))
            for _ in range(10):
                angle = random.uniform(0, math.pi * 2)
                self.sparks.append(Spark(ai.x, ai.y - 30, angle, random.uniform(30, 60), (255, 255, 255), random.uniform(40, 80), random.uniform(2, 4), 400))

        if source is not None:
            parts_result = self.spawn_npc_death_parts(ai, source, resolution)
        else:
            parts_result = {"mode": "colored_fallback", "requested": 0, "created": 0}
            for _ in range(10):
                self.particles.append(Particle(
                    ai.x, ai.y - 20,
                    random.uniform(-15, 15) * self.debris_force,
                    random.uniform(-20, -5) * self.debris_force,
                    (220, 38, 38), random.uniform(4, 8), 5000,
                ))

        if corpse["mapping"]:
            self.activate_corpse(ai, corpse["mapping"], corpse["slot"])
        else:
            ai.is_dead = True
        if corpse["mode"] == "remove" and ai in self.ai_list:
            self.ai_list.remove(ai)
        self.target_ai_count = max(0, self.target_ai_count - 1)
        new_image_particles = [
            particle for particle in self.particles[particles_before:]
            if particle.image is not None
        ]
        result = {
            "instance": ai,
            "instance_id": id(ai),
            "profile": profile,
            "profile_index": profile_index,
            "source_idx": source_index,
            "revision": analysis.get("revision") if analysis else None,
            "corpse_mode": corpse["mode"],
            "parts_mode": parts_result["mode"],
            "requested": parts_result["requested"],
            "created": parts_result["created"],
            "particle_ids": {id(particle) for particle in new_image_particles},
            "particles_before": particles_before,
            "particles_after": len(self.particles),
            "update_logged": False,
            "render_logged": False,
            "remaining": None,
            "rendered": None,
        }
        self.last_npc_death_result = result
        log_debug(
            f"[NPC DEATH PARTS] corpse_mode={corpse['mode']} "
            f"parts_mode={parts_result['mode']} requested={parts_result['requested']} "
            f"created={parts_result['created']} particles_after={len(self.particles)}"
        )
        return result

    def trigger_synergy_attack(self):
        if getattr(self, 'synergy_cooldown', 0) > 0 or len(self.profiles) <= 1: return
        
        # Find a target NPC that is alive, within range, and has <= 25% max_hp
        target_ai = None
        for ai in self.ai_list:
            if not getattr(ai, 'is_prop', False) and not ai.is_dead and ai.visible:
                max_hp = getattr(ai, 'max_hp', 10)
                if ai.hp <= max_hp * 0.25:
                    dist_x = abs(self.x - ai.x)
                    dist_y = abs(self.y - ai.y)
                    # Increased range for easier execution
                    if dist_x < 500 and dist_y < 200:
                        target_ai = ai
                        break
                        
        if not target_ai: return # No suitable target found
        
        self.synergy_cooldown = 5000 # 5 seconds cooldown
        self.synergy_vfx_timer = 1000 # 1 second of cinematic slow-mo and darkening
        
        # Turn player towards the target
        self.facing_right = self.x < target_ai.x
        
        # 1. Player triggers SKILL 1 or ComboAttack_1
        p_prof = self.profiles[0]
        if p_prof.mappings.get("SKILL 1"):
            self.trigger_action("SKILL 1")
        elif p_prof.mappings.get("ComboAttack_1"):
            self.trigger_action("ComboAttack_1")
            
        # 2. Spawn Assist AI (Temporary)
        assist_idx = getattr(self, 'swap_target_idx', 0)
        if assist_idx == 0 or assist_idx >= len(self.profiles): assist_idx = 1
        target_p = self.profiles[assist_idx]
        
        assist_ai = AseAI(self, target_p, is_temp=True)
        
        # Position the assist AI on the opposite side of the NPC
        offset = 60
        if self.x < target_ai.x:
            assist_ai.x = target_ai.x + offset
            assist_ai.facing_right = False
        else:
            assist_ai.x = target_ai.x - offset
            assist_ai.facing_right = True
            
        assist_ai.y = self.y # Match player's Y level
        
        skill_slot = "SKILL 1" if target_p.mappings.get("SKILL 1") else "ComboAttack_1"
        tags_enter = list(target_p.mappings.get("Swap_Enter", []))
        tags_skill = list(target_p.mappings.get(skill_slot, []))
        
        assist_ai.active_action_slot = skill_slot
        
        # Determine the total duration of the player's attack to sync the assist AI
        player_attack_duration = 0
        if p_prof.mappings.get(skill_slot):
            p_src = self.sources[0]
            for tag_info in p_prof.mappings.get(skill_slot):
                f_start, f_end = p_src.tags.get(tag_info[1], (0, 0))
                for f in range(f_start, f_end + 1):
                    if f < len(p_src.frames): player_attack_duration += p_src.frames[f]['duration']
        
        assist_ai.action_queue = tags_enter + tags_skill
        if assist_ai.action_queue:
            assist_ai.active_tag_info = assist_ai.action_queue.pop(0)
            if assist_ai.active_tag_info[0] >= 0 and assist_ai.active_tag_info[0] < len(self.sources):
                src = self.sources[assist_ai.active_tag_info[0]]
                assist_ai.frame_idx, assist_ai.action_end_frame = src.tags.get(assist_ai.active_tag_info[1], (0,0))
                assist_ai.anim_timer = 0
                
        # Make assist AI invincible to hitstop during this intro phase so they don't fall behind
        assist_ai.synergy_invulnerable = True
        
        self.temp_ai_list.append(assist_ai)
        
        # Mark NPC for delayed execution on the next hit
        target_ai.pending_execution = 2000

    def trigger_prop_death(self, ai):
        if ai.is_dead: return None
        dead_loop_mapping = self.valid_dead_loop_mapping(ai)
        if dead_loop_mapping:
            self.activate_corpse(ai, dead_loop_mapping, "DEAD_LOOP")
            return "corpse_loop"
        dead_mapping = self.valid_death_mapping(ai, "DEAD")
        if dead_mapping:
            self.activate_corpse(ai, dead_mapping, "DEAD")
            return "corpse_dead"
        ai.is_dead = True
        branch = "fallback"
        created = 0
        if ai.profile.source_idx >= 0 and ai.profile.source_idx < len(self.sources):
            prop_src = self.sources[ai.profile.source_idx]
            analysis = ensure_source_slice_analysis(prop_src)
            created = self.create_precise_parts_from_analysis(
                prop_src, analysis, ai.x, ai.y, ai.facing_right, 10000,
            )
            if created:
                branch = "parts"
            if not created:
                created = self.create_grid_debris(prop_src, ai.frame_idx, ai.x, ai.y, ai.facing_right, 10000)
                if created:
                    branch = "grid"
        if not created:
            for _ in range(15):
                self.particles.append(Particle(ai.x, ai.y - 20, random.uniform(-15, 15)*self.debris_force, random.uniform(-20, -5)*self.debris_force, (139, 69, 19), random.uniform(4, 8), random.randint(500, 1000)))
        if ai in getattr(self, 'prop_list', []): self.prop_list.remove(ai)
        return branch

    def check_hits(self):
        if not self.active_tag_info or self.active_tag_info[0] < 0 or self.active_tag_info[0] >= len(self.sources): return
        src = self.sources[self.active_tag_info[0]]
        hitboxes = []
        has_hit_slice = False
        shoot_pt = None
        for name, keys in src.slices.items():
            active_key = None
            for key in keys:
                if key['frame'] <= self.frame_idx:
                    if active_key is None or key['frame'] > active_key['frame']: active_key = key
            if active_key:
                b = active_key['bounds']
                ox = (b['x'] - src.orig_w // 2) if self.facing_right else -(b['x'] - src.orig_w // 2 + b['w'])
                if "shoot" in name.lower():
                    shoot_pt = (self.x + ox + b['w']//2, self.y + b['y'] - src.orig_h // 2 + b['h']//2)
                elif "hit" in name.lower() and not getattr(self, 'is_ranged_combo', False):
                    has_hit_slice = True
                    hitboxes.append(pygame.Rect(self.x + ox, self.y + b['y'] - src.orig_h // 2, b['w'], b['h']))

        if self.active_action_slot:
            slot_l = self.active_action_slot.lower()
            tag_name_l = self.active_tag_info[1].lower()
            if ("attack" in slot_l or "powerbomb" in slot_l or "dash" in slot_l or "skill" in slot_l) and "ready" not in tag_name_l and "end" not in tag_name_l:
                tr = src.tags.get(self.active_tag_info[1], (0, 0))
                # Only trigger on the first frame of the attack animation
                if self.frame_idx == tr[0] and getattr(self, 'last_shot_frame', -1) != self.frame_idx:
                    self.last_shot_frame = self.frame_idx
                    if getattr(self, 'is_ranged_combo', False) and "attack" in slot_l:
                        proj_vx = 15 if self.facing_right else -15
                        px, py = shoot_pt if shoot_pt else (self.x + (20 if self.facing_right else -20), self.y - 30)
                        ptag = next((t for t in src.tags.keys() if "projectile" in t.lower() or "shoot" in t.lower()), None)
                        self.projectiles.append(Projectile(self, px, py, proj_vx, 0, self.active_tag_info[0] if ptag else None, ptag))
                        self.play_sound('dash')
                    elif not has_hit_slice:
                        hw, hh = 90, 50
                        # Enlarge hitbox significantly if this is a synergy attack
                        if "skill" in slot_l and getattr(self, 'synergy_vfx_timer', 0) > 0:
                            hw, hh = 150, 100
                            self.vx = 20 if self.facing_right else -20
                            
                        ox = 10 if self.facing_right else -10 - hw
                        hitboxes.append(pygame.Rect(self.x + ox, self.y - 50, hw, hh))

        for ai in self.ai_list[:] + getattr(self, 'prop_list', [])[:]:
            if getattr(ai, 'last_hit_frame_idx', -1) != self.frame_idx and ai.visible and not ai.is_dead:
                ai_rect = pygame.Rect(ai.x - 20, ai.y - 60, 40, 60) # Default approximate hurtbox
                for hb in hitboxes:
                    if hb.colliderect(ai_rect):
                        dmg = random.randint(1, 3)
                        ai.hp -= dmg; ai.last_hit_frame_idx = self.frame_idx
                        
                        # Add floating damage number
                        self.damage_numbers.append({'val': dmg, 'x': ai.x + random.uniform(-10, 10), 'y': ai.y - 60, 'lifetime': 1000, 'max_life': 1000, 'vy': -2})
                        
                        if self.shake_enabled: self.shake_timer = 10; self.shake_intensity = 5
                        self.hitstop_timer = 120 # 120ms Hit-stop for impact (Increased for better feel)
                        self.play_sound('hit')

                        # Knockback (only for NPCs, not props)
                        if not getattr(ai, 'is_prop', False):
                            ai.vx = 8 if self.x < ai.x else -8
                            ai.vy = -6 # Increased airborne knockback
                            
                            ai.hit_count = getattr(ai, 'hit_count', 0) + 1
                            hit_slot = "HIT_1" if ai.hit_count % 2 == 1 else "HIT_2"
                            if not ai.profile.mappings.get(hit_slot, []): hit_slot = "HIT_1"
                            ai.trigger_action(hit_slot)                        
                        # Generate Impact Sparks
                        for _ in range(5):
                            angle = random.uniform(math.pi*0.8, math.pi*1.2) if self.x < ai.x else random.uniform(-math.pi*0.2, math.pi*0.2)
                            self.sparks.append(Spark(ai.x, ai.y - 30, angle, random.uniform(20, 40), (255, 200, 50), random.uniform(15, 30), random.uniform(1, 2), 200))
                            
                        # Generate Hit Particles
                        hit_particles_spawned = False
                        if 0 <= ai.profile.source_idx < len(self.sources):
                            hit_source = self.sources[ai.profile.source_idx]
                            hit_particles_spawned = self.create_custom_hit_particles(hit_source, ai.x, ai.y) > 0
                                                
                        if not hit_particles_spawned:
                            for _ in range(8):
                                self.particles.append(Particle(ai.x, ai.y - 30, random.uniform(-10, 10)*self.debris_force, random.uniform(-15, -5)*self.debris_force, (200, 200, 200) if getattr(ai, 'is_prop', False) else (220, 38, 38), random.uniform(2, 5), random.randint(300, 600)))
                        
                        if getattr(ai, 'is_prop', False):
                            ai.stage_hp -= 1
                            if ai.stage_hp <= 0:
                                ai.prop_state += 1 # Advance to next break state
                                
                                # Check if the next Break state actually exists in the Aseprite file.
                                # If Break1 or Break2 doesn't exist, immediately skip to destruction (state 3).
                                if ai.prop_state < 3:
                                    next_state_name = f"Break{ai.prop_state}"
                                    if not ai.profile.mappings.get(next_state_name, []):
                                        ai.prop_state = 3 # Fast-forward to total destruction
                                
                                if ai.prop_state >= 3:
                                    self.trigger_prop_death(ai)
                                else:
                                    # Reset HP for the next stage (Break1 or Break2)
                                    ai.stage_hp = 3
                        else:
                            if ai.hp <= 0 or getattr(ai, 'pending_execution', 0) > 0:
                                self.trigger_npc_death(ai)
                        break # Only hit once per attack frame

        # Check hits on interactive debris particles
        for p in getattr(self, 'particles', []):
            if getattr(p, 'hit_cooldown', 0) > 0:
                p.hit_cooldown -= 16.6
                continue
            pw = p.image.get_width() if p.image else p.size
            ph = p.image.get_height() if p.image else p.size
            p_rect = pygame.Rect(p.x - pw/2, p.y - ph/2, pw, ph)
            for hb in hitboxes:
                if hb.colliderect(p_rect):
                    p.vx = (random.uniform(5, 20) if self.facing_right else random.uniform(-20, -5)) * self.debris_force
                    p.vy = random.uniform(-15, -5) * self.debris_force
                    p.rot_speed = random.uniform(-30, 30)
                    p.lifetime = min(p.max_life, p.lifetime + 2000) # Give it some extra life if kicked
                    p.hit_cooldown = 300 # Prevent multi-hits
                    break
                    
        # Check Projectile Hits
        for proj in getattr(self, 'projectiles', []):
            if not proj.active: continue
            # Approximate projectile hitbox (e.g. 30x30)
            proj_rect = pygame.Rect(proj.x - 15, proj.y - 15, 30, 30)
            
            for ai in self.ai_list[:] + getattr(self, 'prop_list', [])[:]:
                if ai.hit_cooldown <= 0 and ai.visible and not ai.is_dead:
                    ai_rect = pygame.Rect(ai.x - 20, ai.y - 60, 40, 60)
                    if proj_rect.colliderect(ai_rect):
                        dmg = random.randint(1, 3)
                        ai.hp -= dmg; ai.hit_cooldown = 150
                        self.damage_numbers.append({'val': dmg, 'x': ai.x + random.uniform(-10, 10), 'y': ai.y - 60, 'lifetime': 1000, 'max_life': 1000, 'vy': -2})
                        
                        if self.shake_enabled: self.shake_timer = 10; self.shake_intensity = 3
                        
                        if not getattr(ai, 'is_prop', False):
                            ai.vx = 6 if proj.vx > 0 else -6
                            ai.vy = -4
                            
                            ai.hit_count = getattr(ai, 'hit_count', 0) + 1
                            hit_slot = "HIT_1" if ai.hit_count % 2 == 1 else "HIT_2"
                            if not ai.profile.mappings.get(hit_slot, []): hit_slot = "HIT_1"
                            ai.trigger_action(hit_slot)
                        
                        # Generate Impact Sparks
                        for _ in range(5):
                            angle = random.uniform(math.pi*0.8, math.pi*1.2) if proj.vx > 0 else random.uniform(-math.pi*0.2, math.pi*0.2)
                            self.sparks.append(Spark(ai.x, ai.y - 30, angle, random.uniform(20, 40), (255, 200, 50), random.uniform(15, 30), random.uniform(1, 2), 200))
                            
                        if getattr(ai, 'is_prop', False):
                            ai.stage_hp -= 1
                            if ai.stage_hp <= 0:
                                ai.prop_state += 1
                                if ai.prop_state < 3:
                                    next_state_name = f"Break{ai.prop_state}"
                                    if not ai.profile.mappings.get(next_state_name, []):
                                        ai.prop_state = 3
                                if ai.prop_state >= 3:
                                    self.trigger_prop_death(ai)
                                else:
                                    ai.stage_hp = 3
                        else:
                            if ai.hp <= 0:
                                self.trigger_npc_death(ai)
                            
                        proj.active = False
                        proj.lifetime = 0
                        break

    def update(self, keys, ground_y, dt):
        original_dt = dt
        performance = self.performance_monitor
        if hasattr(self, "_btn_lock"):
            self._btn_lock -= 1
            if self._btn_lock <= 0: delattr(self, "_btn_lock")
            
        if getattr(self, 'synergy_cooldown', 0) > 0:
            self.synergy_cooldown -= original_dt
            
        if getattr(self, 'synergy_vfx_timer', 0) > 0:
            self.synergy_vfx_timer -= original_dt
            dt = dt * 0.3 # 30% speed for cinematic slow-mo
            
        if getattr(self, 'hitstop_timer', 0) > 0:
            self.hitstop_timer -= original_dt
            dt = dt * getattr(self, 'hitstop_slow_factor', 0.1) # Variable slow down
        else:
            self.hitstop_slow_factor = 0.1
            
        self.check_hits()
        
        # Update particles and compact survivors in one pass.
        particle_update_started = time.perf_counter_ns() if performance and performance.enabled else None
        alive_particles = []
        for p in self.particles:
            p.update(dt, self.gravity, ground_y, self.platforms)
            if p.lifetime > 0:
                alive_particles.append(p)
        self.particles = alive_particles
        death_result = getattr(self, "last_npc_death_result", None)
        if isinstance(death_result, dict) and not death_result.get("update_logged"):
            tracked = [
                particle for particle in self.particles
                if id(particle) in death_result.get("particle_ids", set())
            ]
            visible = sum(
                1 for particle in tracked
                if particle.image is not None
                and particle.lifetime > 0
                and particle.image.get_width() > 0
                and particle.image.get_height() > 0
                and _alpha_pixel_count(particle.image) > 0
            )
            death_result["remaining"] = len(tracked)
            death_result["image_particles"] = len(tracked)
            death_result["visible"] = visible
            death_result["update_logged"] = True
            log_debug(
                f"[NPC DEATH UPDATE] created={death_result['created']} "
                f"remaining={len(tracked)} image_particles={len(tracked)} visible={visible}"
            )
        alive_sparks = []
        for s in getattr(self, 'sparks', []):
            s.update(dt)
            if s.lifetime > 0:
                alive_sparks.append(s)
        self.sparks = alive_sparks
        alive_projectiles = []
        for proj in getattr(self, 'projectiles', []):
            proj.update(dt)
            if proj.lifetime > 0:
                alive_projectiles.append(proj)
        self.projectiles = alive_projectiles
            
        # Update Damage Numbers
        alive_damage_numbers = []
        for dmg in getattr(self, 'damage_numbers', []):
            dmg['lifetime'] -= dt
            if dmg['lifetime'] > 0:
                dmg['y'] += dmg['vy'] * (dt/16.6)
                alive_damage_numbers.append(dmg)
        self.damage_numbers = alive_damage_numbers
        if performance and performance.enabled:
            performance.record_since("particle_update", particle_update_started)
            
        while sum(1 for ai in self.ai_list if not ai.is_dead) < self.target_ai_count:
            npc_indices = [index for index, profile in enumerate(self.profiles) if profile_kind(profile, index) == "npc"]
            if not npc_indices:
                self.target_ai_count = 0
                break
            roam_idx = getattr(self, 'roaming_npc_idx', npc_indices[0])
            if roam_idx not in npc_indices:
                roam_idx = npc_indices[0]
                self.roaming_npc_idx = roam_idx
            self.spawn_npc_profile(roam_idx, increase_target=False)
        while sum(1 for ai in self.ai_list if not ai.is_dead) > self.target_ai_count:
            removable = next((ai for ai in reversed(self.ai_list) if not ai.is_dead), None)
            if removable is None: break
            self.ai_list.remove(removable)
        if self.drop_through_timer > 0: self.drop_through_timer -= dt
        if self.shake_timer > 0: self.shake_timer -= dt / 16.6
        if getattr(self, 'swap_vfx_timer', 0) > 0: self.swap_vfx_timer -= dt
        if self.vfx_enabled:
            alive_afterimages = []
            for ai in self.afterimages:
                ai['alpha'] -= 15 * (dt/16.6)
                if ai['alpha'] > 0:
                    alive_afterimages.append(ai)
            self.afterimages = alive_afterimages
            if self.dash_timer > 0:
                self.ghost_timer += dt
                if self.ghost_timer >= 30: 
                    self.ghost_timer = 0; s_idx = self.active_tag_info[0] if self.active_tag_info else 0; self.afterimages.append({'x': self.x, 'y': self.y, 's': s_idx, 'f': self.frame_idx, 'right': self.facing_right, 'alpha': 180})
        if self.swap_timer > 0:
            self.swap_timer -= dt
            if self.swap_timer <= 0: self.x, self.y = self.spawn_x, self.spawn_y; self.visible = True; self.trigger_action("Swap_Enter")
            return
        for i in range(2):
            if self.dash_cooldowns[i] > 0:
                self.dash_cooldowns[i] -= dt
                if self.dash_cooldowns[i] <= 0: self.dash_charges = min(2, self.dash_charges + 1)
        for i in range(3):
            if self.skill_cooldowns[i] > 0:
                self.skill_cooldowns[i] = max(0, self.skill_cooldowns[i] - dt)
        if self.pbomb_pause_timer > 0:
            self.pbomb_pause_timer -= dt; self.vy = 0
            if self.pbomb_pause_timer <= 0: self.vy = self.powerbomb_speed; self.pbomb_pause_timer = 0
        elif self.dash_timer > 0: self.dash_timer -= dt; self.vy = 0
        elif self.attack_move_timer > 0: self.attack_move_timer -= dt; self.vy += self.gravity * 0.5
        else:
            self.vx *= 0.82; can_move = not self.active_tag_info or self.active_action_slot in ["FALL", "JUMPATTACK"]
            if can_move:
                if keys[pygame.K_RIGHT]: self.vx = 4.2; self.facing_right = True
                elif keys[pygame.K_LEFT]: self.vx = -4.2; self.facing_right = False
            self.vy += self.gravity * (dt / 16.6)
        # X-Axis Movement & Collision
        self.x += self.vx * (dt/16.6)
        if hasattr(self, "solid_boxes"):
            player_rect = pygame.Rect(self.x-10, self.y-50, 20, 50) # Approx Hitbox
            for box in self.solid_boxes:
                if box.colliderect(player_rect):
                    if self.vx > 0: self.x = box.left - 10
                    elif self.vx < 0: self.x = box.right + 10
                    self.vx = 0

        # Y-Axis Movement & Collision
        self.y += self.vy * (dt/16.6); self.grounded = False
        if hasattr(self, "solid_boxes"):
            player_rect = pygame.Rect(self.x-10, self.y-50, 20, 50)
            for box in self.solid_boxes:
                if box.colliderect(player_rect):
                    if self.vy > 0: 
                        self.y = box.top + 50; self.grounded = True; self.vy = 0; self.jumps_left = 2
                        if self.active_action_slot == "FALL": self.active_tag_info = None; self.active_action_slot = None
                    elif self.vy < 0: self.y = box.bottom + 50; self.vy = 0
        
        # Grounding Logic
        if self.y >= ground_y: 
            if self.active_action_slot == "POWERBOMB" and self.vy > 0 and self.shake_enabled: self.shake_timer = 15; self.shake_intensity = 15
            self.y = ground_y; self.vy = 0; self.grounded = True; self.jumps_left = 2
            if self.active_action_slot == "FALL": self.active_tag_info = None; self.active_action_slot = None
        if self.vy >= 0 and self.drop_through_timer <= 0:
            for plat in self.platforms:
                if plat.collidepoint(self.x, self.y) and self.y - (self.vy * (dt/16.6)) <= plat.top + 10: 
                    # PowerBomb Impact on Platform
                    if self.active_action_slot == "POWERBOMB" and self.shake_enabled: self.shake_timer = 15; self.shake_intensity = 15
                    self.y = plat.top; self.vy = 0; self.grounded = True; self.jumps_left = 2
                    if self.active_action_slot == "FALL": self.active_tag_info = None; self.active_action_slot = None

        # Ground dust belongs only to a dash that started and remains grounded.
        # This runs after collision/grounding so walking off a ledge cannot emit
        # one extra airborne dust particle from the previous frame's state.
        emit_ground_dash_dust(self)
        
        if self.grounded and (self.active_action_slot == "JUMPATTACK" or self.active_action_slot == "POWERBOMB"):
            if self.active_tag_info: self.play_next_in_queue()
        if self.cam_follow:
            self.cam_x += (self.x - self.cam_x) * 0.25; self.cam_y += (self.y + self.cam_v_offset - self.cam_y) * (0.3 if self.grounded else 0.25)
        
        # Combo Reset Logic
        if self.combo_reset_timer > 0:
            self.combo_reset_timer -= dt
            if self.combo_reset_timer <= 0: self.combo_step = 0
            
        if self.visible:
            if not self.active_tag_info:
                # Early Fall Trigger: Change state to FALL when upward velocity slows down (vy > -4.0)
                state = "WALK" if self.grounded and abs(self.vx) > 0.5 else ("IDLE" if self.grounded else ("JUMP" if self.vy < -4.0 else "FALL"))
                if state == "FALL" and self.active_action_slot != "FALL" and self.active_action_slot != "POWERBOMB": self.trigger_action("FALL")
                if not self.active_tag_info:
                    m = self.profiles[0].mappings.get(state, []) if self.profiles else []; target_info = m[0] if m else None
                else: target_info = self.active_tag_info
            else: target_info = self.active_tag_info
            
            if target_info and target_info[0] >= 0 and target_info[0] < len(self.sources):
                src = self.sources[target_info[0]]; tr = src.tags.get(target_info[1], (0,0))
                if self.frame_idx < tr[0] or self.frame_idx > tr[1]: self.frame_idx = tr[0]; self.anim_timer = 0
                if not self.is_paused or self.step_forward:
                    self.anim_timer += dt
                    if self.step_forward: self.anim_timer = src.frames[self.frame_idx]['duration']; self.step_forward = False
                if self.frame_idx < len(src.frames):
                    dur = src.frames[self.frame_idx]['duration']
                    if self.anim_timer >= dur:
                        self.frame_idx += 1; self.anim_timer = 0
                        if self.active_tag_info and self.frame_idx > self.action_end_frame:
                            if target_info[1] == "Swap_Exit": self.visible = False; self.swap_timer = 500; self.active_tag_info = None; return
                            is_skill = "SKILL" in str(self.active_action_slot)
                            is_loop = "(loop)" in target_info[1].lower()
                            is_fall = self.active_action_slot == "FALL"
                            
                            if is_loop:
                                if is_fall or not is_skill: self.frame_idx = tr[0] # Continuous loop
                                elif is_skill and self.loop_counter < 1: self.frame_idx = tr[0]; self.loop_counter += 1
                                else: self.play_next_in_queue()
                            else: self.play_next_in_queue()
                        elif self.frame_idx > tr[1]: self.frame_idx = tr[0]
                else: self.frame_idx = tr[0]
        actor_update_started = time.perf_counter_ns() if performance and performance.enabled else None
        for ai in self.ai_list:
            if not getattr(ai, "is_partner", False):
                ai.update(ground_y, dt)
        for prop in getattr(self, 'prop_list', []): prop.update(ground_y, dt)
        alive_temp_ai = []
        for ai in getattr(self, 'temp_ai_list', []):
            use_dt = dt
            if getattr(ai, 'synergy_invulnerable', False) and ai.active_tag_info and "enter" in ai.active_tag_info[1].lower():
                use_dt = original_dt
            ai.update(ground_y, use_dt)
            if ai.visible:
                alive_temp_ai.append(ai)
        self.temp_ai_list = alive_temp_ai
        if performance and performance.enabled:
            performance.record_since("actor_update", actor_update_started)

    def draw_sprite(self, screen, x, y, source_idx, f_idx, facing_right, cam_x, cam_y, cx, cy, entity=None):
        if source_idx < 0 or source_idx >= len(self.sources): return
        src = self.sources[source_idx]; scaled = src.get_frame(f_idx, self.zoom, facing_right)
        if not scaled: return
        ground_offset = entity_ground_alignment_offset(
            self, entity, source_idx,
        ) if entity is not None else 0.0
        f = src.frames[min(max(0, f_idx), len(src.frames)-1)]; ox, oy = f['ox']*self.zoom, (f['oy'] + ground_offset)*self.zoom
        if not facing_right: ox = -ox - scaled.get_width()
        screen.blit(scaled, (int(cx + (x - cam_x)*self.zoom + ox), int(cy + (y - cam_y)*self.zoom + oy)))
        if self.show_hitboxes:
            has_hit_slice = False
            has_hurt_slice = False
            for name, keys in src.slices.items():
                active_key = None
                for key in keys:
                    if key['frame'] <= f_idx:
                        if active_key is None or key['frame'] > active_key['frame']: active_key = key
                if active_key:
                    if "hit" in name.lower(): has_hit_slice = True
                    elif "hurt" in name.lower() or "body" in name.lower(): has_hurt_slice = True
                    b = active_key['bounds']; sx = cx + (x - cam_x) * self.zoom; sy = cy + (y - cam_y + ground_offset) * self.zoom; final_x = sx + (b['x'] - src.orig_w // 2) * self.zoom; final_y = sy + (b['y'] - src.orig_h // 2) * self.zoom; final_w = b['w'] * self.zoom; final_h = b['h'] * self.zoom
                    if not facing_right: final_x = sx - (b['x'] - src.orig_w // 2 + b['w']) * self.zoom
                    col = (220, 38, 38) if "hit" in name.lower() else (22, 163, 74); pygame.draw.rect(screen, col, (final_x, final_y, final_w, final_h), 2)
                    if self.zoom > 1.5 and getattr(self, 'font_10', None): txt = self.font_10.render(name, True, col); screen.blit(txt, (final_x, final_y - 12))
            
            # Auto-generate default hurtbox
            if not has_hurt_slice:
                hx, hy = cx + (x - cam_x - 20) * self.zoom, cy + (y - cam_y + ground_offset - 60) * self.zoom
                pygame.draw.rect(screen, (22, 163, 74), (hx, hy, 40*self.zoom, 60*self.zoom), 2)
                if self.zoom > 1.5 and getattr(self, 'font_10', None): screen.blit(self.font_10.render("Auto_Hurtbox", True, (22, 163, 74)), (hx, hy - 12))
                
            # Auto-generate default hitbox for attacks
            if not has_hit_slice and entity and getattr(entity, 'active_action_slot', None):
                slot_l = entity.active_action_slot.lower()
                tag_name_l = entity.active_tag_info[1].lower() if entity.active_tag_info else ""
                if ("attack" in slot_l or "powerbomb" in slot_l or "dash" in slot_l or "skill" in slot_l) and "ready" not in tag_name_l and "end" not in tag_name_l:
                    if entity.active_tag_info:
                        tr = src.tags.get(entity.active_tag_info[1], (0, 0))
                        if f_idx == tr[0] and not getattr(entity, 'is_prop', False):
                            hw, hh = 90, 50
                            hox = 10 if facing_right else -10 - hw
                            hx = cx + (x - cam_x + hox) * self.zoom
                            hy = cy + (y - cam_y - 50) * self.zoom
                            pygame.draw.rect(screen, (220, 38, 38), (hx, hy, hw*self.zoom, hh*self.zoom), 2)
                            if self.zoom > 1.5 and getattr(self, 'font_10', None): screen.blit(self.font_10.render("Auto_Hitbox", True, (220, 38, 38)), (hx, hy - 12))

    def get_overlay(self, w, h, color):
        if not hasattr(self, '_overlays'): self._overlays = {}
        key = (w, h, color)
        if key not in self._overlays:
            surf = pygame.Surface((w, h), pygame.SRCALPHA)
            surf.fill(color)
            self._overlays[key] = surf
        return self._overlays[key]
        
    def get_viewport_overlay(self, w, h, vr):
        if not hasattr(self, '_vp_overlay') or getattr(self, '_vp_overlay_key', None) != (w, h, vr.x, vr.y, vr.w, vr.h):
            surf = pygame.Surface((w, h), pygame.SRCALPHA)
            surf.fill((0, 0, 0, 160))
            pygame.draw.rect(surf, (0, 0, 0, 0), vr) # Cut transparent hole
            self._vp_overlay = surf
            self._vp_overlay_key = (w, h, vr.x, vr.y, vr.w, vr.h)
        return self._vp_overlay

    def draw(self, screen, play_w, play_h):
        if not hasattr(self, "solid_boxes"): self.solid_boxes = []
        performance = self.performance_monitor
        cx, cy = play_w // 2, play_h // 2; off_x = random.uniform(-self.shake_intensity*self.base_shake, self.shake_intensity*self.base_shake) if self.shake_timer > 0 else 0; off_y = random.uniform(-self.shake_intensity*self.base_shake, self.shake_intensity*self.base_shake) if self.shake_timer > 0 else 0; cam_x, cam_y = self.cam_x + off_x, self.cam_y + off_y; gx, gy = cx - (cam_x % 100)*self.zoom, cy - (cam_y % 100)*self.zoom
        for i in range(-10, 20): pygame.draw.line(screen, self.grid_color, (int(gx+i*100*self.zoom), 0), (int(gx+i*100*self.zoom), play_h), 1); pygame.draw.line(screen, self.grid_color, (0, int(gy+i*100*self.zoom)), (play_w, int(gy+i*100*self.zoom)), 1)
        background_update_started = time.perf_counter_ns() if performance and performance.enabled else None
        self.update_bg_cache()
        if performance and performance.enabled:
            performance.record_since("background_update", background_update_started)
        background_render_started = time.perf_counter_ns() if performance and performance.enabled else None
        for bg in self.bg_layers:
            if bg.get('cached_bg'):
                bg_w = bg['cached_bg'].get_width()
                bg_h = bg['cached_bg'].get_height()
                bx = cx + (self.spawn_x - cam_x) * bg.get('parallax', 1.0) * self.zoom + bg.get('off_x', 0) * self.zoom - bg_w // 2
                by = cy + (self.spawn_y - cam_y) * bg.get('parallax', 1.0) * self.zoom + bg.get('off_y', 0) * self.zoom - bg_h // 2
                
                # Vertical Culling (Skip if entirely above or below the viewport)
                if by > play_h or by + bg_h < 0:
                    continue

                if bg.get('loop_x') and bg_w > 0:
                    start_x = bx % bg_w
                    if start_x > 0: start_x -= bg_w
                    
                    for draw_x in range(int(start_x), int(play_w), int(bg_w)):
                        # Horizontal Culling per tile
                        if draw_x > play_w or draw_x + bg_w < 0: continue
                        screen.blit(bg['cached_bg'], (draw_x, int(by)))
                else:
                    # Horizontal Culling for non-looping background
                    if bx > play_w or bx + bg_w < 0: continue
                    screen.blit(bg['cached_bg'], (int(bx), int(by)))
        if performance and performance.enabled:
            performance.record_since("background_render", background_render_started)
        actor_render_started = time.perf_counter_ns() if performance and performance.enabled else None
        
        # Draw Platforms
        for i, p in enumerate(self.platforms): 
            px, py, pw, ph = int(cx+(p.x-cam_x)*self.zoom), int(cy+(p.y-cam_y)*self.zoom), int(p.w*self.zoom), int(p.h*self.zoom)
            if px + pw < 0 or px > play_w or py + ph < 0 or py > play_h: continue # Culling
            
            p_surf = pygame.Surface((pw, ph), pygame.SRCALPHA)
            col = (255, 255, 0, self.platform_alpha) if self.edit_platforms and self.selected_plat == i else (80, 80, 100, self.platform_alpha)
            pygame.draw.rect(p_surf, col, (0, 0, pw, ph), border_radius=int(3*self.zoom))
            if self.edit_platforms and self.selected_plat == i:
                # Resize Handle (Bottom-Right)
                pygame.draw.rect(p_surf, (255, 0, 0), (pw-10, ph-10, 10, 10))
                # Delete Button (Top-Right)
                pygame.draw.rect(p_surf, (220, 38, 38), (pw-15, 0, 30, 30), border_radius=15)
                pygame.draw.line(p_surf, (255, 255, 255), (pw-7, 8), (pw+7, 22), 3)
                pygame.draw.line(p_surf, (255, 255, 255), (pw+7, 8), (pw-7, 22), 3)
            screen.blit(p_surf, (px, py))

        # Draw Solid Boxes
        for i, b in enumerate(self.solid_boxes):
            px, py, pw, ph = int(cx+(b.x-cam_x)*self.zoom), int(cy+(b.y-cam_y)*self.zoom), int(b.w*self.zoom), int(b.h*self.zoom)
            if px + pw < 0 or px > play_w or py + ph < 0 or py > play_h: continue # Culling
            
            b_surf = pygame.Surface((pw, ph), pygame.SRCALPHA)
            col = (255, 100, 0, self.platform_alpha) if self.edit_platforms and self.selected_plat == i + 1000 else (50, 50, 60, self.platform_alpha)
            pygame.draw.rect(b_surf, col, (0, 0, pw, ph))
            if self.edit_platforms and self.selected_plat == i + 1000:
                pygame.draw.rect(b_surf, (255, 0, 0), (pw-10, ph-10, 10, 10))
                # Delete Button (Top-Right)
                pygame.draw.rect(b_surf, (220, 38, 38), (pw-15, 0, 30, 30), border_radius=15)
                pygame.draw.line(b_surf, (255, 255, 255), (pw-7, 8), (pw+7, 22), 3)
                pygame.draw.line(b_surf, (255, 255, 255), (pw+7, 8), (pw-7, 22), 3)
            screen.blit(b_surf, (px, py))

        # Draw Props in Edit Mode
        if self.edit_platforms:
            for i, prop in enumerate(getattr(self, "prop_list", [])):
                pw, ph = int(40*self.zoom), int(60*self.zoom)
                px, py = int(cx+(prop.x-cam_x)*self.zoom - pw//2), int(cy+(prop.y-cam_y)*self.zoom - ph)
                
                col = (255, 140, 0, 150) if self.selected_plat == i + 2000 else (100, 100, 100, 100)
                pr_surf = pygame.Surface((pw, ph), pygame.SRCALPHA)
                pygame.draw.rect(pr_surf, col, (0, 0, pw, ph), border_radius=int(3*self.zoom))
                
                if self.selected_plat == i + 2000:
                    # Delete Button (Top-Right)
                    pygame.draw.rect(pr_surf, (220, 38, 38), (pw-15, 0, 30, 30), border_radius=15)
                    pygame.draw.line(pr_surf, (255, 255, 255), (pw-7, 8), (pw+7, 22), 3)
                    pygame.draw.line(pr_surf, (255, 255, 255), (pw+7, 8), (pw-7, 22), 3)
                screen.blit(pr_surf, (px, py))
        
        pygame.draw.line(screen, (100,100,100), (int(cx+(0-cam_x)*self.zoom), int(cy+(500-cam_y)*self.zoom)), (int(cx+(5000-cam_x)*self.zoom), int(cy+(500-cam_y)*self.zoom)), 2)
        
        # Cinematic Lighting Effect for Synergy Attack
        if getattr(self, 'synergy_vfx_timer', 0) > 0:
            alpha = min(180, int((self.synergy_vfx_timer / 1000.0) * 180))
            if alpha > 0:
                dark_overlay = self.get_overlay(play_w, play_h, (10, 10, 20, alpha))
                screen.blit(dark_overlay, (0, 0))
                
        if self.vfx_enabled:
            for ai in self.afterimages:
                src = self.sources[ai['s']]; sc = src.get_frame(ai['f'], self.zoom, ai['right'])
                if sc:
                    img = sc.copy(); img.fill((100, 150, 255, ai['alpha']), special_flags=pygame.BLEND_RGBA_MULT); f = src.frames[min(ai['f'], len(src.frames)-1)]; ox, oy = f['ox']*self.zoom, f['oy']*self.zoom
                    if not ai['right']: ox = -ox - sc.get_width()
                    screen.blit(img, (int(cx + (ai['x'] - cam_x)*self.zoom + ox), int(cy + (ai['y'] - cam_y)*self.zoom + oy)))
        below_player_actors, foreground_actors = split_actor_render_layers(self)
        for ai in below_player_actors:
            if ai.visible and not getattr(ai, "is_partner", False):
                ai_s = (
                    ai.active_tag_info[0]
                    if ai.active_tag_info
                    else ai.profile.source_idx
                )
                self.draw_sprite(
                    screen, ai.x, ai.y, ai_s, ai.frame_idx, ai.facing_right,
                    cam_x, cam_y, cx, cy, entity=ai,
                )
        if self.visible:
            cur_s = self.active_tag_info[0] if self.active_tag_info else 0
            if not self.active_tag_info:
                state = "WALK" if self.grounded and abs(self.vx) > 0.5 else ("IDLE" if self.grounded else ("JUMP" if self.vy < 0 else "FALL")); m = self.profiles[0].mappings.get(state, []) if self.profiles else []; cur_s = m[0][0] if m else 0
            self.draw_sprite(screen, self.x, self.y, cur_s, self.frame_idx, self.facing_right, cam_x, cam_y, cx, cy, entity=self)
            
            # --- SWAP VFX: Yellow Stroke (Outline) ---
            if getattr(self, "swap_vfx_timer", 0) > 0:
                prog = (self.swap_vfx_max_timer - self.swap_vfx_timer) / self.swap_vfx_max_timer
                src = self.sources[cur_s]; sc = src.get_frame(self.frame_idx, self.zoom, self.facing_right)
                
                if sc:
                    # Caching Logic for VFX
                    current_key = (self.frame_idx, self.facing_right, cur_s)
                    if not hasattr(self, "last_vfx_key") or self.last_vfx_key != current_key:
                        mask = pygame.mask.from_surface(sc)
                        self.cached_vfx_points = mask.outline()
                        self.last_vfx_key = current_key
                    
                    points = getattr(self, "cached_vfx_points", [])
                    if points and len(points) > 2:
                        alpha = int(255 * (1.0 - prog))
                        f = src.frames[min(max(0, self.frame_idx), len(src.frames)-1)]; ox, oy = f['ox']*self.zoom, f['oy']*self.zoom
                        if not self.facing_right: ox = -ox - sc.get_width()
                        bx = int(cx + (self.x - cam_x)*self.zoom + ox)
                        by = int(cy + (self.y - cam_y)*self.zoom + oy)
                        
                        stroke_surf = pygame.Surface((sc.get_width(), sc.get_height()), pygame.SRCALPHA)
                        pygame.draw.lines(stroke_surf, (255, 255, 0, alpha), True, points, max(1, int(self.zoom)))
                        screen.blit(stroke_surf, (bx, by))

        for ai in foreground_actors:
            if ai.visible and not getattr(ai, "is_partner", False):
                ai_s = ai.active_tag_info[0] if ai.active_tag_info else ai.profile.source_idx; self.draw_sprite(screen, ai.x, ai.y, ai_s, ai.frame_idx, ai.facing_right, cam_x, cam_y, cx, cy, entity=ai)
                
                # Draw HP for NPCs (not props)
                if (
                    not getattr(ai, 'is_prop', False)
                    and not getattr(ai, 'is_corpse', False)
                ):
                    hp_pct = max(0, ai.hp / getattr(ai, 'max_hp', 10))
                    hx = int(cx + (ai.x - cam_x) * self.zoom - 20)
                    hy = int(cy + (ai.y - cam_y) * self.zoom - 80)
                    if hx > 0 and hx < play_w and hy > 0 and hy < play_h:
                        pygame.draw.rect(screen, (220, 38, 38), (hx, hy, 40, 5))
                        pygame.draw.rect(screen, (22, 163, 74), (hx, hy, int(40 * hp_pct), 5))
                        if getattr(self, 'font_12', None):
                            hp_txt = self.font_12.render(f"HP: {ai.hp}", True, (255, 255, 255))
                            screen.blit(hp_txt, (hx + 20 - hp_txt.get_width()//2, hy - 15))

            adx, ady = (ai.x-cam_x)*self.zoom, (ai.y-cam_y)*self.zoom
            if not getattr(ai, "is_corpse", False) and (abs(adx)>play_w//2 or abs(ady)>play_h//2): ang = math.atan2(ady, adx); px, py = cx+math.cos(ang)*(play_w//2-40), cy+math.sin(ang)*(play_h//2-40); pygame.draw.circle(screen, (220,38,38), (int(px), int(py)), 12); pygame.draw.line(screen, (255,255,255), (px, py), (px-math.cos(ang)*8, py-math.sin(ang)*8), 2)
            
        # Draw Projectiles
        for proj in getattr(self, 'projectiles', []):
            if proj.active:
                if proj.source_idx is not None and proj.source_idx >= 0 and proj.source_idx < len(self.sources):
                    self.draw_sprite(screen, proj.x, proj.y, proj.source_idx, proj.frame_idx, proj.facing_right, cam_x, cam_y, cx, cy)
                else:
                    px = int(cx + (proj.x - cam_x) * self.zoom)
                    py = int(cy + (proj.y - cam_y) * self.zoom)
                    pygame.draw.circle(screen, (59, 130, 246), (px, py), int(15 * self.zoom))
                    pygame.draw.circle(screen, (255, 255, 255), (px, py), int(8 * self.zoom))

        # Draw Floating Damage Numbers
        for dmg in getattr(self, 'damage_numbers', []):
            dx = int(cx + (dmg['x'] - cam_x) * self.zoom)
            dy = int(cy + (dmg['y'] - cam_y) * self.zoom)
            if dx > 0 and dx < play_w and dy > 0 and dy < play_h and getattr(self, 'font_dmg', None):
                alpha = int(255 * (dmg['lifetime'] / dmg['max_life']))
                txt_surf = self.font_dmg.render(str(dmg['val']), True, (255, 255, 255))
                # Outline
                bg_surf = self.font_dmg.render(str(dmg['val']), True, (0, 0, 0))
                # Apply alpha hack
                temp_surf = pygame.Surface((txt_surf.get_width()+2, txt_surf.get_height()+2), pygame.SRCALPHA)
                for ox, oy in [(-1,-1), (-1,1), (1,-1), (1,1), (0,-1), (-1,0), (1,0), (0,1)]: temp_surf.blit(bg_surf, (ox+1, oy+1))
                temp_surf.blit(txt_surf, (1, 1))
                temp_surf.set_alpha(alpha)
                screen.blit(temp_surf, (dx - temp_surf.get_width()//2, dy))
            
        if performance and performance.enabled:
            performance.record_since("actor_render", actor_render_started)

        # Draw Particles
        particle_render_started = time.perf_counter_ns() if performance and performance.enabled else None
        death_result = getattr(self, "last_npc_death_result", None)
        tracked_death_ids = death_result.get("particle_ids", set()) if isinstance(death_result, dict) else set()
        rendered_death_parts = 0
        for p in getattr(self, 'particles', []):
            px = int(cx + (p.x - cam_x) * self.zoom)
            py = int(cy + (p.y - cam_y) * self.zoom)
            s = int(p.size * self.zoom)
            if p.image:
                iw, ih = int(p.image.get_width()*self.zoom), int(p.image.get_height()*self.zoom)
                if px + iw > 0 and px - iw < play_w and py + ih > 0 and py - ih < play_h:
                    if p.cached_zoom != self.zoom or abs(p.cached_rotation - p.rotation) > 1.0 or p.cached_surface is None:
                        if p.cached_scaled_zoom != self.zoom or p.cached_scaled_surface is None:
                            p.cached_scaled_surface = pygame.transform.scale(
                                p.image, (max(1, iw), max(1, ih)),
                            )
                            p.cached_scaled_zoom = self.zoom
                        normalized_rotation = p.rotation % 360.0
                        p.cached_surface = (
                            p.cached_scaled_surface
                            if normalized_rotation == 0.0
                            else pygame.transform.rotate(p.cached_scaled_surface, p.rotation)
                        )
                        p.cached_zoom = self.zoom
                        p.cached_rotation = p.rotation
                    
                    rect = p.cached_surface.get_rect(center=(px, py))
                    screen.blit(p.cached_surface, rect.topleft)
                    if id(p) in tracked_death_ids:
                        rendered_death_parts += 1
            else:
                if px + s > 0 and px < play_w and py + s > 0 and py < play_h:
                    pygame.draw.rect(screen, p.color, (px, py, s, s))
        if (
            isinstance(death_result, dict)
            and death_result.get("update_logged")
            and not death_result.get("render_logged")
        ):
            death_result["rendered"] = rendered_death_parts
            death_result["render_logged"] = True
            log_debug(
                f"[NPC DEATH RENDER] image_particles={death_result.get('image_particles', 0)} "
                f"rendered={rendered_death_parts} camera=({self.cam_x},{self.cam_y}) zoom={self.zoom}"
            )
                    
        # Draw Sparks
        for s in getattr(self, 'sparks', []):
            px = int(cx + (s.x - cam_x) * self.zoom)
            py = int(cy + (s.y - cam_y) * self.zoom)
            length = int(s.length * self.zoom)
            width = max(1, int(s.width * self.zoom))
            if px + length > 0 and px - length < play_w and py + length > 0 and py - length < play_h:
                end_x = px - math.cos(s.angle) * length
                end_y = py - math.sin(s.angle) * length
                alpha = max(0, min(255, int(255 * (s.lifetime / s.max_life))))
                if alpha > 0:
                    surf = pygame.Surface((abs(end_x - px) + width*2, abs(end_y - py) + width*2), pygame.SRCALPHA)
                    # Simple line drawing with alpha hack: draw onto a surface then blit
                    lx, ly = max(0, min(px, end_x) - px + width), max(0, min(py, end_y) - py + width)
                    ex, ey = max(0, max(px, end_x) - px + width), max(0, max(py, end_y) - py + width)
                    if px > end_x: lx, ex = ex, lx
                    if py > end_y: ly, ey = ey, ly
                    pygame.draw.line(surf, (*s.color, alpha), (lx, ly), (ex, ey), width)
                    screen.blit(surf, (min(px, end_x) - width, min(py, end_y) - width), special_flags=pygame.BLEND_RGB_ADD)
        if performance and performance.enabled:
            performance.record_since("particle_render", particle_render_started)

        if getattr(self, 'show_viewport', True):
            vw, vh = getattr(self, 'target_w', 640) * self.zoom, getattr(self, 'target_h', 360) * self.zoom; vr = pygame.Rect(cx - vw//2, cy - vh//2, vw, vh)
            overlay = self.get_viewport_overlay(play_w, play_h, vr)
            screen.blit(overlay, (0, 0)); pygame.draw.rect(screen, (255, 255, 255), vr, 1)
            if getattr(self, 'font_12', None): screen.blit(self.font_12.render(f"Viewport: {self.target_w}x{self.target_h} (16:9)", True, (255,255,255)), (vr.x, vr.y - 18))
            
        # Draw HUD (Bottom Left)
        hud_y = play_h - 80
        # HP Bar
        pygame.draw.rect(screen, (40, 40, 45), (20, hud_y, 200, 20), border_radius=4)
        hp_pct = max(0, getattr(self, 'hp', 100) / getattr(self, 'max_hp', 100))
        pygame.draw.rect(screen, (220, 38, 38), (20, hud_y, int(200 * hp_pct), 20), border_radius=4)
        pygame.draw.rect(screen, (255, 255, 255), (20, hud_y, 200, 20), 2, border_radius=4)
        if getattr(self, 'font_b', None): screen.blit(self.font_b.render(f"HP {int(getattr(self, 'hp', 100))}/{getattr(self, 'max_hp', 100)}", True, (255,255,255)), (28, hud_y+2))
        
        # Dash Charges
        for i, dash_rect in enumerate(dash_charge_hud_rects(hud_y)):
            col = (59, 130, 246) if i < getattr(self, 'dash_charges', 2) else (60, 60, 70)
            pygame.draw.rect(screen, col, dash_rect, border_radius=2)
            
        # Skill Cooldowns
        for i in range(3):
            cd = getattr(self, 'skill_cooldowns', [0,0,0])[i]
            sx = 230 + i * 50
            pygame.draw.rect(screen, (50, 50, 60), (sx, hud_y - 15, 40, 40), border_radius=6)
            if cd > 0:
                overlay_h = int(40 * (cd / 3000.0))
                pygame.draw.rect(screen, (0, 0, 0, 150), (sx, hud_y - 15 + (40 - overlay_h), 40, overlay_h), border_radius=6)
                if getattr(self, 'font_b', None):
                    cd_txt = self.font_b.render(f"{cd/1000.0:.1f}", True, (255, 255, 255))
                    screen.blit(cd_txt, (sx + 20 - cd_txt.get_width()//2, hud_y - 5))
            else:
                pygame.draw.rect(screen, (22, 163, 74), (sx, hud_y - 15, 40, 40), 2, border_radius=6)
            if getattr(self, 'font_10', None):
                screen.blit(self.font_10.render(f"S{i+1}", True, (200,200,200)), (sx+12, hud_y+27))
        
        # Popup Overlay Draw
        if self.popup:
            msg_w, msg_h = 540, 260; cx, cy = screen.get_width()//2, screen.get_height()//2
            overlay = self.get_overlay(screen.get_width(), screen.get_height(), (0, 0, 0, 128))
            screen.blit(overlay, (0, 0))
            
            pygame.draw.rect(screen, (40, 40, 45), (cx-msg_w//2, cy-msg_h//2, msg_w, msg_h), border_radius=10)
            pygame.draw.rect(screen, (60, 60, 65), (cx-msg_w//2, cy-msg_h//2, msg_w, msg_h), 2, border_radius=10)
            
            # Use globally available font_b and font_s from main() scoping or just assume they exist
            # Note: since font_b is built in main(), drawing it here will just access it globally.
            if hasattr(self, 'font_b') and self.font_b:
                title = self.popup.get("title", tr("common.confirm"))
                title_image = self.font_b.render(title, True, (255, 255, 255))
                screen.blit(title_image, (cx-title_image.get_width()//2, cy-105))
            if hasattr(self, 'font_12') and self.font_12:
                for line_index, line in enumerate(str(self.popup['msg']).splitlines()):
                    line_image = self.font_12.render(line, True, (200, 200, 200))
                    screen.blit(line_image, (cx-line_image.get_width()//2, cy-68+line_index*22))

            yes_btn = pygame.Rect(cx-120, cy+65, 100, 34); no_btn = pygame.Rect(cx+20, cy+65, 100, 34)
            pygame.draw.rect(screen, (59, 130, 246), yes_btn, border_radius=5)
            pygame.draw.rect(screen, (220, 38, 38), no_btn, border_radius=5)
            if hasattr(self, 'font_b') and self.font_b:
                draw_centered_label(screen, self.font_b, self.popup.get("confirm_label", tr("common.confirm")), yes_btn)
                draw_centered_label(screen, self.font_b, self.popup.get("cancel_label", tr("common.cancel")), no_btn)
def check_application():
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    try:
        pygame.init()
        screen = pygame.display.set_mode((960, 640))
        player = AsepritePlayer()
        if not player.load_settings(notify_missing_assets=False):
            raise RuntimeError(f"Settings check failed: {player.settings_path}")
        example_resources = {
            resource["path"]
            for variant in (1, 2)
            for resource in (
                example_preset(variant)["sources"]
                + example_preset(variant)["bg_layers"]
            )
        }
        missing_examples = [
            path for path in example_resources
            if not os.path.isfile(app_resource_path(path))
        ]
        frozen_runtime = bool(getattr(sys, "frozen", False))
        if missing_examples and not frozen_runtime:
            raise RuntimeError("Missing example resources: " + ", ".join(sorted(missing_examples)))
        tk_patchlevel = check_tk_runtime() if frozen_runtime else None
        player.update(pygame.key.get_pressed(), 500, 16.6)
        player.draw(screen, 800, 570)
        pygame.display.flip()
        print(application_check_success_message(
            len(example_resources) - len(missing_examples),
            expected_example_count=(
                len(example_resources) if frozen_runtime else None
            ),
            tk_patchlevel=tk_patchlevel,
        ))
        return 0
    except Exception as e:
        log_debug(f"[ERROR] Application check failed: {e}")
        print(f"CHECK FAILED: {e}")
        return 1
    finally:
        pygame.quit()


def check_aseprite():
    try:
        executable = ase_manager.get_path(allow_prompt=False)
        version = run_aseprite(["--version"], executable=executable).stdout.strip()
        fixture = app_resource_path(os.path.join("Testfiles", "Test01.aseprite"))
        if not os.path.isfile(fixture):
            print(f"ASEPRITE CHECK OK: {version or os.path.basename(executable)}; fixture export skipped because test assets are not bundled; expected={fixture}")
            return 0
        with tempfile.TemporaryDirectory(prefix="ase_viewer_check_") as temp_dir:
            png_path = os.path.join(temp_dir, "sheet.png"); json_path = os.path.join(temp_dir, "data.json")
            data = export_aseprite(fixture, png_path, json_path, executable=executable)
            print(f"ASEPRITE CHECK OK: {version or os.path.basename(executable)}; frames={len(data['frames'])}; fixture={fixture}")
        return 0
    except AsepriteError as e:
        log_debug(f"[ERROR] Aseprite check failed: {e}")
        print(f"ASEPRITE CHECK FAILED: {e}")
        return 1


def _source_render_digest(source):
    digest = hashlib.sha256()
    for frame in source.frames:
        digest.update(pygame.image.tostring(frame["img"], "RGBA"))
        digest.update(f"{frame['ox']}:{frame['oy']}:{frame['duration']}".encode("ascii"))
    return digest.hexdigest()


def check_layers():
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    try:
        pygame.init(); pygame.display.set_mode((1, 1))
        fixture = app_resource_path(os.path.join("resources", "examples", "shared", "sources", "Cailin_00_Public.aseprite"))
        if not os.path.isfile(fixture):
            fixture = app_resource_path(os.path.join("Testfiles", "Test01.aseprite"))
        source = AseSource(fixture, 0)
        original_summary = layer_inventory_summary(source.layers)
        if not source.layers or original_summary["duplicate_keys"]:
            raise RuntimeError(f"invalid layer inventory: {original_summary}")
        original_order = list(original_summary["order"])
        original_visibility = {layer["path"]: layer["key"] in source.visible_layer_keys for layer in source.layers}
        original_digest = _source_render_digest(source)
        candidates = [layer for layer in source.layers if original_visibility[layer["path"]] and not layer["is_group"]]
        if not candidates:
            raise RuntimeError("fixture has no visible renderable layer to toggle")
        toggled = []
        changed_render = False
        for layer_path in dict.fromkeys((candidates[0]["path"], candidates[-1]["path"])):
            layer_key = next(layer["key"] for layer in source.layers if layer["path"] == layer_path)
            if not source.set_layer_visibility(layer_key, False) or not source.export_and_load():
                raise RuntimeError(f"could not disable layer {layer_path}")
            current = next(layer for layer in source.layers if layer["path"] == layer_path)
            if current["key"] in source.visible_layer_keys or [item["path"] for item in source.layers] != original_order:
                raise RuntimeError(f"layer list changed after disabling {layer_path}")
            changed_render = changed_render or _source_render_digest(source) != original_digest
            source.set_layer_visibility(current["key"], True)
            if not source.export_and_load():
                raise RuntimeError(f"could not restore layer {layer_path}")
            toggled.append(layer_path)
        source.visible_layer_keys = {layer["key"] for layer in source.layers if original_visibility.get(layer["path"], layer["original_visible"])}
        if not source.export_and_load() or _source_render_digest(source) != original_digest:
            raise RuntimeError("restored layer render does not match the original")
        if not changed_render:
            raise RuntimeError("first/last layer toggles did not change the rendered frames")
        final_summary = layer_inventory_summary(source.layers)
        if final_summary["order"] != original_order:
            raise RuntimeError("layer order changed during toggle/export")
        print(
            "LAYERS CHECK OK: "
            f"fixture={fixture}; total={final_summary['total']}; groups={final_summary['groups']}; "
            f"renderable={final_summary['renderable']}; duplicate_keys={final_summary['duplicate_keys']}; "
            f"first={original_order[0]}; last={original_order[-1]}; toggled={len(toggled)}"
        )
        return 0
    except (AsepriteError, OSError, RuntimeError) as e:
        log_debug(f"[ERROR] Layers check failed: {e}")
        print(f"LAYERS CHECK FAILED: {e}")
        return 1
    finally:
        pygame.quit()


class _SmokeSource:
    def __init__(self, source_id=0, file_path="<memory>"):
        self.id = source_id; self.file_path = file_path; self.name = f"GUI Smoke Source {source_id}"; self.is_prop_source = False
        image = pygame.Surface((16, 16), pygame.SRCALPHA); image.fill((80, 180, 255, 255))
        self.frames = [{"img": image, "ox": -8, "oy": -16, "duration": 40}]
        profile = example_preset(1)["profiles"][source_id]
        names = sorted({mapping[1] for entries in profile["mappings"].values() for mapping in entries})
        self.tags = {name: (0, 0) for name in names}; self.tag_list = list(names); self.slices = {}; self.orig_w = 16; self.orig_h = 16
        self.layers = []; self.visible_layer_keys = set(); self.visible_layers = set()
    def get_frame(self, frame_idx, zoom, facing_right):
        image = pygame.transform.scale(self.frames[0]["img"], (max(1, int(16 * zoom)), max(1, int(16 * zoom))))
        return image if facing_right else pygame.transform.flip(image, True, False)
    def clear_cache(self): pass
    def check_for_reload(self): return False


class _SmokeKeys:
    def __init__(self, *pressed): self.pressed = set(pressed)
    def __getitem__(self, key): return key in self.pressed


def check_gui():
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    stage = "pygame initialization"
    try:
        pygame.init(); screen = pygame.display.set_mode((960, 640))
        with tempfile.TemporaryDirectory(prefix="ase_viewer_gui_check_") as temp_dir:
            stage = "player and example creation"
            player = AsepritePlayer(project_path=os.path.join(temp_dir, "project.json"), settings_path=os.path.join(temp_dir, "settings.json"))
            if not player._load_example(1, persist=False, source_factory=lambda path, source_id: _SmokeSource(source_id, path)):
                raise RuntimeError("EX 1 preparation failed")
            player.profiles[0].mappings["ComboAttack_1"] = [[0, "ComboAttack_1"]]
            player.profiles[0].mappings["ComboAttack_2"] = [[0, "ComboAttack_2"]]
            player.profiles[0].mappings["DASH"] = [[0, "Dash"]]
            player.profiles[0].mappings["Swap_Enter"] = [[0, "Swap_Enter"]]
            player.profiles[0].mappings["Swap_Exit"] = [[0, "Swap_Exit"]]
            npc_profile = AseProfile("NPC_SMOKE", 0, kind="npc"); npc_profile.mappings = {key: list(value) for key, value in player.profiles[0].mappings.items()}
            prop_profile = AseProfile("PROP_SMOKE", 0, kind="prop"); prop_profile.mappings = {key: list(value) for key, value in player.profiles[0].mappings.items()}; prop_profile.is_prop_profile = True
            player.profiles.append(npc_profile)
            npc = AseAI(player, npc_profile); prop = AseAI(player, prop_profile, is_prop=True, hp=3)
            player.ai_list = [npc]; player.prop_list = [prop]; player.target_ai_count = 1
            stage = "movement and dash"
            player.grounded = True; start_x = player.x
            player.update(_SmokeKeys(pygame.K_RIGHT), 500, 16.6)
            if player.x <= start_x: raise RuntimeError("right movement did not advance the player")
            player.trigger_action("DASH"); player.update(_SmokeKeys(), 500, 16.6)
            stage = "attack and combo"
            player.grounded = True; player.active_action_slot = None; player.handle_attack(_SmokeKeys()); player.handle_attack(_SmokeKeys())
            stage = "swap"
            player.active_action_slot = None; player.active_tag_info = None; player.action_queue = []; player.execute_swap()
            if not player.temp_ai_list: raise RuntimeError("swap did not create an outgoing temporary actor")
            stage = "NPC, prop, platform update"
            npc.update(500, 16.6); prop.update(500, 16.6)
            if not player.platforms: raise RuntimeError("example did not create platforms")
            stage = "multi-frame render"
            for _ in range(3):
                player.update(_SmokeKeys(), 500, 16.6); player.draw(screen, 800, 570); pygame.display.flip()
            if os.path.exists(player.project_path) or os.path.exists(player.settings_path):
                raise RuntimeError("GUI check unexpectedly wrote project or settings data")
        print(f"GUI CHECK OK: movement, dash, combo, swap, NPC, prop, platforms, and rendering; app_root={APP_ROOT}")
        return 0
    except Exception as e:
        log_debug(f"[ERROR] GUI check failed during {stage}: {e}")
        print(f"GUI CHECK FAILED during {stage}: {e}")
        return 1
    finally:
        pygame.quit()


def performance_object_counts(player, tooltip_count=0):
    particles = getattr(player, "particles", [])
    return {
        "partner": len(partner_roster_profiles(player)),
        "npc": len(getattr(player, "ai_list", [])),
        "prop": len(getattr(player, "prop_list", [])),
        "image_particles": sum(particle.image is not None for particle in particles),
        "color_particles": sum(particle.image is None for particle in particles),
        "backgrounds": len(getattr(player, "bg_layers", [])),
        "tooltips": int(tooltip_count),
    }


def format_performance_summary(monitor, heading="[PERFORMANCE SUMMARY]"):
    data = monitor.final_summary()
    top_sections = sorted(
        (
            (name, values["avg_ms"])
            for name, values in data["sections"].items()
            if values["avg_ms"] > 0
        ),
        key=lambda item: item[1],
        reverse=True,
    )[:5]
    lines = [
        heading,
        f"frames={data['frames']}",
        f"average_fps={data['fps']:.2f}",
        f"frame_avg_ms={data['frame_avg_ms']:.4f}",
        f"frame_p95_ms={data['frame_p95_ms']:.4f}",
        f"frame_p99_ms={data['frame_p99_ms']:.4f}",
        f"frame_max_ms={data['frame_max_ms']:.4f}",
        f"spikes_over_25ms={data['spikes_over_25ms']}",
        "",
        "top_sections:",
    ]
    lines.extend(f"{name}={value:.4f}ms" for name, value in top_sections)
    return "\n".join(lines)


def main(profile_performance=False):
    log_debug(f"[SYSTEM] {APP_TITLE} {APP_VERSION} starting")
    pygame.init(); pygame.mixer.init()
    pygame.display.set_caption(app_window_title())
    initial_size = calculate_initial_window_size(current_desktop_size())
    screen = pygame.display.set_mode(initial_size, pygame.RESIZABLE | pygame.DOUBLEBUF | pygame.HWSURFACE, vsync=1)
    invalidate_ui_layout_for_window_size(initial_size)
    clock = pygame.time.Clock(); player = AsepritePlayer(); sidebar_mode = SIDEBAR_MAPPING; slot_scroll = tag_scroll = settings_scroll = 0; settings_section = SETTINGS_SECTION_CONTROLS_APP; font_s = create_ui_font(12); font_b = create_ui_font(14, bold=True); font_h = create_ui_font(11); is_dragging_cam = False; last_m_pos = (0,0); selected_slot = None; folds = {"LANGUAGE": True, "PROPS": True, "NPCS": True, "PHYSICS": True, "AI & COMBAT": True, "JUICE & VFX": True, "LAYERS": True, "CAMERA": True, "BG IMAGE": True, "BG COLOR": True, "CONTROLS": True}
    tooltip_controller = TooltipController(delay_ms=400)
    performance = PerformanceMonitor(enabled=profile_performance, window_size=600)
    player.performance_monitor = performance
    binding_key = None; active_input_attr = None; input_text = ""
    workspace_scroll = 0
    workspace_controls = []
    workspace_viewport = None
    while True:
        frame_started = performance.begin_frame()
        limiter_started = time.perf_counter_ns() if performance.enabled else None
        raw_dt = clock.tick(60)
        performance.record_since("frame_limiter", limiter_started)
        dt = raw_dt * player.playback_speed if player else raw_dt
        sw, sh = screen.get_size(); sidebar_w = SIDEBAR_WIDTH; play_w = sw - sidebar_w; play_h = sh - TOP_UI_HEIGHT; m_pos = pygame.mouse.get_pos()
        sidebar_header_rect, sidebar_content_rect = sidebar_rects(play_w, sh, sidebar_w)
        settings_body_global_rect = pygame.Rect(
            play_w,
            TOP_UI_HEIGHT + SETTINGS_SECTION_NAV_HEIGHT,
            sidebar_w,
            max(
                0,
                sidebar_content_rect.h - SETTINGS_SECTION_NAV_HEIGHT,
            ),
        )
        tooltip_regions = []
        
        # [OPTIMIZATION] Restrict drawing strictly to the visible game area to prevent massive overdraw under UI panels
        screen.set_clip(pygame.Rect(0, TOP_UI_HEIGHT, play_w, play_h))
        screen.fill(player.bg_color)
        
        # Draw main game area
        if player:
            update_started = time.perf_counter_ns() if performance.enabled else None
            player.update(pygame.key.get_pressed(), 500, dt)
            performance.record_since("update", update_started)
            world_render_started = time.perf_counter_ns() if performance.enabled else None
            player.draw(screen, play_w, play_h)
            draw_parallax_offset_gizmo(screen, player, play_w, play_h, font_s)
            performance.record_since("world_render", world_render_started)

        # Reset clip for UI
        ui_render_started = time.perf_counter_ns() if performance.enabled else None
        screen.set_clip(None)
        pygame.draw.rect(screen, (25, 25, 30), (play_w, 0, sidebar_w, sh)); pygame.draw.rect(screen, (35, 35, 40), (0, 0, play_w, 70))        
        # --- TOP UI ROW 1 (Project & Files) ---
        # Group 1: File Management
        new_proj, load_prev, sv_proj = layout_button_row([
            (tr("common.new"), 70, 125),
            (tr("common.load"), 65, 110),
            (tr("common.save"), 60, 100),
        ], font_b, 10, 5)
        pygame.draw.rect(screen, (220, 38, 38), new_proj, border_radius=5); draw_centered_label(screen, font_b, tr("common.new"), new_proj)
        register_tooltip(tooltip_regions, new_proj, "tooltip.project.new")
        
        has_prev = player.project_file_available
        pygame.draw.rect(screen, (59, 130, 246) if has_prev else (60, 60, 70), load_prev, border_radius=5); draw_centered_label(screen, font_b, tr("common.load"), load_prev, (255,255,255) if has_prev else (120, 120, 120))
        register_tooltip(tooltip_regions, load_prev, "tooltip.project.load")
        
        pygame.draw.rect(screen, (100, 100, 110), sv_proj, border_radius=5); draw_centered_label(screen, font_b, tr("common.save"), sv_proj)
        register_tooltip(tooltip_regions, sv_proj, "tooltip.project.save")
        
        first_separator_x = sv_proj.right + 10
        pygame.draw.line(screen, (80, 80, 90), (first_separator_x, 5), (first_separator_x, 33), 2)
        
        # Group 2: Examples
        example_btn, ex2_btn = layout_button_row([("EX 1", 50, 60), ("EX 2", 50, 60)], font_b, first_separator_x + 10, 5)
        pygame.draw.rect(screen, (34, 139, 34), example_btn, border_radius=5); draw_centered_label(screen, font_b, "EX 1", example_btn)
        pygame.draw.rect(screen, (34, 139, 34), ex2_btn, border_radius=5); draw_centered_label(screen, font_b, "EX 2", ex2_btn)
        
        (
            tag_setup_btn, selection_scene_btn,
            selection_resource_btn, settings_btn,
        ) = sidebar_navigation_button_rects(
            play_w, sidebar_w,
        )

        # --- TOP UI ROW 2 (Tools & Settings) ---
        edit_p_btn, add_p_btn, add_b_btn = layout_button_row([
            (tr("ui.edit_platform"), 100, 130),
            (tr("ui.add_platform"), 80, 115),
            (tr("ui.add_box"), 80, 100),
        ], font_b, 10, 38)
        pygame.draw.rect(screen, (220, 38, 38) if player.edit_platforms else (60, 60, 70), edit_p_btn, border_radius=5); draw_centered_label(screen, font_b, tr("ui.edit_platform"), edit_p_btn)
        register_tooltip(tooltip_regions, edit_p_btn, "tooltip.platform.edit")
        
        if player.edit_platforms:
            pygame.draw.rect(screen, (59, 130, 246), add_p_btn, border_radius=5); draw_centered_label(screen, font_b, tr("ui.add_platform"), add_p_btn)
            pygame.draw.rect(screen, (255, 140, 0), add_b_btn, border_radius=5); draw_centered_label(screen, font_b, tr("ui.add_box"), add_b_btn)
            register_tooltip(tooltip_regions, add_p_btn, "tooltip.platform.add")
            register_tooltip(tooltip_regions, add_b_btn, "tooltip.solid_box.add")

        # Group 3: Asset Addition (row 2 keeps translated labels away from project tabs)
        add_src, add_npc, add_prop = layout_button_row([
            (tr("ui.add_source"), 65, 105),
            (tr("ui.add_npc"), 65, 100),
            (tr("ui.add_prop"), 70, 105),
        ], font_b, add_b_btn.right + 10, 38)
        pygame.draw.rect(screen, (59, 130, 246), add_src, border_radius=5); draw_centered_label(screen, font_b, tr("ui.add_source"), add_src)
        pygame.draw.rect(screen, (22, 163, 74), add_npc, border_radius=5); draw_centered_label(screen, font_b, tr("ui.add_npc"), add_npc)
        pygame.draw.rect(screen, (220, 140, 38), add_prop, border_radius=5); draw_centered_label(screen, font_b, tr("ui.add_prop"), add_prop)
        register_tooltip(tooltip_regions, add_src, "tooltip.source.add")
        register_tooltip(tooltip_regions, add_npc, "tooltip.npc.add")
        register_tooltip(tooltip_regions, add_prop, "tooltip.prop.add")
        performance.record_since("ui_render", ui_render_started)
        events_started = time.perf_counter_ns() if performance.enabled else None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                if player and not profile_performance:
                    player.save_project(); player.save_settings()
                if profile_performance:
                    print(format_performance_summary(performance))
                pygame.quit()
                return
            if event.type == pygame.VIDEORESIZE:
                cancel_parallax_gizmo_drag(player, restore=True)
                cancel_parallax_offset_edit(player, restore=True)
                tooltip_controller.reset()
                resize_w = max(min(MIN_WINDOW_SIZE[0], current_desktop_size()[0]), event.w)
                resize_h = max(min(MIN_WINDOW_SIZE[1], current_desktop_size()[1]), event.h)
                invalidate_ui_layout_for_window_size((resize_w, resize_h))
                screen = pygame.display.set_mode((resize_w, resize_h), pygame.RESIZABLE | pygame.DOUBLEBUF | pygame.HWSURFACE, vsync=1)
                settings_scroll = clamp_settings_scroll(
                    settings_scroll,
                    settings_content_height(player, folds, settings_section),
                    max(0, resize_h - TOP_UI_HEIGHT - SETTINGS_SECTION_NAV_HEIGHT),
                )
            if event.type == pygame.WINDOWFOCUSLOST:
                cancel_parallax_gizmo_drag(player, restore=True)
                cancel_parallax_offset_edit(player, restore=True)
            if event.type == pygame.DROPFILE:
                sid = player.add_source(event.file)
                if sid is not None:
                    player.resource_status_message = tr("selection.imported_choose_role")
            if event.type == pygame.MOUSEBUTTONDOWN:
                tooltip_controller.reset()
                if player.popup:
                    # Popup Handling (Yes/No) Collision only
                    cx, cy = screen.get_width()//2, screen.get_height()//2
                    yes_btn = pygame.Rect(cx-120, cy+65, 100, 34)
                    no_btn = pygame.Rect(cx+20, cy+65, 100, 34)
                    
                    if yes_btn.collidepoint(m_pos):
                        if player.popup['cb']: player.popup['cb']()
                        player.popup = None
                    elif no_btn.collidepoint(m_pos):
                        if player.popup.get('no_cb'): player.popup['no_cb']()
                        player.popup = None
                else:
                    if (
                        event.button == 1
                        and begin_parallax_gizmo_drag(player, m_pos, play_w, play_h)
                    ):
                        is_dragging_cam = False
                        continue
                    if event.button == 3 and m_pos[0] < play_w: is_dragging_cam = True; last_m_pos = m_pos; player.cam_follow = False
                    if event.button == 1:
                        # Top Bar Interaction
                        if m_pos[1] < TOP_UI_HEIGHT:
                            header_target = sidebar_header_click_target(
                                m_pos, tag_setup_btn, selection_scene_btn,
                                selection_resource_btn, settings_btn,
                            )
                            if header_target == SIDEBAR_MAPPING:
                                sidebar_mode = set_sidebar_mode(
                                    sidebar_mode, SIDEBAR_MAPPING,
                                )
                            elif header_target == SIDEBAR_SETTINGS:
                                sidebar_mode = set_sidebar_mode(sidebar_mode, SIDEBAR_SETTINGS)
                                if sidebar_mode == SIDEBAR_SETTINGS:
                                    settings_scroll = clamp_settings_scroll(
                                        settings_scroll,
                                        settings_content_height(player, folds, settings_section),
                                        settings_body_global_rect.h,
                                    )
                            elif header_target == SIDEBAR_SCENE:
                                sidebar_mode = set_sidebar_mode(sidebar_mode, SIDEBAR_SCENE)
                                workspace_scroll = (
                                    workspace_selected_row_index(player, SIDEBAR_SCENE) * 42
                                    if sidebar_mode == SIDEBAR_SCENE else 0
                                )
                            elif header_target == SIDEBAR_RESOURCES:
                                sidebar_mode = set_sidebar_mode(sidebar_mode, SIDEBAR_RESOURCES)
                                workspace_scroll = (
                                    workspace_selected_row_index(player, SIDEBAR_RESOURCES) * 58
                                    if sidebar_mode == SIDEBAR_RESOURCES else 0
                                )
                            elif m_pos[0] < play_w and new_proj.collidepoint(m_pos):
                                p = select_file([("Aseprite", "*.aseprite *.ase")])
                                if p: player = AsepritePlayer(p)
                            elif m_pos[0] < play_w and example_btn.collidepoint(m_pos) and player:
                                player.load_example()
                            elif m_pos[0] < play_w and ex2_btn.collidepoint(m_pos) and player:
                                player.load_example2()
                            elif m_pos[0] < play_w and load_prev.collidepoint(m_pos) and has_prev: player.load_settings(); player.load_project()
                            elif m_pos[0] < play_w and sv_proj.collidepoint(m_pos) and player: player.save_settings(); player.save_project()
                            elif m_pos[0] < play_w and add_src.collidepoint(m_pos) and player:
                                p = select_file([("Aseprite", "*.aseprite *.ase")])
                                if p:
                                    sid = player.add_source(p)
                                    if sid is not None:
                                        player.resource_status_message = tr("selection.imported_choose_role")
                            elif m_pos[0] < play_w and add_npc.collidepoint(m_pos) and player:
                                p = select_file([("Aseprite", "*.aseprite *.ase")])
                                if p:
                                    player.register_npc_source(p)
                            elif m_pos[0] < play_w and add_prop.collidepoint(m_pos) and player:
                                p = select_file([("Aseprite", "*.aseprite *.ase")])
                                if p:
                                    player.register_prop_source(p)
                            elif m_pos[0] < play_w and edit_p_btn.collidepoint(m_pos): player.edit_platforms = not player.edit_platforms; player.selected_plat = None
                            elif m_pos[0] < play_w and player.edit_platforms and add_p_btn.collidepoint(m_pos):
                                cx, cy = play_w // 2, play_h // 2
                                cam_x, cam_y = player.cam_x, player.cam_y
                                player.platforms.append(pygame.Rect(cam_x, cam_y, 200, 20))
                            elif m_pos[0] < play_w and player.edit_platforms and add_b_btn.collidepoint(m_pos):
                                cx, cy = play_w // 2, play_h // 2
                                cam_x, cam_y = player.cam_x, player.cam_y
                                if not hasattr(player, "solid_boxes"): player.solid_boxes = []
                                player.solid_boxes.append(pygame.Rect(cam_x, cam_y, 100, 100))

                        elif (
                            sidebar_mode in {SIDEBAR_SCENE, SIDEBAR_RESOURCES}
                            and sidebar_content_rect.collidepoint(m_pos)
                        ):
                            clicked_control = next(
                                (control for control in reversed(workspace_controls)
                                 if control["rect"].collidepoint(m_pos)),
                                None,
                            )
                            if clicked_control and clicked_control["enabled"]:
                                action = clicked_control["action"]
                                value = clicked_control["value"]
                                if action == "select_actor":
                                    select_scene_actor(player, value)
                                elif action == "select_resource":
                                    select_resource_row(player, value)
                                elif action == "despawn_selected":
                                    despawn_selected_npc(player)
                                elif action == "delete_corpse":
                                    delete_selected_corpse(player)
                                elif action == "delete_all_corpses":
                                    delete_all_corpses(player)
                                elif action == "focus_selected":
                                    focus_selected_scene_object(player)
                                elif action == "scene_filter":
                                    set_scene_object_filter(player, value)
                                    workspace_scroll = (
                                        workspace_selected_row_index(
                                            player, SIDEBAR_SCENE,
                                        ) * 42
                                    )
                                else:
                                    activate_resource_action(player, action, value)

                        elif player.edit_platforms and m_pos[0] < play_w and m_pos[1] > TOP_UI_HEIGHT:
                            cx, cy = play_w // 2, play_h // 2
                            cam_x, cam_y = player.cam_x, player.cam_y
                            hit = False
                            
                            if getattr(player, 'selected_plat', None) is not None:
                                if player.selected_plat < 1000 and player.selected_plat < len(player.platforms):
                                    p = player.platforms[player.selected_plat]
                                    px, py, pw = cx+(p.x-cam_x)*player.zoom, cy+(p.y-cam_y)*player.zoom, p.w*player.zoom
                                    if pygame.Rect(px+pw-15, py-15, 30, 30).collidepoint(m_pos):
                                        player.platforms.pop(player.selected_plat)
                                        player.selected_plat = None; hit = True
                                elif player.selected_plat >= 1000 and player.selected_plat < 2000 and (player.selected_plat - 1000) < len(getattr(player, "solid_boxes", [])):
                                    b = player.solid_boxes[player.selected_plat - 1000]
                                    px, py, pw = cx+(b.x-cam_x)*player.zoom, cy+(b.y-cam_y)*player.zoom, b.w*player.zoom
                                    if pygame.Rect(px+pw-15, py-15, 30, 30).collidepoint(m_pos):
                                        player.solid_boxes.pop(player.selected_plat - 1000)
                                        player.selected_plat = None; hit = True
                                elif player.selected_plat >= 2000 and (player.selected_plat - 2000) < len(getattr(player, "prop_list", [])):
                                    prop = player.prop_list[player.selected_plat - 2000]
                                    px, py, pw = cx+(prop.x-cam_x)*player.zoom, cy+(prop.y-cam_y)*player.zoom, 40*player.zoom
                                    if pygame.Rect(px+pw-15, py-60*player.zoom-15, 30, 30).collidepoint(m_pos):
                                        player.prop_list.pop(player.selected_plat - 2000)
                                        player.selected_plat = None; hit = True

                            if not hit:
                                # Check Props first
                                for i, prop in enumerate(getattr(player, "prop_list", [])):
                                    rect = pygame.Rect(cx+(prop.x-cam_x)*player.zoom - 20*player.zoom, cy+(prop.y-cam_y)*player.zoom - 60*player.zoom, 40*player.zoom, 60*player.zoom)
                                    if rect.collidepoint(m_pos):
                                        player.selected_plat = i + 2000; player.resize_mode = False
                                        player.drag_offset = (prop.x - (cam_x + (m_pos[0]-cx)/player.zoom), prop.y - (cam_y + (m_pos[1]-cy)/player.zoom))
                                        hit = True; break
                                # Check Platforms
                                if not hit:
                                    for i, p in enumerate(player.platforms):
                                        rect = pygame.Rect(cx+(p.x-cam_x)*player.zoom, cy+(p.y-cam_y)*player.zoom, p.w*player.zoom, p.h*player.zoom)
                                        handle = pygame.Rect(rect.right-10, rect.bottom-10, 10, 10)
                                        if handle.collidepoint(m_pos):
                                            player.selected_plat = i; player.resize_mode = True; hit = True; break
                                        elif rect.collidepoint(m_pos):
                                            player.selected_plat = i; player.resize_mode = False
                                            player.drag_offset = (p.x - (cam_x + (m_pos[0]-cx)/player.zoom), p.y - (cam_y + (m_pos[1]-cy)/player.zoom))
                                            hit = True; break
                                # Check Boxes if not hit
                                if not hit and hasattr(player, "solid_boxes"):
                                    for i, b in enumerate(player.solid_boxes):
                                        rect = pygame.Rect(cx+(b.x-cam_x)*player.zoom, cy+(b.y-cam_y)*player.zoom, b.w*player.zoom, b.h*player.zoom)
                                        handle = pygame.Rect(rect.right-10, rect.bottom-10, 10, 10)
                                        if handle.collidepoint(m_pos):
                                            player.selected_plat = i + 1000; player.resize_mode = True; hit = True; break
                                        elif rect.collidepoint(m_pos):
                                            player.selected_plat = i + 1000; player.resize_mode = False
                                            player.drag_offset = (b.x - (cam_x + (m_pos[0]-cx)/player.zoom), b.y - (cam_y + (m_pos[1]-cy)/player.zoom))
                                            hit = True; break
                            if not hit: player.selected_plat = None

                        elif (
                            sidebar_mode == SIDEBAR_SETTINGS
                            and settings_section_click_target(
                                (
                                    m_pos[0] - play_w,
                                    m_pos[1] - TOP_UI_HEIGHT,
                                ),
                                sidebar_w,
                            ) is not None
                        ):
                            transition = settings_section_transition(
                                settings_section_click_target(
                                    (
                                        m_pos[0] - play_w,
                                        m_pos[1] - TOP_UI_HEIGHT,
                                    ),
                                    sidebar_w,
                                ),
                            )
                            settings_section = transition["section"]
                            settings_scroll = transition["scroll"]
                            binding_key = transition["binding_key"]
                            active_input_attr = transition["active_input_attr"]
                        elif (
                            sidebar_content_rect.collidepoint(m_pos)
                            and (
                                sidebar_mode != SIDEBAR_SETTINGS
                                or settings_body_global_rect.collidepoint(m_pos)
                            )
                        ):
                            if sidebar_mode == SIDEBAR_SETTINGS:
                                cy = (
                                    TOP_UI_HEIGHT + SETTINGS_SECTION_NAV_HEIGHT
                                    + settings_scroll
                                    + settings_section_intro_height(settings_section)
                                )
                                for cat in settings_section_model(
                                    settings_section,
                                )["categories"]:
                                    hr = pygame.Rect(play_w+10, cy, sidebar_w-20, 30)
                                    if hr.collidepoint(m_pos):
                                        folds[cat] = not folds[cat]
                                        settings_scroll = clamp_settings_scroll(
                                            settings_scroll,
                                            settings_content_height(player, folds, settings_section),
                                            settings_body_global_rect.h,
                                        )
                                        break
                                    cy += 35
                                    if folds[cat]:
                                        if cat == "LANGUAGE":
                                            ko_btn = pygame.Rect(play_w+20, cy, 120, 30)
                                            en_btn = pygame.Rect(play_w+150, cy, 120, 30)
                                            selected_language = LANG_KO if ko_btn.collidepoint(m_pos) else LANG_EN if en_btn.collidepoint(m_pos) else None
                                            if selected_language and selected_language != player.language:
                                                player.language = set_current_language(selected_language)
                                                player.save_settings()
                                                settings_scroll = clamp_settings_scroll(
                                                    settings_scroll,
                                                    settings_content_height(player, folds, settings_section),
                                                    settings_body_global_rect.h,
                                                )
                                            cy += 45
                                        elif cat == "PROPS":
                                            for i, s in enumerate([s for s in player.sources if getattr(s, 'is_prop_source', False)]):
                                                ly = cy
                                                spawn_btn, export_btn = sidebar_action_rects(sidebar_w, ly, font_h)
                                                
                                                if not hasattr(player, "_btn_lock"):
                                                    # Spawn Button (Left Click)
                                                    if pygame.Rect(play_w+spawn_btn.x, spawn_btn.y, spawn_btn.w, spawn_btn.h).collidepoint(m_pos):
                                                        new_prof = AseProfile(f"PROP_{len(player.profiles)}", s.id, kind="prop")
                                                        new_prof.is_prop_profile = True
                                                        player.profiles.append(new_prof)
                                                        player.auto_map_profile(new_prof)
                                                        player.prop_list.append(AseAI(player, new_prof, is_prop=True, hp=3))
                                                        player._btn_lock = 15
                                                    # Export Button (Left Click)
                                                    elif pygame.Rect(play_w+export_btn.x, export_btn.y, export_btn.w, export_btn.h).collidepoint(m_pos):
                                                        prop_profile = next(
                                                            (
                                                                profile for profile_index, profile in enumerate(player.profiles)
                                                                if profile_kind(profile, profile_index) == "prop" and profile.source_idx == s.id
                                                            ),
                                                            None,
                                                        )
                                                        if prop_profile is None:
                                                            show_user_error("SAVE is disabled", "No PROP profile references this source.")
                                                        else:
                                                            begin_slice_export(player, s, "PROP")
                                                        player._btn_lock = 15
                                                
                                                cy += 35
                                            cy += 10
                                        elif cat == "NPCS":
                                            npc_rows = [
                                                (profile_index, profile)
                                                for profile_index, profile in enumerate(player.profiles)
                                                if profile_kind(profile, profile_index) == "npc"
                                            ]
                                            for profile_index, profile in npc_rows:
                                                ly = cy
                                                row_rect = pygame.Rect(play_w+20, ly-2, sidebar_w-40, 28)
                                                spawn_btn, export_btn = sidebar_action_rects(sidebar_w, ly, font_h)
                                                spawn_hit = pygame.Rect(
                                                    play_w+spawn_btn.x, spawn_btn.y, spawn_btn.w, spawn_btn.h
                                                ).collidepoint(m_pos)
                                                export_hit = pygame.Rect(
                                                    play_w+export_btn.x, export_btn.y, export_btn.w, export_btn.h
                                                ).collidepoint(m_pos)
                                                if not hasattr(player, "_btn_lock"):
                                                    if spawn_hit:
                                                        player.spawn_npc_profile(profile_index)
                                                        player._btn_lock = 15
                                                    elif export_hit:
                                                        if 0 <= profile.source_idx < len(player.sources):
                                                            begin_slice_export(player, player.sources[profile.source_idx], "NPC")
                                                        else:
                                                            show_user_error(
                                                                "NPC source is missing",
                                                                f"{profile.name} does not reference a valid Aseprite source.",
                                                            )
                                                        player._btn_lock = 15
                                                    elif row_rect.collidepoint(m_pos):
                                                        player.cur_profile_idx = profile_index
                                                        if 0 <= profile.source_idx < len(player.sources):
                                                            player.cur_source_idx = profile.source_idx
                                                        player._btn_lock = 15
                                                cy += 35
                                            cy += NPC_SLICE_STATUS_PANEL_HEIGHT
                                        elif cat == "PHYSICS": cy += 185
                                        elif cat == "AI & COMBAT": cy += ai_combat_content_height(player)
                                        elif cat == "JUICE & VFX": cy += 195
                                        elif cat == "LAYERS": cy += (layer_list_height(len(player.sources[min(player.cur_source_idx, len(player.sources)-1)].layers)) if player.sources else 55) + 20
                                        elif cat == "CAMERA": cy += 85
                                        elif cat == "BG IMAGE": cy += 85 + 25 + max(1, ((len(player.bg_layers)-1)//5 + 1)) * 30 + 10 + (270 if valid_background_layer_index(player) >= 0 else 35)
                                        elif cat == "BG COLOR": cy += 170
                                        elif cat == "CONTROLS": cy += max(1, len(player.key_map or {})) * 30 + 34
                            elif sidebar_mode == SIDEBAR_MAPPING and player.profiles:
                                cur_p = player.profiles[player.cur_profile_idx]
                                # 1. Slot Area Selection (80 ~ 450)
                                if 80 < m_pos[1] < 450:
                                    for i, action in enumerate(cur_p.mappings.keys()):
                                        rect = pygame.Rect(play_w+20, MAPPING_SLOT_TOP+i*38+slot_scroll, sidebar_w-40, 34)
                                        if rect.collidepoint(m_pos): 
                                            selected_slot = action
                                
                                # 2. Tag Area Selection
                                elif m_pos[1] >= MAPPING_TAG_TOP:
                                    if selected_slot and player.sources:
                                        src = player.sources[min(player.cur_source_idx, len(player.sources)-1)]
                                        for idx, tag in enumerate(src.tag_list):
                                            tag_rect = pygame.Rect(play_w+20, MAPPING_TAG_TOP+idx*25+tag_scroll, sidebar_w-40, 22)
                                            if tag_rect.collidepoint(m_pos):
                                                target = [player.cur_source_idx, tag]
                                                if target in cur_p.mappings[selected_slot]: 
                                                    cur_p.mappings[selected_slot].remove(target)
                                                else: 
                                                    cur_p.mappings[selected_slot].append(target)
                
                    # Right Click Handling (Remove Tabs / Clear Mappings)
                    elif event.button == 3 and player:
                        if m_pos[1] < TOP_UI_HEIGHT:
                            # The old hidden profile/source strips no longer own
                            # right-click delete actions. Use the explicit,
                            # confirmed Resource Library REMOVE action instead.
                            pass
                        elif (
                            sidebar_content_rect.collidepoint(m_pos)
                            and (
                                sidebar_mode != SIDEBAR_SETTINGS
                                or settings_body_global_rect.collidepoint(m_pos)
                            )
                        ):
                            if sidebar_mode in {SIDEBAR_SCENE, SIDEBAR_RESOURCES}:
                                pass
                            elif sidebar_mode == SIDEBAR_SETTINGS:
                                cy = (
                                    TOP_UI_HEIGHT + SETTINGS_SECTION_NAV_HEIGHT
                                    + settings_scroll
                                    + settings_section_intro_height(settings_section)
                                )
                                for cat in settings_section_model(
                                    settings_section,
                                )["categories"]:
                                    hr = pygame.Rect(play_w+10, cy, sidebar_w-20, 30)
                                    cy += 35
                                    if folds[cat]:
                                        if cat == "LANGUAGE":
                                            cy += 45
                                        elif cat == "PROPS":
                                            for s in [src for src in player.sources if getattr(src, 'is_prop_source', False)]:
                                                if pygame.Rect(play_w+20, cy-2, sidebar_w-40, 28).collidepoint(m_pos):
                                                    show_source_removal_result(player.remove_source_by_index(s.id))
                                                    break # Break loop after modifying list
                                                cy += 35
                                            cy += 10
                                        elif cat == "NPCS":
                                            cy += len([
                                                profile for profile_index, profile in enumerate(player.profiles)
                                                if profile_kind(profile, profile_index) == "npc"
                                            ]) * 35 + NPC_SLICE_STATUS_PANEL_HEIGHT
                                        elif cat == "PHYSICS": cy += 185
                                        elif cat == "AI & COMBAT": cy += ai_combat_content_height(player)
                                        elif cat == "JUICE & VFX": cy += 195
                                        elif cat == "LAYERS": cy += (layer_list_height(len(player.sources[min(player.cur_source_idx, len(player.sources)-1)].layers)) if player.sources else 55) + 20
                                        elif cat == "CAMERA": cy += 85
                                        elif cat == "BG IMAGE": cy += 85 + 25 + max(1, ((len(player.bg_layers)-1)//5 + 1)) * 30 + 10 + (270 if valid_background_layer_index(player) >= 0 else 35)
                                        elif cat == "BG COLOR": cy += 170
                                        elif cat == "CONTROLS": cy += max(1, len(player.key_map or {})) * 30 + 34
                            elif sidebar_mode == SIDEBAR_MAPPING and player.profiles:
                                cur_p = player.profiles[player.cur_profile_idx]
                                for i, action in enumerate(cur_p.mappings.keys()):
                                    if pygame.Rect(play_w+20, MAPPING_SLOT_TOP+i*38+slot_scroll, sidebar_w-40, 34).collidepoint(m_pos): cur_p.mappings[action] = []
            if event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                was_parallax_drag = bool(getattr(player, "parallax_gizmo_dragging", False))
                was_parallax_slider = bool(getattr(player, "parallax_offset_edit", None))
                changed = end_parallax_gizmo_drag(player)
                changed = commit_parallax_offset_edit(player) or changed
                if changed:
                    player.save_settings()
                if was_parallax_drag or was_parallax_slider:
                    continue
            if event.type == pygame.MOUSEBUTTONUP and event.button == 3: is_dragging_cam = False
            if event.type == pygame.KEYDOWN and player:
                if event.key == pygame.K_F10:
                    enable_performance = not performance.enabled
                    performance.set_enabled(enable_performance, clear=enable_performance)
                    player.performance_monitor = performance
                    continue
                if active_input_attr:
                    if event.key == pygame.K_RETURN:
                        try:
                            val = float(input_text)
                            if active_input_attr in ['target_ai_count', 'bg_color_0', 'bg_color_1', 'bg_color_2']: val = int(val)
                            
                            if active_input_attr.startswith('bg_color_'):
                                idx = int(active_input_attr.split('_')[-1])
                                player.bg_color[idx] = max(0, min(255, int(val)))
                            elif active_input_attr.startswith('bglayer_'):
                                parts = active_input_attr.split('_', 2)
                                l_idx = int(parts[1])
                                l_attr = parts[2]
                                if (
                                    l_attr not in BACKGROUND_LAYER_SLIDER_DEFAULTS
                                    or not 0 <= l_idx < len(getattr(player, "bg_layers", []))
                                ):
                                    raise ValueError("Background layer input is no longer active.")
                                offset_before = (
                                    get_parallax_layer_offset(player.bg_layers[l_idx])
                                    if l_attr in {"off_x", "off_y"}
                                    else None
                                )
                                player.bg_layers[l_idx][l_attr] = int(val) if "alpha" in l_attr or "off" in l_attr else float(val)
                                player.bg_layers[l_idx]['needs_update'] = True
                                if offset_before is not None:
                                    push_parallax_offset_history(
                                        player,
                                        player.bg_layers[l_idx],
                                        offset_before,
                                        get_parallax_layer_offset(player.bg_layers[l_idx]),
                                        f"input_{l_attr}",
                                    )
                            else:
                                setattr(player, active_input_attr, val)
                            player.save_settings()
                            if "bg_" in active_input_attr or "bglayer_" in active_input_attr: player.bg_needs_update = True
                        except ValueError:
                            pass # Ignore invalid inputs
                        active_input_attr = None
                    elif event.key == pygame.K_ESCAPE:
                        cancel_parallax_offset_edit(player)
                        active_input_attr = None
                    elif event.key == pygame.K_BACKSPACE:
                        input_text = input_text[:-1]
                    else:
                        input_text += event.unicode
                elif (
                    shortcut_result := handle_parallax_history_shortcut(
                        player, event.key,
                        getattr(event, "mod", pygame.key.get_mods()),
                    )
                ):
                    if shortcut_result[1]:
                        player.save_settings()
                elif binding_key:
                    if event.key != pygame.K_ESCAPE:
                        existing_owner = next((k for k, v in player.key_map.items() if v == event.key), None)
                        if existing_owner:
                            player.key_map[existing_owner] = player.key_map[binding_key]
                        player.key_map[binding_key] = event.key
                        player.save_settings()
                    binding_key = None
                else:
                    if "JUMP" not in player.key_map: player.key_map["JUMP"] = pygame.K_SPACE
                    k = event.key; km = player.key_map
                    if sidebar_mode in {SIDEBAR_SCENE, SIDEBAR_RESOURCES} and k == pygame.K_ESCAPE:
                        sidebar_mode = SIDEBAR_MAPPING
                        workspace_controls = []
                        workspace_viewport = None
                    elif sidebar_mode in {SIDEBAR_SCENE, SIDEBAR_RESOURCES} and k == pygame.K_TAB:
                        sidebar_mode = (
                            SIDEBAR_RESOURCES
                            if sidebar_mode == SIDEBAR_SCENE else SIDEBAR_SCENE
                        )
                        workspace_scroll = workspace_selected_row_index(player, sidebar_mode) * (
                            42 if sidebar_mode == SIDEBAR_SCENE else 58
                        )
                    elif sidebar_mode in {SIDEBAR_SCENE, SIDEBAR_RESOURCES} and k in (pygame.K_UP, pygame.K_DOWN):
                        model_key = "scene_rows" if sidebar_mode == SIDEBAR_SCENE else "resource_rows"
                        rows = selection_workspace_model(player)[model_key]
                        if sidebar_mode == SIDEBAR_SCENE:
                            rows = scene_rows_for_current_filter(player, rows)
                        if rows:
                            current_index = workspace_selected_row_index(player, sidebar_mode)
                            next_index = max(
                                0, min(len(rows) - 1, current_index + (-1 if k == pygame.K_UP else 1)),
                            )
                            if sidebar_mode == SIDEBAR_SCENE:
                                select_scene_actor(player, rows[next_index]["key"])
                                workspace_scroll = next_index * 42
                            else:
                                select_resource_row(player, rows[next_index]["source_index"])
                                workspace_scroll = next_index * 58
                    elif k == pygame.K_F5:
                        reload_ok = refresh_all_sources_preserving_scene(player)
                        if reload_ok:
                            player.scene_status_message = ""
                        else:
                            show_user_error(tr("error.source_refresh_title"), tr("error.source_refresh"), key="manual-source-refresh")
                    elif k in [pygame.K_DELETE, pygame.K_BACKSPACE] and getattr(player, 'edit_platforms', False) and player.selected_plat is not None:
                        if player.selected_plat < 1000 and player.selected_plat < len(player.platforms):
                            player.platforms.pop(player.selected_plat)
                        elif player.selected_plat >= 1000 and (player.selected_plat - 1000) < len(getattr(player, 'solid_boxes', [])):
                            player.solid_boxes.pop(player.selected_plat - 1000)
                        player.selected_plat = None
                    elif k == km.get("JUMP") or k == pygame.K_UP:
                        keys = pygame.key.get_pressed()
                        if keys[pygame.K_DOWN] and player.grounded:
                            player.drop_through_timer = 200; player.vy = 5; player.grounded = False
                        elif player.jumps_left > 0:
                            player.vy = player.jump_power; player.grounded = False; player.jumps_left -= 1
                    elif k == km.get("SUMMON", pygame.K_g):
                        recall_live_npcs(player)
                    elif k == km.get("ATTACK"): player.handle_attack(pygame.key.get_pressed())
                    elif k == km.get("DASH"): player.trigger_action("DASH")
                    elif k == km.get("SKILL1"): player.trigger_action("SKILL 1")
                    elif k == km.get("SKILL2"): player.trigger_action("SKILL 2")
                    elif k == km.get("SKILL3"): player.trigger_action("SKILL 3")
                    elif k == km.get("HIT_1"):
                        player.hit_count = getattr(player, 'hit_count', 0) + 1
                        hit_slot = "HIT_1" if player.hit_count % 2 == 1 else "HIT_2"
                        if not player.profiles[0].mappings.get(hit_slot, []): hit_slot = "HIT_1"
                        player.trigger_action(hit_slot)
                    elif k == km.get("SYNERGY"): player.trigger_synergy_attack()
                    elif k == km.get("SWAP"): 
                        if hasattr(player, 'execute_swap'): player.execute_swap()
                    elif k == pygame.K_f: player.cam_follow = True
                    elif k == pygame.K_h: player.show_hitboxes = not player.show_hitboxes
                    elif k == pygame.K_p: player.is_paused = not player.is_paused
                    elif k == pygame.K_o: player.step_forward = True
                    elif k == pygame.K_LEFTBRACKET: player.playback_speed = max(0.1, player.playback_speed - 0.1)
                    elif k == pygame.K_RIGHTBRACKET: player.playback_speed = min(5.0, player.playback_speed + 0.1)
            if event.type == pygame.MOUSEWHEEL and player:
                tooltip_controller.reset()
                log_debug(f"[WHEEL] m_pos:{m_pos}, play_w:{play_w}, event.y:{event.y}")
                if (
                    sidebar_mode in {SIDEBAR_SCENE, SIDEBAR_RESOURCES}
                    and workspace_viewport
                    and workspace_viewport.collidepoint(m_pos)
                ):
                    workspace_scroll = max(0, workspace_scroll - event.y * 84)
                elif m_pos[0] < play_w:
                    player.zoom = max(0.1, min(player.zoom + event.y * 0.2, 20.0)); [s.clear_cache() for s in player.sources]; player.bg_needs_update = True
                else:
                    delta = event.y * 40
                    if (
                        sidebar_mode == SIDEBAR_SETTINGS
                        and settings_body_global_rect.collidepoint(m_pos)
                    ):
                        calc_h = settings_content_height(
                            player, folds, settings_section,
                        )
                        settings_scroll = clamp_settings_scroll(
                            settings_scroll + delta, calc_h,
                            settings_body_global_rect.h,
                        )
                    elif sidebar_mode == SIDEBAR_MAPPING and m_pos[1] < MAPPING_TAG_TOP:
                        # Slot Scroll Limit
                        if player.profiles:
                            cur_p = player.profiles[player.cur_profile_idx]
                            total_h = len(cur_p.mappings) * 38
                            slot_scroll = max(min(0, slot_scroll + delta), -max(0, total_h - MAPPING_SLOT_HEIGHT))
                    elif sidebar_mode == SIDEBAR_MAPPING:
                        # Tag Scroll Limit
                        if player.sources:
                            src = player.sources[min(player.cur_source_idx, len(player.sources)-1)]
                            total_h = len(src.tag_list) * 25
                            tag_scroll = max(min(0, tag_scroll + delta), -max(0, total_h - (sh - MAPPING_TAG_TOP - 20)))
            if event.type == pygame.MOUSEMOTION and player:
                if update_parallax_gizmo_drag(
                    player,
                    m_pos,
                    bool(pygame.key.get_mods() & pygame.KMOD_SHIFT),
                ):
                    is_dragging_cam = False
                    continue
                if player.edit_platforms and player.selected_plat is not None and pygame.mouse.get_pressed()[0]:
                    cx, cy = play_w // 2, play_h // 2
                    cam_x, cam_y = player.cam_x, player.cam_y
                    
                    if hasattr(player, 'resize_mode') and player.resize_mode:
                        mx, my = (m_pos[0]-cx)/player.zoom + cam_x, (m_pos[1]-cy)/player.zoom + cam_y
                        if player.selected_plat < 1000:
                            p = player.platforms[player.selected_plat]
                            p.w = max(20, mx - p.x); p.h = max(20, my - p.y)
                        else:
                            b = player.solid_boxes[player.selected_plat - 1000]
                            b.w = max(20, mx - b.x); b.h = max(20, my - b.y)
                    else:
                        mx, my = (m_pos[0]-cx)/player.zoom + cam_x, (m_pos[1]-cy)/player.zoom + cam_y
                        if player.selected_plat < 1000:
                            player.platforms[player.selected_plat].x = mx + player.drag_offset[0]
                            player.platforms[player.selected_plat].y = my + player.drag_offset[1]
                        elif player.selected_plat < 2000:
                            player.solid_boxes[player.selected_plat - 1000].x = mx + player.drag_offset[0]
                            player.solid_boxes[player.selected_plat - 1000].y = my + player.drag_offset[1]
                        else:
                            player.prop_list[player.selected_plat - 2000].x = mx + player.drag_offset[0]
                            player.prop_list[player.selected_plat - 2000].y = my + player.drag_offset[1]
                
                elif is_dragging_cam: 
                    dx, dy = m_pos[0] - last_m_pos[0], m_pos[1] - last_m_pos[1]
                    player.cam_x -= dx / player.zoom; player.cam_y -= dy / player.zoom; last_m_pos = m_pos
        performance.record_since("events", events_started)
        ui_render_started = time.perf_counter_ns() if performance.enabled else None
        if sidebar_mode == SIDEBAR_MAPPING:
            draw_mapping_workspace_intro(
                screen, player, (font_s, font_b), sidebar_content_rect,
            )
        if (
            sidebar_mode == SIDEBAR_SETTINGS
            or (sidebar_mode == SIDEBAR_MAPPING and player.profiles)
        ):
            cur_p = player.profiles[player.cur_profile_idx] if player.profiles else None
            if sidebar_mode == SIDEBAR_SETTINGS:
                settings_origin = (play_w, TOP_UI_HEIGHT)
                full_sidebar_content_rect = sidebar_content_rect
                set_surf = pygame.Surface(
                    (sidebar_w, max(1, sidebar_content_rect.h)), pygame.SRCALPHA,
                )
                sidebar_content_rect = settings_body_global_rect
                settings_m_pos = (m_pos[0], m_pos[1] - TOP_UI_HEIGHT)
                set_surf.set_clip(pygame.Rect(
                    0, SETTINGS_SECTION_NAV_HEIGHT, sidebar_w,
                    max(0, set_surf.get_height() - SETTINGS_SECTION_NAV_HEIGHT),
                ))
                cy = SETTINGS_SECTION_NAV_HEIGHT + settings_scroll
                cy = draw_settings_section_intro(
                    set_surf, settings_section, cy, font_s, player,
                )
                for cat in settings_section_model(
                    settings_section,
                )["categories"]:
                    category_label = tr(CATEGORY_TRANSLATION_KEYS[cat])
                    hr = pygame.Rect(10, cy, sidebar_w-20, 30); pygame.draw.rect(set_surf, (50,50,60), hr, border_radius=5); set_surf.blit(font_b.render(f"{'+' if not folds[cat] else '-'} {category_label}", True, (255,255,255)), (hr.x+10, hr.y+7)); cy += 35
                    if folds[cat]:
                        if cat == "LANGUAGE":
                            for language, x in ((LANG_KO, 20), (LANG_EN, 150)):
                                language_btn = pygame.Rect(x, cy, 120, 30)
                                active = player.language == language
                                pygame.draw.rect(set_surf, (59,130,246) if active else (60,60,70), language_btn, border_radius=5)
                                draw_centered_label(set_surf, font_b, tr(f"language.{language}"), language_btn)
                            cy += 45
                        elif cat == "PROPS":
                            for i, s in enumerate([s for s in player.sources if getattr(s, 'is_prop_source', False)]):
                                ly = cy
                                pygame.draw.rect(set_surf, (60,60,70), (20, ly-2, sidebar_w-40, 28), border_radius=4)
                                prop_status = source_slice_status_text(s)
                                set_surf.blit(font_s.render(f"{s.name[:10]}  {prop_status}", True, (255,255,255)), (30, ly+4))
                                spawn_btn, export_btn = sidebar_action_rects(sidebar_w, ly, font_h)
                                pygame.draw.rect(set_surf, (34, 139, 34), spawn_btn, border_radius=4)
                                draw_centered_label(set_surf, font_h, tr("common.spawn"), spawn_btn)
                                register_clipped_tooltip(
                                    tooltip_regions, spawn_btn, "tooltip.prop.spawn",
                                    settings_origin, sidebar_content_rect,
                                )
                                prop_profile = next((p for index, p in enumerate(player.profiles) if profile_kind(p, index) == "prop" and p.source_idx == s.id), None)
                                can_export = prop_profile is not None and slice_export_availability(s)["enabled"]
                                pygame.draw.rect(set_surf, (59, 130, 246) if can_export else (70, 70, 75), export_btn, border_radius=4)
                                draw_centered_label(set_surf, font_h, tr("common.save"), export_btn)
                                register_clipped_tooltip(
                                    tooltip_regions, export_btn, "tooltip.prop.save",
                                    settings_origin, sidebar_content_rect,
                                )
                                cy += 35
                            cy += 10
                        elif cat == "NPCS":
                            npc_rows = [
                                (index, item) for index, item in enumerate(player.profiles)
                                if profile_kind(item, index) == "npc"
                            ]
                            for profile_index, profile in npc_rows:
                                ly = cy
                                row_color = (72, 84, 108) if profile_index == player.cur_profile_idx else (60,60,70)
                                pygame.draw.rect(set_surf, row_color, (20, ly-2, sidebar_w-40, 28), border_radius=4)
                                source_label = f"P:0 / FX:0 / {tr('status.save')}:{tr('status.off')}"
                                if 0 <= profile.source_idx < len(player.sources):
                                    npc_source = player.sources[profile.source_idx]
                                    source_label = source_slice_status_text(npc_source)
                                set_surf.blit(font_s.render(f"{profile.name[:10]}  {source_label}", True, (255,255,255)), (30, ly+4))
                                spawn_btn, export_btn = sidebar_action_rects(sidebar_w, ly, font_h)
                                pygame.draw.rect(set_surf, (34, 139, 34), spawn_btn, border_radius=4)
                                draw_centered_label(set_surf, font_h, tr("common.spawn"), spawn_btn)
                                register_clipped_tooltip(
                                    tooltip_regions, spawn_btn, "tooltip.npc.spawn",
                                    settings_origin, sidebar_content_rect,
                                )
                                can_export = 0 <= profile.source_idx < len(player.sources) and slice_export_availability(player.sources[profile.source_idx])["enabled"]
                                button_color = (59, 130, 246) if can_export else (70,70,75)
                                pygame.draw.rect(set_surf, button_color, export_btn, border_radius=4)
                                draw_centered_label(set_surf, font_h, tr("common.save"), export_btn)
                                register_clipped_tooltip(
                                    tooltip_regions, export_btn, "tooltip.npc.save",
                                    settings_origin, sidebar_content_rect,
                                )
                                cy += 35
                            selected_npc = next(
                                (profile for profile_index, profile in npc_rows if profile_index == player.cur_profile_idx),
                                npc_rows[0][1] if npc_rows else None,
                            )
                            status = npc_slice_status_data(
                                selected_npc, player.sources, getattr(player, "last_npc_death_result", None),
                            )
                            localized_status = localized_npc_status(status)
                            panel = pygame.Rect(20, cy, sidebar_w-40, NPC_SLICE_STATUS_PANEL_HEIGHT-8)
                            pygame.draw.rect(set_surf, (38, 42, 52), panel, border_radius=5)
                            register_clipped_tooltip(
                                tooltip_regions, panel, "tooltip.detected_slices",
                                settings_origin, sidebar_content_rect,
                            )
                            set_surf.blit(font_b.render(tr("status.detected_slices"), True, (120, 190, 255)), (30, cy+7))
                            parts_text = str(status["parts"]) if status["parts"] else tr("common.none")
                            particles_text = str(status["particles"]) if status["particles"] else tr("common.none")
                            set_surf.blit(font_s.render(f"{tr('status.parts')}: {parts_text}", True, (235,235,235)), (30, cy+29))
                            set_surf.blit(font_s.render(f"{tr('status.particles')}: {particles_text}", True, (235,235,235)), (150, cy+29))
                            set_surf.blit(font_s.render(f"{tr('status.death')}: {localized_status['death']}", True, (235,235,235)), (30, cy+50))
                            save_color = (110, 220, 140) if status["save_enabled"] else (200, 150, 120)
                            set_surf.blit(font_s.render(f"{tr('status.save')}: {localized_status['save']}", True, save_color), (30, cy+71))
                            if localized_status["runtime"]:
                                runtime_text = ellipsize_ui_text(localized_status["runtime"], font_s, panel.w-20)
                                set_surf.blit(font_s.render(runtime_text, True, (110, 220, 140)), (30, cy+92))
                            if localized_status["reason"]:
                                reason_text = ellipsize_ui_text(localized_status["reason"], font_s, panel.w-20)
                                set_surf.blit(font_s.render(reason_text, True, (210, 165, 110)), (30, cy+113))
                            cy += NPC_SLICE_STATUS_PANEL_HEIGHT
                        elif cat == "PHYSICS":
                            for i, (label_key, mn, mx, at, inv) in enumerate([("ui.dash_velocity",10,50,"dash_speed",0), ("ui.jump_power",10,25,"jump_power",1), ("ui.powerbomb_speed",10,60,"powerbomb_speed",0), ("ui.platform_alpha",0,255,"platform_alpha",0)]):
                                y = cy+i*45; set_surf.blit(font_s.render(tr(label_key), True, (150,150,150)), (20, y));
                                if at in {"dash_speed", "jump_power"}:
                                    register_clipped_tooltip(
                                        tooltip_regions, pygame.Rect(20, y-5, sidebar_w-40, 30),
                                        f"tooltip.{at.replace('_speed', '_velocity')}",
                                        settings_origin, sidebar_content_rect,
                                    )
                                controls = settings_slider_control_rects(sidebar_w, y)
                                sl = controls["slider"]; pygame.draw.rect(set_surf, (60,60,70), sl)
                                v = slider_setting_value(player, at); n = (v-mn)/(mx-mn) if not inv else (-v-mn)/(mx-mn)
                                pygame.draw.circle(set_surf, (59,130,246), (int(sl.x+n*sl.w), y+9), 8)
                                # Value Text
                                txt_val = input_text + "|" if active_input_attr == at and pygame.time.get_ticks() % 1000 < 500 else (input_text if active_input_attr == at else (f"{int(v)}" if at in ["platform_alpha", "cam_v_offset"] else f"{v:.1f}"))
                                bg_c = (30,30,35) if active_input_attr == at else (45,45,50)
                                pygame.draw.rect(set_surf, bg_c, controls["numeric"], border_radius=3)
                                set_surf.blit(font_s.render(txt_val, True, (255,255,255) if active_input_attr == at else (200,200,200)), (controls["numeric"].x+3, y))
                                draw_slider_reset_button(set_surf, font_h, controls["reset"])
                                register_clipped_tooltip(
                                    tooltip_regions, controls["reset"], "tooltip.setting_reset",
                                    settings_origin, sidebar_content_rect,
                                )
                                
                                if m_pos[1] > TOP_UI_HEIGHT and pygame.mouse.get_pressed()[0]:
                                    if controls["reset"].move(play_w, 0).collidepoint(settings_m_pos) and not hasattr(player, "_btn_lock"):
                                        reset_slider_setting(player, at)
                                        active_input_attr = None; input_text = ""; player._btn_lock = 10
                                    elif controls["numeric"].move(play_w, 0).collidepoint(settings_m_pos):
                                        if active_input_attr != at: active_input_attr = at; input_text = str(int(v)) if at in ["platform_alpha", "cam_v_offset"] else str(round(v, 1))
                                    elif sl.move(play_w, 0).inflate(0,10).collidepoint(settings_m_pos):
                                        active_input_attr = None
                                        ratio = max(0.0, min(1.0, (m_pos[0]-(play_w+sl.x))/sl.w))
                                        setattr(player, at, mn+ratio*(mx-mn) if not inv else -(mn+ratio*(mx-mn))); player.save_settings()
                            cy += 185
                        elif cat == "AI & COMBAT":
                            for i, (label_key, mn, mx, at) in enumerate([("ui.ai_count",0,10,"target_ai_count"), ("ui.npc_max_hp",1,100,"npc_max_hp"), ("ui.attack_forward",0,30,"atk_forward_v")]):
                                y = cy+i*45; set_surf.blit(font_s.render(tr(label_key), True, (150,150,150)), (20, y)); controls = settings_slider_control_rects(sidebar_w, y); sl = controls["slider"]; pygame.draw.rect(set_surf, (60,60,70), sl); v = slider_setting_value(player, at); n = (v-mn)/(mx-mn); pygame.draw.circle(set_surf, (59,130,246), (int(sl.x+n*sl.w), y+9), 8)
                                txt_val = input_text + "|" if active_input_attr == at and pygame.time.get_ticks() % 1000 < 500 else (input_text if active_input_attr == at else (f"{int(v)}" if at in ["target_ai_count", "npc_max_hp"] else f"{v:.1f}"))
                                pygame.draw.rect(set_surf, (30,30,35) if active_input_attr == at else (45,45,50), controls["numeric"], border_radius=3)
                                set_surf.blit(font_s.render(txt_val, True, (255,255,255) if active_input_attr == at else (200,200,200)), (controls["numeric"].x+3, y))
                                draw_slider_reset_button(set_surf, font_h, controls["reset"])
                                register_clipped_tooltip(
                                    tooltip_regions, controls["reset"], "tooltip.setting_reset",
                                    settings_origin, sidebar_content_rect,
                                )
                                if m_pos[1] > TOP_UI_HEIGHT and pygame.mouse.get_pressed()[0]:
                                    if controls["reset"].move(play_w, 0).collidepoint(settings_m_pos) and not hasattr(player, "_btn_lock"):
                                        reset_slider_setting(player, at)
                                        active_input_attr = None; input_text = ""; player._btn_lock = 10
                                    elif controls["numeric"].move(play_w, 0).collidepoint(settings_m_pos):
                                        if active_input_attr != at: active_input_attr = at; input_text = str(int(v)) if at in ["target_ai_count", "npc_max_hp"] else str(round(v, 1))
                                    elif sl.move(play_w, 0).inflate(0,10).collidepoint(settings_m_pos):
                                        active_input_attr = None
                                        ratio = max(0.0, min(1.0, (m_pos[0]-(play_w+sl.x))/sl.w))
                                        value = mn+ratio*(mx-mn)
                                        setattr(player, at, value if at not in ["target_ai_count", "npc_max_hp"] else int(value)); player.save_settings()
                            
                            y = cy + 135
                            set_surf.blit(font_s.render(tr("ui.ranged_combo"), True, (150,150,150)), (20, y))
                            btn = pygame.Rect(sidebar_w-60, y-5, 40, 20); val = getattr(player, 'is_ranged_combo', False)
                            pygame.draw.rect(set_surf, (22, 163, 74) if val else (220, 38, 38), btn, border_radius=10)
                            pygame.draw.circle(set_surf, (255,255,255), (btn.x+30 if val else btn.x+10, btn.y+10), 8)
                            if sidebar_content_rect.collidepoint(m_pos) and pygame.mouse.get_pressed()[0] and pygame.Rect(play_w+btn.x, y-5, btn.w, btn.h).collidepoint(settings_m_pos):
                                if not hasattr(player, "_btn_lock"): setattr(player, 'is_ranged_combo', not val); player._btn_lock = 10; player.save_settings()

                            y = cy + 175
                            set_surf.blit(font_s.render(tr("ui.swap_target"), True, (150,150,150)), (20, y))
                            j_offset = 0
                            swap_indices = swap_candidate_profile_indices(player)
                            for j in swap_indices:
                                btn = pygame.Rect(110 + (j_offset%4)*55, y - 5 + (j_offset//4)*30, 50, 24)
                                is_sel = getattr(player, 'swap_target_idx', 0) == j
                                pygame.draw.rect(set_surf, (59,130,246) if is_sel else (60,60,70), btn, border_radius=4)
                                role_label = "PARTNER" if profile_kind(player.profiles[j], j) == "partner" else "NPC"
                                button_label = f"P {j}" if role_label == "PARTNER" else f"NPC {j}"
                                set_surf.blit(font_h.render(button_label, True, (255,255,255)), (btn.x+8, btn.y+5))
                                if sidebar_content_rect.collidepoint(m_pos) and pygame.mouse.get_pressed()[0] and pygame.Rect(play_w+btn.x, btn.y, btn.w, btn.h).collidepoint(settings_m_pos):
                                    player.swap_target_idx = j; player.save_settings()
                                j_offset += 1
                                
                            y_roam = y + 35 + max(0, ((len(player.profiles)-2)//4)*30)
                            set_surf.blit(font_s.render(tr("ui.roaming_target"), True, (150,150,150)), (20, y_roam))
                            j_offset_r = 0
                            for j in (
                                index for index, profile in enumerate(player.profiles)
                                if index > 0 and profile_kind(profile, index) == "npc"
                            ):
                                btn = pygame.Rect(110 + (j_offset_r%4)*55, y_roam - 5 + (j_offset_r//4)*30, 50, 24)
                                is_sel = getattr(player, 'roaming_npc_idx', 1) == j
                                pygame.draw.rect(set_surf, (22,163,74) if is_sel else (60,60,70), btn, border_radius=4)
                                set_surf.blit(font_h.render(f"NPC {j}", True, (255,255,255)), (btn.x+8, btn.y+5))
                                if sidebar_content_rect.collidepoint(m_pos) and pygame.mouse.get_pressed()[0] and pygame.Rect(play_w+btn.x, btn.y, btn.w, btn.h).collidepoint(settings_m_pos):
                                    player.roaming_npc_idx = j; player.save_settings()
                                j_offset_r += 1

                            behavior_y = (
                                cy + 245
                                + max(0, ((len(player.profiles)-2)//4)*30) * 2
                            )
                            behavior_header = pygame.Rect(
                                20, behavior_y - 5, sidebar_w - 40, 24,
                            )
                            set_surf.blit(
                                font_s.render(
                                    tr("ui.npc_behavior"), True, (150,150,150),
                                ),
                                (20, behavior_y),
                            )
                            register_clipped_tooltip(
                                tooltip_regions, behavior_header,
                                "tooltip.npc_behavior",
                                settings_origin, sidebar_content_rect,
                            )
                            for row_index, (profile_index, profile) in enumerate(
                                npc_profile_entries(player)
                            ):
                                row_y = behavior_y + 28 + row_index * 32
                                name_text = ellipsize_ui_text(
                                    profile.name, font_h, 125,
                                )
                                set_surf.blit(
                                    font_h.render(name_text, True, (210,210,215)),
                                    (25, row_y + 5),
                                )
                                behavior = normalize_npc_behavior(
                                    getattr(profile, "ai_behavior", "balanced"),
                                )
                                behavior_btn = pygame.Rect(
                                    165, row_y, sidebar_w - 190, 25,
                                )
                                pygame.draw.rect(
                                    set_surf, (59,130,246),
                                    behavior_btn, border_radius=5,
                                )
                                draw_centered_label(
                                    set_surf, font_h,
                                    tr(f"npc_behavior.{behavior}"),
                                    behavior_btn,
                                )
                                register_clipped_tooltip(
                                    tooltip_regions,
                                    pygame.Rect(20, row_y, sidebar_w - 40, 27),
                                    "tooltip.npc_behavior",
                                    settings_origin, sidebar_content_rect,
                                )
                                if (
                                    sidebar_content_rect.collidepoint(m_pos)
                                    and pygame.mouse.get_pressed()[0]
                                    and pygame.Rect(
                                        play_w + behavior_btn.x,
                                        behavior_btn.y,
                                        behavior_btn.w,
                                        behavior_btn.h,
                                    ).collidepoint(settings_m_pos)
                                    and not hasattr(player, "_btn_lock")
                                ):
                                    cycle_npc_behavior(profile)
                                    player.cur_profile_idx = profile_index
                                    player._btn_lock = 15
                                    player.save_project()

                            npc_entries = npc_profile_entries(player)
                            if not npc_entries:
                                no_npc_text = ellipsize_ui_text(
                                    tr("settings.npc.empty"), font_s,
                                    sidebar_w - 48,
                                )
                                set_surf.blit(
                                    font_s.render(no_npc_text, True, (210,155,115)),
                                    (24, behavior_y + 30),
                                )
                            replay_y = (
                                behavior_y + 28
                                + len(npc_entries) * 32
                                + (22 if not npc_entries else 0) + 4
                            )
                            replay_btn = pygame.Rect(
                                20, replay_y, sidebar_w - 40, 28,
                            )
                            pygame.draw.rect(
                                set_surf, (79, 70, 229),
                                replay_btn, border_radius=5,
                            )
                            draw_centered_label(
                                set_surf, font_h,
                                tr("ui.replay_npc_intro"), replay_btn,
                            )
                            register_clipped_tooltip(
                                tooltip_regions, replay_btn,
                                "tooltip.replay_npc_intro",
                                settings_origin, sidebar_content_rect,
                            )
                            if (
                                sidebar_content_rect.collidepoint(m_pos)
                                and pygame.mouse.get_pressed()[0]
                                and pygame.Rect(
                                    play_w + replay_btn.x,
                                    replay_btn.y,
                                    replay_btn.w,
                                    replay_btn.h,
                                ).collidepoint(settings_m_pos)
                                and not hasattr(player, "_btn_lock")
                            ):
                                replay_npc_intro(player)
                                player._btn_lock = 15
                            replay_status = getattr(
                                player, "npc_intro_replay_status", "",
                            )
                            if replay_status:
                                status_text = ellipsize_ui_text(
                                    replay_status, font_s, sidebar_w - 48,
                                )
                                set_surf.blit(
                                    font_s.render(
                                        status_text, True, (180, 200, 230),
                                    ),
                                    (24, replay_y + 34),
                                )

                            cy += ai_combat_content_height(player)
                        elif cat == "JUICE & VFX":
                            helper_text = ellipsize_ui_text(
                                tr("settings.vfx.help"), font_h, sidebar_w - 40,
                            )
                            set_surf.blit(font_h.render(helper_text, True, (135,145,165)), (20, cy))
                            cy += 20
                            for i, (label_key, at) in enumerate([("ui.enable_shake", "shake_enabled"), ("ui.enable_ghost", "vfx_enabled")]):
                                y = cy+i*40; set_surf.blit(font_s.render(tr(label_key), True, (150,150,150)), (20, y)); btn = pygame.Rect(sidebar_w-60, y-5, 40, 20); val = getattr(player, at); pygame.draw.rect(set_surf, (22, 163, 74) if val else (220, 38, 38), btn, border_radius=10); pygame.draw.circle(set_surf, (255,255,255), (btn.x+30 if val else btn.x+10, btn.y+10), 8)
                                if at == "shake_enabled":
                                    register_clipped_tooltip(
                                        tooltip_regions, pygame.Rect(20, y-5, sidebar_w-40, 30),
                                        "tooltip.shake", settings_origin, sidebar_content_rect,
                                    )
                                if sidebar_content_rect.collidepoint(m_pos) and pygame.mouse.get_pressed()[0] and pygame.Rect(play_w+btn.x, y-5, btn.w, btn.h).collidepoint(settings_m_pos):
                                    if not hasattr(player, "_btn_lock"): setattr(player, at, not val); player._btn_lock = 10; player.save_settings()
                            y = cy + 85; set_surf.blit(font_s.render(tr("ui.shake_power"), True, (150,150,150)), (20, y));
                            controls = settings_slider_control_rects(sidebar_w, y); sl = controls["slider"]; pygame.draw.rect(set_surf, (60,60,70), sl); shake_value = slider_setting_value(player, "base_shake"); n = shake_value / 3.0;
                            pygame.draw.circle(set_surf, (220, 38, 38), (int(sl.x+n*sl.w), y+9), 8)
                            
                            txt_val = input_text + "|" if active_input_attr == "base_shake" and pygame.time.get_ticks() % 1000 < 500 else (input_text if active_input_attr == "base_shake" else f"{shake_value:.1f}")
                            pygame.draw.rect(set_surf, (30,30,35) if active_input_attr == "base_shake" else (45,45,50), controls["numeric"], border_radius=3)
                            set_surf.blit(font_s.render(txt_val, True, (255,255,255) if active_input_attr == "base_shake" else (200,200,200)), (controls["numeric"].x+3, y))
                            draw_slider_reset_button(set_surf, font_h, controls["reset"])
                            register_clipped_tooltip(tooltip_regions, controls["reset"], "tooltip.setting_reset", settings_origin, sidebar_content_rect)
                            
                            if m_pos[1] > TOP_UI_HEIGHT and pygame.mouse.get_pressed()[0]:
                                if controls["reset"].move(play_w, 0).collidepoint(settings_m_pos) and not hasattr(player, "_btn_lock"):
                                    reset_slider_setting(player, "base_shake"); active_input_attr = None; input_text = ""; player._btn_lock = 10
                                elif controls["numeric"].move(play_w, 0).collidepoint(settings_m_pos):
                                    if active_input_attr != "base_shake": active_input_attr = "base_shake"; input_text = str(round(shake_value, 1))
                                elif sl.move(play_w, 0).inflate(0,10).collidepoint(settings_m_pos):
                                    active_input_attr = None
                                    player.base_shake = max(0.0, min(1.0, (m_pos[0]-(play_w+sl.x))/sl.w)) * 3.0; player.save_settings()

                            y = cy + 130; set_surf.blit(font_s.render(tr("ui.debris_force"), True, (150,150,150)), (20, y));
                            controls = settings_slider_control_rects(sidebar_w, y); sl = controls["slider"]; pygame.draw.rect(set_surf, (60,60,70), sl); debris_value = slider_setting_value(player, "debris_force"); n = debris_value / 5.0;
                            pygame.draw.circle(set_surf, (220, 140, 38), (int(sl.x+n*sl.w), y+9), 8)
                            
                            txt_val = input_text + "|" if active_input_attr == "debris_force" and pygame.time.get_ticks() % 1000 < 500 else (input_text if active_input_attr == "debris_force" else f"{debris_value:.1f}")
                            pygame.draw.rect(set_surf, (30,30,35) if active_input_attr == "debris_force" else (45,45,50), controls["numeric"], border_radius=3)
                            set_surf.blit(font_s.render(txt_val, True, (255,255,255) if active_input_attr == "debris_force" else (200,200,200)), (controls["numeric"].x+3, y))
                            draw_slider_reset_button(set_surf, font_h, controls["reset"])
                            register_clipped_tooltip(tooltip_regions, controls["reset"], "tooltip.setting_reset", settings_origin, sidebar_content_rect)
                            
                            if m_pos[1] > TOP_UI_HEIGHT and pygame.mouse.get_pressed()[0]:
                                if controls["reset"].move(play_w, 0).collidepoint(settings_m_pos) and not hasattr(player, "_btn_lock"):
                                    reset_slider_setting(player, "debris_force"); active_input_attr = None; input_text = ""; player._btn_lock = 10
                                elif controls["numeric"].move(play_w, 0).collidepoint(settings_m_pos):
                                    if active_input_attr != "debris_force": active_input_attr = "debris_force"; input_text = str(round(debris_value, 1))
                                elif sl.move(play_w, 0).inflate(0,10).collidepoint(settings_m_pos):
                                    active_input_attr = None
                                    player.debris_force = max(0.0, min(1.0, (m_pos[0]-(play_w+sl.x))/sl.w)) * 5.0; player.save_settings()

                            cy += 195
                        elif cat == "LAYERS":
                            layer_help = ellipsize_ui_text(
                                tr("settings.layers.help"), font_h, sidebar_w - 40,
                            )
                            set_surf.blit(font_h.render(layer_help, True, (135,145,165)), (20, cy))
                            cy += 20
                            if player.sources:
                                src = player.sources[min(player.cur_source_idx, len(player.sources)-1)]
                                for layer in src.layers:
                                    layer_key = layer["key"]; layer_label = layer["name"]; layer_depth = layer.get("depth", 0); ly = cy; is_vis = layer_key in src.visible_layer_keys; l_rect = pygame.Rect(15, ly-2, sidebar_w-30, 24); hvr = pygame.Rect(play_w+15, ly-2, sidebar_w-30, 24).collidepoint(settings_m_pos)
                                    register_clipped_tooltip(
                                        tooltip_regions, l_rect, "tooltip.layer_visibility",
                                        settings_origin, sidebar_content_rect,
                                    )
                                    if hvr: pygame.draw.rect(set_surf, (60,60,70), l_rect, border_radius=4)
                                    pygame.draw.rect(set_surf, (22, 163, 74) if is_vis else (60, 60, 70), (20, ly+2, 16, 16), border_radius=3); label_x = 45 + min(layer_depth, 8) * 12; set_surf.blit(font_s.render(layer_label[:38], True, (255,255,255) if is_vis else (150,150,150)), (label_x, ly+2))
                                    if m_pos[1] > TOP_UI_HEIGHT and pygame.mouse.get_pressed()[0] and hvr and not hasattr(player, "_btn_lock"):
                                        src.set_layer_visibility(layer_key, not is_vis)
                                        if not src.export_and_load():
                                            src.set_layer_visibility(layer_key, is_vis)
                                            show_user_error(tr("error.layer_reload_title"), tr("error.layer_reload"))
                                        if cur_p is not None:
                                            player.auto_map_profile(cur_p)
                                        player._btn_lock = 15; src.clear_cache()
                                    cy += 28
                                cy += 10
                            else:
                                empty_panel = draw_resource_required_notice(
                                    set_surf, font_s, pygame.Rect(20, cy, sidebar_w-40, 48),
                                )
                                register_clipped_tooltip(
                                    tooltip_regions, empty_panel, "tooltip.resource_required",
                                    settings_origin, sidebar_content_rect,
                                )
                                cy += 55
                        elif cat == "CAMERA":
                            # Cam Offset Slider
                            y = cy; mn, mx, at = -500, 300, "cam_v_offset"
                            set_surf.blit(font_s.render(tr("ui.camera_offset"), True, (150,150,150)), (20, y))
                            controls = settings_slider_control_rects(sidebar_w, y); sl = controls["slider"]; pygame.draw.rect(set_surf, (60,60,70), sl)
                            v = slider_setting_value(player, at); n = (v-mn)/(mx-mn)
                            pygame.draw.circle(set_surf, (59,130,246), (int(sl.x+n*sl.w), y+9), 8)
                            
                            txt_val = input_text + "|" if active_input_attr == at and pygame.time.get_ticks() % 1000 < 500 else (input_text if active_input_attr == at else f"{int(v)}")
                            pygame.draw.rect(set_surf, (30,30,35) if active_input_attr == at else (45,45,50), controls["numeric"], border_radius=3)
                            set_surf.blit(font_s.render(txt_val, True, (255,255,255) if active_input_attr == at else (200,200,200)), (controls["numeric"].x+3, y))
                            draw_slider_reset_button(set_surf, font_h, controls["reset"])
                            register_clipped_tooltip(tooltip_regions, controls["reset"], "tooltip.setting_reset", settings_origin, sidebar_content_rect)
                            
                            if m_pos[1] > TOP_UI_HEIGHT and pygame.mouse.get_pressed()[0]:
                                if controls["reset"].move(play_w, 0).collidepoint(settings_m_pos) and not hasattr(player, "_btn_lock"):
                                    reset_slider_setting(player, at); active_input_attr = None; input_text = ""; player._btn_lock = 10
                                elif controls["numeric"].move(play_w, 0).collidepoint(settings_m_pos):
                                    if active_input_attr != at: active_input_attr = at; input_text = str(int(v))
                                elif sl.move(play_w, 0).inflate(0,10).collidepoint(settings_m_pos):
                                    active_input_attr = None
                                    ratio = max(0.0, min(1.0, (m_pos[0]-(play_w+sl.x))/sl.w))
                                    setattr(player, at, mn+ratio*(mx-mn)); player.save_settings()
                            
                            # Show Guide Button
                            y = cy + 45; set_surf.blit(font_s.render(tr("ui.show_guide"), True, (150,150,150)), (20, y)); btn = pygame.Rect(sidebar_w-60, y-5, 40, 20); val = player.show_viewport; pygame.draw.rect(set_surf, (59, 130, 246) if val else (60, 60, 70), btn, border_radius=10); pygame.draw.circle(set_surf, (255,255,255), (btn.x+30 if val else btn.x+10, btn.y+10), 8)
                            register_clipped_tooltip(
                                tooltip_regions, pygame.Rect(20, y-5, sidebar_w-40, 30),
                                "tooltip.show_guide", settings_origin, sidebar_content_rect,
                            )
                            if sidebar_content_rect.collidepoint(m_pos) and pygame.mouse.get_pressed()[0] and pygame.Rect(play_w+btn.x, y-5, btn.w, btn.h).collidepoint(settings_m_pos):
                                if not hasattr(player, "_btn_lock"): player.show_viewport = not val; player._btn_lock = 15; player.save_settings()
                            cy += 85
                        elif cat == "BG IMAGE":
                            unity_button_width = calculate_button_width(
                                tr("unity.copy_button"), font_b, 150, maximum_width=230,
                            )
                            unity_copy_btn = pygame.Rect(20, cy, unity_button_width, 28)
                            pygame.draw.rect(set_surf, (79, 70, 229), unity_copy_btn, border_radius=5)
                            draw_centered_label(set_surf, font_b, tr("unity.copy_button"), unity_copy_btn)
                            register_clipped_tooltip(
                                tooltip_regions, unity_copy_btn, "tooltip.unity_copy",
                                settings_origin, sidebar_content_rect,
                            )
                            if (
                                m_pos[1] > TOP_UI_HEIGHT
                                and pygame.mouse.get_pressed()[0]
                                and pygame.Rect(play_w + unity_copy_btn.x, unity_copy_btn.y, unity_copy_btn.w, unity_copy_btn.h).collidepoint(settings_m_pos)
                                and not hasattr(player, "_btn_lock")
                            ):
                                player._btn_lock = 15
                                prompt_unity_parallax_export(player)
                            cy += 40

                            gizmo_y = cy
                            gizmo_label_rect = pygame.Rect(20, gizmo_y - 5, sidebar_w - 40, 24)
                            set_surf.blit(
                                font_s.render(tr("ui.parallax_gizmo"), True, (150,150,150)),
                                (20, gizmo_y),
                            )
                            gizmo_btn = pygame.Rect(sidebar_w - 60, gizmo_y - 5, 40, 20)
                            gizmo_enabled = bool(getattr(player, "parallax_gizmo_enabled", False))
                            pygame.draw.rect(
                                set_surf,
                                (22, 163, 74) if gizmo_enabled else (60, 60, 70),
                                gizmo_btn,
                                border_radius=10,
                            )
                            pygame.draw.circle(
                                set_surf,
                                (255,255,255),
                                (gizmo_btn.x + 30 if gizmo_enabled else gizmo_btn.x + 10, gizmo_btn.y + 10),
                                8,
                            )
                            register_clipped_tooltip(
                                tooltip_regions, gizmo_label_rect, "tooltip.parallax_gizmo",
                                settings_origin, sidebar_content_rect,
                            )
                            if (
                                sidebar_content_rect.collidepoint(m_pos)
                                and pygame.mouse.get_pressed()[0]
                                and pygame.Rect(
                                    play_w + gizmo_btn.x, gizmo_btn.y,
                                    gizmo_btn.w, gizmo_btn.h,
                                ).collidepoint(settings_m_pos)
                                and not hasattr(player, "_btn_lock")
                            ):
                                set_parallax_gizmo_enabled(player, not gizmo_enabled)
                                player._btn_lock = 15
                            selected_gizmo_layer = selected_parallax_layer(player)
                            gizmo_status_key = "status.parallax_gizmo_on" if (
                                selected_gizmo_layer is not None
                                and (selected_gizmo_layer.get("img") or selected_gizmo_layer.get("cached_bg"))
                            ) else "status.parallax_gizmo_select"
                            visible_status_key = (
                                getattr(player, "parallax_history_status_key", "")
                                or (gizmo_status_key if gizmo_enabled else "")
                            )
                            if visible_status_key:
                                set_surf.blit(
                                    font_h.render(tr(visible_status_key), True, (120, 190, 255)),
                                    (20, gizmo_y + 20),
                                )
                            cy += 45

                            # Layers header
                            set_surf.blit(font_s.render(tr("ui.layers"), True, (150,150,150)), (20, cy))
                            add_lyr_btn = pygame.Rect(sidebar_w-45, cy-5, 25, 20); pygame.draw.rect(set_surf, (22, 163, 74), add_lyr_btn, border_radius=4); set_surf.blit(font_b.render("+", True, (255,255,255)), (add_lyr_btn.x+8, add_lyr_btn.y+3))
                            if sidebar_content_rect.collidepoint(m_pos) and pygame.mouse.get_pressed()[0] and pygame.Rect(play_w+add_lyr_btn.x, add_lyr_btn.y, add_lyr_btn.w, add_lyr_btn.h).collidepoint(settings_m_pos) and not hasattr(player, "_btn_lock"):
                                player.bg_layers.append({"path": "", "off_x": 0, "off_y": 0, "zoom": 2.0, "alpha": 255, "parallax": 1.0, "img": None, "cached_bg": None, "needs_update": True, "last_mtime": 0})
                                player.active_bg_layer = len(player.bg_layers) - 1
                                player._btn_lock = 15; player.save_settings()
                            cy += 25
                            
                            # Layer Tabs
                            for l_i in range(len(player.bg_layers)):
                                tab_rect = pygame.Rect(20 + (l_i%5)*45, cy + (l_i//5)*30, 40, 24)
                                is_sel = player.active_bg_layer == l_i
                                pygame.draw.rect(set_surf, (59, 130, 246) if is_sel else (60, 60, 70), tab_rect, border_radius=4)
                                set_surf.blit(font_h.render(f"L{l_i}", True, (255,255,255)), (tab_rect.x+10, tab_rect.y+5))
                                if sidebar_content_rect.collidepoint(m_pos) and pygame.mouse.get_pressed()[0] and pygame.Rect(play_w+tab_rect.x, tab_rect.y, tab_rect.w, tab_rect.h).collidepoint(settings_m_pos): player.active_bg_layer = l_i
                            
                            cy += max(1, ((len(player.bg_layers)-1)//5 + 1)) * 30 + 10
                            if valid_background_layer_index(player) < 0:
                                empty_lines = wrap_ui_text(
                                    tr("settings.background.empty"), font_s,
                                    sidebar_w - 40,
                                )
                                for line_index, line in enumerate(empty_lines[:2]):
                                    set_surf.blit(
                                        font_s.render(line, True, (210,155,115)),
                                        (20, cy + line_index * 16),
                                    )
                                cy += 35

                            if valid_background_layer_index(player) >= 0:
                                l_idx = valid_background_layer_index(player)
                                l_data = player.bg_layers[l_idx]
                                
                                # Move / Delete row
                                bg_btn = pygame.Rect(20, cy, 80, 25); pygame.draw.rect(set_surf, (100,100,110), bg_btn, border_radius=5); draw_centered_label(set_surf, font_h, tr("ui.load_image"), bg_btn)
                                up_btn = pygame.Rect(110, cy, 30, 25); pygame.draw.rect(set_surf, (80,80,90), up_btn, border_radius=5); draw_centered_label(set_surf, font_h, tr("common.up"), up_btn)
                                dn_btn = pygame.Rect(150, cy, 30, 25); pygame.draw.rect(set_surf, (80,80,90), dn_btn, border_radius=5); draw_centered_label(set_surf, font_h, tr("common.down"), dn_btn)
                                del_btn = pygame.Rect(190, cy, 40, 25); pygame.draw.rect(set_surf, (220,38,38), del_btn, border_radius=5); draw_centered_label(set_surf, font_h, tr("common.remove"), del_btn)
                                
                                if m_pos[1] > TOP_UI_HEIGHT and pygame.mouse.get_pressed()[0] and not hasattr(player, "_btn_lock"):
                                    if pygame.Rect(play_w+bg_btn.x, bg_btn.y, bg_btn.w, bg_btn.h).collidepoint(settings_m_pos):
                                        p = select_file([("Image", "*.png *.jpg *.bmp")])
                                        if p: 
                                            l_data['path'] = p; l_data['img'] = pygame.image.load(p).convert_alpha()
                                            l_data['needs_update'] = True; l_data['last_mtime'] = os.path.getmtime(p)
                                            player.save_settings()
                                        player._btn_lock = 15
                                    elif pygame.Rect(play_w+up_btn.x, up_btn.y, up_btn.w, up_btn.h).collidepoint(settings_m_pos) and l_idx > 0:
                                        player.bg_layers[l_idx], player.bg_layers[l_idx-1] = player.bg_layers[l_idx-1], player.bg_layers[l_idx]
                                        player.active_bg_layer -= 1; player._btn_lock = 15; player.save_settings()
                                    elif pygame.Rect(play_w+dn_btn.x, dn_btn.y, dn_btn.w, dn_btn.h).collidepoint(settings_m_pos) and l_idx < len(player.bg_layers)-1:
                                        player.bg_layers[l_idx], player.bg_layers[l_idx+1] = player.bg_layers[l_idx+1], player.bg_layers[l_idx]
                                        player.active_bg_layer += 1; player._btn_lock = 15; player.save_settings()
                                    elif pygame.Rect(play_w+del_btn.x, del_btn.y, del_btn.w, del_btn.h).collidepoint(settings_m_pos):
                                        player.bg_layers.pop(l_idx)
                                        player.active_bg_layer = max(0, l_idx - 1)
                                        player._btn_lock = 15; player.save_settings()
                                
                                cy += 40
                                
                                if l_idx < len(player.bg_layers): # Check if valid
                                    for i, (label_key, mn, mx, at) in enumerate([("ui.x_offset",-2000,2000,"off_x"), ("ui.y_offset",-2000,2000,"off_y"), ("ui.scale",0.1,10,"zoom"), ("ui.alpha",0,255,"alpha"), ("ui.parallax",-2.0,5.0,"parallax")]):
                                        y = cy+i*40; set_surf.blit(font_s.render(tr(label_key), True, (150,150,150)), (20, y))
                                        tooltip_key = {"off_x": "tooltip.x_offset", "off_y": "tooltip.y_offset", "zoom": "tooltip.scale", "parallax": "tooltip.parallax"}.get(at)
                                        register_clipped_tooltip(
                                            tooltip_regions, pygame.Rect(20, y-5, sidebar_w-40, 30),
                                            tooltip_key, settings_origin, sidebar_content_rect,
                                        )
                                        controls = settings_slider_control_rects(sidebar_w, y, slider_left=80)
                                        sl = controls["slider"]; pygame.draw.rect(set_surf, (60,60,70), sl)
                                        default_value = BACKGROUND_LAYER_SLIDER_DEFAULTS[at]
                                        v = _finite_number(l_data.get(at, default_value), default_value); n = max(0, min(1, (v-mn)/(mx-mn)))
                                        pygame.draw.circle(set_surf, (220,38,38), (int(sl.x+n*sl.w), y+9), 8)
                                        
                                        is_int_at = "off" in at or "alpha" in at
                                        attr_name = f"bglayer_{l_idx}_{at}"
                                        txt_val = input_text + "|" if active_input_attr == attr_name and pygame.time.get_ticks() % 1000 < 500 else (input_text if active_input_attr == attr_name else (f"{int(v)}" if is_int_at else f"{v:.2f}"))
                                        pygame.draw.rect(set_surf, (30,30,35) if active_input_attr == attr_name else (45,45,50), controls["numeric"], border_radius=3)
                                        set_surf.blit(font_s.render(txt_val, True, (255,255,255) if active_input_attr == attr_name else (200,200,200)), (controls["numeric"].x+3, y))
                                        draw_slider_reset_button(set_surf, font_h, controls["reset"])
                                        register_clipped_tooltip(tooltip_regions, controls["reset"], "tooltip.setting_reset", settings_origin, sidebar_content_rect)
                                        
                                        if m_pos[1] > TOP_UI_HEIGHT and pygame.mouse.get_pressed()[0]:
                                            if controls["reset"].move(play_w, 0).collidepoint(settings_m_pos) and not hasattr(player, "_btn_lock"):
                                                reset_slider_setting(player, at, layer_index=l_idx)
                                                active_input_attr = None; input_text = ""; player._btn_lock = 10
                                            elif controls["numeric"].move(play_w, 0).collidepoint(settings_m_pos):
                                                if active_input_attr != attr_name:
                                                    active_input_attr = attr_name
                                                    input_text = str(int(v)) if is_int_at else str(round(v, 2))
                                            elif sl.move(play_w, 0).inflate(0,10).collidepoint(settings_m_pos):
                                                active_input_attr = None
                                                if at in {"off_x", "off_y"}:
                                                    begin_parallax_offset_edit(
                                                        player, l_data, f"slider_{at}",
                                                    )
                                                ratio = max(0.0, min(1.0, (m_pos[0]-(play_w+sl.x))/sl.w))
                                                l_data[at] = mn+ratio*(mx-mn)
                                                if is_int_at: l_data[at] = int(l_data[at])
                                                l_data['needs_update'] = True
                                                if at not in {"off_x", "off_y"}:
                                                    player.save_settings()
                                    
                                    # Loop X Toggle
                                    ly = cy + 200
                                    set_surf.blit(font_s.render(tr("ui.loop_x"), True, (150,150,150)), (20, ly))
                                    btn = pygame.Rect(sidebar_w-60, ly-5, 40, 20)
                                    val = l_data.get('loop_x', False)
                                    pygame.draw.rect(set_surf, (22, 163, 74) if val else (220, 38, 38), btn, border_radius=10)
                                    pygame.draw.circle(set_surf, (255,255,255), (btn.x+30 if val else btn.x+10, btn.y+10), 8)
                                    
                                    if sidebar_content_rect.collidepoint(m_pos) and pygame.mouse.get_pressed()[0] and pygame.Rect(play_w+btn.x, ly-5, btn.w, btn.h).collidepoint(settings_m_pos):
                                        if not hasattr(player, "_btn_lock"):
                                            l_data['loop_x'] = not val
                                            l_data['needs_update'] = True
                                            player._btn_lock = 15; player.save_settings()
                                            
                                    cy += 230
                        elif cat == "BG COLOR":
                            for i, c in enumerate(['R','G','B']):
                                y = cy+i*35; set_surf.blit(font_s.render(c, True, (150,150,150)), (20, y)); controls = settings_slider_control_rects(sidebar_w, y, slider_left=40); sl = controls["slider"]; pygame.draw.rect(set_surf, (60,60,70), sl); color_value = int(_finite_number(player.bg_color[i] if i < len(player.bg_color) else BACKGROUND_COLOR_DEFAULTS[i], BACKGROUND_COLOR_DEFAULTS[i])); pygame.draw.circle(set_surf, (220, 38, 38) if i==0 else (22, 163, 74) if i==1 else (59, 130, 246), (int(sl.x+color_value/255*sl.w), y+9), 8)
                                
                                attr_name = f"bg_color_{i}"
                                txt_val = input_text + "|" if active_input_attr == attr_name and pygame.time.get_ticks() % 1000 < 500 else (input_text if active_input_attr == attr_name else str(color_value))
                                pygame.draw.rect(set_surf, (30,30,35) if active_input_attr == attr_name else (45,45,50), controls["numeric"], border_radius=3)
                                set_surf.blit(font_s.render(txt_val, True, (255,255,255) if active_input_attr == attr_name else (200,200,200)), (controls["numeric"].x+3, y))
                                draw_slider_reset_button(set_surf, font_h, controls["reset"])
                                register_clipped_tooltip(tooltip_regions, controls["reset"], "tooltip.setting_reset", settings_origin, sidebar_content_rect)
                                
                                if m_pos[1] > TOP_UI_HEIGHT and pygame.mouse.get_pressed()[0]:
                                    if controls["reset"].move(play_w, 0).collidepoint(settings_m_pos) and not hasattr(player, "_btn_lock"):
                                        reset_slider_setting(player, attr_name, color_index=i)
                                        active_input_attr = None; input_text = ""; player._btn_lock = 10
                                    elif controls["numeric"].move(play_w, 0).collidepoint(settings_m_pos):
                                        if active_input_attr != attr_name: active_input_attr = attr_name; input_text = str(color_value)
                                    elif sl.move(play_w, 0).inflate(0,10).collidepoint(settings_m_pos):
                                        active_input_attr = None
                                        ratio = max(0.0, min(1.0, (m_pos[0]-(play_w+sl.x))/sl.w))
                                        player.bg_color[i] = int(ratio*255); player.save_settings()
                            cy += 110
                            for i, p in enumerate([(15,15,18), (120,120,120), (240,240,240), (34,139,34)]):
                                pr = pygame.Rect(20+i*45, cy, 35, 30); pygame.draw.rect(set_surf, p, pr, border_radius=3)
                                if sidebar_content_rect.collidepoint(m_pos) and pygame.mouse.get_pressed()[0] and pygame.Rect(play_w+20+i*45, cy, 35, 30).collidepoint(settings_m_pos): player.bg_color = list(p); player.save_settings()
                            cy += 60
                        elif cat == "CONTROLS":
                            key_items = list((getattr(player, "key_map", {}) or {}).items())
                            if not key_items:
                                empty_text = ellipsize_ui_text(
                                    tr("control.unavailable"), font_s, sidebar_w - 40,
                                )
                                set_surf.blit(font_s.render(empty_text, True, (210,155,115)), (20, cy))
                            for i, (act, k) in enumerate(key_items):
                                y = cy+i*30; set_surf.blit(font_s.render(control_action_label(act), True, (150,150,150)), (20, y))
                                k_name = tr("common.press_key") if binding_key == act else pygame.key.name(k).upper()
                                col = (220, 38, 38) if binding_key == act else (60, 60, 70)
                                btn = pygame.Rect(120, y-2, 100, 20)
                                pygame.draw.rect(set_surf, col, btn, border_radius=4)
                                set_surf.blit(font_s.render(k_name, True, (255,255,255)), (125, y+2))
                                if sidebar_content_rect.collidepoint(m_pos) and pygame.mouse.get_pressed()[0] and pygame.Rect(play_w+120, y-2, 100, 20).collidepoint(settings_m_pos):
                                    if not hasattr(player, '_btn_lock'): binding_key = act; player._btn_lock = 10
                            message_y = cy + max(1, len(key_items)) * 30
                            if key_items and "SYNERGY" not in dict(key_items):
                                set_surf.blit(font_s.render(tr("settings.synergy.empty"), True, (210,155,115)), (20, message_y))
                            cy += max(1, len(key_items)) * 30 + 34
                set_surf.set_clip(None)
                draw_settings_section_navigation(
                    set_surf, settings_section, font_h,
                    tooltip_regions, settings_origin,
                )
                screen.blit(set_surf, settings_origin)
                sidebar_content_rect = full_sidebar_content_rect
                pygame.draw.line(
                    screen, (59, 130, 246),
                    (play_w, TOP_UI_HEIGHT), (play_w, sh), 2,
                )
            else:
                slot_clip = pygame.Surface((sidebar_w-20, MAPPING_SLOT_HEIGHT), pygame.SRCALPHA)
                for i, a in enumerate(cur_p.mappings.keys()):
                    r = pygame.Rect(10, i*38+slot_scroll, sidebar_w-40, 34); is_sel = selected_slot == a; pygame.draw.rect(slot_clip, (59,130,246) if is_sel else (45,45,50), r, border_radius=5); slot_clip.blit(font_b.render(a, True, (255,255,255)), (r.x+10, r.y+3))
                    ms = ", ".join([f"{m[1]}" for m in cur_p.mappings[a]]); slot_clip.blit(font_s.render(f"-> {ms[:45]}", True, (200,200,200) if not is_sel else (255,255,255)), (r.x+10, r.y+18))
                screen.blit(slot_clip, (play_w+10, MAPPING_SLOT_TOP))
                if player.sources:
                    pygame.draw.rect(screen, (20,20,25), (play_w+15, MAPPING_TAG_TOP, sidebar_w-30, sh-MAPPING_TAG_TOP-15), border_radius=5); src = player.sources[min(player.cur_source_idx, len(player.sources)-1)]; screen.blit(font_b.render(tr("ui.tags_from", name=src.name[:20]), True, (100,100,100)), (play_w+20, MAPPING_TAG_TOP-20)); cs = pygame.Surface((sidebar_w-40, sh-MAPPING_TAG_TOP-20), pygame.SRCALPHA)
                    for idx, t in enumerate(src.tag_list):
                        tag_rect = pygame.Rect(0, idx*25+tag_scroll, sidebar_w-40, 22); is_m = selected_slot and [player.cur_source_idx, t] in cur_p.mappings[selected_slot]; h = tag_rect.move(play_w+20, MAPPING_TAG_TOP).collidepoint(m_pos); pygame.draw.rect(cs, (59,130,246) if is_m else ((70,70,80) if h else (40,40,45)), tag_rect, border_radius=3); cs.blit(font_s.render(t, True, (255,255,255)), (tag_rect.x+10, tag_rect.y+4))
                    screen.blit(cs, (play_w+20, MAPPING_TAG_TOP))
            # Combo Stack Display
            if player.combo_step > 0:
                for i in range(4):
                    col = (220, 38, 38) if i < player.combo_step else (60, 60, 70)
                    pygame.draw.rect(screen, col, (play_w - 150 + i*35, sh - 130, 30, 10), border_radius=3)
                screen.blit(font_h.render(tr("ui.combo_step", step=player.combo_step), True, (255,255,255)), (play_w - 150, sh - 145))
        if sidebar_mode in {SIDEBAR_SCENE, SIDEBAR_RESOURCES}:
            workspace_result = draw_selection_workspace(
                screen, player, sidebar_mode, workspace_scroll,
                (font_s, font_b), tooltip_regions,
                viewport_rect=sidebar_content_rect,
            )
            workspace_controls = workspace_result["controls"]
            workspace_scroll = workspace_result["scroll_offset"]
            workspace_viewport = workspace_result["viewport"]
        else:
            workspace_controls = []
            workspace_viewport = None
        draw_bottom_key_guide(
            screen, player, sidebar_mode, play_w, font_h, tooltip_regions,
        )
        draw_sidebar_header(
            screen, player, sidebar_mode,
            tag_setup_btn, selection_scene_btn,
            selection_resource_btn, settings_btn,
            (font_s, font_b), tooltip_regions, sidebar_header_rect,
        )
        # Render FPS and Zoom
        fps = int(clock.get_fps())
        fps_color = (22, 163, 74) if fps >= 55 else ((220, 160, 38) if fps >= 30 else (220, 38, 38))
        screen.blit(font_b.render(f"FPS: {fps} | Zoom: {player.zoom:.1f}x", True, fps_color), (10, 75))

        performance.record_since("ui_render", ui_render_started)
        tooltip_render_started = time.perf_counter_ns() if performance.enabled else None
        tooltip_key = tooltip_controller.update(
            tooltip_regions,
            m_pos,
            pygame.time.get_ticks(),
            blocked=bool(player.popup) or is_dragging_cam or any(pygame.mouse.get_pressed()),
        )
        if tooltip_key:
            render_tooltip(screen, font_s, tr(tooltip_key), m_pos)
        performance.record_since("tooltip_render", tooltip_render_started)

        if performance.enabled:
            overlay_surfaces = performance.overlay_surfaces(
                font_h,
                pygame.time.get_ticks(),
                ui_text_cache_usage(),
                512 * max(1, len(_UI_FONT_CACHE)),
            )
            if overlay_surfaces:
                overlay_width = max(surface.get_width() for surface in overlay_surfaces) + 20
                overlay_height = len(overlay_surfaces) * 17 + 16
                overlay = pygame.Surface((overlay_width, overlay_height), pygame.SRCALPHA)
                overlay.fill((15, 18, 24, 220))
                for index, rendered in enumerate(overlay_surfaces):
                    overlay.blit(rendered, (10, 8 + index * 17))
                screen.blit(overlay, (10, 100))

        display_started = time.perf_counter_ns() if performance.enabled else None
        pygame.display.flip()
        performance.record_since("display", display_started)
        performance.end_frame(
            frame_started,
            performance_object_counts(player, len(tooltip_regions)),
        )
        if profile_performance:
            now_ms = pygame.time.get_ticks()
            if now_ms - performance._last_profile_report_at >= 5000:
                performance._last_profile_report_at = now_ms
                print(format_performance_summary(performance, heading="[PERFORMANCE 5S]"))


class _BenchmarkKeys:
    def __getitem__(self, _key):
        return False


def run_performance_benchmark(warmup_frames=120, measured_frames=600, seed=240724):
    warmup_frames = max(0, int(warmup_frames))
    measured_frames = max(1, int(measured_frames))
    seed = int(seed)
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    pygame.init()
    random.seed(seed)
    screen = pygame.Surface((960, 640), pygame.SRCALPHA)
    with tempfile.TemporaryDirectory(prefix="ase_viewer_perf_") as temp_dir:
        project_path = os.path.join(temp_dir, "project.json")
        settings_path = os.path.join(temp_dir, "settings.json")
        player = AsepritePlayer(project_path=project_path, settings_path=settings_path)
        player.zoom = 1.0
        player.gravity = 0.0
        player.show_hitboxes = False
        player.show_viewport = False
        player.visible = False
        player.target_ai_count = 8
        profile = AseProfile("Benchmark", -1, kind="npc")
        profile.mappings = {}
        player.profiles = [profile]
        player.ai_list = [AseAI(player, profile, hp=10) for _ in range(8)]
        player.prop_list = [AseAI(player, profile, is_prop=True) for _ in range(5)]

        background_image = pygame.Surface((320, 180), pygame.SRCALPHA)
        background_image.fill((20, 40, 80, 255))
        player.bg_layers = [
            {
                "img": background_image,
                "zoom": 1.0,
                "alpha": 255,
                "parallax": index / 10.0,
                "off_x": 0,
                "off_y": 0,
                "loop_x": index % 2 == 0,
                "cached_bg": None,
                "needs_update": True,
            }
            for index in range(6)
        ]

        part_image = pygame.Surface((18, 18), pygame.SRCALPHA)
        pygame.draw.circle(part_image, (255, 180, 40, 255), (9, 9), 8)
        for index in range(100):
            particle = Particle(
                250 + (index % 20) * 22,
                150 + (index // 20) * 25,
                0,
                0,
                (255, 255, 255),
                8,
                1_000_000_000,
                image=part_image,
            )
            particle.rot_speed = 5 + (index % 7)
            player.particles.append(particle)
        for index in range(100):
            player.particles.append(Particle(
                200 + (index % 25) * 20,
                300 + (index // 25) * 18,
                0,
                0,
                (120, 220, 255),
                4,
                1_000_000_000,
            ))

        keys = _BenchmarkKeys()
        for _ in range(warmup_frames):
            player.update(keys, 500, 16.6)
            player.draw(screen, 960, 640)

        monitor = PerformanceMonitor(enabled=True, window_size=measured_frames)
        player.performance_monitor = monitor
        counts = performance_object_counts(player)
        for _ in range(measured_frames):
            frame_started = monitor.begin_frame()
            update_started = time.perf_counter_ns()
            player.update(keys, 500, 16.6)
            monitor.record_since("update", update_started)
            render_started = time.perf_counter_ns()
            player.draw(screen, 960, 640)
            monitor.record_since("world_render", render_started)
            monitor.end_frame(frame_started, counts)

        result = monitor.final_summary()
        result.update({
            "version": APP_VERSION,
            "seed": seed,
            "warmup_frames": warmup_frames,
            "measured_frames": measured_frames,
            "actors": len(player.ai_list) + len(player.prop_list),
            "image_particles": counts["image_particles"],
            "color_particles": counts["color_particles"],
            "background_layers": counts["backgrounds"],
            "project_saved": os.path.exists(project_path),
            "settings_saved": os.path.exists(settings_path),
        })
        return result


def print_performance_benchmark(result):
    sections = result["sections"]
    print("PERFORMANCE BENCHMARK OK")
    print(f"version={result['version']}")
    print(f"seed={result['seed']}")
    print(f"frames={result['measured_frames']}")
    print(f"actors={result['actors']}")
    print(f"image_particles={result['image_particles']}")
    print(f"color_particles={result['color_particles']}")
    print(f"background_layers={result['background_layers']}")
    print(f"frame_avg_ms={result['frame_avg_ms']:.4f}")
    print(f"frame_p95_ms={result['frame_p95_ms']:.4f}")
    print(f"frame_p99_ms={result['frame_p99_ms']:.4f}")
    print(f"frame_max_ms={result['frame_max_ms']:.4f}")
    print(f"spikes_over_25ms={result['spikes_over_25ms']}")
    print(f"update_avg_ms={sections['update']['avg_ms']:.4f}")
    print(f"background_render_avg_ms={sections['background_render']['avg_ms']:.4f}")
    print(f"actor_render_avg_ms={sections['actor_render']['avg_ms']:.4f}")
    print(f"particle_render_avg_ms={sections['particle_render']['avg_ms']:.4f}")
    print(f"world_render_avg_ms={sections['world_render']['avg_ms']:.4f}")
    print(f"project_saved={str(result['project_saved']).lower()}")
    print(f"settings_saved={str(result['settings_saved']).lower()}")


def _sidebar_check_player():
    sources = [
        SimpleNamespace(
            name=f"Source_{index + 1}.aseprite",
            file_path=f"Source_{index + 1}.aseprite",
            source_revision=1,
            slice_analysis_revision=None,
            slice_export_analysis=None,
        )
        for index in range(3)
    ]
    profiles = [
        SimpleNamespace(name="PLAYER", source_idx=0, kind="player", is_prop_profile=False),
        SimpleNamespace(name="NPC_1", source_idx=1, kind="npc", is_prop_profile=False),
        SimpleNamespace(name="NPC_2", source_idx=2, kind="npc", is_prop_profile=False),
    ]
    npc = SimpleNamespace(profile=profiles[1], visible=True, is_corpse=False)
    return SimpleNamespace(
        sources=sources,
        profiles=profiles,
        ai_list=[npc],
        prop_list=[],
        cur_profile_idx=0,
        cur_source_idx=0,
        selected_scene_actor_key=None,
        language=LANG_KO,
        visible=True,
        bg_layers=[{} for _ in range(6)],
    )


def _draw_sidebar_check_settings(
    surface, content_rect, scroll_offset, font, tooltip_regions,
    section=SETTINGS_SECTION_CONTROLS_APP,
):
    section = normalize_settings_section(section)
    content_surface = pygame.Surface(
        (content_rect.w, max(1, content_rect.h)), pygame.SRCALPHA,
    )
    origin = content_rect.topleft
    body_rect = pygame.Rect(
        content_rect.x,
        content_rect.y + SETTINGS_SECTION_NAV_HEIGHT,
        content_rect.w,
        max(0, content_rect.h - SETTINGS_SECTION_NAV_HEIGHT),
    )
    visible_controls = []
    content_surface.set_clip(pygame.Rect(
        0, SETTINGS_SECTION_NAV_HEIGHT,
        content_rect.w, body_rect.h,
    ))
    cy = SETTINGS_SECTION_NAV_HEIGHT + int(scroll_offset)
    cy = draw_settings_section_intro(content_surface, section, cy, font)
    for index, category in enumerate(
        settings_section_model(section)["categories"],
    ):
        local_rect = pygame.Rect(
            10, cy + index * 110, content_rect.w - 20, 30,
        )
        pygame.draw.rect(content_surface, (50, 50, 60), local_rect, border_radius=5)
        content_surface.blit(
            font.render(tr(CATEGORY_TRANSLATION_KEYS[category]), True, (255, 255, 255)),
            (local_rect.x + 10, local_rect.y + 7),
        )
        clipped = clipped_global_rect(local_rect, origin, body_rect)
        if clipped is not None:
            visible_controls.append(clipped)
        register_clipped_tooltip(
            tooltip_regions, local_rect, "tooltip.options", origin, body_rect,
        )
    content_surface.set_clip(None)
    nav_rects = draw_settings_section_navigation(
        content_surface, section, font, tooltip_regions, origin,
    )
    visible_controls.extend(
        rect.move(origin) for rect in nav_rects.values()
    )
    surface.blit(content_surface, origin)
    return visible_controls


def run_sidebar_ui_check():
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    pygame.init()
    set_current_language(LANG_KO)
    width, height = 2048, 1118
    play_width = width - SIDEBAR_WIDTH
    header_rect, content_rect = sidebar_rects(play_width, height)
    (
        mapping_button, scene_button, resource_button, options_button,
    ) = sidebar_navigation_button_rects(play_width)
    font_small = create_ui_font(12)
    font_bold = create_ui_font(14, bold=True)
    player = _sidebar_check_player()
    mode = SIDEBAR_MAPPING
    settings_scroll = -600
    results = {}

    with tempfile.TemporaryDirectory(prefix="ase_sidebar_ui_") as temp_dir:
        def render_frame(
            filename, current_mode, scroll=0,
            settings_section=SETTINGS_SECTION_CONTROLS_APP,
        ):
            surface = pygame.Surface((width, height), pygame.SRCALPHA)
            surface.fill((35, 35, 40, 255))
            pygame.draw.rect(surface, (25, 25, 30), content_rect)
            tooltip_regions = []
            visible_controls = []
            if current_mode in {SIDEBAR_SCENE, SIDEBAR_RESOURCES}:
                draw_selection_workspace(
                    surface, player, current_mode, 0,
                    (font_small, font_bold), tooltip_regions,
                    viewport_rect=content_rect,
                )
            elif current_mode == SIDEBAR_SETTINGS:
                visible_controls = _draw_sidebar_check_settings(
                    surface, content_rect, scroll, font_small, tooltip_regions,
                    settings_section,
                )
            else:
                mapping_result = draw_mapping_workspace_intro(
                    surface, player, (font_small, font_bold), content_rect,
                )
                visible_controls = [mapping_result["title_rect"]]
            content_tooltips = list(tooltip_regions)
            draw_sidebar_header(
                surface, player, current_mode,
                mapping_button, scene_button, resource_button, options_button,
                (font_small, font_bold), tooltip_regions, header_rect,
            )
            pygame.image.save(surface, os.path.join(temp_dir, filename))
            return visible_controls, content_tooltips

        mapping_controls, mapping_tooltips = render_frame("01_mapping.png", mode)
        results["mapping_content_overlap"] = sum(
            1 for rect in mapping_controls if rect.colliderect(header_rect)
        )
        results["mapping_tooltip_overlap"] = sum(
            1 for rect, _key in mapping_tooltips
            if pygame.Rect(rect).colliderect(header_rect)
        )
        results["tag_setup_button_click"] = (
            mapping_button.centerx > play_width
            and sidebar_header_click_target(
                mapping_button.center, mapping_button, scene_button,
                resource_button, options_button,
            ) == SIDEBAR_MAPPING
        )
        results["header_button_order"] = (
            mapping_button.left < scene_button.left
            < resource_button.left < options_button.left
        )
        results["scene_button_click"] = (
            scene_button.centerx > play_width
            and sidebar_header_click_target(
                scene_button.center, mapping_button, scene_button,
                resource_button, options_button,
            ) == SIDEBAR_SCENE
        )
        mode = set_sidebar_mode(mode, SIDEBAR_SCENE)
        render_frame("02_scene.png", mode)

        results["resource_button_click"] = (
            resource_button.centerx > play_width
            and sidebar_header_click_target(
                resource_button.center, mapping_button, scene_button,
                resource_button, options_button,
            ) == SIDEBAR_RESOURCES
        )
        mode = set_sidebar_mode(mode, SIDEBAR_RESOURCES)
        render_frame("03_resources.png", mode)

        results["options_button_click"] = (
            sidebar_header_click_target(
                options_button.center, mapping_button, scene_button,
                resource_button, options_button,
            ) == SIDEBAR_SETTINGS
        )
        mode = set_sidebar_mode(mode, SIDEBAR_SETTINGS)
        render_frame("04_settings_top.png", mode, 0)
        controls, tooltips = render_frame(
            "05_settings_scrolled.png", mode, settings_scroll,
            SETTINGS_SECTION_VIEW_BACKGROUND,
        )
        section_rects = settings_section_button_rects(content_rect.w)
        results["settings_sections_clickable"] = all(
            settings_section_click_target(rect.center, content_rect.w) == section
            for section, rect in section_rects.items()
        )
        results["settings_sections_disjoint"] = all(
            not first_rect.colliderect(second_rect)
            for first_index, first_rect in enumerate(section_rects.values())
            for second_rect in list(section_rects.values())[first_index + 1:]
        )
        results["header_overlap_pixels"] = sum(
            1 for rect in controls if rect.colliderect(header_rect)
        )
        results["hidden_controls_in_header"] = results["header_overlap_pixels"]
        results["hidden_tooltips_in_header"] = sum(
            1 for rect, _key in tooltips if pygame.Rect(rect).colliderect(header_rect)
        )

        mode = set_sidebar_mode(mode, SIDEBAR_SCENE)
        results["exclusive_modes"] = mode == SIDEBAR_SCENE
        if not all((
            results["tag_setup_button_click"],
            results["header_button_order"],
            results["scene_button_click"],
            results["resource_button_click"],
            results["options_button_click"],
            results["exclusive_modes"],
            results["mapping_content_overlap"] == 0,
            results["mapping_tooltip_overlap"] == 0,
            results["header_overlap_pixels"] == 0,
            results["hidden_controls_in_header"] == 0,
            results["hidden_tooltips_in_header"] == 0,
            results["settings_sections_clickable"],
            results["settings_sections_disjoint"],
        )):
            raise RuntimeError(f"Sidebar UI check failed: {results}")

    pygame.quit()
    print("SIDEBAR UI CHECK OK")
    print(f"version={APP_VERSION}")
    print(f"tag_setup_button_click={str(results['tag_setup_button_click']).lower()}")
    print(f"header_button_order={str(results['header_button_order']).lower()}")
    print(f"scene_button_click={str(results['scene_button_click']).lower()}")
    print(f"resource_button_click={str(results['resource_button_click']).lower()}")
    print(f"options_button_click={str(results['options_button_click']).lower()}")
    print(f"exclusive_modes={str(results['exclusive_modes']).lower()}")
    print(f"mapping_content_overlap={results['mapping_content_overlap']}")
    print(f"mapping_tooltip_overlap={results['mapping_tooltip_overlap']}")
    print(f"header_overlap_pixels={results['header_overlap_pixels']}")
    print(f"hidden_controls_in_header={results['hidden_controls_in_header']}")
    print(f"hidden_tooltips_in_header={results['hidden_tooltips_in_header']}")
    print(f"settings_sections_clickable={str(results['settings_sections_clickable']).lower()}")
    print(f"settings_sections_disjoint={str(results['settings_sections_disjoint']).lower()}")
    print(f"settings_scroll={settings_scroll}")
    return results


def debug_sporeheart_npc():
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
    os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
    source_path = os.path.join(APP_ROOT, "SporeHeart.aseprite")
    if not os.path.isfile(source_path):
        matches = []
        for root, directories, files in os.walk(APP_ROOT):
            directories[:] = [
                name for name in directories
                if name.casefold() not in {"build", "dist", "venv", ".venv", "__pycache__"}
            ]
            for filename in files:
                stem, extension = os.path.splitext(filename)
                if stem.casefold() == "sporeheart" and extension.casefold() in {".aseprite", ".ase"}:
                    matches.append(os.path.join(root, filename))
        if not matches:
            print("SPOREHEART NPC DEBUG FAILED: SporeHeart.aseprite was not found.")
            return 1
        source_path = sorted(matches)[0]
    source_hash = file_sha256(source_path)
    try:
        pygame.init()
        screen = pygame.display.set_mode((800, 570))
        with tempfile.TemporaryDirectory(prefix="ase_viewer_spore_debug_") as temp_dir:
            player = AsepritePlayer(
                project_path=os.path.join(temp_dir, "project.json"),
                settings_path=os.path.join(temp_dir, "settings.json"),
            )
            player.visible = False
            player.show_viewport = False
            registration = player.register_npc_source(source_path, profile_name="SporeHeart")
            if registration is None:
                raise RuntimeError("NPC registration callback failed.")
            source = registration["source"]
            profile = registration["profile"]
            npc = registration["instance"]
            analysis = ensure_source_slice_analysis(source)
            if len(analysis["valid_parts_slices"]) != 9 or len(analysis["valid_particle_slices"]) != 7:
                raise RuntimeError("SporeHeart Slice counts do not match 9 Parts / 7 Particles.")

            other_profile = AseProfile("Other NPC", registration["source_idx"], kind="npc")
            player.profiles.append(other_profile)
            player.cur_profile_idx = player.profiles.index(other_profile)
            npc.x = 400
            npc.y = 400
            npc.facing_right = True
            player.cam_follow = False
            player.cam_x = 400
            player.cam_y = 400
            result = player.trigger_npc_death(npc)
            if not isinstance(result, dict):
                raise RuntimeError("NPC death did not return a runtime result.")
            player.update(_SmokeKeys(), 500, 16.6)
            player.draw(screen, 800, 570)

            spawned = player.spawn_npc_profile(registration["profile_idx"])
            if spawned is None or spawned.profile is not profile:
                raise RuntimeError("Existing-source NPC SPAWN callback used the wrong profile.")
            spawned.x = 400
            spawned.y = 400
            spawned_result = player.trigger_npc_death(spawned)
            player.update(_SmokeKeys(), 500, 16.6)
            player.draw(screen, 800, 570)
            prop_analysis = ensure_source_slice_analysis(source)
            npc_signature = [
                (
                    item["slice_name"],
                    item["bounds"],
                    hashlib.sha256(pygame.image.tostring(item["image"], "RGBA")).hexdigest(),
                )
                for item in analysis["valid_parts_slices"]
            ]
            prop_signature = [
                (
                    item["slice_name"],
                    item["bounds"],
                    hashlib.sha256(pygame.image.tostring(item["image"], "RGBA")).hexdigest(),
                )
                for item in prop_analysis["valid_parts_slices"]
            ]
            checks = {
                "corpse": result["corpse_mode"] == "dead_loop" and npc in player.ai_list and npc.is_corpse,
                "parts": result["parts_mode"] == "precise" and result["created"] == 9,
                "update": result["remaining"] == 9,
                "render": result["rendered"] == 9,
                "selection": result["profile"] is profile and result["source_idx"] == registration["source_idx"],
                "spawn": (
                    spawned_result["profile"] is profile
                    and spawned_result["source_idx"] == registration["source_idx"]
                    and spawned_result["corpse_mode"] == "dead_loop"
                    and spawned_result["parts_mode"] == "precise"
                    and spawned_result["created"] == 9
                    and spawned_result["remaining"] == 9
                    and spawned_result["rendered"] == 9
                ),
                "analysis": npc_signature == prop_signature,
                "hash": file_sha256(source_path) == source_hash,
            }
            if not all(checks.values()):
                raise RuntimeError(f"Runtime checks failed: {checks}")
            print("SPOREHEART NPC DEBUG OK")
            print(f"version={APP_VERSION}")
            print(f"parts_detected={len(analysis['valid_parts_slices'])}")
            print(f"particles_detected={len(analysis['valid_particle_slices'])}")
            print(f"corpse_mode={result['corpse_mode']}")
            print(f"parts_mode={result['parts_mode']}")
            print(f"parts_created={result['created']}")
            print(f"parts_after_update={result['remaining']}")
            print(f"parts_rendered={result['rendered']}")
            return 0
    except Exception as e:
        log_debug(f"[ERROR] SporeHeart NPC debug failed: {e}\n{traceback.format_exc()}")
        print(f"SPOREHEART NPC DEBUG FAILED: {e}")
        return 1
    finally:
        pygame.quit()


if __name__ == "__main__":
    log_boot()
    if "--check-sidebar-ui" in sys.argv:
        run_sidebar_ui_check()
        sys.exit(0)
    if "--benchmark-performance" in sys.argv:
        benchmark_result = run_performance_benchmark()
        print_performance_benchmark(benchmark_result)
        sys.exit(0)
    if "--debug-sporeheart-npc" in sys.argv:
        sys.exit(debug_sporeheart_npc())
    if "--check-layers" in sys.argv:
        sys.exit(check_layers())
    if "--check-gui" in sys.argv:
        sys.exit(check_gui())
    if "--check-aseprite" in sys.argv:
        sys.exit(check_aseprite())
    if "--check" in sys.argv:
        sys.exit(check_application())
    main(profile_performance="--profile-performance" in sys.argv)
