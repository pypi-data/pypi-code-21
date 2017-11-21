from TexSoup import TexSoup


def update_cells(cells):
  """Update cells from notebook"""
  print("UPDATE_CELLS")
  if cells is not None:
    for cell in cells:
      print(cell)
      print(cell['type'])

  return cells


def update_tex(tex):
  """Update tex lines"""
  if tex is not None:
    print(tex)
    soup = TexSoup(tex)
    print(soup)

  return tex
