import os
import updater

if not (os.path.exists("lookups")):
    print("downloading lookup files")
    updater.update(
        "https://update.structuralab.com/structuraUpdate", "Structura1-6", ""
    )

import json
from structura_core import structura
from numpy import array, int32, minimum
import nbtlib
from textual import on, work
from textual.app import App, ComposeResult
from textual.containers import HorizontalGroup, VerticalGroup
from textual.widgets import (
    Button,
    Input,
    Header,
    Footer,
    Label,
    Checkbox,
    Static,
    OptionList,
)
from textual_fspicker import FileOpen, FileSave, Filters
from textual.validation import Function
from textual_slider import Slider

debug = False

global added_models


def is_float(value: str) -> bool:
    try:
        float(value)
        return True
    except ValueError:
        return False


def file_of_type(file_path: str, file_type: str) -> bool:
    if os.path.exists(file_path) and file_path.endswith(file_type):
        return True
    else:
        return False


class StructuraApp(App):
    BINDINGS = []
    CSS_PATH = "structura_tui.tcss"

    def compose(self) -> ComposeResult:
        yield Header("Structura")
        yield VerticalGroup(
            HorizontalGroup(
                Label("Structure File", classes="label"),
                Input(
                    id="structure_file_location",
                    placeholder="Path to structure file",
                    validators=[
                        Function(
                            lambda string: file_of_type(string, "mcstructure"),
                            failure_description="File does not exist",
                        )
                    ],
                ),
                Button(
                    "Browse",
                    variant="primary",
                    id="browse_structure_file",
                    classes="fsBrowser",
                ),
            ),
            HorizontalGroup(
                Label("Icon File", classes="label"),
                Input(
                    id="icon_file_location",
                    placeholder="Path to icon file",
                    validators=[
                        Function(
                            lambda string: file_of_type(string, "png"),
                            failure_description="File does not exist",
                        )
                    ],
                ),
                Button(
                    "Browse",
                    variant="primary",
                    id="browse_icon_file",
                    classes="fsBrowser",
                ),
            ),
            HorizontalGroup(
                Label("Pack Name", classes="label"),
                Input(id="pack_name", placeholder="Name of the pack"),
                Static("", classes="sideButton"),
            ),
            VerticalGroup(
                HorizontalGroup(
                    Label("Name Tag", classes="label"),
                    Input(
                        id="name_tag",
                        placeholder="Name required on the armor stand to display the model",
                    ),
                    Button(
                        "Add Model",
                        variant="primary",
                        id="addModel",
                        classes="sideButton",
                    ),
                ),
                HorizontalGroup(
                    Static("Offsets", classes="label"),
                    Input(
                        id="offset_x",
                        classes="offsets",
                        placeholder="X Offset",
                        value="0.0",
                        validators=[
                            Function(
                                is_float, failure_description="Not a floating point"
                            )
                        ],
                    ),
                    Input(
                        id="offset_y",
                        classes="offsets",
                        placeholder="Y Offset",
                        value="0.0",
                        validators=[
                            Function(
                                is_float, failure_description="Not a floating point"
                            )
                        ],
                    ),
                    Input(
                        id="offset_z",
                        classes="offsets",
                        placeholder="Z Offset",
                        value="0.0",
                        validators=[
                            Function(
                                is_float, failure_description="Not a floating point"
                            )
                        ],
                    ),
                    Static("", classes="sideButton"),
                    id="offsetInputs",
                ),
                HorizontalGroup(
                    Label("Transparency", classes="label"),
                    Label("0%", classes="sliderLabel"),
                    Slider(min=0, max=100, step=1, id="model_transparency"),
                    Label("100%", classes="sliderLabel"),
                    Label(
                        "0%", id="transparency_value", classes="sliderLabel"
                    ),
                    Static("", classes="sideButton"),
                    id="transparencyGroup",
                ),
                HorizontalGroup(
                    Static("", classes="sideButton"),
                    OptionList(
                        "Structure1",
                        "Structure2",
                        "Structure3",
                        markup=False,
                        id="structureList",
                    ),
                    Button(
                        "Remove Model",
                        id="removeModel",
                        classes="sideButton",
                    ),
                    id="modelListGroup",
                ),
                id="advanced_options",
                classes="advanced",
            ),
            HorizontalGroup(
                Checkbox("Advanced", id="advancedToggle"),
                Checkbox("Make Lists", id="makeLists"),
                Checkbox("Big Build mode", id="bigBuildMode", classes="advanced"),
                Button("Make Pack", variant="primary", id="makePack"),
                id="footerButtons",
            ),
            id="root",
        )
        yield Footer()

    def on_mount(self) -> None:
        advanced_elements = self.query(".advanced")
        for advanced_element in advanced_elements:
            advanced_element.styles.display = "none"

    async def open_file(self, input_id: str, file_filter: Filters) -> None:
        if opened := await self.push_screen_wait(
            FileOpen(
                must_exist=False,
                filters=file_filter,
            )
        ):
            self.query_one(f"#{input_id}", Input).value = str(opened)

    @on(Button.Pressed, "#browse_structure_file")
    @work
    async def handle_browse_structure_file(self) -> None:
        await self.open_file(
            input_id="structure_file_location",
            file_filter=Filters(
                ("MCStructure", lambda f: f.suffix.lower() == ".mcstructure"),
            ),
        )

    @on(Button.Pressed, "#browse_icon_file")
    @work
    async def handle_browse_icon_file(self) -> None:
        await self.open_file(
            input_id="icon_file_location",
            file_filter=Filters(
                ("PNG", lambda f: f.suffix.lower() == ".png"),
            ),
        )

    @on(Checkbox.Changed, "#advancedToggle")
    @work
    async def handle_advanced_toggle(self) -> None:
        advanced_elements = self.query(".advanced")
        for advanced_element in advanced_elements:
            advanced_element.styles.display = (
                "block" if self.query_one("#advancedToggle").value else "none"
            )
        self.query_one("#footerButtons").styles.grid_size_columns = (
            4 if self.query_one("#advancedToggle").value else 3
        )

    @on(Slider.Changed, "#model_transparency")
    @work
    async def update_transparency_value(self, event: Slider.Changed) -> None:
        """Update the transparency value label when the slider changes."""
        self.query_one("#transparency_value", Label).update(f"{event.value}%")


if __name__ == "__main__":
    app = StructuraApp()
    app.run()
