""" GMSH as a context manager. """


from contextlib import AbstractContextManager
from dataclasses import dataclass
from pathlib import PurePath
from typing import NamedTuple, Optional, TypeAlias, Union

import gmsh

OptionalPathLike: TypeAlias = Union[None, str, PurePath]


@dataclass(frozen=True, slots=True)
class GmshContextManager(AbstractContextManager):
    """Context manager for GMSH"""

    # pylint: disable=too-many-instance-attributes

    element_order: int = 1

    terminal: bool = False
    gui: bool = False

    filename: Optional[PurePath] = None
    msh_file_version: Optional[float] = None
    save_width: Optional[int] = None
    save_height: Optional[int] = None
    save_compress: bool = False

    hide_model_Entities: bool = True

    def __enter__(self):
        # Initialize the Gmsh API.
        gmsh.initialize()

        if self.terminal:
            # Information is printed on the terminal.
            gmsh.option.setNumber("General.Terminal", 1)
        else:
            # Information is not printed on the terminal.
            gmsh.option.setNumber("General.Terminal", 0)

        # Copy meshing method transfinite when duplicating geometrical entities with
        # built-in geometry kernel.
        gmsh.option.setNumber("Geometry.CopyMeshingMethod", 1)

        # Use alternative transfinite arrangement when meshing 3-sided surfaces.
        gmsh.option.setNumber("Mesh.TransfiniteTri", 1)

        # Element order.
        if self.element_order >= 1:
            gmsh.option.setNumber("Mesh.ElementOrder", self.element_order)
        else:
            raise ValueError("Element order must be an integer greater or equal to 1.")

        # Number of smoothing steps applied to the final mesh.
        gmsh.option.setNumber("Mesh.Smoothing", 0)

        # Add a new model and set it as the current model.
        if self.filename is None:
            gmsh.model.add("mesh")
        else:
            gmsh.model.add(self.filename.stem)

    def __exit__(self, exc_type, exc_value, exc_tb):
        # Synchronize the built-in CAD representation with the current Gmsh model.
        gmsh.model.geo.synchronize()

        # Generate a mesh of the current model, up to dimension dim 2.
        gmsh.model.mesh.generate(2)

        _set_options_graphical(self.hide_model_Entities)

        if self.gui:
            # Create and run the FLTK graphical user interface.
            gmsh.fltk.run()

        if self.filename is not None:
            match self.filename.suffix:
                case ".msh":
                    _save_msh(self.filename, self.msh_file_version)
                case _:
                    _save_ext(
                        self.filename,
                        self.save_width,
                        self.save_height,
                        self.save_compress,
                    )

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
    """Set"""
    # Hide the small axes.
    gmsh.option.setNumber("General.SmallAxes", 0)

    # Hide the model entities of dimensions 0 and 1.
    if hide_model_Entities:
        gmsh.model.setVisibility(gmsh.model.getEntities(0), 0)
        gmsh.model.setVisibility(gmsh.model.getEntities(1), 0)

    # Display faces of surface mesh
    gmsh.option.setNumber("Mesh.SurfaceFaces", 1)

    # Mesh coloring by physical group
    gmsh.option.setNumber("Mesh.ColorCarousel", 2)

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


def _save_msh(filename: PurePath, msh_file_version: Optional[float]) -> None:
    """Save msh."""
    if msh_file_version is not None:
        # Version of the MSH file format to use.
        gmsh.option.setNumber("Mesh.MshFileVersion", msh_file_version)

    # Write a file. The export format is determined by the file extension.
    gmsh.write(str(filename))


def _save_ext(
    filename: PurePath,
    save_width: Optional[int],
    save_height: Optional[int],
    save_compress: bool,
) -> None:
    """Save ext."""
    if save_compress:
        # Compress PostScript/PDF output using zlib.
        gmsh.option.setNumber("Print.EpsCompress", 1)

    if save_width is not None:
        # Width of printed image.
        gmsh.option.setNumber("Print.Width", save_width)

    if save_height is not None:
        # Height of printed image.
        gmsh.option.setNumber("Print.Height", save_height)

    # Create the FLTK graphical user interface.
    gmsh.fltk.initialize()

    # Write a file. The export format is determined by the file extension.
    gmsh.write(str(filename))

    # Close the FLTK graphical user interface.
    gmsh.fltk.finalize()
