import gdstk
import random
import math
min_metal6_width = 1.7 #1.64  # Minimum Metal6 width in microns
min_metal6_spacing = 1.7 #1.64 


length = 8  # Reduced from 8
avg_width = 4  # Reduced from 3
gap = 1  # Reduced from 1

sizeX = 16
sizeY = 16



x_width = [6,6,2,2,6,6,6,2,6,2,6,2,6,2,2,6]
y_width = [6,6,2,2,6,6,6,2,6,2,6,2,6,2,2,6]

structure = [[random.randint(0, 1) for _ in range(sizeY)] for _ in range(sizeX)]


# The GDSII file is called a library, which contains multiple cells.
lib = gdstk.Library()

# Geometry must be placed in cells.
cell = lib.new_cell("my_logo")

# Increase the grid size to create more TopMetal1 coverage
for i in range(sizeX):  # Reduced from 10
    start_x = 0
    start_stub = (length-y_width[0]) /2 - min_metal6_spacing
    print("start_stub", y_width[0])
  
    for j in range(sizeY):  # Reduced from 10
        if j>0 and structure[i][j] == 1 and structure[i][j-1] == 0: 
            start_x = j
            start_stub = (length-y_width[j-1]) /2 - min_metal6_spacing
            

        if j>0 and structure[i][j] == 0 and structure[i][j-1] == 1 or j==len(structure[i])-1 and structure[i][j] == 1:
            end_x = j-1
            end_stub = (length-y_width[j]) /2 - min_metal6_spacing
            if j==len(structure[i])-1 and structure[i][j] == 1:
                end_x = j
                

          
            vert_width = x_width[i]
            
            block_length = length * (end_x-start_x+1)
           

            # Create the geometry (a single rectangle) and add it to the cell.
            tx = start_x*(length)
            ty = i*(length)
        
            #low_rect = gdstk.rectangle((tx+(length-horz_width)/2, ty), (tx+(length-horz_width)/2+horz_width, ty+length), layer=126)  # TopMetal1
            rect = gdstk.rectangle((tx-start_stub, ty+(length-vert_width)/2), (tx+block_length+end_stub, ty+(length-vert_width)/2+vert_width), layer=126)  # TopMetal1
            cell.add(rect)

##invert for easier usage
structure = [[1 - cell for cell in row] for row in structure]


# Increase the grid size to create more TopMetal1 coverage
for i in range(sizeY):  # Reduced from 10
    start_y = 0
    start_stub = (length-x_width[0]) /2 - min_metal6_spacing
  
    for j in range(sizeX):  # Reduced from 10
        #print("j", j, "i", i, structure[j][i])
        if j>0 and structure[j][i] == 1 and structure[j-1][i] == 0: 
            start_y = j
            start_stub = (length-x_width[j-1]) /2 - min_metal6_spacing

        if j>0 and structure[j][i] == 0 and structure[j-1][i] == 1 or j==len(structure)-1 and structure[j][i] == 1:
            end_y = j-1
            end_stub = (length-x_width[j]) /2 - min_metal6_spacing
            if j==len(structure)-1 and structure[j][i] == 1:
                end_y = j
                
        
            horz_width = y_width[i]
            
            block_length = length * (end_y-start_y+1)
            

            # Create the geometry (a single rectangle) and add it to the cell.
            ty = start_y*(length)
            tx = i*(length)
        
            #low_rect = gdstk.rectangle((tx+(length-horz_width)/2, ty), (tx+(length-horz_width)/2+horz_width, ty+length), layer=126)  # TopMetal1
            #rect = gdstk.rectangle((tx, ty+(length-vert_width)/2), (tx+block_length, ty+(length-vert_width)/2+vert_width), layer=126)  # TopMetal1
            rect = gdstk.rectangle((tx+(length-horz_width)/2, ty-start_stub), (tx+(length-horz_width)/2+horz_width, ty+block_length+end_stub), layer=126) 
            cell.add(rect)

        
            
        


# Add PR boundary (placement and routing boundary)
# Layer 189, datatype 4 for IHP SG13G2 PR boundary
pr_boundary = gdstk.rectangle((0, 0), (30, 30), layer=189, datatype=4)
cell.add(pr_boundary)

# Add comprehensive Active fillers (layer 1) to meet minimum density requirements
# Use consistent 2x2um fillers to ensure AFil.a compliance (1um < width < 5um)
active_dist = 1.5
active_size = 3.0 
overhang = 0.18

for i in range(28):
    for j in range(28):
        tx = i * (active_size + active_dist) + 2
        ty = j * (active_size + active_dist) + 2

       
        rect1 = gdstk.rectangle((tx, ty), (tx+active_size, ty+active_size), layer=1, datatype=22)
        cell.add(rect1)
        
        poly_rect = gdstk.rectangle((tx-overhang, ty-overhang), (tx+active_size+overhang, ty+active_size+overhang), layer=5, datatype=22)
        cell.add(poly_rect)

        




# Generate LEF file
def write_lef_file(filename, cell_name, cell_bounds, pins):
    """Write a LEF file for the cell"""
    with open(filename, 'w') as f:
        f.write("# LEF file generated for {}\n".format(cell_name))
        f.write("VERSION 5.8 ;\n")
        f.write("NAMESCASESENSITIVE ON ;\n")
        f.write("DIVIDERCHAR \"/\" ;\n")
        f.write("BUSBITCHARS \"[]\" ;\n")
        f.write("UNITS\n")
        f.write("   DATABASE MICRONS 1000 ;\n")
        f.write("END UNITS\n\n")
        
        # Define the cell
        f.write("MACRO {}\n".format(cell_name))
        f.write("   CLASS BLOCK ;\n")
        f.write("   FOREIGN {} 0 0 ;\n".format(cell_name))
        f.write("   SIZE {:.3f} BY {:.3f} ;\n".format(cell_bounds[2] - cell_bounds[0], cell_bounds[3] - cell_bounds[1]))
        f.write("   SYMMETRY X Y ;\n")
        
        # No pins - pure blackbox module
        # No OBS section needed for pure artwork on TopMetal1
        
        f.write("END {}\n".format(cell_name))

# Calculate cell bounds (back to original size)
cell_width = sizeY*length  # 32 microns
cell_height = sizeX*length  # 32 microns
cell_bounds = (0, 0, cell_width, cell_height)

# Write LEF file
write_lef_file("../macros/my_logo.lef", "my_logo", cell_bounds, [])

# Save the library in a GDSII or OASIS file.
lib.write_gds("../macros/my_logo.gds")

# Optionally, save an image of the cell as SVG.
cell.write_svg("../macros/my_logo.svg")