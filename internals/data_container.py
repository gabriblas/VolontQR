from collections import namedtuple
from enum import StrEnum
from io import BytesIO

from nicegui import binding
from pypdf import PdfReader, PdfWriter
from validators import url as check_url

QR_ERRORS = StrEnum("QR_errors", "l m q h")


class PdfData:
    def __init__(self, content):
        self.page = PdfReader(content).pages[0]

        self.height = self.page.mediabox.height
        self.width = self.page.mediabox.width

        tmp_buf = BytesIO()
        tmp_writer = PdfWriter()
        tmp_writer.add_page(self.page)
        tmp_writer.write(tmp_buf)
        self.bytes = tmp_buf.getvalue()


@binding.bindable_dataclass
class Data:
    fg_color: str = "#000000"
    bg_color: str = "#ffffff"
    x: float = 50
    y: float = 50
    d: float = 50
    r: float = 0
    err: int = 4

    valid_links = None
    all_links = None

    bg: PdfData = None
    logo: PdfData = None
    output: bytes = None

    def on_upl_bg(self, event):
        self.bg = PdfData(event.content)

    def on_upl_logo(self, event):
        self.logo = PdfData(event.content)

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