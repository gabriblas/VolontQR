from colorsys import rgb_to_hls

from nicegui import ui
from nicegui.elements.mixins.value_element import ValueElement

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
                with ui.row():
                    ui.label("Links").classes("text-xl")
                    ui.space()
                    self.chip_ok = (
                        ui.chip("0", color="green", icon="r_thumb_up")
                        .classes("text-2xs")
                        .props('dense text-color="white"')
                    )
                    self.chip_no = (
                        ui.chip("0", color="red", icon="r_thumb_down")
                        .classes("text-2xs")
                        .props('dense text-color="white"')
                    )

                self.cm = ui.codemirror("", language="HTTP", on_change=self.check_links)
                self.cm.classes("w-full flex-grow").style("max-width:18rem")

    def check_links(self, event):
        indices = self.link_callback(event)

        js = "const gutterElements = document.querySelectorAll('.cm-gutterElement');"
        for i in indices.valid:
            js += f"if (gutterElements[{i}]) {{gutterElements[{i + 1}].style.color = 'green';gutterElements[{i + 1}].style.fontWeight = 'normal';}}"
        for i in indices.invalid:
            js += f"if (gutterElements[{i}]) {{gutterElements[{i + 1}].style.color = 'red';gutterElements[{i + 1}].style.fontWeight = 'bold';}}"

        ui.run_javascript(js)

        self.chip_ok.set_text(f"{len(indices.valid)}")
        self.chip_no.set_text(f"{len(indices.invalid)}")


class AccuracySelector(ui.row):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.classes("w-full items-center gap-4").style("width: 100%")
        with self:
            ui.label("Accuratezza").classes("whitespace-nowrap")

            m = len(QR_ERRORS)
            self.radio = ui.radio(list(range(1, m + 1))).props("inline")
            ui.space()
            ui.icon("sym_r_help").classes("text-xl").tooltip(
                "Un valore più alto risulta in un QR code più grande ma che verrà riconosciuto meglio. Questo è estremamente consigliato se un logo è incluso al centro del QR code."
            )


class ColorSelector(ValueElement, ui.button):
    def __init__(self, label, allow_alpha=False, **kwargs):
        self.label = ui.label(label)
        super().__init__(value="#ffffff", **kwargs)
        self._prev = None
        with self:
            self.ico = ui.icon("palette")
            self.cp = ui.color_picker(on_pick=self.on_pick)
        if allow_alpha:
            self.switch = ui.switch("Trasparente")
            self.switch.on_value_change(self.toggle_alpha)
            self.bind_enabled_from(self.switch, "value", lambda v: not v)

    @staticmethod
    def smart_invert(color):
        r = int(color[1:3], 16) / 256
        g = int(color[3:5], 16) / 256
        b = int(color[5:7], 16) / 256
        lum = rgb_to_hls(r, g, b)[1]  # luminance
        return "#000000" if lum > 0.5 else "#ffffff"

    def bind_value(self, *args, **kwargs):
        ret = super().bind_value(*args, **kwargs)
        self.on_pick(None)
        return ret

    def on_pick(self, event):
        self.classes(remove=f"!bg-[{self.value}]")
        if event is not None:
            self.value = event.color
        self.classes(add=f"!bg-[{self.value}]")
        self.ico.style(f"color: {self.smart_invert(self.value)}")

    def toggle_alpha(self, event):
        if isinstance(self.value, str):
            self._prev = self.value
            self.value = None
        else:
            self.value = self._prev


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
    def __init__(self, *args, **kwargs):
        super().__init__(icon="r_file_download", *args, **kwargs)
        self.on_click(self.download)
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
    def __init__(self, label, min=0, max=100):
        super().__init__(label=label, min=min, max=max)
        self.slid = ui.slider(min=min, max=max).style("width:100%").bind_value(self)


class NumberKnob(ui.number):
    def __init__(self, label):
        super().__init__(label=label, min=0, max=360)
        self.knob = ui.knob(
            min=0, max=360, center_color="white", track_color="grey-4"
        ).bind_value(self)
