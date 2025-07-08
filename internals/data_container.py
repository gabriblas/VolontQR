from collections import namedtuple
from enum import StrEnum
from io import BytesIO

from nicegui import binding
from pypdf import PdfReader, PdfWriter, PageObject
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


class DataContainer:
    def __init__(self):
        self.style = dict(light="#ffffff", dark="#000000")
        self.x = self.y = self.d = 50
        self.r = 0
        self.err = QR_ERRORS.m

        self.bg = None
        self.logo = None
        self.valid_links = list()
        self.all_links = list()
        self.pdf_bytes = None

    def on_upd_bg(self, event):
        self.dl_btn.outdate()
        self.bg = PdfReader(event.content).pages[0]
        self.height = self.bg.mediabox.height
        self.width = self.bg.mediabox.width

        bg_buf = BytesIO()
        temp_writer = PdfWriter()
        temp_writer.add_page(self.bg)
        temp_writer.write(bg_buf)
        self.bg_bytes = bg_buf.getvalue()

    def on_upd_logo(self, event):
        self.dl_btn.outdate()
        self.bg = PdfReader(event.content).pages[0]

        bg_buf = BytesIO()
        temp_writer = PdfWriter()
        temp_writer.add_page(self.bg)
        temp_writer.write(bg_buf)
        self.logo = bg_buf.getvalue()

    def on_upd_links(self, event):
        self.dl_btn.outdate()
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

    def on_upd_err(self, event):
        self.dl_btn.outdate()
        self.err = list(QR_ERRORS)[event.value - 1]

    def on_upd_fg_col(self, event):
        self.dl_btn.outdate()
        self.style.update(dark=event.color)

    def on_upd_bg_col(self, event):
        self.dl_btn.outdate()
        self.style.update(light=event.color)

    def on_upd_bg_alpha(self, event):
        self.dl_btn.outdate()
        pc = self.style["light"]
        if event.value:
            self.style.update(light=None)
        else:
            self.style.update(light=self._prev_col)
        self._prev_col = pc

    def on_upd_x(self, event):
        self.dl_btn.outdate()
        self.x = event.value

    def on_upd_y(self, event):
        self.dl_btn.outdate()
        self.y = event.value

    def on_upd_d(self, event):
        self.dl_btn.outdate()
        self.d = event.value

    def on_upd_r(self, event):
        self.dl_btn.outdate()
        self.r = event.value

    def link_dl_btn(self, btn):
        self.dl_btn = btn
