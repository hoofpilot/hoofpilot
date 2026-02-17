import os
import re
import threading
from enum import IntEnum

import pyray as rl
import requests
from openpilot.common.basedir import BASEDIR
from openpilot.system.ui.lib.application import FontWeight, gui_app
from openpilot.system.ui.lib.multilang import tr
from openpilot.system.ui.widgets import Widget
from openpilot.system.ui.widgets import DialogResult
from openpilot.system.ui.widgets.button import Button, ButtonStyle
from openpilot.system.ui.widgets.confirm_dialog import ConfirmDialog
from openpilot.system.ui.widgets.label import Label
from openpilot.selfdrive.ui.ui_state import ui_state
from openpilot.system.version import terms_version, training_version, terms_version_sp
from openpilot.system.ui.hoofpilot.widgets.tree_dialog import TreeFolder, TreeNode, TreeOptionDialog

DEBUG = False
IMPERIAL_COUNTRIES = {"US", "GB", "BS"}  # United States, United Kingdom, The Bahamas

STEP_RECTS = [rl.Rectangle(104, 800, 633, 175), rl.Rectangle(1835, 0, 2159, 1080), rl.Rectangle(1835, 0, 2156, 1080),
              rl.Rectangle(1526, 473, 427, 472), rl.Rectangle(1643, 441, 217, 223), rl.Rectangle(1835, 0, 2155, 1080),
              rl.Rectangle(1786, 591, 267, 236), rl.Rectangle(1353, 0, 804, 1080), rl.Rectangle(1458, 485, 633, 211),
              rl.Rectangle(95, 794, 1158, 187), rl.Rectangle(1560, 170, 392, 397), rl.Rectangle(1835, 0, 2159, 1080),
              rl.Rectangle(1351, 0, 807, 1080), rl.Rectangle(1835, 0, 2158, 1080), rl.Rectangle(1531, 82, 441, 920),
              rl.Rectangle(1336, 438, 490, 393), rl.Rectangle(1835, 0, 2159, 1080), rl.Rectangle(1835, 0, 2159, 1080),
              rl.Rectangle(87, 795, 1187, 186)]

DM_RECORD_STEP = 9
DM_RECORD_YES_RECT = rl.Rectangle(695, 794, 558, 187)

RESTART_TRAINING_RECT = rl.Rectangle(87, 795, 472, 186)


class OnboardingState(IntEnum):
  TERMS = 0
  ONBOARDING = 1
  DECLINE = 2
  LOCATION = 3
  MAPS = 4


class TrainingGuide(Widget):
  def __init__(self, completed_callback=None):
    super().__init__()
    self._completed_callback = completed_callback

    self._step = 0
    self._load_image_paths()

    # Load first image now so we show something immediately
    self._textures = [gui_app.texture(self._image_paths[0])]
    self._image_objs = []

    threading.Thread(target=self._preload_thread, daemon=True).start()

  def _load_image_paths(self):
    paths = [fn for fn in os.listdir(os.path.join(BASEDIR, "selfdrive/assets/training")) if re.match(r'^step\d*\.png$', fn)]
    paths = sorted(paths, key=lambda x: int(re.search(r'\d+', x).group()))
    self._image_paths = [os.path.join(BASEDIR, "selfdrive/assets/training", fn) for fn in paths]

  def _preload_thread(self):
    # PNG loading is slow in raylib, so we preload in a thread and upload to GPU in main thread
    # We've already loaded the first image on init
    for path in self._image_paths[1:]:
      self._image_objs.append(gui_app._load_image_from_path(path))

  def _handle_mouse_release(self, mouse_pos):
    if rl.check_collision_point_rec(mouse_pos, STEP_RECTS[self._step]):
      # Record DM camera?
      if self._step == DM_RECORD_STEP:
        yes = rl.check_collision_point_rec(mouse_pos, DM_RECORD_YES_RECT)
        print(f"putting RecordFront to {yes}")
        ui_state.params.put_bool("RecordFront", yes)

      # Restart training?
      elif self._step == len(self._image_paths) - 1:
        if rl.check_collision_point_rec(mouse_pos, RESTART_TRAINING_RECT):
          self._step = -1

      self._step += 1

      # Finished?
      if self._step >= len(self._image_paths):
        self._step = 0
        if self._completed_callback:
          self._completed_callback()

  def _update_state(self):
    if len(self._image_objs):
      self._textures.append(gui_app._load_texture_from_image(self._image_objs.pop(0)))

  def _render(self, _):
    # Safeguard against fast tapping
    step = min(self._step, len(self._textures) - 1)
    rl.draw_texture(self._textures[step], 0, 0, rl.WHITE)

    # progress bar
    if 0 < step < len(STEP_RECTS) - 1:
      h = 20
      w = int((step / (len(STEP_RECTS) - 1)) * self._rect.width)
      rl.draw_rectangle(int(self._rect.x), int(self._rect.y + self._rect.height - h),
                        w, h, rl.Color(70, 91, 234, 255))

    if DEBUG:
      rl.draw_rectangle_lines_ex(STEP_RECTS[step], 3, rl.RED)

    return -1


