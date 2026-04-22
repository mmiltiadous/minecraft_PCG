import logging
import random
from random import randint
import numpy as np
from numpy import array, var
from termcolor import colored
from gdpc import Block, Editor
from gdpc import geometry as geo
from gdpc import minecraft_tools as mt
from gdpc import editor_tools as et
from gdpc import lookup as lu
import sys
from glm import ivec2, ivec3
from gdpc import __url__, Editor, Block, geometry
from gdpc.exceptions import InterfaceConnectionError, BuildAreaNotSetError
from gdpc.vector_tools import Y, addY, dropY, line3D, circle, fittingCylinder
from glm import ivec2, ivec3
from gdpc import __url__, Editor, Block
from gdpc.exceptions import InterfaceConnectionError, BuildAreaNotSetError
from gdpc.vector_tools import addY, dropY
from gdpc.minecraft_tools import signBlock
from gdpc.editor_tools import placeContainerBlock
from gdpc.geometry import placeBox, placeCuboid
from glm import ivec2, ivec3

from gdpc import __url__, Editor, Block, Box, Transform
from gdpc.exceptions import InterfaceConnectionError, BuildAreaNotSetError
from gdpc.vector_tools import addY, dropY
from gdpc.transform import rotatedBoxTransform, flippedBoxTransform
from gdpc.geometry import placeBox, placeCheckeredBox
import matplotlib.pyplot as plt

from gdpc.vector_tools import Vec2iLike, Vec3iLike, Rect, Box, cylinder, fittingCylinder, fittingEllipsoid, fittingSphere, line3D, lineSequence3D, ellipsoid
from gdpc.block import Block, transformedBlockOrPalette
from gdpc.editor import Editor

from gdpc import interface

# The minimum build area size in the XZ-plane for this example.
min_size_build_area = ivec2(30, 30)
# Create an editor object.
# The Editor class provides a high-level interface to interact with the Minecraft world.
myeditor= Editor(buffering=True)
myeditor.buffering = True
myeditor.bufferLimit = 1024
myeditor.caching = True
myeditor.cacheLimit = 8192
# myeditor.flushBuffer()
# Check if the editor can connect to the GDMC HTTP interface.
try:
    myeditor.checkConnection()
except InterfaceConnectionError:
    print(
        f"Error: Could not connect to the GDMC HTTP interface at {myeditor.host}!\n"
        "To use GDPC, you need to use a \"backend\" that provides the GDMC HTTP interface.\n"
        "For example, by running Minecraft with the GDMC HTTP mod installed.\n"
        f"See {__url__}/README.md for more information."
    )
    sys.exit(1)
# Get the build area.
try:
    mybuildArea = myeditor.getBuildArea() #get the buildarea
    mybuildRect = mybuildArea.toRect()
except BuildAreaNotSetError:
    print(
        "Error: failed to get the build area!\n"
        "Make sure to set the build area with the /setbuildarea command in-game.\n"
        "For example: /setbuildarea ~0 0 ~0 ~64 200 ~64"
    )
    sys.exit(1)
FIRSTX, FIRSTY, FIRSTZ = mybuildArea.begin
ENDX, ENDY, ENDZ = mybuildArea.last
# Check if the build area is large enough in the XZ-plane.
if any(dropY(mybuildArea.size) <min_size_build_area):
    print(
        "Error: the build area is too small for this example!\n"
        f"It should be at least {tuple(min_size_build_area)} blocks large in the XZ-plane."
    )
    sys.exit(1)
# Get a world slice
print("Loading world slice...")
myworldSlice = myeditor.loadWorldSlice(mybuildArea.toRect(),cache=True)
print("World slice loaded!")
#print buld area details
print('Build Area details:...')
print('Build area',mybuildArea)
print('FIRSTX, FIRSTY, FIRSTZ', FIRSTX, FIRSTY, FIRSTZ)
print('LASTX, LASTY, LASTZ ',ENDX, ENDY, ENDZ )


