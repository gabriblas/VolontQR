import asyncio
from collections import namedtuple
from concurrent.futures import ProcessPoolExecutor
from io import BytesIO

from pypdf import PageObject, PdfReader, PdfWriter, Transformation
from segno import make as make_qr

from .data_container import QR_ERRORS

Transform = namedtuple("Transform", ["x", "y", "d", "r"])


async def make_page(link, error, transform, bg_bytes, fg_color, bg_color):
    bg_page = PdfReader(BytesIO(bg_bytes)).pages[0]

    buffer = BytesIO()
    qr = make_qr(link, error=error)
    qr.save(buffer, kind="pdf", dark=fg_color, light=bg_color)
    stamp = PdfReader(buffer).pages[0]

    s = (
        transform.d
        * min(bg_page.mediabox.width, bg_page.mediabox.height)
        / max(stamp.mediabox.height, stamp.mediabox.width)
    )
    stamp.add_transformation(Transformation().scale(s, s), expand=True)

    xo = stamp.mediabox.width / 2
    yo = stamp.mediabox.height / 2
    stamp.add_transformation(
        Transformation().translate(-xo, -yo).rotate(transform.r).translate(xo, yo),
        expand=True,
    )

    x = bg_page.mediabox.width * transform.x - xo
    y = bg_page.mediabox.height * transform.y - yo
    stamp.add_transformation(Transformation().translate(x, y), expand=True)

    new_page = PageObject.create_blank_page(
        width=bg_page.mediabox.width, height=bg_page.mediabox.height
    )
    new_page.merge_page(bg_page)
    new_page.merge_page(stamp, expand=True, over=True)

    temp_writer = PdfWriter()
    temp_writer.add_page(new_page)
    out_buf = BytesIO()
    temp_writer.write(out_buf)
    return out_buf.getvalue()


def assemble_pages(pages, optimize=True):
    writer = PdfWriter()
    for page in pages:
        writer.add_page(PdfReader(BytesIO(page)).pages[0])

    if optimize:
        writer.compress_identical_objects(remove_identicals=True, remove_orphans=True)

        for page in writer.pages:
            page.compress_content_streams()  # better results if not run in parallel

    pdf_buffer = BytesIO()
    writer.write(pdf_buffer)
    return pdf_buffer.getvalue()


async def make(data, pages, preview, optimize=True):
    # setup the parameters for parallel page generation
    # params = await asyncio.to_thread(setup, data, preview)
    tx = Transform(data.x / 100, data.y / 100, data.d / 100, data.r)
    links = data.valid_links[:1] if preview else data.valid_links
    error = list(QR_ERRORS)[data.err - 1]

    tasks = [
        make_page(link, error, tx, data.bg.bytes, data.fg_color, data.bg_color)
        for link in links
    ]

    for future in asyncio.as_completed(tasks):
        page = await future
        pages.append(page)

    # assemble pages
    pdf_buffer = assemble_pages(pages, optimize)

    return pdf_buffer
