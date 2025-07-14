import asyncio
from concurrent.futures import ProcessPoolExecutor
from io import BytesIO
from functools import partial

from pypdf import PageObject, PdfReader, PdfWriter, Transformation
from segno import make as make_qr


def make_page(link, error, color, transform, bg):
    bg = PdfReader(BytesIO(bg)).pages[0]

    buffer = BytesIO()
    qr = make_qr(link, error=error)
    qr.save(buffer, kind="pdf", dark=color.fg, light=color.bg)
    stamp = PdfReader(buffer).pages[0]

    s = (
        transform.d
        * min(bg.mediabox.width, bg.mediabox.height)
        / max(stamp.mediabox.height, stamp.mediabox.width)
    )
    stamp.add_transformation(Transformation().scale(s, s), expand=True)

    xo = stamp.mediabox.width / 2
    yo = stamp.mediabox.height / 2
    stamp.add_transformation(
        Transformation().translate(-xo, -yo).rotate(transform.r).translate(xo, yo),
        expand=True,
    )

    x = bg.mediabox.width * transform.x - xo
    y = bg.mediabox.height * transform.y - yo
    stamp.add_transformation(Transformation().translate(x, y), expand=True)

    new_page = PageObject.create_blank_page(
        width=bg.mediabox.width, height=bg.mediabox.height
    )
    new_page.merge_page(bg)
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
    links = data.valid_links[:1] if preview else data.valid_links

    make_page_special = partial(
        make_page,
        error=data.error_level,
        color=data.colors,
        transform=data.transforms,
        bg=data.bg.bytes,
    )

    # parallel page generation
    loop = asyncio.get_running_loop()

    with ProcessPoolExecutor() as executor:
        # Submit all tasks
        tasks = [loop.run_in_executor(executor, make_page_special, l) for l in links]

        # Process tasks as they complete
        for future in asyncio.as_completed(tasks):
            page = await future
            pages.append(page)

    # assemble pages
    pdf_buffer = assemble_pages(pages, optimize)

    return pdf_buffer
