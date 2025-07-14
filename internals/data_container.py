from collections import namedtuple
from io import BytesIO

from nicegui import binding
from pypdf import PdfReader, PdfWriter
from validators import url as check_url
from dataclasses import field

QR_ERRORS = ["l", "m", "q", "h"]
Transforms = namedtuple("Transforms", ["x", "y", "d", "r"])
Colors = namedtuple("Colors", ["fg", "bg"])


@binding.bindable_dataclass
class PdfData:
    data: bytes = None
    x: float = 50
    y: float = 50
    d: float = 50
    r: float = 0

    def on_update(self, event):
        tmp_buf = BytesIO()
        tmp_writer = PdfWriter()

        tmp_writer.add_page(PdfReader(event.content).pages[0])
        tmp_writer.write(tmp_buf)
        self.data = tmp_buf.getvalue()

    @property
    def transform(self):
        return Transforms(self.x / 100, self.y / 100, self.d / 100, -self.r)


@binding.bindable_dataclass
class Data:
    fg_color: str = "#000000"
    bg_color: str = "#ffffff"
    err: int = 4

    valid_links = None
    all_links = None

    bg: PdfData = field(default_factory=PdfData)
    logo: PdfData = field(default_factory=PdfData)
    output: bytes = None

    def on_upd_links(self, event):
        self.all_links = event.value.split("\n")
        self.valid_links = list()
        valid_indx = list()
        invalid_indx = list()
        for i, link in enumerate(self.all_links):
            if check_url(link):
                valid_indx.append(i)
                self.valid_links.append(link)
            else:
                invalid_indx.append(i)
        return namedtuple("Indices", ["valid", "invalid"])(valid_indx, invalid_indx)

    @property
    def error_level(self):
        return QR_ERRORS[self.err - 1]

    @property
    def colors(self):
        return Colors(self.fg_color, self.bg_color)
