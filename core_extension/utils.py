import bleach


# Richtext validator with Bleach
def filter_class(name, value):
    if name == "class" and value in ("content-image", "ul-default", "ol-default"):
        return True
    else:
        return False


allowed_tags = ("a", "b", "blockquote", "br", "dd", "div", "dl", "dt", "em",
                "h1", "h2", "h3", "h4", "h5", "h6", "i", "img", "li", "ol",
                "p", "s", "span", "strong", "table", "tbody", "td", "tfoot",
                "th", "thead", "tr", "tt", "u", "ul")


allowed_attrs = {
    "a": ["href", "name", "title"],
    "img": ["align", "alt", "height", "src", "width"],
    "th": ["colspan", "rowspan"],
    "td": ["colspan", "rowspan"],
    "div": filter_class,
    "ul": filter_class,
    "ol": filter_class,
}


def html_validator(html):
    return bleach.clean(html, tags=allowed_tags, attributes=allowed_attrs, strip_comments=True)