def createborder():
    #create the 100*100 border for building area
    heights = myworldSlice.heightmaps["MOTION_BLOCKING_NO_LEAVES"]
    heights_array = np.array(heights)
    
    diffx=np.abs(ENDX-FIRSTX)
    diffz=np.abs(ENDZ-FIRSTZ)
    heights_list = [
        heights_array[0:diffx, 0].tolist(),
        heights_array[0, 0:diffz].tolist(),
        heights_array[diffx, 0:diffz].tolist(),
        heights_array[0:diffx, diffz].tolist()
    ]
    
    min_height_border = min(np.min(heights_list[0]),np.min(heights_list[1]),np.min(heights_list[2]),np.min(heights_list[3]))
    max_height_border = max(np.max(heights_list[0]),np.max(heights_list[1]),np.max(heights_list[2]),np.max(heights_list[3]))
    # Print the results
    print("Minimum height within the build area:", min_height_border)
    # for i in range(7):
    #     geometry.placeRectOutline(myeditor, mybuildArea.toRect(), min_height_border+i, Block("red_concrete"))
    geometry.placeCuboidWireframe(myeditor, (FIRSTX,min_height_border,FIRSTZ),(ENDX,max_height_border,ENDZ), Block("red_concrete"))
    # i=0
    # while min_height_border+i!=max_height_border:
    #     geometry.placeRectOutline(myeditor, mybuildArea.toRect(), min_height_border+i, Block("red_concrete"))
    #     i=i+1

def chooserandom(kind):
    #choose random objects and materials
    cubes = None
    #outside
    if kind == 'pillar':
        cubes = list(lu.QUARTZES)
    elif kind == "ground":
        cubes = list(lu.OVERWORLD_BRICKS)
    elif kind== 'dirt':
        cubes = list(lu.SPREADING_DIRTS)
    elif kind == 'berriers':
        cubes = list(lu.BARRIERS)
    elif kind == "walls":
        cubes = list(lu.OVERWORLD_BRICKS)
    elif kind == 'roof':
        cubes = list(lu.PLANKS)
    elif kind=='stone':
        cubes= list(lu.STONES)
    elif kind == "entry":
        cubes=list(lu.DOORS)
    elif kind == "outentry":
        cubes=list(lu.GATES)
    elif kind=='window':
        cubes=list(lu.GLASSES)
    #inside
    elif kind == "carpet":
        cubes = list(lu.CARPETS)
    elif kind == 'lights':
        cubes = list(lu.LANTERNS)
    elif kind == "bed":
        cubes = list(lu.BEDS)
    i = random.randint(0, len(cubes) - 1)    
    return cubes[i]


