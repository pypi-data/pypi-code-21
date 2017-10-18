from . import generic


class Parser(generic.Parser):
    def get_body_images(self):
        body = generic.re.search(generic.regex.body, self.content)
        image_urls = {'with_extension': [], 'without_extension': []}

        matches = generic.re.search(
            '<img(?=[^\>]+(?:jpe?g|gif|png|tiff|bmp))(?:[^\>]+)data-a-dynamic-image="([^\"]+)"(?:[^\>]+)>',
            body.group(1), flags=generic.re.IGNORECASE
        )

        if matches:
            image_urls['with_extension'] = generic.html.unescape(matches.group(1)).split("\"")[1::2]

        return image_urls

