from nicegui import ui, app, ElementFilter
import base64
from internals.data_container import DataContainer
from internals.async_qr import make
from time import sleep
from threading import Thread

import internals.widgets as widgets


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

    pdf_bytes = await make(data, [], preview=True, optimize=False)

    pdf_base64 = base64.b64encode(pdf_bytes).decode("utf-8")
    pdf_data_url = f"data:application/pdf;base64,{pdf_base64}"

    card.remove(sk)
    card.remove(cs)
    with card:
        ui.html(
            f'<iframe class="w-full h-full" src="{pdf_data_url}"></iframe>'
        ).classes("h-full w-full").mark("preview")


def percentage(pages, total, btn: widgets.MakeButton):
    original = btn.text
    while len(pages) != total:
        btn.set_text(f"{len(pages) / total:.0%}")
        sleep(0.1)
    btn.set_text(original)


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
    percentage_thread = Thread(
        target=percentage, args=(pages, len(data.valid_links), make_btn)
    )
    percentage_thread.start()
    data.pdf_bytes = await make(data, pages, preview=False, optimize=True)

    percentage_thread.join()
    make_btn.enable()
    dl_btn.remove(spin)
    dl_btn.set_icon(icon)
    dl_btn.set_data(data.pdf_bytes)


data = DataContainer()


@ui.page("/")
def main():
    ui.query(".nicegui-content").classes("h-screen w-screen")
    with ui.row().classes("h-full w-full"):
        with widgets.MainColumn("Dati"):
            ui.upload(
                label="File di sfondo (.pdf)",
                max_files=1,
                auto_upload=True,
                on_upload=data.on_upd_bg,
            )

            widgets.LinksContainer(data.on_upd_links)

        with widgets.MainColumn("Stile"):
            widgets.AccuracySelector(data)
            with ui.row().classes("w-full items-center gap-4"):
                ui.label("Primo piano")
                widgets.ColorSelector(data.on_upd_fg_col, data.style["dark"])
                ui.label("Sfondo")
                widgets.ColorSelector(
                    data.on_upd_bg_col,
                    data.style["light"],
                    alpha_callback=data.on_upd_bg_alpha,
                )

            with ui.grid(columns="1fr 2fr 1fr 2fr").classes(
                "w-full justify-items-center align-items-center"
            ):
                widgets.NumberSlider("x", data.on_upd_x, data.x)
                widgets.NumberSlider("y", data.on_upd_y, data.y)

                widgets.NumberSlider("Dimensioni", data.on_upd_d, data.d, min=1)
                widgets.NumberKnob("Ruota", data.on_upd_r, data.r)

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
                    widgets.DownloadButton(data).mark("download")
            ui.card().classes("w-full h-full flex justify-center").mark("preview")


app.native.settings["ALLOW_DOWNLOADS"] = True
app.on_connect(lambda event: app.native.main_window.maximize())

if __name__ == "__main__":
    ui.run(
        title="VolontQR",
        reload=False,
        native=True,
    )
