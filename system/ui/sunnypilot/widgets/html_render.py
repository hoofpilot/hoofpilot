"""
Copyright (c) 2021-, Haibin Wen, sunnypilot, and a number of other contributors.

This file is part of sunnypilot and is licensed under the MIT License.
See the LICENSE.md file in the root directory for more details.
"""
from openpilot.system.ui.lib.application import gui_app
from openpilot.system.ui.lib.animation import ease_out_cubic, LinearAnimation, scale_from_center
from openpilot.system.ui.widgets import DialogResult
from openpilot.system.ui.widgets.html_render import HtmlModal


class HtmlModalSP(HtmlModal):
  def __init__(self, file_path=None, text=None, callback=None):
    super().__init__(file_path=file_path, text=text)
    self._callback = callback
    self._dialog_result = DialogResult.NO_ACTION
    self._anim = LinearAnimation(0.2)
    self._anim.start('in')
    self._ok_button._click_callback = self._on_ok_clicked

  def _on_ok_clicked(self):
    self._dialog_result = DialogResult.CONFIRM
    gui_app.set_modal_overlay(None)

    if self._callback:
      self._callback(self._dialog_result)

  def reset(self):
    self._dialog_result = DialogResult.NO_ACTION
    self._anim.start('in')

  def _render(self, rect):
    progress = ease_out_cubic(self._anim.step())
    result = -1

    def _draw():
      nonlocal result
      result = super(HtmlModalSP, self)._render(rect)

    scale_from_center(rect, 0.96 + 0.04 * progress, _draw)
    return result
