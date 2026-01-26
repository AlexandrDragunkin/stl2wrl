# -*- coding: utf-8 -*-

# Converts STL file to VRML/WRL file.
# Avoids re-creating points if points of a facet overlap on the model.
# Object model is gray
# Bradley Boccuzzi 2020-2025

import argparse
import os
from collections import OrderedDict

try:
    import stl
    from stl import mesh
    import numpy

    NUMPY_STL_AVAILABLE = True
except ImportError:
    NUMPY_STL_AVAILABLE = False
    print(
        f"""Could not import numpy-stl. Conversion of STL binary files will not be available.
         NOTE: '26.01.2026' (DAR) Dependency (VENV37) pip install numpy-stl==3.1.2 -U --target <UserProto>/site-packages
         """
        # "
    )


def convert(stl_dir: str, wrl_dir: str, sf: float) -> None:
    """
    Converts an STL file to a WRL file.

    Args:
        stl_dir (str): Path to the input STL file
        wrl_dir (str): Path to the output WRL file
        sf (float): Scaling factor for the model
    """
    # Open our desired STL file
    stl_fd = open(stl_dir, 'r', encoding='UTF-8')
    wrl_fd = open(wrl_dir, 'w', encoding='UTF-8')
    
    # Create and populate model object
    temp_model = Model()
    parse_stl(stl_fd, temp_model, sf)

    vrml = generate_vrml(temp_model)
    
    wrl_fd.write(vrml)
    wrl_fd.flush()
    wrl_fd.close()
    # Close the STL input file descriptor
    stl_fd.close()


def parse_stl(file, model: 'Model', sf: float) -> None:
    """
    Parses an STL file and populates the model with facets.

    Args:
        file: File descriptor for the STL file
        model (Model): Model object to populate with facets
        sf (float): Scaling factor for the model
    """
    # Need to convert mm to in.
    _scaling_factor = float(sf)
    # Quick and dirty parsing
    for line in file:
        # solid<*whitespace>(name)
        if "solid " in line:
            model_name = line.split()[1]
            model.set_name(model_name)

        # Define facet
        if "facet normal" in line:
            # Obtain a facet surface normal
            surface_normal = line.split()[2:5]
            normal_x = surface_normal[0]
            normal_y = surface_normal[1]
            normal_z = surface_normal[2]
            temp_normal = Vertex(normal_x, normal_y, normal_z)

            # Clear 'outer loop' string with this readline statement below
            line = file.readline()
            # Obtain individual vertex from the file
            temp_vertex = []
            for i in range(3):
                line = file.readline()
                # Begin triangle loop
                # if "outer loop" in line:
                if "vertex" in line:
                    points = line.split()[1:4]
                    # TODO - How many decimal places are acceptable for VRML?
                    # "SFFloats and MFFloats are written to the VRML file in ISO C floating point format"
                    # - https://www.web3d.org/documents/specifications/14772/V2.0/part1/fieldsRef.html
                    # TODO - Command line scaling factor
                    point_x = '%0.7f' % (float(points[0]) / _scaling_factor)
                    point_y = '%0.7f' % (float(points[1]) / _scaling_factor)
                    point_z = '%0.7f' % (float(points[2]) / _scaling_factor)

                    vertex = Vertex(point_x, point_y, point_z)
                    temp_vertex.append(vertex)

            # Create individual triangle for the facet based on the three vertices obtained above
            temp_triangle = Triangle(temp_vertex[0], temp_vertex[1], temp_vertex[2])

            # Create a facet from surface normal and triangle
            temp_facet = Facet(temp_triangle, temp_normal)

            # Add facet to the model
            model.add_facet(temp_facet)


# Quick and dirty export
# Shape {
#   geometry IndexedFaceSet {
#       creaseAngle 0.50 coordIndex [index, index, index, index,...]
#
#       coord Coordinate {
#           point [
#               x y z, //index 0
#               x y z, //index 1
#               . . .,
#               x y z, //index N-1
#               x y z  //index N
#           ]
#       }
#   }
#
#   apperance properties
#
# }

# Default color of everything is gray
_default_texture = "Shape {\n\tappearance Appearance {material DEF MAT Material {\n\t\tambientIntensity 0.45\n\t\tdiffuseColor 0.8 0.8 0.7\n\t\tspecularColor 0.19 0.28 0.3\n\t\temissiveColor 0.0 0.0 0.0\n\t\tshininess 0.85\n\t\ttransparency 0.0\n\t\t}\n\t}\n}"

_string_template = "#VRML V2.0 utf8\n#Generated with stl2wrl - Bradley Boccuzzi 2020-2025\n\n<default_texture>\nShape {\n\tgeometry IndexedFaceSet {\n\t\tcreaseAngle 0.50 coordIndex [<index_list>]\n\t\tcoord Coordinate {\n\t\t\tpoint [\n<point_list>\n\t\t\t]\n\t\t}\n\t}\n\tappearance Appearance{material USE MAT}\n}"