class TermsPage(Widget):
  def __init__(self, on_accept=None, on_decline=None):
    super().__init__()
    self._on_accept = on_accept
    self._on_decline = on_decline

    self._title = Label(tr("Welcome to hoofpilot!"), font_size=90, font_weight=FontWeight.BOLD, text_alignment=rl.GuiTextAlignment.TEXT_ALIGN_LEFT)
    self._desc = Label(tr("You must accept the Terms and Conditions in order to use hoofpilot. Read the latest terms at https://comma.ai/terms before continuing."),
                       font_size=90, font_weight=FontWeight.MEDIUM, text_alignment=rl.GuiTextAlignment.TEXT_ALIGN_LEFT)

    self._decline_btn = Button(tr("Decline"), click_callback=on_decline)
    self._accept_btn = Button(tr("Agree"), button_style=ButtonStyle.PRIMARY, click_callback=on_accept)

  def _render(self, _):
    welcome_x = self._rect.x + 95
    welcome_x = self._rect.x + 95
    welcome_y = self._rect.y + 165
    welcome_rect = rl.Rectangle(welcome_x, welcome_y, self._rect.width - welcome_x, 90)
    self._title.render(welcome_rect)

    desc_x = welcome_x
    # TODO: Label doesn't top align when wrapping
    desc_y = welcome_y - 100
    desc_rect = rl.Rectangle(desc_x, desc_y, self._rect.width - desc_x, self._rect.height - desc_y - 250)
    self._desc.render(desc_rect)

    btn_y = self._rect.y + self._rect.height - 160 - 45
    btn_width = (self._rect.width - 45 * 3) / 2
    self._decline_btn.render(rl.Rectangle(self._rect.x + 45, btn_y, btn_width, 160))
    self._accept_btn.render(rl.Rectangle(self._rect.x + 45 * 2 + btn_width, btn_y, btn_width, 160))

    if DEBUG:
      rl.draw_rectangle_lines_ex(welcome_rect, 3, rl.RED)
      rl.draw_rectangle_lines_ex(desc_rect, 3, rl.RED)

    return -1