def createoutsite(BestX,BestZ,ground_height1,ground_height2,ground_height3,ground_height4,max_height,length,height):
    pillar = chooserandom ("pillar")
    ground = chooserandom("ground")
    wall = chooserandom("walls")
    entry = chooserandom("entry")
    outentry = chooserandom("outentry")
    dirt = chooserandom('dirt')
    stone=chooserandom('stone')
    roof=chooserandom('roof')
    window=chooserandom('window')
    berriers = chooserandom('berriers')
    # crops_flowers = chooserandom('crops/flowers')
    y = max_height

    # Choose a random side for the garden
    garden_side = random.choice(["1", "2", "3", "4"])
    
    #choose random area for house between 10 to 30
    # Build the random*random house
    length_out= np.round(length/2)
    # ground_height = y-5
    names = ["Alice", "Bob", "Charlie", "David", "Eve", "Frank", "Grace", "Hannah", "Ian", "Jasmine"]
    #choose random person to own the house
    random_name = random.choice(names)
    #place pillars on four edges
    # geo.placeFittingCylinder(myeditor, (BestX - 1 - 2,  ground_height, BestZ - 1 - 2), (BestX - 1 - 2+2, ground_height+3, BestZ - 1 - 2+2), Block(pillar))
    # geo.placeFittingCylinder(myeditor, (BestX + length + 1 + 3-2,  ground_height, BestZ + length+1 + 3-2), (BestX + length + 1 + 3, ground_height+3, BestZ + length+1 + 3), Block(pillar))
    # geo.placeFittingCylinder(myeditor, (BestX + length + 1 + 3-2,  ground_height, BestZ - 1 - 2), (BestX + length + 1 + 3, ground_height+3, BestZ - 1 - 2+2), Block(pillar))
    # geo.placeFittingCylinder(myeditor, (BestX - 1 - 2,  ground_height, BestZ + length+1 + 3-2), (BestX - 1 - 2+2, ground_height+3, BestZ + length+1 + 3), Block(pillar))
    #1
    height2=0#uncoment
    #height2=int(placeFittingCylinder(myeditor, (BestX - 1 - 2,  ground_height1, BestZ - 1 - 2), (BestX - 1 - 2+2, max_height-1, BestZ - 1 - 2+2), Block(pillar))/5)
    geo.placeFittingCylinder(myeditor, (BestX - 1 - 2,  ground_height1+height2 , BestZ - 1 - 2), (BestX - 1 - 2+2, max_height-1, BestZ - 1 - 2+2), Block(pillar))
    #2
    # height2=int(placeFittingCylinder(myeditor, (BestX + length + 1 + 3-2,  ground_height2+height2, BestZ + length+1 + 3-2), (BestX + length + 1 + 3, max_height-1, BestZ + length+1 + 3), Block(pillar))/5)
    geo.placeFittingCylinder(myeditor, (BestX + length + 1 + 3-2,  ground_height2, BestZ + length+1 + 3-2), (BestX + length + 1 + 3, max_height-1, BestZ + length+1 + 3), Block(pillar))
    #3
    # height2=int(placeFittingCylinder(myeditor, (BestX + length + 1 + 3-2,  ground_height3, BestZ - 1 - 2), (BestX + length + 1 + 3, max_height-1, BestZ - 1 - 2+2), Block(pillar))/5)
    geo.placeFittingCylinder(myeditor, (BestX + length + 1 + 3-2,  ground_height3+height2, BestZ - 1 - 2), (BestX + length + 1 + 3, max_height-1, BestZ - 1 - 2+2), Block(pillar))
    #4
    # height2=int(placeFittingCylinder(myeditor, (BestX - 1 - 2,  ground_height4, BestZ + length+1 + 3-2), (BestX - 1 - 2+2, max_height-1, BestZ + length+1 + 3), Block(pillar))/5)
    geo.placeFittingCylinder(myeditor, (BestX - 1 - 2,  ground_height4+height2, BestZ + length+1 + 3-2), (BestX - 1 - 2+2, max_height-1, BestZ + length+1 + 3), Block(pillar))
    # Place the ground
    geo.placeCuboid(myeditor, (BestX - 1 - 2, y - 1, BestZ - 1 - 2), (BestX + length + 1 + 3, y - 1, BestZ + length+1 + 3), Block(ground))
    # Place outside area 
    chest = Block("chest", data='{Items: [{Slot: 13b, id: "apple", Count: 1b}]}')
    chest_yes_no = random.choice([0,1])
    sign = signBlock(
    "spruce", wall=False, rotation=random.choice([1,2,3,4]),
    line2="This is the home", line3=f" of {random_name}", color="orange", isGlowing=True
    )
    if garden_side == "1":
        geo.placeCuboid(myeditor, (BestX-2, y - 1, BestZ + length + 1), (BestX - 1 - length_out, y - 1, BestZ + length + 1 - length_out), Block(stone))
        geo.placeCuboid(myeditor, (BestX-2, y , BestZ + length + 1), (BestX - 1 - length_out, y , BestZ + length + 1 - length_out), Block(dirt))
        geo.placeCuboid(myeditor, (BestX-3, y + 1 , BestZ + length + 1), (BestX-3, y + 1, BestZ + length + 1), sign)          
    elif garden_side == "2":
        geo.placeCuboid(myeditor, (BestX - 1, y - 1, BestZ-2), (BestX  + length_out, y - 1, BestZ - 1- length_out ), Block(ground))
        geo.placeCuboid(myeditor, (BestX - 1, y , BestZ-2), (BestX  + length_out, y , BestZ - 1- length_out ), Block(dirt))
        geo.placeCuboid(myeditor, (BestX - 1, y+1 , BestZ-3), (BestX - 1, y +1, BestZ-3), sign)
        # geo.placeCuboid(myeditor, (BestX - 1, y+1 , BestZ-5), (BestX - 1, y +1, BestZ-5), crops_flowers)
    elif garden_side == "3":
        geo.placeCuboid(myeditor, (BestX  + length +3, y - 1, BestZ ), (BestX + length + length_out +2, y - 1, BestZ  + length_out), Block(ground))
        geo.placeCuboid(myeditor, (BestX  + length +3, y , BestZ ), (BestX + length + length_out +2, y , BestZ  + length_out), Block(dirt))
        geo.placeCuboid(myeditor, (BestX  + length +4, y +1, BestZ ), (BestX  + length +4, y +1, BestZ ), sign) 
        # geo.placeCuboid(myeditor, (BestX  + length +6, y +1, BestZ ), (BestX  + length +6, y +1, BestZ ), crops_flowers)
    elif garden_side == "4":
        geo.placeCuboid(myeditor, (BestX - 1, y - 1, BestZ + length + 1 +2 ), (BestX - 1 + length_out, y - 1, BestZ + length + 1 + length_out +1), Block(ground))
        geo.placeCuboid(myeditor, (BestX - 1, y , BestZ + length + 1 +2 ), (BestX - 1 + length_out, y , BestZ + length + 1 + length_out +1), Block(dirt))
        geo.placeCuboid(myeditor, (BestX - 1, y +1, BestZ + length + 1 +3 ), (BestX - 1, y+1 , BestZ + length + 1 +3 ), sign)
        # geo.placeCuboid(myeditor, (BestX - 1, y +1, BestZ + length + 1 +5 ), (BestX - 1, y+1 , BestZ + length + 1 +5 ), crops_flowers)
    if chest_yes_no==1:
        if garden_side == "1": 
            geo.placeCuboid(myeditor, (BestX - 1 - length_out, y+1 , BestZ + length + 1 - length_out), (BestX - 1 - length_out, y+1 , BestZ + length + 1 - length_out), chest)        
        elif garden_side == "2":
            geo.placeCuboid(myeditor, (BestX  + length_out, y+1 , BestZ - 1- length_out ), (BestX  + length_out, y +1, BestZ - 1- length_out ), chest)
        elif garden_side == "3":
            geo.placeCuboid(myeditor, (BestX + length + length_out +2, y+1 , BestZ  + length_out), (BestX + length + length_out +2, y+1 , BestZ  + length_out), chest) 
        elif garden_side == "4":
            geo.placeCuboid(myeditor, (BestX - 1 + length_out, y +1, BestZ + length + 1 + length_out +1), (BestX - 1 + length_out, y+1 , BestZ + length + 1 + length_out +1), chest) 
    #Place berriers
    geo.placeCuboidWireframe(myeditor, (BestX - 1 - 1, y, BestZ - 1 - 1), (BestX + length + 1 + 2, y, BestZ + length+1 + 2), Block(berriers)) 
    #Place walls         
    geo.placeCuboid(myeditor, (BestX , y - 1, BestZ ), (BestX , y - 1 + height, BestZ + length ), Block(wall))
    geo.placeCuboid(myeditor, (BestX , y - 1, BestZ ), (BestX + length , y - 1 + height, BestZ ), Block(wall))
    geo.placeCuboid(myeditor, (BestX + length + 1, y - 1, BestZ ), (BestX + length + 1, y - 1 + height, BestZ + length), Block(wall))
    geo.placeCuboid(myeditor, (BestX + length + 1, y - 1, BestZ + length+1), (BestX , y - 1 + height, BestZ + length+1), Block(wall))  
    # place roof
    i=0
    while not (BestX + i == BestX + length + 1 - i and BestZ + i == BestZ + length + 1 - i):
        if BestX + i -1== BestX + length + 1 - i and BestZ + i -1== BestZ + length + 1 - i:
            break
        else:
            geo.placeCuboid(myeditor, (BestX + i, y - 1 + height +i, BestZ+i), (BestX + length + 1-i, y - 1 + height +i, BestZ + length+1-i ), Block(roof))
            i=i+1    
    #Place Entries
    place=random.choice([1,2,3])
    geo.placeCuboid(myeditor, (BestX  ,  y, BestZ+place ), (BestX  ,  y, BestZ + place), Block(entry, {"facing": "east"}))
    place=random.choice([1,2,3])
    geo.placeCuboid(myeditor, (BestX -2 ,  y, BestZ+place ), (BestX -2 ,  y, BestZ + place), Block(outentry, {"facing": "east"}))
    #Place Window/s
    number_of_windows= random.choice(["1", "2", "3", "4"])
    if number_of_windows=='1' or number_of_windows=='2' or number_of_windows=='3' or number_of_windows=='4':
        geo.placeCuboid(myeditor, (BestX +3, y - 1+3, BestZ ), (BestX + length-3 , y - 1 + height-3, BestZ ), Block(window))
    if number_of_windows=='2' or number_of_windows=='3' or number_of_windows=='4' :
        geo.placeCuboid(myeditor, (BestX , y - 1+3, BestZ+3 ), (BestX , y - 1-3 + height, BestZ + length-3 ), Block(window))    
    if number_of_windows=='3' or number_of_windows=='4':
        geo.placeCuboid(myeditor, (BestX + length + 1, y - 1+3, BestZ+3 ), (BestX + length + 1, y - 1 + height-3, BestZ + length-3), Block(window))
    if number_of_windows=='4':
        geo.placeCuboid(myeditor, (BestX + length + 1-3, y - 1+3, BestZ + length+1), (BestX +3, y - 1 + height-3, BestZ + length+1), Block(window))  



