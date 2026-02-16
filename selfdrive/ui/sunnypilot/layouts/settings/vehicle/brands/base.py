import abc


class BrandSettings(abc.ABC):
  def __init__(self):
    self.items = []

  @abc.abstractmethod
  def update_settings(self) -> None:
    """Update the settings based on the current vehicle brand."""

