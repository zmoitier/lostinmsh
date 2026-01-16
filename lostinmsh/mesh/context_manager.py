"""GMSH as a context manager."""

from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import PurePath
from types import TracebackType
from typing import Any, Self

import gmsh

from ..type_alias import DimName, Tag


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
        renumber_nodes: str | None, default "RCMK"
            Renumbering strategy for the nodes. If None, no renumbering is performed.
        show_terminal_output: bool, default False
            If True, show Gmsh terminal output.
        show_gui: bool, default False
            If True, launch the Gmsh GUI.

    Raises:
        ValueError: If the element order is less than 1.
    """

    filename: PurePath | None
    key_val: dict[str, Any]
    renumber_nodes: str | None
    show_gui: bool

    def __init__(
        self,
        *,
        filename: PurePath | str | None = None,
        element_order: int = 1,
        additional_options: dict[str, Any] | None = None,
        renumber_nodes: str | None = "RCMK",
        show_terminal_output: bool = True,
        show_gui: bool = False,
    ) -> None:
        """Initialized gmsh options.

        Parameters
        ----------
        filename : PurePath | str | None, optional, default None
            Path to the output mesh file. If None, the mesh is not saved.
        element_order : int, optional, default 1
            Order of the finite elements. Must be an integer >= 1.
        additional_options : dict[str, Any] | None, optional, default None
            Additional Gmsh options as a dictionary of key-value pairs. See GMSH documentation
            http://gmsh.info/doc/texinfo/gmsh.html#Gmsh-options.
        renumber_nodes: str | None, default "RCMK"
            Renumbering strategy for the nodes. If None, no renumbering is performed.
        show_terminal_output: bool, default False
            If True, show Gmsh terminal output.
        show_gui: bool, default False
            If True, launch the Gmsh GUI.

        Raises
        ------
        ValueError
            If the element order is less than 1.
        """

        self.filename = PurePath(filename) if filename is not None else None

        if element_order < 1:
            raise ValueError("Element order must be an integer >= 1.")

        self.renumber_nodes = renumber_nodes

        self.show_gui = show_gui

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
        data: list[tuple[str, Any]] = [
            ("filename", self.filename),
            ("Launch GMSH GUI", self.show_gui),
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
class GmshContextManager:
    """Context manager for GMSH."""

    options: GmshOptions
    domain_tags: dict[DimName, list[Tag]] = field(
        default_factory=lambda: defaultdict(list)
    )

    def update_domain_tags(self: Self, domain_tags: dict[DimName, list[Tag]]) -> None:
        for key, val in domain_tags.items():
            self.domain_tags[key].extend(val)
        return None

    def __enter__(self: Self) -> Self:
        # Initialize the Gmsh API.
        gmsh.initialize()

        for key, val in self.options.key_val.items():
            gmsh.option.set_number(key, val)

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

        for (dim, name), tags in self.domain_tags.items():
            gmsh.model.add_physical_group(dim=dim, tags=tags, name=name)

        # Generate a mesh of the current model, up to dimension dim 2.
        gmsh.model.mesh.generate(2)

        if self.options.renumber_nodes is not None:
            # Renumber the nodes to improve the matrix bandwidth.
            old, new = gmsh.model.mesh.compute_renumbering(self.options.renumber_nodes)
            gmsh.model.mesh.renumber_nodes(old, new)

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


def open_msh_file(filename: PurePath | str) -> None:
    """Open a mesh file in GMSH.

    Parameters
    ----------
    filename : PurePath | str
        Path to the mesh file to be opened.
    """

    gmsh.initialize()
    gmsh.open(str(filename))
    gmsh.fltk.run()
    gmsh.finalize()

    return None