def decorateinside(BestX, BestY, BestZ,length):
    carpet=chooserandom('carpet')
    lights=chooserandom('lights')
    bed=chooserandom('bed')
    carpet_size=random.choice([3,4,5,6])
    geo.placeCuboid(myeditor, (BestX - 1 - 2 + carpet_size, BestY , BestZ - 1 - 2+carpet_size), (BestX + length + 1 + 3-carpet_size, BestY , BestZ + length+1 + 3-carpet_size), Block(carpet))
    #Assign the positions
    position01=(BestX + length -1 , BestY , BestZ + length-4 )
    position02=(BestX + length -5 , BestY , BestZ + length-4 )
    position11=(BestX + length -1 , BestY , BestZ + length-4 +2)
    position12=(BestX + length -5, BestY , BestZ + length-4 +2)
    position21=(BestX + length -1 , BestY , BestZ + length-4 +4 )
    position20=(BestX + length -3 , BestY , BestZ + length-4 +4)
    position22=(BestX + length -5 , BestY , BestZ + length-4 +4)
    #again same positions to keep the originals unchainged since we switch them 
    position001=(BestX + length -1 , BestY , BestZ + length-4 )
    position002=(BestX + length -5 , BestY , BestZ + length-4 )
    position011=(BestX + length -1 , BestY , BestZ + length-4 +2)
    position012=(BestX + length -5, BestY , BestZ + length-4 +2)
    position021=(BestX + length -1 , BestY , BestZ + length-4 +4 )
    position020=(BestX + length -3 , BestY , BestZ + length-4 +4)
    position022=(BestX + length -5 , BestY , BestZ + length-4 +4)

    #position of lamb always according to position of teracotta
    position_lamp= tuple(x + y for x, y in zip(position01, (0,1,0)))

    #randomly switch positions
    choice=random.choice([0,1])
    if choice==1:
        position001=random.choice([position01,position02])
        if position001==position02:
            position002=position01
        else:
            position002=position02
    choice=random.choice([0,1])
    if choice==1:
        position012=random.choice([position12,position21])
        if position012==position21:
            position021=position12
        else:
            position021=position21
    choice=random.choice([0,1])
    if choice==1:
        position011=random.choice([position11,position22])
        if position011==position22:
            position022=position11
        else:
            position022=position22

    position_lamp= tuple(x + y for x, y in zip(position001, (0,1,0)))
    
    #place random decoration
    geo.placeCuboid(myeditor, position001,position001, Block(random.choice(list(lu. GLAZED_TERRACOTTAS))))
    geo.placeCuboid(myeditor, position_lamp,position_lamp, Block(lights))
    geo.placeCuboid(myeditor, (BestX + length -3 , BestY , BestZ + length-4 ),(BestX + length -3 , BestY , BestZ + length-4 ), Block(bed))
    geo.placeCuboid(myeditor, position002,position002, Block(random.choice(list(lu.BANNERS))))

    geo.placeCuboid(myeditor, position011,position011, Block(random.choice(list(lu. USABLE_BLOCKS))))
    geo.placeCuboid(myeditor,  position012,position012, Block(random.choice(list(lu.TORCHES))))

    geo.placeCuboid(myeditor, position021,position021, Block(random.choice(list(lu.MAP_TRANSPARENT))))
    geo.placeCuboid(myeditor, position022,position022, Block(random.choice(list(lu.JOB_SITE_BLOCKS))))
    geo.placeCuboid(myeditor, position20,position20, Block(random.choice(list(lu.CHESTS))))

