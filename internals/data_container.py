from collections import namedtuple
from io import BytesIO

from nicegui import binding
from pypdf import PdfReader, PdfWriter
from validators import url as check_url
from dataclasses import field

QR_ERRORS = ["l", "m", "q", "h"]
CInt = namedtuple("CInt", ["fg", "bg"])
TInt = namedtuple("TInt", ["x", "y", "d", "r"])


def pdf2bytes(pdf):
    pdfpage = PdfReader(pdf).pages[0]
    with PdfWriter() as tmp_writer:
        with BytesIO() as tmp_buf:
            tmp_writer.add_page(pdfpage)
            tmp_writer.write(tmp_buf)
            return tmp_buf.getvalue()


@binding.bindable_dataclass
class Transform:
    x: float = 50
    y: float = 50
    d: float = 50
    r: float = 0

    def to_internals(self):
        return TInt(self.x / 100, self.y / 100, self.d / 100, -self.r)


@binding.bindable_dataclass
class Colors:
    fg: str = "#000000"
    bg: str = "#ffffff"

    def to_internals(self):
        return CInt(self.fg, self.bg)


@binding.bindable_dataclass
class Data:
    bg: bytes = None
    logo: bytes = None

    colors: Colors = field(default_factory=Colors)
    err: int = 4

    qr_tx: Transform = field(default_factory=Transform)
    logo_tx: Transform = field(default_factory=Transform)

    valid_links: list = field(default_factory=list)
    all_links: list = field(default_factory=list)

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

    def on_upd_bg(self, event):
        self.bg = pdf2bytes(event.content)

    def on_upd_logo(self, event):
        self.logo = pdf2bytes(event.content)

    @property
    def error_level(self):
        return QR_ERRORS[self.err - 1]
