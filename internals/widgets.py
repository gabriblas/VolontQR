from colorsys import rgb_to_hls

from nicegui import ui

from .data_container import QR_ERRORS


class MainColumn(ui.column):
    def __init__(self, title, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.classes("h-full max-h-screen")
        with self:
            self.title_row = ui.row().classes("w-full")
            with self.title_row:
                ui.label(title).classes("text-2xl")


class LinksContainer(ui.card):
    def __init__(self, link_callback, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.link_callback = link_callback
        self.classes("w-full flex-grow min-h-0")
        with self:
            with ui.column().classes("h-full w-full"):
                ui.label("Links").classes("text-xl")
                self.cm = ui.codemirror("", language="HTTP", on_change=self.check_links)
                self.cm.classes("w-full flex-grow").style("max-width:18rem")
                with ui.row():
                    self.chip_ok = ui.chip(color="green", icon="r_thumb_up")
                    self.chip_no = ui.chip(color="red", icon="r_thumb_down")

    def check_links(self, event):
        indices = self.link_callback(event)

        js = "const gutterElements = document.querySelectorAll('.cm-gutterElement');"
        for i in indices.valid:
            js += f"if (gutterElements[{i}]) {{gutterElements[{i + 1}].style.color = 'green';gutterElements[{i + 1}].style.fontWeight = 'normal';}}"
        for i in indices.invalid:
            js += f"if (gutterElements[{i}]) {{gutterElements[{i + 1}].style.color = 'red';gutterElements[{i + 1}].style.fontWeight = 'bold';}}"

        ui.run_javascript(js)

        self.chip_ok.set_text(
            f"{len(indices.valid)} valid{'o' if len(indices.valid) == 1 else 'i'}"
        )
        self.chip_no.set_text(
            f"{len(indices.invalid)} non valid{'o' if len(indices.invalid) == 1 else 'i'}"
        )


class AccuracySelector(ui.row):
    def __init__(self, data, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.classes("w-full items-center gap-4").style("width: 100%")
        with self:
            ui.label("Accuratezza").classes("whitespace-nowrap")

            m = len(QR_ERRORS)
            self.slider = ui.slider(min=1, max=m, step=1, value=m)
            self.slider.on_value_change(data.on_upd_err)
            self.slider.props("label-always").classes("flex-grow").style("width: 80px")
            ui.tooltip(
                "Un valore più alto risulta in un QR code più grande ma che verrà riconosciuto meglio. Questo è estremamente consigliato se un logo è incluso al centro del QR code."
            ).style("width: 30em")


class ColorSelector(ui.button):
    def __init__(self, callback, color, alpha_callback=None, **kwargs):
        super().__init__(color=color, **kwargs)
        self.callback = callback
        with self:
            self.ico = ui.icon("palette").style(f"color: {self.bg2fg(color)}")
            self.cp = ui.color_picker(value=color, on_pick=self.on_pick)
        if alpha_callback is not None:
            switch = ui.switch("Trasparente").on_value_change(alpha_callback)
            self.bind_enabled_from(switch, "value", lambda v: not v)

    @staticmethod
    def bg2fg(bg):
        r = int(bg[1:3], 16) / 256
        g = int(bg[3:5], 16) / 256
        b = int(bg[5:7], 16) / 256
        lum = rgb_to_hls(r, g, b)[1]  # luminance
        return "#000000" if lum > 0.5 else "#ffffff"

    def on_pick(self, event):
        bg = event.color
        self.classes(f"!bg-[{bg}]")
        self.ico.style(f"color: {self.bg2fg(bg)}")
        self.callback(event)


class MakeButton(ui.button):
    def __init__(self, callback, text, *args, **kwargs):
        super().__init__(text, *args, **kwargs)
        self.callback = callback
        self.on_click(self.make)

    async def make(self, event):
        self.disable()
        await self.callback(event)
        self.enable()


class DownloadButton(ui.button):
    def __init__(self, data_container, *args, **kwargs):
        super().__init__(icon="r_file_download", *args, **kwargs)
        self.on_click(self.download)
        data_container.link_dl_btn(self)
        self.reset()

    def set_data(self, data):
        self.data = data
        self.clear()  # remove outdated tooltip
        self.props('color="green"')
        self.enable()

    def outdate(self):
        if not self.props["disable"]:
            self.props('color="orange"')
            with self:
                ui.tooltip(
                    "I biglietti generati non corrispondono alle ultime modifiche."
                )

    def reset(self):
        self.disable()
        self.props('color="grey"')
        self.data = None

    def download(self):
        ui.download.content(self.data, "tickets.pdf", media_type="pdf")


class NumberSlider(ui.number):
    def __init__(self, lab, callback, value, min=0):
        super().__init__(label=lab, min=min, max=100, value=value)
        self.slid = (
            ui.slider(min=0, max=100, value=value).style("width:100%").bind_value(self)
        )
        self.on_value_change(callback)


class NumberKnob(ui.number):
    def __init__(self, lab, callback, value):
        super().__init__(label=lab, min=0, max=360, value=value)
        self.knob = ui.knob(
            min=0, max=360, value=value, center_color="white", track_color="grey-4"
        ).bind_value(self)
        self.on_value_change(callback)