def createstairs(X_stairs,Z_stairs,max_height,min_h,BestX,BestZ):
    #placed at the start of Building Area
    
    buildRect = mybuildArea.toRect()
    transform = Transform((1,2,3), 1, (True, False, False))
    # print(f"1: {transform}")
    translation = Transform((1,1,0))
    vec = ivec3(1,2,3)
    result = translation * vec
    rotate1 = Transform(rotation=1)
    rotate2 = Transform(rotation=2)
    rotate3 = Transform(rotation=3)
    vec = ivec3(1,2,3)
    rotated1 = rotate1 * vec
    rotated2 = rotate2 * vec
    rotated3 = rotate3 * vec
    flipX  = Transform(flip=(True, False, False))
    flipXY = Transform(flip=(True, True, False))
    vec = ivec3(1,2,3)
    flippedX  = flipX  * vec
    flippedXY = flipXY * vec
    transform1 = Transform(translation=(1,1,1)) @ Transform(rotation=1) # Rotate first, then translate
    transform2 = Transform(rotation=1) @ Transform(translation=(1,1,1)) # Translate first, then rotate
    myeditor.transform @= Transform(translation=addY(buildRect.offset))
    # Now, when you place a block at (1,100,1), you place it at the *local* (1,100,1) position. If the
    # build area started at X=10, Z=20, this would be the global position (11,100,21).
    position = (X_stairs-FIRSTX,min_h,Z_stairs-FIRSTZ)
    # print(f"\nBuild area XZ offset: {tuple(buildRect.offset)}")
    print(f"Placing a stairs at global position {tuple(myeditor.transform * position)}")
    # Define a staircase function.
    def buildStaircase(editor):
        """Build a 3x3x3 staircase."""
        for z in range(3):
            for y in range(z):
                placeBox(editor, Box(ivec3(0,y,z), ivec3(3,1,1)), Block("cobblestone"))
            placeBox(editor, Box(ivec3(0,z,z), ivec3(3,1,1)), Block("oak_stairs", {"facing": "south"}))

    # Build the staircase at local coordinates (5,100,1).
    # Notice how we're stacking two "local coordinate systems" on top of each other.
    A=X_stairs-FIRSTX
    B=min_h
    C=Z_stairs-FIRSTZ
    transform = Transform((A,B,C))
    myeditor.transform.push(transform) # Transform.push() is equivalent to @=
    buildStaircase(myeditor)
    myeditor.transform.pop(transform)  # Transform.pop() does the opposite of Transform.push()
    while B<=max_height-2:
        geo.placeCuboid(myeditor, (A+2, B+2,C+5), (A, B+2, C+3),  Block("cobblestone"))
        if B+2>=max_height-2:
            break
        with myeditor.pushTransform(Transform((A+3,B+3,C+5), rotation=3)):
            buildStaircase(myeditor)
        geo.placeCuboid(myeditor, (A+8, B+5, C+5), (A+6, B+5,C+3),  Block("cobblestone"))
        if B+5>=max_height-2:
            break
        with myeditor.pushTransform(Transform((A+6,B+6,C+2), flip=(False, False, True))):
            buildStaircase(myeditor)
        geo.placeCuboid(myeditor, (A+8, B+8, C-1), (A+6, B+8, C-3),  Block("cobblestone"))
        if B+8>=max_height-2:
            break
        with myeditor.pushTransform(Transform((A+5,B+9,C-3), rotation=1)):
            buildStaircase(myeditor)
        geo.placeCuboid(myeditor, (A+2, B+11,C-1), (A, B+11, C-3),  Block("cobblestone"))
        if B+11>=max_height-2:
            
            break
        with myeditor.pushTransform(Transform((A,B+12,C))):
            buildStaircase(myeditor)
        A=A
        B=B+12
        C=C

        
        #geo.placeCuboid(myeditor, (A+2, B+11,C-1), (A, B+11, C-3),  Block("cobblestone"))


        # geo.placeCuboid(BestX - 1 - 2, max_height- 1, BestZ - 1 - 2), (BestX + length + 1 + 3,  max_height - 1, BestZ + length+1 + 3)
    