class DeclinePage(Widget):
  def __init__(self, back_callback=None):
    super().__init__()
    self._text = Label(tr("You must accept the Terms of Service in order to use hoofpilot."),
                       font_size=90, font_weight=FontWeight.MEDIUM, text_alignment=rl.GuiTextAlignment.TEXT_ALIGN_LEFT)
    self._back_btn = Button(tr("Back"), click_callback=back_callback)
    self._uninstall_btn = Button(tr("Decline, uninstall hoofpilot"), button_style=ButtonStyle.DANGER,
                                 click_callback=self._on_uninstall_clicked)

  def _on_uninstall_clicked(self):
    ui_state.params.put_bool("DoUninstall", True)
    gui_app.request_close()

  def _render(self, _):
    btn_y = self._rect.y + self._rect.height - 160 - 45
    btn_width = (self._rect.width - 45 * 3) / 2
    self._back_btn.render(rl.Rectangle(self._rect.x + 45, btn_y, btn_width, 160))
    self._uninstall_btn.render(rl.Rectangle(self._rect.x + 45 * 2 + btn_width, btn_y, btn_width, 160))

    # text rect in middle of top and button
    text_height = btn_y - (200 + 45)
    text_rect = rl.Rectangle(self._rect.x + 165, self._rect.y + (btn_y - text_height) / 2 + 10, self._rect.width - (165 * 2), text_height)
    if DEBUG:
      rl.draw_rectangle_lines_ex(text_rect, 3, rl.RED)
    self._text.render(text_rect)


