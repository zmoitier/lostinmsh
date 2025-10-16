"""GMSH as a context manager."""

from contextlib import AbstractContextManager
from dataclasses import dataclass, field
from pathlib import PurePath
from types import TracebackType
from typing import Any, NamedTuple, Self

import gmsh

from .helper_type import DomainTags


@dataclass(slots=True)
class GmshOptions:
    """Gmsh options.

    Attributes:
    ------------
        filename: PurePath | None, default None
            Path to the output mesh file. If None, the mesh is not saved.
        element_order: int, default 1
            Order of the finite elements. Must be an integer >= 1.
        additional_options: dict[str, Any] | None, default None
            Additional Gmsh options as a dictionary of key-value pairs. See GMSH documentation
            http://gmsh.info/doc/texinfo/gmsh.html#Gmsh-options.
        renumber_nodes: Renumbering strategy for the nodes. If None, no renumbering is performed.
        show_terminal_output: bool, default False
            If True, show Gmsh terminal output.
        show_gui: bool, default False
            If True, launch the Gmsh GUI.
        hide_model_entities: bool, default True
            If True, hide the model entities of dimensions 0 and 1 in the GUI.

    Raises:
        ValueError: If the element order is less than 1.
    """

    filename: PurePath | None
    key_val: dict[str, Any]
    renumber_nodes: str | None
    show_gui: bool
    hide_model_entities: bool

    def __init__(
        self,
        *,
        filename: PurePath | str | None = None,
        element_order: int = 1,
        additional_options: dict[str, Any] | None = None,
        renumber_nodes: str | None = "RCMK",
        show_terminal_output: bool = False,
        show_gui: bool = False,
        hide_model_entities: bool = True,
    ) -> None:
        """Initialize GmshOptions."""
        self.filename = PurePath(filename) if filename is not None else None

        if element_order < 1:
            raise ValueError("Element order must be an integer >= 1.")

        self.renumber_nodes = renumber_nodes

        self.show_gui = show_gui
        self.hide_model_entities = hide_model_entities

        key_val = {
            "General.Terminal": int(show_terminal_output),
            "General.SmallAxes": 0,
            "Geometry.CopyMeshingMethod": 1,
            "Mesh.ElementOrder": element_order,
            "Mesh.TransfiniteTri": 1,
            "Mesh.Smoothing": 0,
            "Mesh.Algorithm": 6,  # 5 is better than 6 at capturing sharp mesh size transitions.
            "Mesh.MeshSizeExtendFromBoundary": 0,
            "Mesh.SurfaceFaces": 1,
            "Mesh.ColorCarousel": 2,
        }
        if additional_options is not None:
            key_val.update(additional_options)

        self.key_val = key_val

        return None

    def __str__(self) -> str:
        data = [
            ("filename", self.filename),
            ("Launch GMSH GUI", self.show_gui),
            ("Hide model entities", self.hide_model_entities),
            ("Renumber nodes", self.renumber_nodes),
            ("Gmsh options", ""),
        ]
        data.extend(((f"  {key}", val) for key, val in self.key_val.items()))

        n = max(len(key) for key, _ in data) + 1
        return "".join(
            f"{key} {'.' * (n - len(key)) if val != '' else ''} {val}\n"
            for key, val in data
        )


@dataclass(frozen=True, slots=True)
class GmshContextManager(AbstractContextManager):
    """Context manager for GMSH."""

    options: GmshOptions
    domain_tags: DomainTags = field(default_factory=dict)

    def __enter__(self: Self) -> Self:
        # Initialize the Gmsh API.
        gmsh.initialize()

        for key, val in self.options.key_val.items():
            gmsh.option.setNumber(key, val)

        # Add a new model and set it as the current model.
        if self.options.filename is None:
            gmsh.model.add("mesh")
        else:
            gmsh.model.add(self.options.filename.stem)

        return self

    def __exit__(
        self: Self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        # Synchronize the built-in CAD representation with the current Gmsh model.
        gmsh.model.geo.synchronize()

        for domain, tags in self.domain_tags.items():
            gmsh.model.addPhysicalGroup(dim=domain.dim, tags=tags, name=domain.name)

        # Generate a mesh of the current model, up to dimension dim 2.
        gmsh.model.mesh.generate(2)

        if self.options.renumber_nodes is not None:
            # Renumber the nodes to improve the matrix bandwidth.
            old, new = gmsh.model.mesh.compute_renumbering(self.options.renumber_nodes)
            gmsh.model.mesh.renumber_nodes(old, new)

        _set_options_graphical(self.options.hide_model_entities)

        if self.options.show_gui:
            # Create and run the FLTK graphical user interface.
            gmsh.fltk.run()

        if self.options.filename is not None:
            # Write a file. The export format is determined by the file extension.
            match self.options.filename.suffix:
                case ".msh":
                    gmsh.write(str(self.options.filename))
                case _:
                    gmsh.fltk.initialize()
                    gmsh.write(str(self.options.filename))
                    gmsh.fltk.finalize()

        # Finalize the Gmsh API.
        gmsh.finalize()

        if exc_type is not None:
            print(f"\n{exc_type}")

        if exc_value is not None:
            print(f"\n{exc_value}")

        if traceback is not None:
            print(f"\n{traceback}")


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