# Generates VRML world file from model object
def generate_vrml(model: 'Model') -> str:
    """
    Generates VRML world file from model object.

    Args:
        model (Model): Model object containing facets

    Returns:
        str: VRML formatted string
    """
    # Index for each vertex
    index = 0
    index_list = []
    point_dict = OrderedDict()

    # Iterate through the model's facets...
    for facet in model.facets:
        for vertex in facet.triangle.vertices:
            # Create a point entry
            point = vertex.x + ' ' + vertex.y + ' ' + vertex.z

            # Add a new point to the point_list if it does not yet exist
            if point not in point_dict:
                point_dict[point] = index
                index_list.append(str(index))
                index += 1
            # ... Otherwise re-use an existing point based on its index
            else:
                index_list.append(str(point_dict[point]))
        # End facet
        index_list.append('-1')

    # Convert lists to strings for generating VRML file
    index_str = ', '.join(index_list)
    
    # Create a list of points in order of addition
    point_list = list(point_dict.keys())
    point_str = ', '.join(point_list)

    # Perform substitution in the template
    return_string = (
        _string_template.replace('<index_list>', index_str)
        .replace('<point_list>', point_str)
        .replace('<default_texture>', _default_texture)
    )

    return return_string


def validate_stl_path(stl_path: str) -> None:
    """
    Validates that stl_path is a full path to a real STL file with ASCII characters.

    Args:
        stl_path (str): Path to the STL file

    Raises:
        ValueError: If the path is not absolute or the file is not an STL ASCII file
        FileNotFoundError: If the file does not exist
    """
    # Check that stl_path is a full path
    if not os.path.isabs(stl_path):
        raise ValueError("stl_path must be a full (absolute) path")

    # Check file extension
    if not stl_path.lower().endswith('.stl'):
        raise ValueError("File must have .stl extension")

    # Check file existence
    if not os.path.exists(stl_path):
        raise FileNotFoundError(f"STL file not found: {stl_path}")

    # Check that the file is a text STL file (not binary)
    try:
        with open(stl_path, 'r', encoding='UTF-8') as test_fd:
            first_line = test_fd.readline()
            if not first_line.strip().startswith('solid'):
                raise ValueError("File is not a valid STL ASCII file")
    except UnicodeDecodeError:
        # If the file is binary and numpy-stl is available, convert it to ASCII
        if NUMPY_STL_AVAILABLE:
            try:
                # Load binary STL file
                binary_stl = mesh.Mesh.from_file(stl_path)

                # Save as ASCII STL
                ascii_path = stl_path + '_ascii.stl'
                binary_stl.save(ascii_path, mode=stl.Mode.ASCII)

                # Replace the original file with the ASCII version
                os.replace(ascii_path, stl_path)
            except Exception as e:
                raise ValueError(f"Failed to convert binary STL file: {e}")
        else:
            raise UnicodeDecodeError("File is not a text STL file (possibly binary)")


# A vertex in 3-dimensional space
class Vertex:
    """
    Represents a vertex in 3-dimensional space.

    Attributes:
        x (str): X coordinate
        y (str): Y coordinate
        z (str): Z coordinate
    """

    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z


# A triangle consisting of 3x 3-dimensional vertices
class Triangle:
    """
    Represents a triangle consisting of 3 vertices in 3-dimensional space.

    Attributes:
        vertices (list): List of 3 Vertex objects
    """

    def __init__(self, v1, v2, v3):
        self.vertices = [v1, v2, v3]


# Each facet holds three vertices (triangle) and a surface normal
class Facet:
    """
    Represents a facet which holds a triangle and a surface normal.

    Attributes:
        triangle (Triangle): Triangle object
        normal (Vertex): Surface normal as a Vertex object
    """

    def __init__(self, triangle, normal):
        self.triangle = triangle
        self.normal = normal


# Model object
# This class generally reflects the structure of an STL file, though could be changed later...
class Model:
    """
    Represents a 3D model made of facets.

    This class generally reflects the structure of an STL file.

    Attributes:
        name (str): Name of the model
        facets (list): List of Facet objects
    """

    def __init__(self):
        # Initialize a model made out of facets, etc...
        self.name = ""
        self.facets = []

    def add_facet(self, facet: 'Facet') -> None:
        """
        Adds a facet to the model.
        
        Args:
            facet (Facet): Facet object to add to the model
        """
        self.facets.append(facet)

    # TODO - should this be part of the parsing stream?
    def set_name(self, name: str) -> None:
        """
        Sets the name of the model.
        
        Args:
            name (str): Name to set for the model
        """
        self.name = name


def main() -> None:
    """
    Main function to convert STL file to WRL file.
    
    Command line arguments:
        stl (str): Path to the STL file
        scaling (float): Scaling factor for the model
    """
    # Configuring CLI argument parsing
    argparser = argparse.ArgumentParser()
    argparser.add_argument("stl")
    argparser.add_argument("scaling")
    args = argparser.parse_args()
    
    # Get STL path and create WRL file name
    stl_path = args.stl
    # Get scaling factor
    sf = args.scaling
    
    # Convert relative path to absolute path
    stl_path = os.path.abspath(stl_path)
    
    try:
        # Check that stl_path is the full path to a real STL file in ASCII characters
        validate_stl_path(stl_path)
    except ValueError as e:
        print(f"File {stl_path} is not an STL file: {e}")
        return
    except UnicodeDecodeError:
        print(f"File {stl_path} is not a text STL file")
        return
    except FileNotFoundError:
        print(f"File {stl_path} not found")
        return

    else:
        # Get WRL file name
        wrl_name = os.path.basename(stl_path).split('.')[0] + '.wrl'
        wrl_path = os.path.join(os.path.dirname(stl_path), wrl_name)

    # Perform conversion
    convert(stl_path, wrl_path, sf)

    print("Conversion complete!")
    # DONE


if __name__ == "__main__":
    main()
