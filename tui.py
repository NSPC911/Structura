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
from textual.widgets.option_list import Option
from textual.screen import ModalScreen
from textual_fspicker import FileOpen, FileSave, Filters
from textual.validation import Function
from textual_slider import Slider

debug = False


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


class StructuraModel(Option):
    def __init__(
        self,
        name: str,
        path: str,
        transparency: int,
    ) -> None:
        super().__init__(prompt=name, id="".join(name.split(" ")))
        self.name_tag = name
        self.name_tag_no_space = "".join(name.split(" "))
        self.path = path
        self.transparency = transparency


class PopupScreen(ModalScreen):
    def __init__(self, message: str) -> None:
        super().__init__()
        self.message = message

    def compose(self) -> ComposeResult:
        yield VerticalGroup(
            VerticalGroup(
                Static("", classes="topPadding"),
                Label(self.message, id="popupMessage"),
            ),
            HorizontalGroup(
                Static("", classes="leftPadding"),
                Button("OK", id="okPopup", variant="primary"),
                Static("", classes="rightPadding"),
            ),
            id="popupScreenRoot",
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:
        self.dismiss(True)


class StructuraApp(App):
    BINDINGS = []
    CSS_PATH = "structura_tui.tcss"

    def inputIsValid(self, element_selector) -> bool:
        element = self.query_one(element_selector)
        element.validate(element.value)
        return element.is_valid

    def showModalScreen(self, message: str) -> None:
        self.push_screen(PopupScreen(message))

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
                    value="",
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
                    value=str(
                        os.path.join(
                            os.path.dirname(os.path.realpath(__file__)),
                            "lookups",
                            "pack_icon.png",
                        )
                    ),
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
                Input(
                    id="pack_name",
                    placeholder="Name of the pack",
                    validators=[
                        Function(
                            lambda string: len(string) > 0,
                            failure_description="Name required",
                        )
                    ],
                    value="",
                ),
                Static("", classes="sideButton"),
            ),
            VerticalGroup(
                HorizontalGroup(
                    Label("Name Tag", classes="label"),
                    Input(
                        id="name_tag",
                        placeholder="Name required on the armor stand to display the model",
                        validators=[
                            Function(
                                lambda string: len(string) > 0,
                                failure_description="Name required",
                            )
                        ],
                    ),
                    Button(
                        "Add Model",
                        variant="primary",
                        id="addModel",
                        classes="sideButton",
                    ),
                    id="nameTagGroup",
                ),
                HorizontalGroup(
                    Static("", classes="sideButton"),
                    Button("Get Global Coords", id="getGlobalCoords"),
                    Button(
                        "Add Model",
                        id="addModel",
                        variant="primary",
                        classes="sideButton",
                    ),
                    id="globalCoordsGroup",
                ),
                HorizontalGroup(
                    Label("Offsets", id="offsetLabel", classes="label"),
                    Label("Corner", id="cornerLabel", classes="label"),
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
                    Label("0%", id="transparencyValue", classes="slider label"),
                    Slider(min=0, max=100, step=1, id="model_transparency"),
                    Static("", classes="sideButton"),
                    id="transparencyGroup",
                ),
                HorizontalGroup(
                    Static("", classes="sideButton"),
                    OptionList(
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
        for advanced_element in self.query(".advanced"):
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
    def handle_advanced_toggle(self) -> None:
        useAdvanced = self.query_one("#advancedToggle").value
        advanced_elements = self.query(".advanced")
        for advanced_element in advanced_elements:
            advanced_element.styles.display = "block" if useAdvanced else "none"
        if useAdvanced:
            self.query_one("#footerButtons").styles.grid_size_columns = 4
        else:
            self.query_one("#footerButtons").styles.grid_size_size_columns = 3

    @on(Checkbox.Changed, "#bigBuildMode")
    def toggle_big_build_mode(self) -> None:
        """Toggle the big build mode."""
        big_build_mode = self.query_one("#bigBuildMode").value
        # I dont have any better way for the labels, there
        # isnt something stated in the docs to update labels
        if big_build_mode:
            self.query_one("#nameTagGroup").styles.display = "none"
            self.query_one("#globalCoordsGroup").styles.display = "block"
            self.query_one("#cornerLabel").styles.display = "block"
            self.query_one("#offsetLabel").styles.display = "none"
        else:
            self.query_one("#nameTagGroup").styles.display = "block"
            self.query_one("#globalCoordsGroup").styles.display = "none"
            self.query_one("#offsetLabel").styles.display = "block"
            self.query_one("#cornerLabel").styles.display = "none"

    @on(Slider.Changed, "#model_transparency")
    def update_transparency_value(self, event: Slider.Changed) -> None:
        """Update the transparency value label when the slider changes."""
        self.query_one("#transparencyValue", Label).update(f"{event.value}%")

    @on(Button.Pressed, "#makePack")
    def make_pack(self, event: Button.Pressed) -> None:
        """Make the pack."""
        self.showModalScreen("   Making pack...")

    @on(Button.Pressed, "#addModel")
    def add_model(self) -> None:
        # check for validations
        inputElements = ["#structure_file_location", "#icon_file_location", "#name_tag"]
        for elementID in inputElements:
            if not self.inputIsValid(elementID):
                element_value = self.query_one(elementID).value
                self.showModalScreen(
                    f"Invalid input in {elementID}: {element_value if len(element_value) > 0 else '<empty>'}"
                )
                return
        if self.query_one("#bigBuildMode").value:
            name = os.path.basename(
                self.query_one("#structure_file_location").value
            ).split(".")[0]
        else:
            name = self.query_one("#name_tag").value
        # ok validation successful
        self.query_one("#structureList").add_option(
            StructuraModel(
                name,
                self.query_one("#structure_file_location").value,
                self.query_one("#model_transparency").value,
            )
        )

    @on(OptionList.OptionSelected, "#structureList")
    def selected_model(self, event: OptionList.OptionSelected) -> None:
        global selectedModel
        selectedModel = event.option

    @on(Button.Pressed, "#removeModel")
    def remove_model(self) -> None:
        # check whether there are models first
        if len(self.query_one("#structureList").options) == 0:
            self.showModalScreen("No models to remove")
            return
        # actually remove the model
        self.query_one("#structureList").remove_option(
            str(selectedModel.name_tag_no_space)
        )
        self.selectedModel = None

    @on(Button.Pressed, "#getGlobalCoords")
    @work
    async def update_global_coordinates(self) -> None:
        # check for model
        if self.query_one("#structureList").options == []:
            self.showModalScreen("No models available")
            return
        mins = array([2147483647,2147483647,2147483647],dtype=int32)
        for modelElement in self.query_one("#structureList").options:
            modelLocation = modelElement.path
            struct = {}
            struct["nbt"] = nbtlib.load(modelLocation, byteorder='little')
            if "" in struct["nbt"].keys():
                struct["nbt"] = struct["nbt"][""]
            struct["mins"] = array(list(map(int, struct["nbt"]["structure_world_origin"])))
            mins = minimum(mins, struct["mins"])
        # update the offsets
        self.query_one("#offset_x").value = str(mins[0])
        self.query_one("#offset_y").value = str(mins[1])
        self.query_one("#offset_z").value = str(mins[2])


if __name__ == "__main__":
    app = StructuraApp()
    app.run()
