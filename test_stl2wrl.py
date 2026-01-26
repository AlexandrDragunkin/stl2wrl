import unittest
import os
import tempfile
import numpy as np
import stl
from stl import mesh
from stl2wrl import Vertex, Triangle, Facet, Model, convert, parse_stl, generate_vrml, validate_stl_path

class TestSTL2WRL(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_stl_content = """solid test
  facet normal 0.0 0.0 1.0
    outer loop
      vertex 0.0 0.0 0.0
      vertex 1.0 0.0 0.0
      vertex 0.0 1.0 0.0
    endloop
  endfacet
  facet normal 0.0 0.0 -1.0
    outer loop
      vertex 0.0 0.0 0.0
      vertex 0.0 1.0 0.0
      vertex 1.0 0.0 0.0
    endloop
  endfacet
endsolid test"""

        self.test_stl_binary = None

    def tearDown(self):
        """Tear down test fixtures after each test method."""
        if self.test_stl_binary and os.path.exists(self.test_stl_binary):
            os.remove(self.test_stl_binary)

    def test_vertex_creation(self):
        """Test Vertex class creation and attributes."""
        vertex = Vertex('1.0', '2.0', '3.0')
        self.assertEqual(vertex.x, '1.0')
        self.assertEqual(vertex.y, '2.0')
        self.assertEqual(vertex.z, '3.0')

    def test_triangle_creation(self):
        """Test Triangle class creation and attributes."""
        v1 = Vertex('0.0', '0.0', '0.0')
        v2 = Vertex('1.0', '0.0', '0.0')
        v3 = Vertex('0.0', '1.0', '0.0')
        triangle = Triangle(v1, v2, v3)
        self.assertEqual(len(triangle.vertices), 3)
        self.assertEqual(triangle.vertices[0], v1)
        self.assertEqual(triangle.vertices[1], v2)
        self.assertEqual(triangle.vertices[2], v3)

    def test_facet_creation(self):
        """Test Facet class creation and attributes."""
        v1 = Vertex('0.0', '0.0', '0.0')
        v2 = Vertex('1.0', '0.0', '0.0')
        v3 = Vertex('0.0', '1.0', '0.0')
        triangle = Triangle(v1, v2, v3)
        normal = Vertex('0.0', '0.0', '1.0')
        facet = Facet(triangle, normal)
        self.assertEqual(facet.triangle, triangle)
        self.assertEqual(facet.normal, normal)

    def test_model_creation_and_facet_addition(self):
        """Test Model class creation and facet addition."""
        model = Model()
        self.assertEqual(model.name, "")
        self.assertEqual(model.facets, [])
        
        # Add a facet to the model
        v1 = Vertex('0.0', '0.0', '0.0')
        v2 = Vertex('1.0', '0.0', '0.0')
        v3 = Vertex('0.0', '1.0', '0.0')
        triangle = Triangle(v1, v2, v3)
        normal = Vertex('0.0', '0.0', '1.0')
        facet = Facet(triangle, normal)
        
        model.add_facet(facet)
        self.assertEqual(len(model.facets), 1)
        self.assertEqual(model.facets[0], facet)

    def test_model_name_setting(self):
        """Test Model name setting."""
        model = Model()
        model.set_name("TestModel")
        self.assertEqual(model.name, "TestModel")

    def test_stl_parsing(self):
        """Test parsing of STL file content."""
        model = Model()
        
        # Create a temporary file with test STL content
        with tempfile.NamedTemporaryFile(mode='w', suffix='.stl', delete=False) as f:
            f.write(self.test_stl_content)
            temp_stl_path = f.name
        
        try:
            with open(temp_stl_path, 'r') as stl_file:
                parse_stl(stl_file, model, 1.0)
            
            # Check that model was populated correctly
            self.assertEqual(model.name, "test")
            self.assertEqual(len(model.facets), 2)
            
            # Check first facet
            first_facet = model.facets[0]
            self.assertEqual(first_facet.normal.x, '0.0')
            self.assertEqual(first_facet.normal.y, '0.0')
            self.assertEqual(first_facet.normal.z, '1.0')
            
            # Check triangle vertices
            triangle = first_facet.triangle
            self.assertEqual(len(triangle.vertices), 3)
            self.assertEqual(triangle.vertices[0].x, '0.0000000')
            self.assertEqual(triangle.vertices[0].y, '0.0000000')
            self.assertEqual(triangle.vertices[0].z, '0.0000000')
            
        finally:
            os.remove(temp_stl_path)

    def test_vrml_generation(self):
        """Test VRML generation from model."""
        model = Model()
        model.set_name("TestModel")
        
        # Create and add facets
        v1 = Vertex('0.0000000', '0.0000000', '0.0000000')
        v2 = Vertex('1000.0000000', '0.0000000', '0.0000000')
        v3 = Vertex('0.0000000', '1000.0000000', '0.0000000')
        triangle = Triangle(v1, v2, v3)
        normal = Vertex('0.0', '0.0', '1.0')
        facet = Facet(triangle, normal)
        model.add_facet(facet)
        
        vrml_content = generate_vrml(model)
        
        # Check that VRML content contains expected elements
        self.assertIn("#VRML V2.0 utf8", vrml_content)
        self.assertIn("coordIndex [0, 1, 2, -1]", vrml_content)
        self.assertIn("0.0000000 0.0000000 0.0000000", vrml_content)
        self.assertIn("1000.0000000 0.0000000 0.0000000", vrml_content)
        self.assertIn("0.0000000 1000.0000000 0.0000000", vrml_content)

    def test_stl_to_wrl_conversion(self):
        """Test complete STL to WRL conversion."""
        # Create a temporary STL file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.stl', delete=False) as f:
            f.write(self.test_stl_content)
            temp_stl_path = f.name
        
        # Create output WRL file path
        temp_wrl_path = temp_stl_path.replace('.stl', '.wrl')
        
        try:
            # Perform conversion
            convert(temp_stl_path, temp_wrl_path, 1.0)
            
            # Check that WRL file was created
            self.assertTrue(os.path.exists(temp_wrl_path))
            
            # Check WRL file content
            with open(temp_wrl_path, 'r') as wrl_file:
                wrl_content = wrl_file.read()
            
            self.assertIn("#VRML V2.0 utf8", wrl_content)
            self.assertIn("coordIndex [0, 1, 2, 3, 4, 5, -1]", wrl_content)
            
        finally:
            # Clean up temporary files
            if os.path.exists(temp_stl_path):
                os.remove(temp_stl_path)
            if os.path.exists(temp_wrl_path):
                os.remove(temp_wrl_path)

    def test_validate_stl_path_valid(self):
        """Test validation of valid STL path."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.stl', delete=False) as f:
            f.write(self.test_stl_content)
            temp_stl_path = f.name
        
        try:
            # This should not raise an exception
            validate_stl_path(temp_stl_path)
        finally:
            os.remove(temp_stl_path)

    def test_validate_stl_path_invalid_extension(self):
        """Test validation of file with invalid extension."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write(self.test_stl_content)
            temp_txt_path = f.name
        
        try:
            with self.assertRaises(ValueError):
                validate_stl_path(temp_txt_path)
        finally:
            os.remove(temp_txt_path)

    def test_validate_stl_path_nonexistent(self):
        """Test validation of nonexistent file."""
        with self.assertRaises(FileNotFoundError):
            validate_stl_path("/nonexistent/file.stl")

    def test_scaling_factor(self):
        """Test that scaling factor is applied correctly."""
        model = Model()
        
        # Create a temporary file with test STL content
        with tempfile.NamedTemporaryFile(mode='w', suffix='.stl', delete=False) as f:
            f.write(self.test_stl_content)
            temp_stl_path = f.name
        
        try:
            with open(temp_stl_path, 'r') as stl_file:
                parse_stl(stl_file, model, 2.0)  # Scale by 2.0
            
            # Check that coordinates were scaled correctly
            first_facet = model.facets[0]
            triangle = first_facet.triangle
            # Original vertex was 0.0 0.0 0.0, scaled by 2.0 should still be 0.0000000
            self.assertEqual(triangle.vertices[0].x, '0.0000000')
            self.assertEqual(triangle.vertices[0].y, '0.0000000')
            self.assertEqual(triangle.vertices[0].z, '0.0000000')
            
            # Original vertex was 1.0 0.0 0.0, scaled by 2.0 should be 0.5000000
            self.assertEqual(triangle.vertices[1].x, '0.5000000')
            self.assertEqual(triangle.vertices[1].y, '0.0000000')
            self.assertEqual(triangle.vertices[1].z, '0.0000000')
            
        finally:
            os.remove(temp_stl_path)

    @unittest.skipIf(not hasattr(mesh, 'Mesh'), "numpy-stl not available")
    def test_binary_stl_conversion(self):
        """Test conversion of binary STL file."""
        # Create a binary STL file using numpy-stl
        data = np.zeros(1, dtype=mesh.Mesh.dtype)
        data['vectors'][0] = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]])
        test_mesh = mesh.Mesh(data)
        
        # Save as binary STL
        with tempfile.NamedTemporaryFile(suffix='.stl', delete=False) as f:
            test_mesh.save(f.name, mode=stl.Mode.BINARY)
            self.test_stl_binary = f.name
        
        # Test validation of binary STL
        # This should not raise an exception if numpy-stl is available
        try:
            validate_stl_path(self.test_stl_binary)
        except UnicodeDecodeError:
            # This is expected for binary files when numpy-stl is not available
            self.fail("Binary STL validation failed unexpectedly")

if __name__ == '__main__':
    unittest.main()