def find_equal_submatrices(matrixA, matrixB,length):
    equal_indices_all = []
    equal_indices_3 = []
    equal_indices_2 = []
    equal_indices_1 = []
    rows, cols = matrixA.shape
    for i in range(3, rows - length - 4):
        for j in range(3, cols - length - 4):
            submatrixA = matrixA[i-3:i-1, j-3:j-1]
            submatrixB = matrixB[i-3:i-1, j-3:j-1]

            submatrixC = matrixA[i+ length +2:i + length + 4,j + length+2:j+length+4]
            submatrixD = matrixB[i+ length +2:i + length + 4,j + length+2:j+length+4]

            submatrixE = matrixA[i + length +2:i+length+4, j-3:j-1]
            submatrixF = matrixB[i + length +2:i+length+4, j-3:j-1]

            submatrixG = matrixA[i-3:i-1, j+length+2:j+length+4]
            submatrixH = matrixB[i-3:i-1, j+length+2:j+length+4]

            conditions_met =  np.array_equal(submatrixA, submatrixB) + np.array_equal(submatrixC, submatrixD)+ np.array_equal(submatrixE, submatrixF)+  np.array_equal(submatrixG, submatrixH)
            
            if conditions_met==4:
                equal_indices_all.append((i, j))
            elif conditions_met==3:
                equal_indices_3.append((i, j))
            elif conditions_met==2:
                equal_indices_2.append((i, j))
            elif conditions_met==1:
                equal_indices_1.append((i, j))
    return equal_indices_all,  equal_indices_3, equal_indices_2, equal_indices_1