class LocationSetupPage(Widget):
  def __init__(self, continue_callback=None, skip_callback=None, restore_overlay_callback=None):
    super().__init__()
    self._continue_callback = continue_callback
    self._skip_callback = skip_callback
    self._restore_overlay_callback = restore_overlay_callback

    self._country_ref = ""
    self._country_title = ""
    self._state_ref = ""
    self._state_title = ""

    self._title = Label(tr("Location Setup"), font_size=90, font_weight=FontWeight.BOLD,
                        text_alignment=rl.GuiTextAlignment.TEXT_ALIGN_LEFT)
    self._desc = Label(tr("Select your country and state/province. This helps set units and optionally download local maps."),
                       font_size=70, font_weight=FontWeight.MEDIUM, text_alignment=rl.GuiTextAlignment.TEXT_ALIGN_LEFT)

    self._country_btn = Button(tr("Select Country"), button_style=ButtonStyle.PRIMARY,
                               click_callback=self._on_select_country_clicked, font_size=56)
    self._state_btn = Button(tr("State/Province (Optional)"), click_callback=self._on_select_state_clicked, font_size=50)
    self._continue_btn = Button(tr("Continue"), button_style=ButtonStyle.PRIMARY, click_callback=self._on_continue_clicked)
    self._skip_btn = Button(tr("Skip"), click_callback=self._on_skip_clicked)

  def _fetch_location_nodes(self, region_type: str, callback):
    def _worker():
      base_url = "https://raw.githubusercontent.com/pfeiferj/openpilot-mapd/main/"
      if region_type == "Country":
        url = base_url + "nation_bounding_boxes.json"
        try:
          data = requests.get(url, timeout=10).json()
          nodes = sorted([TreeNode(ref=k, data={"display_name": v["full_name"]}) for k, v in data.items()],
                         key=lambda n: n.data["display_name"])
        except Exception:
          nodes = []
      elif region_type == "State-US":
        url = base_url + "us_states_bounding_boxes.json"
        try:
          data = requests.get(url, timeout=10).json()
          nodes = sorted([TreeNode(ref=k, data={"display_name": v["full_name"]}) for k, v in data.items()],
                         key=lambda n: n.data["display_name"])
          nodes.insert(0, TreeNode(ref="All", data={"display_name": tr("All states (~6.0 GB)")}))
        except Exception:
          nodes = []
      else:
        # Canada provinces fallback list
        provinces = [
          ("AB", "Alberta"), ("BC", "British Columbia"), ("MB", "Manitoba"), ("NB", "New Brunswick"),
          ("NL", "Newfoundland and Labrador"), ("NS", "Nova Scotia"), ("NT", "Northwest Territories"),
          ("NU", "Nunavut"), ("ON", "Ontario"), ("PE", "Prince Edward Island"), ("QC", "Quebec"),
          ("SK", "Saskatchewan"), ("YT", "Yukon"),
        ]
        nodes = [TreeNode(ref=r, data={"display_name": n}) for r, n in provinces]
        nodes.insert(0, TreeNode(ref="All", data={"display_name": tr("All provinces")}))

      callback(nodes)

    threading.Thread(target=_worker, daemon=True).start()

  @staticmethod
  def _group_nodes_alpha(nodes: list[TreeNode]) -> list[TreeFolder]:
    buckets: dict[str, list[TreeNode]] = {}
    for n in nodes:
      name = n.data.get("display_name", n.ref)
      key = (name[:1].upper() if name else "#")
      if not key.isalpha():
        key = "#"
      buckets.setdefault(key, []).append(n)

    folders: list[TreeFolder] = []
    for key in sorted(buckets.keys()):
      folders.append(TreeFolder(folder=key, nodes=buckets[key]))
    return folders

  def _open_selection_dialog(self, title: str, nodes: list[TreeNode], current_ref: str, on_done, use_alpha_folders: bool = True):
    folders = self._group_nodes_alpha(nodes) if use_alpha_folders else [TreeFolder(folder="", nodes=nodes)]
    dialog = TreeOptionDialog(tr(title), folders, current_ref=current_ref, search_prompt=tr("Perform a search"))

    def _handle_exit(res):
      # Ignore internal overlay swaps (e.g., opening search keyboard), which emit NO_ACTION.
      if res == DialogResult.NO_ACTION:
        return
      on_done(res, dialog.selection_ref)
      # Restore onboarding overlay so cancel/back from selector doesn't drop to home UI.
      if self._restore_overlay_callback is not None:
        self._restore_overlay_callback()

    dialog.on_exit = _handle_exit
    gui_app.set_modal_overlay(dialog, callback=_handle_exit)

  def _on_select_country_clicked(self):
    self._country_btn.set_enabled(False)
    self._country_btn.set_text(tr("FETCHING..."))

    def _after_fetch(nodes: list[TreeNode]):
      self._country_btn.set_enabled(True)
      self._country_btn.set_text(tr("Select Country"))
      if not nodes:
        return

      def _on_done(res, ref):
        if res != DialogResult.CONFIRM or not ref:
          return
        node = next((n for n in nodes if n.ref == ref), None)
        self._country_ref = ref
        self._country_title = node.data.get("display_name", ref) if node else ref
        # Reset state/province when country changes.
        self._state_ref = ""
        self._state_title = ""

      self._open_selection_dialog("Select Country", nodes, self._country_ref, _on_done, use_alpha_folders=True)

    self._fetch_location_nodes("Country", _after_fetch)

  def _on_select_state_clicked(self):
    if not self._country_ref:
      return

    if self._country_ref not in {"US", "CA"}:
      return

    self._state_btn.set_enabled(False)
    self._state_btn.set_text(tr("FETCHING..."))

    def _after_fetch(nodes: list[TreeNode]):
      self._state_btn.set_enabled(True)
      self._state_btn.set_text(tr("State/Province (Optional)"))
      if not nodes:
        return

      def _on_done(res, ref):
        if res != DialogResult.CONFIRM or not ref:
          return
        node = next((n for n in nodes if n.ref == ref), None)
        self._state_ref = ref
        self._state_title = node.data.get("display_name", ref) if node else ref

      self._open_selection_dialog("Select State/Province", nodes, self._state_ref, _on_done, use_alpha_folders=False)

    region_type = "State-US" if self._country_ref == "US" else "Province-CA"
    self._fetch_location_nodes(region_type, _after_fetch)

  def _on_continue_clicked(self):
    if not self._country_ref:
      return
    if self._continue_callback:
      self._continue_callback(self._country_ref, self._country_title, self._state_ref, self._state_title)

  def _on_skip_clicked(self):
    if self._skip_callback is None:
      return

    def _cb(res: int):
      if res == DialogResult.CONFIRM:
        self._skip_callback()
      else:
        # Keep onboarding active when user cancels skip.
        if self._restore_overlay_callback is not None:
          self._restore_overlay_callback()

    gui_app.set_modal_overlay(
      ConfirmDialog(
        tr("Skip location setup? You can configure maps and units later in Settings."),
        tr("Skip"),
        tr("Cancel"),
        rich=False,
      ),
      callback=_cb,
    )

  def _render(self, _):
    title_rect = rl.Rectangle(self._rect.x + 95, self._rect.y + 120, self._rect.width - 190, 90)
    self._title.render(title_rect)

    desc_rect = rl.Rectangle(self._rect.x + 95, self._rect.y + 250, self._rect.width - 190, 220)
    self._desc.render(desc_rect)

    country_rect = rl.Rectangle(self._rect.x + 95, self._rect.y + 500, self._rect.width - 190, 140)
    country_text = self._country_title if self._country_title else tr("Select Country")
    self._country_btn.set_text(country_text)
    self._country_btn.render(country_rect)

    state_rect = rl.Rectangle(self._rect.x + 95, self._rect.y + 680, self._rect.width - 190, 140)
    self._state_btn.set_enabled(bool(self._country_ref) and self._country_ref in {"US", "CA"})
    if not self._country_ref:
      self._state_btn.set_text(tr("State/Province (Select country first)"))
    elif self._country_ref not in {"US", "CA"}:
      self._state_btn.set_text(tr("State/Province (Not required)"))
    else:
      state_text = self._state_title if self._state_title else tr("State/Province (Optional)")
      self._state_btn.set_text(state_text)
    self._state_btn.render(state_rect)

    btn_y = self._rect.y + self._rect.height - 160 - 45
    btn_width = (self._rect.width - 45 * 3) / 2
    self._skip_btn.render(rl.Rectangle(self._rect.x + 45, btn_y, btn_width, 160))
    self._continue_btn.set_enabled(bool(self._country_ref))
    self._continue_btn.render(rl.Rectangle(self._rect.x + 45 * 2 + btn_width, btn_y, btn_width, 160))

    return -1


