import asyncio
from concurrent.futures import ProcessPoolExecutor
from io import BytesIO
from functools import partial

from pypdf import PageObject, PdfReader, PdfWriter, Transformation
from segno import make as make_qr


def apply_transform(stamp, ref, tx):

    # scaling
    s = (
        tx.d
        * max(ref.mediabox.width, ref.mediabox.height)
        / max(stamp.mediabox.width, stamp.mediabox.height)
    )
    stamp.add_transformation(Transformation().scale(s, s), expand=True)

    # rotation
    xo = stamp.mediabox.width / 2
    yo = stamp.mediabox.height / 2
    stamp.add_transformation(
        Transformation().translate(-xo, -yo).rotate(tx.r).translate(xo, yo)
    )

    # translation
    x = ref.mediabox.width * tx.x - xo
    y = ref.mediabox.height * tx.y - yo
    stamp.add_transformation(Transformation().translate(x, y))


def make_page(link, error, color, bg, qr_tx, logo, logo_tx):
    bg_page = PdfReader(BytesIO(bg)).pages[0]
    if logo is not None:
        logo_stamp = PdfReader(BytesIO(logo)).pages[0]

    buffer = BytesIO()
    qr = make_qr(link, error=error)
    qr.save(buffer, kind="pdf", dark=color.fg, light=color.bg)
    qr_stamp = PdfReader(buffer).pages[0]

    apply_transform(qr_stamp, bg_page, qr_tx)
    if logo is not None:
        apply_transform(logo_stamp, qr_stamp, logo_tx)

    new_page = PageObject.create_blank_page(
        width=bg_page.mediabox.width, height=bg_page.mediabox.height
    )
    new_page.merge_page(bg_page)
    if logo is not None:
        qr_stamp.merge_page(logo_stamp, expand=True, over=True)
    new_page.merge_page(qr_stamp, expand=True, over=True)

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


async def make(container, pages, preview, optimize=True):
    # setup the parameters for parallel page generation
    links = container.valid_links[:1] if preview else container.valid_links

    make_page_special = partial(
        make_page,
        error=container.error_level,
        color=container.colors.to_internals(),
        bg=container.bg,
        qr_tx=container.qr_tx.to_internals(),
        logo=container.logo,
        logo_tx=container.logo_tx.to_internals(),
    )
    make_page_special(links[0])

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
