import base64
from threading import Thread
from time import sleep
from functools import wraps

from nicegui import ElementFilter, app, ui

import internals.widgets as widgets
from infos import NAME, VERSION, WEBSITE
from internals.async_qr import make
from internals.data_container import Data


def validating(func):
    @wraps(func)
    async def decorated(event):
        kwargs = dict(type="negative", position="bottom-right")
        if container.bg is None:
            ui.notify("Nessuno sfondo caricato.", **kwargs)
        elif len(container.all_links) == 0:
            ui.notify("Nessun link specificato", **kwargs)
        elif len(container.valid_links) == 0:
            ui.notify("Nessun link valido specificato", **kwargs)
        else:
            if container.logo is not None and container.err < 3:
                ui.notify(
                    "Aggiungere un logo con una bassa accuratezza è sconsigliato!",
                    position="bottom-right",
                    type="warning",
                )
            return await func(event)

    return decorated


@validating
async def make_preview(event):
    card = list(ElementFilter(kind=ui.card, marker="preview"))[0]
    try:
        iframe = list(ElementFilter(kind=ui.html, marker="preview"))[0]
        card.remove(iframe)
    except IndexError:
        pass
    with card:
        sk = ui.skeleton(square=True, animation="fade", height="75%", width="100%")
        with ui.card_section().classes("w-full") as cs:
            ui.skeleton("text").classes("text-subtitle1")
            ui.skeleton("text").classes("text-subtitle1 w-1/2")
            ui.skeleton("text").classes("text-caption")

    pdf_bytes = await make(container, [], preview=True, optimize=False)

    pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")
    pdf_data_url = f"data:application/pdf;base64,{pdf_base64}"

    card.remove(sk)
    card.remove(cs)
    with card:
        ui.html(
            f'<iframe class="w-full h-full" src="{pdf_data_url}"></iframe>'
        ).classes("h-full w-full").mark("preview")


def percentage(data, pages, btn: widgets.MakeButton):
    original = btn.text
    total = len(data.valid_links)
    while len(pages) != total:
        btn.set_text(f"{len(pages) / total:.0%}")
        sleep(0.1)
    while data.pdf_bytes is None:
        btn.set_text("Ottimizzazione...")
        sleep(0.1)
    btn.set_text(original)


@validating
async def make_pdf(event):
    make_btn = list(ElementFilter(kind=ui.button, marker="make_pdf"))[0]
    dl_btn = list(ElementFilter(kind=widgets.DownloadButton, marker="download"))[0]
    make_btn.disable()
    dl_btn.reset()
    icon = dl_btn.icon
    dl_btn.set_icon(None)
    with dl_btn:
        spin = ui.spinner(color="white")

    pages = list()
    container.pdf_bytes = None
    percentage_thread = Thread(target=percentage, args=(container, pages, make_btn))
    percentage_thread.start()
    container.pdf_bytes = await make(container, pages, preview=False, optimize=True)

    percentage_thread.join()
    make_btn.enable()
    dl_btn.remove(spin)
    dl_btn.set_icon(icon)
    dl_btn.set_data(container.pdf_bytes)


@ui.page("/")
def main():
    ui.query(".nicegui-content").classes("h-screen w-screen")

    # Title bar
    with ui.row().classes("h-[20px] w-full items-center"):
        ui.label(f"🚀{NAME}").classes("text-2xl")
        ui.space()
        ui.label(VERSION)
        ui.add_head_html(
            '<link href="https://unpkg.com/eva-icons@1.1.3/style/eva-icons.css" rel="stylesheet" />'
        )
        with ui.link(target=WEBSITE).classes("text-2xl").tooltip("GitHub"):
            ui.icon("eva-github").classes("fill-white scale-125 m-1")

    with ui.row().classes("h-full w-full"):
        with widgets.MainColumn("Dati"):
            ui.upload(
                label="Sfondo (.pdf)",
                max_files=1,
                auto_upload=True,
                on_upload=container.on_upd_bg,
            ).mark("bg")

            ui.upload(
                label="Logo (.pdf)",
                max_files=1,
                auto_upload=True,
                on_upload=container.on_upd_logo,
            ).mark("logo")

            widgets.LinksContainer(container.on_upd_links)

        with widgets.MainColumn("Stile"):
            with ui.card().classes("w-full"):
                ui.label("Codice QR").classes("text-xl")
                widgets.AccuracySelector().radio.bind_value(container, "err")
                with ui.row().classes("w-full items-center gap-4"):
                    cs = widgets.ColorSelector("Primo piano")
                    cs.bind_value(container.colors, "fg")
                    cs = widgets.ColorSelector("Sfondo", allow_alpha=True)
                    cs.bind_value(container.colors, "bg")

                with ui.grid(columns="1fr 2fr 1fr 2fr").classes(
                    "w-full justify-items-center"
                ):
                    widgets.NumberSlider("x").bind_value(container.qr_tx, "x")
                    widgets.NumberSlider("y").bind_value(container.qr_tx, "y")
                    widgets.NumberSlider("Dimensioni", min=1).bind_value(
                        container.qr_tx, "d"
                    )
                    widgets.NumberKnob("Ruota").bind_value(container.qr_tx, "r")

            with ui.card().classes("w-full"):
                ui.label("Logo").classes("text-xl")
                with ui.grid(columns="1fr 2fr 1fr 2fr").classes(
                    "w-full justify-items-center"
                ):
                    widgets.NumberSlider("x").bind_value(container.logo_tx, "x")
                    widgets.NumberSlider("y").bind_value(container.logo_tx, "y")
                    widgets.NumberSlider("Dimensioni", min=1).bind_value(
                        container.logo_tx, "d"
                    )
                    widgets.NumberKnob("Ruota").bind_value(container.logo_tx, "r")

        with widgets.MainColumn("Anteprima") as col:
            col.classes("flex-grow")  # fill remaining space
            with col.title_row:
                ui.space()
                spin = ui.spinner(size="xs").classes("h-full").mark("preview")
                spin.set_visibility(False)
                widgets.MakeButton(make_preview, "Anteprima", icon="visibility").mark(
                    "preview"
                )
                with ui.button_group():
                    make_btn = widgets.MakeButton(make_pdf, "Genera tutti").mark(
                        "make_pdf"
                    )
                    make_btn.classes(add="w-[150px]")
                    widgets.DownloadButton().mark("download")
            ui.card().classes("w-full h-full flex justify-center").mark("preview")


if __name__ in ["__main__", "__mp_main__"]:
    container = Data()

    app.native.settings["ALLOW_DOWNLOADS"] = True
    # app.on_connect(lambda event: app.native.main_window.maximize())
    ui.run(
        title=NAME,
        reload=True,
        # native=True,
    )
