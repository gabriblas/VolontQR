import asyncio
from collections import namedtuple
from concurrent.futures import ProcessPoolExecutor
from io import BytesIO

from pypdf import PageObject, PdfReader, PdfWriter, Transformation
from segno import make as make_qr

Parameters = namedtuple(
    "Parameters", ["data", "error", "style", "transform", "bg", "width", "height"]
)
Transform = namedtuple("Transform", ["x", "y", "d", "r"])


def setup(data, preview):
    tx = Transform(data.x / 100, data.y / 100, data.d / 100, data.r)
    params = list()

    for link in data.valid_links[:1] if preview else data.valid_links:
        p = Parameters(
            link, data.err.value, data.style, tx, data.bg_bytes, data.width, data.height
        )
        params.append(p)

    return params


def make_page(params: Parameters):
    bg_page = PdfReader(BytesIO(params.bg)).pages[0]

    buffer = BytesIO()
    qr = make_qr(params.data, error=params.error)
    qr.save(buffer, kind="pdf", **params.style)
    stamp = PdfReader(buffer).pages[0]

    s = (
        params.transform.d
        * min(bg_page.mediabox.width, bg_page.mediabox.height)
        / max(stamp.mediabox.height, stamp.mediabox.width)
    )
    stamp.add_transformation(Transformation().scale(s, s), expand=True)

    xo = stamp.mediabox.width / 2
    yo = stamp.mediabox.height / 2
    stamp.add_transformation(
        Transformation()
        .translate(-xo, -yo)
        .rotate(params.transform.r)
        .translate(xo, yo),
        expand=True,
    )

    x = bg_page.mediabox.width * params.transform.x - xo
    y = bg_page.mediabox.height * params.transform.y - yo
    stamp.add_transformation(Transformation().translate(x, y), expand=True)

    new_page = PageObject.create_blank_page(width=params.width, height=params.height)
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
    params = await asyncio.to_thread(setup, data, preview)

    # parallel page generation
    loop = asyncio.get_running_loop()

    with ProcessPoolExecutor() as executor:
        # Submit all tasks
        tasks = [loop.run_in_executor(executor, make_page, p) for p in params]

        # Process tasks as they complete
        for future in asyncio.as_completed(tasks):
            page = await future
            pages.append(page)

    # assemble pages
    pdf_buffer = await asyncio.to_thread(assemble_pages, pages, optimize)

    return pdf_buffer