def find_best_area(FIRSTX, FIRSTY, FIRSTZ,length):
    heights1 = myworldSlice.heightmaps["MOTION_BLOCKING_NO_LEAVES"]
    heights2 = myworldSlice.heightmaps["WORLD_SURFACE"]
    heights3 = myworldSlice.heightmaps["OCEAN_FLOOR"]
    heights_array1 = np.array(heights1)
    heights_array2 = np.array(heights2)
    heights_array3 = np.array(heights3)
    # print('apoel',heights_array1,heights_array2,heights_array3)
    # print('apoel2',np.min(heights_array1),np.min(heights_array2),np.min(heights_array3))
    max_height=max(np.max(heights_array1),np.max(heights_array2))
     # Create subplots for heatmaps
    # fig, axs = plt.subplots(1, 3, figsize=(15, 5))

    # # Plot the heatmap for matrix1
    # im1 = axs[0].imshow(heights_array1, cmap='hot', interpolation='nearest')
    # axs[0].set_title('MOTION_BLOCKING_NO_LEAVES')
    # axs[0].set_xlabel('X')
    # axs[0].set_ylabel('Y')
    # axs[0].grid(True)
    # plt.colorbar(im1, ax=axs[0])

    # # Plot the heatmap for matrix2
    # im2 = axs[1].imshow(heights_array2, cmap='hot', interpolation='nearest')
    # axs[1].set_title('World Surface')
    # axs[1].set_xlabel('X')
    # axs[1].set_ylabel('Y')
    # axs[1].grid(True)
    # plt.colorbar(im2, ax=axs[1])

    # # Plot the heatmap for matrix3
    # im3 = axs[2].imshow(heights_array3, cmap='hot', interpolation='nearest')
    # axs[2].set_title('OCEAN_FLOOR')
    # axs[2].set_xlabel('X')
    # axs[2].set_ylabel('Y')
    # axs[2].grid(True)
    # plt.colorbar(im3, ax=axs[2])

    # plt.tight_layout()
    # plt.show()
   

    #find an area where those four positions have no trees
    #so an area where the two heatmaps are different
    #if cant find such are choose a random place and put the house
    #Area1 :(BestX -3,  ground_height, BestZ -3), (BestX - 1 , y - 2, BestZ - 1 )
    #Area 2: (BestX + length +2,  ground_height, BestZ + length+2), (BestX + length + 4, y - 2, BestZ + length+4)
    #Area 3: (BestX + length +2,  ground_height, BestZ -3), (BestX + length + 4, y - 2, BestZ - 1 )
    #Area 4: (BestX - 3,  ground_height, BestZ + length+2), (BestX - 1 , y - 2, BestZ + length+4)
    #check for trees
    equal_indices_all,  equal_indices_3, equal_indices_2, equal_indices_1 = find_equal_submatrices(heights_array1, heights_array2,length)
    # print("Count Indices with equal submatrices:", equal_indices_all[0],len(equal_indices_3),len(equal_indices_2),len(equal_indices_1))
    if len(equal_indices_all)!=0: 
        BestX,BestZ=random.choice(equal_indices_all)
    elif len(equal_indices_3)!=0: 
        BestX,BestZ=random.choice(equal_indices_3)
    elif len(equal_indices_2)!=0: 
        BestX,BestZ=random.choice(equal_indices_2)
    elif len(equal_indices_all)!=0: 
        BestX,BestZ=random.choice(equal_indices_1)
    i=BestX
    j=BestZ  
    # print('Best coordinates',BestX,BestZ)
    #take into account the see
    BestYs1=heights_array3[i-3:i-1, j-3:j-1]
    BestYs2=heights_array3[i+length+2:i+length+4,j+length+2:j+length+4]
    BestYs3=heights_array3[i+length+2:i+length+4, j-3:j-1]
    BestYs4=heights_array3[i-3:i-1, j+length+2:j+length+4]
    # return heights_array1[1][1],heights_array2[1][1],heights_array1[49][49],heights_array2[49][49],heights_array1[1][49],heights_array2[1][49],heights_array1[49][1],heights_array2[49][1]
    

    #find best area for stairs
    matching_pairs = []
    rows1, cols1 = heights_array2.shape
    rows2, cols2 = heights_array3.shape
    
    for i in range(rows1 - 2):
        for j in range(cols1 - 2):
            submatrix1 =heights_array2[i:i+3, j:j+3]
            if submatrix1.shape != (3, 3):
                continue  # Skip if submatrix1 dimensions don't match
            submatrix2 = heights_array3[i:i+3, j:j+3]
            if np.array_equal(submatrix1, submatrix2):
                matching_pairs.append((i, j))
    pair=random.choice(matching_pairs)
            

    return BestX,BestZ,BestYs1,BestYs2,BestYs3,BestYs4,max_height,pair

from typing import Optional, Sequence, Union, List, Iterable



