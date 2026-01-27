# Release Notes - stl2wrl v1.0.0

## What's New in This Version

### Major Improvements
- Full type annotations for all functions and methods
- Comprehensive English documentation for all functions and classes
- Improved error handling for file validation
- Support for both ASCII and binary STL files (using numpy-stl)
- All comments and error messages translated to English

### Compatibility and Dependencies
- Support for Python versions 3.7-3.12
- For working with binary STL files, you need to install:
  - numpy (version 1.19.0 or higher)
  - numpy-stl (version 3.1.2)
- For K3 environment (Python 3.7 32-bit Windows only):
  ```
  pip install numpy-stl==3.1.2 -U --target <UserProto>/site-packages
  ```

### Performance
Performance testing was conducted on a Windows 11 system with AMD Ryzen 7 5800H processor:

#### Small model (zynq_chip.stl - scale 0.01):
- Processing time: 1.38 seconds
- Command: `python stl2wrl.py demo\zynq_chip.stl 0.01`

#### Large model (440.stl - scale 1.0):
- File size: over 150 MB
- Processing time: 18.17 seconds
- Command: `python stl2wrl.py demo/440.stl 1`

### Usage
Converting STL file to WRL format:
```
# Scaling factor 2.54 for mm/inch conversion
# Output is stored in demos/zynq_chip.wrl, ready for import into KiCAD
./stl2wrl.py demos/zynq_chip.stl 2.54
```

### KiCAD Integration
- Support for import into KiCAD
- Compatibility with component footprints
- Support for large 3D models

### Project Contributors
- Original implementation: Bradley Boccuzzi
- Improvements: Alexander Dragunkin and SOURCECRAFT CODE assistant

### License
This project is distributed under the GNU General Public License v3.0.