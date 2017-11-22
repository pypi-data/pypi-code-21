from markdown.inlinepatterns import LinkPattern, handleAttributes
from markdown.extensions import Extension
from markdown import util
import base64
import urllib

NOBRACKET = r'[^\]\[]*'
BRK = (
    r'\[(' +
    (NOBRACKET + r'(\[')*6 +
    (NOBRACKET + r'\])*')*6 +
    NOBRACKET + r')\]'
)
IMAGE_LINK_RE = r'\!' + BRK + r'\s*\((<.*?>|([^")]+"[^"]*"|[^\)]*))\)'

class ImagePatternBase64(LinkPattern):

    def handleMatch(self, m):

        el = util.etree.Element("img")
        src_parts = m.group(9).split()
        if src_parts:
            src = src_parts[0]
            if src[0] == "<" and src[-1] == ">":
                src = src[1:-1]

            image = get_image(self.sanitize_url(self.unescape(src)))
            el.set('src', image)
        else:
            el.set('src', "")
        if len(src_parts) > 1:
            el.set('title', dequote(self.unescape(" ".join(src_parts[1:]))))

        if self.markdown.enable_attributes:
            truealt = handleAttributes(m.group(2), el)
        else:
            truealt = m.group(2)

        el.set('alt', self.unescape(truealt))
        return el


class ImageDownloaderExtension(Extension):

    def extendMarkdown(self, md, md_globals):
        md.inlinePatterns.add('image_base64', ImagePatternBase64(IMAGE_LINK_RE, md), '<image_link')


def get_image(image_path):

    try:
        image_file = urllib.request.urlopen(image_path)
        image_result = ''

        image_result = convert_image(image_file)

    except:
        image_result = get_local_image(image_path)

    return image_result

def get_local_image(image_path):

    with open(image_path, "rb") as image_file:
        return convert_image(image_file)

def convert_image(image_file):

    image_content_base64 = base64.b64encode(image_file.read())

    return 'data:image/png;base64,' + image_content_base64.decode('utf8')
