def get_highlighted_description(params, param_name: str, descriptions: list[str]) -> str:
  index = int(params.get(param_name, return_default=True))
  lines = []
  for i, desc in enumerate(descriptions):
    if i == index:
      lines.append(f"<b>{desc}</b>")
    else:
      lines.append(f"{desc}")

  return "<br>".join(lines)

