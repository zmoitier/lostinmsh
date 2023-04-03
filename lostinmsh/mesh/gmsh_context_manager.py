"""GMSH as a context manager."""


from contextlib import AbstractContextManager
from dataclasses import dataclass, field
from pathlib import PurePath
from typing import Any, NamedTuple, Optional, TypeAlias, Union

import gmsh

from .helper_type import DomainTags

OptionalPathLike: TypeAlias = Union[None, str, PurePath]


@dataclass(slots=True)
class GmshOptions:
    """GMSH Options.

    http://gmsh.info/doc/texinfo/gmsh.html#Gmsh-options

    Attributes
    ----------
    element_order : int, default=1
    terminal : bool, default=False
    gui : bool,default=False
    filename : OptionalPathLike, optional
    hide_model_entities : bool, default=True
    additional_options : dict[str, Any], optional
    """

    gui: bool = False
    filename: Optional[PurePath] = None
    hide_model_entities: bool = True
    option_value: dict[str, Any] = field(default_factory=dict)

    def __init__(
        self,
        *,
        element_order: int = 1,
        terminal: bool = False,
        gui: bool = False,
        filename: OptionalPathLike = None,
        hide_model_entities: bool = True,
        additional_options: Optional[dict[str, Any]] = None,
    ) -> None:
        if element_order < 1:
            raise ValueError("Element order must be an integer greater or equal to 1.")

        self.gui = gui
        self.filename = PurePath(filename) if filename is not None else None
        self.hide_model_entities = hide_model_entities

        option_value = {
            "General.Terminal": int(terminal),
            "General.SmallAxes": 0,
            "Geometry.CopyMeshingMethod": 1,
            "Mesh.ElementOrder": element_order,
            "Mesh.TransfiniteTri": 1,
            "Mesh.Smoothing": 0,
            "Mesh.SurfaceFaces": 1,
            "Mesh.ColorCarousel": 2,
            "Mesh.Algorithm": 5,  # The Delaunay is better than the Frontal-Delaunay at capturing sharp mesh size transitions.
        }
        if additional_options is not None:
            option_value.update(additional_options)

        self.option_value = option_value

    def __str__(self) -> str:
        data = [
            ("Launch GMSH GUI", self.gui),
            ("filename", self.filename),
            ("Hide model entities", self.hide_model_entities),
            ("#", ""),
            ("Gmsh options", ""),
        ]
        data.extend(((f"  {key}", val) for key, val in self.option_value.items()))
        return _pretty_print(data)


def _pretty_print(data: list[tuple[str, Any]]) -> str:
    """Pretty print."""
    max_len = max(len(d[0]) for d in data) + 1
    return "".join(
        f"{d[0]} {'.' * (max_len - len(d[0]))} {d[1]}\n" if d[0][0] != "#" else "\n"
        for d in data
    )


@dataclass(frozen=True, slots=True)
class GmshContextManager(AbstractContextManager):
    """Context manager for GMSH."""

    gmsh_options: GmshOptions
    domain_tags: DomainTags = field(default_factory=dict)

    def __enter__(self):
        # Initialize the Gmsh API.
        gmsh.initialize()

        for key, val in self.gmsh_options.option_value.items():
            gmsh.option.setNumber(key, val)

        # Add a new model and set it as the current model.
        if self.gmsh_options.filename is None:
            gmsh.model.add("mesh")
        else:
            gmsh.model.add(self.gmsh_options.filename.stem)

        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        # Synchronize the built-in CAD representation with the current Gmsh model.
        gmsh.model.geo.synchronize()

        for domain, tags in self.domain_tags.items():
            gmsh.model.addPhysicalGroup(dim=domain.dim, tags=tags, name=domain.name)

        # Generate a mesh of the current model, up to dimension dim 2.
        gmsh.model.mesh.generate(2)

        # _set_options_graphical(self.gmsh_options.hide_model_entities)

        if self.gmsh_options.gui:
            # Create and run the FLTK graphical user interface.
            gmsh.fltk.run()

        if self.gmsh_options.filename is not None:
            # Write a file. The export format is determined by the file extension.
            match self.gmsh_options.filename.suffix:
                case ".msh":
                    gmsh.write(str(self.gmsh_options.filename))
                case _:
                    gmsh.fltk.initialize()
                    gmsh.write(str(self.gmsh_options.filename))
                    gmsh.fltk.finalize()

        # Finalize the Gmsh API.
        gmsh.finalize()

        if exc_type is not None:
            print(f"\n{exc_type}")

        if exc_value is not None:
            print(f"\n{exc_value}")

        if exc_tb is not None:
            print(f"\n{exc_tb}")


INT_TO_STR = {
    0: "Zero",
    1: "One",
    2: "Two",
    3: "Three",
    4: "Four",
    5: "Five",
    6: "Six",
    7: "Seven",
    8: "Eight",
    9: "Nine",
    10: "Ten",
    11: "Eleven",
    12: "Twelve",
    13: "Thirteen",
    14: "Fourteen",
    15: "Fifteen",
    16: "Sixteen",
    17: "Seventeen",
    18: "Eighteen",
    19: "Nineteen",
}


class Color(NamedTuple):
    """Color representation."""

    # matplotlib color name
    mpl: str

    # RGBA representation
    r: int
    g: int
    b: int
    a: int = 255


C_POLYGON = Color("C2", 44, 160, 44)
C_VACUUM = Color("C0", 31, 119, 180)
C_PML = Color("C1", 255, 127, 14)


def _set_options_graphical(hide_model_Entities: bool) -> None:
    """Set."""

    # Hide the model entities of dimensions 0 and 1.
    if hide_model_Entities:
        gmsh.model.setVisibility(gmsh.model.getEntities(0), 0)
        gmsh.model.setVisibility(gmsh.model.getEntities(1), 0)

    name_to_color = {
        gmsh.model.getPhysicalName(dim=d, tag=t): f"Mesh.Color.{INT_TO_STR[t]}"
        for (d, t) in gmsh.model.getPhysicalGroups(dim=2)
    }

    for name, color in name_to_color.items():
        if name == "Vacuum":
            gmsh.option.setColor(color, C_VACUUM.r, C_VACUUM.g, C_VACUUM.b, C_VACUUM.a)
        elif name == "PML":
            gmsh.option.setColor(color, C_PML.r, C_PML.g, C_PML.b, C_PML.a)
        else:
            gmsh.option.setColor(
                color, C_POLYGON.r, C_POLYGON.g, C_POLYGON.b, C_POLYGON.a
            )
