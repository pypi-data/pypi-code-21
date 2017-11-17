from selenium import webdriver
from selenium.webdriver import ActionChains
from PIL import Image
import io, base64, math, os


def render_snapshots(filepath, build_dir='/tmp/build_dir'):
  window_width = 800
  window_height = 600
  browser = _chrome(window_width, window_height)
  # Get all of the output cells
  outputs = '.code_cell .output_wrapper .output'
  browser.get('file://%s' % filepath)
  elems = browser.find_elements_by_css_selector(outputs)
  images = []
  try:
    for i, ele in enumerate(elems):
      filename = os.path.join(build_dir, 'output-%d.png' % i)
      #       if not os.path.exists(filename):
      _render_element_screenshot(browser, ele, filename, window_width,
                                 window_height)
      images.append(filename)
  finally:
    browser.quit()

  return images


def _render_element_screenshot(browser, ele, filename, window_width,
                               window_height):
  img = get_element_screenshot(browser, ele, window_width, window_height)
  img.save(filename)
  return filename


def _chrome(window_width=900, window_height=600):
  """Chrome instance"""
  chrome_options = webdriver.ChromeOptions()
  chrome_options.add_argument('--window-size=%d,%d' % (window_width,
                                                       window_height))
  chrome_options.add_argument('--headless')
  chrome_options.add_argument('--incognito')

  browser = webdriver.Chrome(chrome_options=chrome_options)
  return browser


def get_element_screenshot(browser, element, window_width, window_height):
  """Get a screenshot of the element"""
  try:
    browser.execute_script(
        "arguments[0].scrollIntoView({behavior: 'instant', block: 'start'});",
        element)

    width = element.size["width"]
    height = element.size["height"]

    scr_png = browser.get_screenshot_as_png()
    scr_img = Image.open(io.BytesIO(scr_png))
    # left, top, right, bottom
    dims = (
        int(0),
        int(5),
        window_width * 2,
        int(height) * 2,
    )
    img = scr_img.crop(dims)

    basewidth = 1200
    wpercent = (basewidth / float(img.size[0]))
    hsize = int((float(img.size[1]) * float(wpercent)))
    img = img.resize((basewidth, hsize), Image.ANTIALIAS)

    return img

  except:
    return None