class MapDownloadPage(Widget):
  def __init__(self, yes_callback=None, no_callback=None):
    super().__init__()
    self._yes_callback = yes_callback
    self._no_callback = no_callback

    self._title = Label(tr("Download Offline Maps?"), font_size=90, font_weight=FontWeight.BOLD,
                        text_alignment=rl.GuiTextAlignment.TEXT_ALIGN_LEFT)
    self._desc = Label(tr("Do you want to download offline maps for your selected region now? The download will run in the background."),
                       font_size=70, font_weight=FontWeight.MEDIUM, text_alignment=rl.GuiTextAlignment.TEXT_ALIGN_LEFT)

    self._no_btn = Button(tr("Not Now"), click_callback=lambda: self._no_callback() if self._no_callback else None)
    self._yes_btn = Button(tr("Download"), button_style=ButtonStyle.PRIMARY, click_callback=lambda: self._yes_callback() if self._yes_callback else None)

  def _render(self, _):
    title_rect = rl.Rectangle(self._rect.x + 95, self._rect.y + 180, self._rect.width - 190, 90)
    self._title.render(title_rect)

    desc_rect = rl.Rectangle(self._rect.x + 95, self._rect.y + 340, self._rect.width - 190, 260)
    self._desc.render(desc_rect)

    btn_y = self._rect.y + self._rect.height - 160 - 45
    btn_width = (self._rect.width - 45 * 3) / 2
    self._no_btn.render(rl.Rectangle(self._rect.x + 45, btn_y, btn_width, 160))
    self._yes_btn.render(rl.Rectangle(self._rect.x + 45 * 2 + btn_width, btn_y, btn_width, 160))

    return -1