def placeFittingCylinder(
    editor: Editor,
    corner1: Vec3iLike, corner2: Vec3iLike,
    block: Union[Block, Sequence[Block]],
    axis=1, tube=False, hollow=False,
    replace: Optional[Union[str, List[str]]] = None
):
    """Place blocks in the shape of the largest cylinder that fits between <corner1> and <corner2>."""
    # Transform only the key points instead of all points
    corner1 = editor.transform * corner1
    corner2 = editor.transform * corner2
    block = transformedBlockOrPalette(block, editor.transform.rotation, editor.transform.flip)
    
    # Get the positions of the cylinder
    positions = fittingCylinder(corner1, corner2, axis, tube, hollow)
    positions2=[]
    # Check each position before placing the block
    #print(positions)
    j=0
    i=0
    for pos in positions:
        #print('pos:',pos)
        j=j+1
        blocks = interface.getBlocks(pos, size=(1, 1, 1))
        block_ids = [block[1].id for block in blocks]
        # Check if any block exists at the position
        # Check if there's already a block at the current position
        #print('blockid:',str(block_ids)[12:])
        endstr=len(str(block_ids))-2
        #print(str(block_ids)[12:endstr]==str('cloud') or str(block_ids)[12:endstr]==str('air') or str(block_ids)[12:endstr]==str('snow') or str(block_ids)[12:endstr]==str('snow_block')or str(block_ids)[12:endstr]==str('grass') or str(block_ids)[12:endstr]==str('dirt'))
        if str(block_ids)[12:endstr]==str('cloud') or str(block_ids)[12:endstr]==str('air') or str(block_ids)[12:endstr]==str('snow') or str(block_ids)[12:endstr]==str('snow_block') or str(block_ids)[12:endstr]==str('grass') or str(block_ids)[12:endstr]==str('dirt'):
            i=i+1
            positions2.append(pos)
            #print('place the block ok at',pos)
            editor.placeBl
            ock(pos, block)
            #print('i',i) 
        if i>=30 or j>=10:
            break
        #print('height2',j,i)
    return min(i,j)


def main():
    length=random.randint(7, 12)
    height=random.randint(10, 15)
    print('creating border for 100*100 area...')
    createborder()
    print('Finding best area to build the house..')
    BestX,BestZ,BestYs1,BestYs2,BestYs3,BestYs4,max_height,pair=find_best_area(FIRSTX, FIRSTY, FIRSTZ,length)
    # #transform to game coordinates
    BestX=min(FIRSTX,ENDX)+BestX
    BestZ=min(FIRSTZ,ENDZ)+BestZ
    print('Best coordinates X,Z', BestX, BestZ)
    #for stairs-not used for now
    min_h=np.min(myworldSlice.heightmaps["OCEAN_FLOOR"][pair[0]:pair[0]+3,pair[1]:pair[1]+3])
    X_stairs=min(FIRSTX,ENDX)+pair[0]
    Z_stairs=min(FIRSTZ,ENDZ)+pair[1]
    max_height=int(max_height)/3*3
    ground_height1=np.min(BestYs1)
    ground_height2=np.min(BestYs2)
    ground_height3=np.min(BestYs3)
    ground_height4=np.min(BestYs4)
    print('Creating the outside of the house..')
    createoutsite(BestX,BestZ,ground_height1,ground_height2,ground_height3,ground_height4,max_height,length,height)
    print('Decorate...')
    decorateinside(BestX,max_height,BestZ,length)

    # print('maxheight',max_height)
    numstairs=(max_height-2)/3
    # print('numstairs',numstairs)
    if numstairs%4==0:
        # print('444444')
        X_stairs= BestX + length + 1 + 3-2 -3
        Z_stairs=BestZ + length+1 + 3+7-2
    elif numstairs%3==0:
        # print('3333333')
        X_stairs=  BestX + length + 1 + 3 - 7
        Z_stairs= BestZ + length+1 + 3-2
    elif numstairs%2==0:
        # print('222222')
        X_stairs=BestX - 1 - 2+2
        Z_stairs=BestZ - 1 - 2-7
    else :
        # print('111111')
        X_stairs= BestX - 1 - 2-1- 8 
        Z_stairs=BestZ - 1 - 2+2
    # geo.placeCuboid(myeditor, (BestX - 1 - 2, max_height - 1, BestZ - 1 - 2), (BestX + length + 1 + 3, max_height - 1, BestZ + length+1 + 3), Block(ground))
    print('Create stairs to reach the house...')
    createstairs(X_stairs,Z_stairs,max_height,min_h,BestX,BestZ)
    print('Finish')
    
if __name__ == '__main__':
    main()

 

  






   