class OnboardingWindow(Widget):
  def __init__(self):
    super().__init__()
    self._accepted_terms: bool = ui_state.params.get("HasAcceptedTerms") == terms_version
    self._training_done: bool = ui_state.params.get("CompletedTrainingVersion") == training_version
    self._location_done: bool = ui_state.params.get_bool("OnboardingLocationSetupDone")

    if not self._accepted_terms:
      self._state = OnboardingState.TERMS
    elif not self._training_done:
      self._state = OnboardingState.ONBOARDING
    elif not self._location_done:
      self._state = OnboardingState.LOCATION
    else:
      self._state = OnboardingState.ONBOARDING

    # Windows
    def _restore_overlay():
      gui_app.set_modal_overlay(self)

    self._terms = TermsPage(on_accept=self._on_terms_accepted, on_decline=self._on_terms_declined)
    self._training_guide: TrainingGuide | None = None
    self._decline_page = DeclinePage(back_callback=self._on_decline_back)
    self._location_page = LocationSetupPage(
      continue_callback=self._on_location_selected,
      skip_callback=self._on_location_skipped,
      restore_overlay_callback=_restore_overlay,
    )
    self._maps_page = MapDownloadPage(yes_callback=self._on_maps_download_yes, no_callback=self._on_maps_download_no)

    self._pending_country_ref = ""
    self._pending_country_title = ""
    self._pending_state_ref = ""
    self._pending_state_title = ""

  @property
  def completed(self) -> bool:
    return self._accepted_terms and self._training_done and self._location_done

  def _on_terms_declined(self):
    self._state = OnboardingState.DECLINE

  def _on_decline_back(self):
    self._state = OnboardingState.TERMS

  def _on_terms_accepted(self):
    ui_state.params.put("HasAcceptedTerms", terms_version)
    ui_state.params.put("HasAcceptedTermsSP", terms_version_sp)
    if not self._training_done:
      self._state = OnboardingState.ONBOARDING
    elif not self._location_done:
      self._state = OnboardingState.LOCATION
    else:
      gui_app.set_modal_overlay(None)

  def _on_completed_training(self):
    ui_state.params.put("CompletedTrainingVersion", training_version)
    self._training_done = True
    if self._location_done:
      gui_app.set_modal_overlay(None)
    else:
      self._state = OnboardingState.LOCATION

  def _finalize_location_setup(self):
    ui_state.params.put_bool("OnboardingLocationSetupDone", True)
    self._location_done = True
    gui_app.set_modal_overlay(None)

  def _on_location_selected(self, country_ref: str, country_title: str, state_ref: str, state_title: str):
    self._pending_country_ref = country_ref
    self._pending_country_title = country_title
    self._pending_state_ref = state_ref
    self._pending_state_title = state_title

    # Unit default from location.
    use_imperial = country_ref in IMPERIAL_COUNTRIES
    ui_state.params.put_bool("IsMetric", not use_imperial)

    # Set map region now; actual download starts only if user confirms next page.
    ui_state.params.put_bool("OsmLocal", True)
    ui_state.params.put("OsmLocationName", country_ref)
    ui_state.params.put("OsmLocationTitle", country_title)

    if state_ref:
      ui_state.params.put("OsmStateName", state_ref)
      ui_state.params.put("OsmStateTitle", state_title)
    else:
      ui_state.params.remove("OsmStateName")
      ui_state.params.remove("OsmStateTitle")

    self._state = OnboardingState.MAPS

  def _on_location_skipped(self):
    self._finalize_location_setup()

  def _on_maps_download_yes(self):
    # This triggers mapd to download/update in the background while onboarding exits.
    ui_state.params.put_bool("OsmDbUpdatesCheck", True)
    self._finalize_location_setup()

  def _on_maps_download_no(self):
    self._finalize_location_setup()

  def _render(self, _):
    if self._training_guide is None:
      self._training_guide = TrainingGuide(completed_callback=self._on_completed_training)

    if self._state == OnboardingState.TERMS:
      self._terms.render(self._rect)
    elif self._state == OnboardingState.ONBOARDING:
      if not self._training_done:
        self._training_guide.render(self._rect)
      else:
        if self._location_done:
          gui_app.set_modal_overlay(None)
        else:
          self._state = OnboardingState.LOCATION
    elif self._state == OnboardingState.DECLINE:
      self._decline_page.render(self._rect)
    elif self._state == OnboardingState.LOCATION:
      self._location_page.render(self._rect)
    elif self._state == OnboardingState.MAPS:
      self._maps_page.render(self._rect)
    return -1
