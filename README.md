# Minecraft-pcg

## Description
 
Procedural Content Generation (PCG) in Minecraft as part of the Modern Game AI (MGAI) course assignment. A Python-based house generator built with the [GDPC](https://github.com/avdstaaij/gdpc) framework, which interfaces with Minecraft Java Edition through the GDMC HTTP mod to place blocks and read terrain live while the game is running.

 
##  Files
 
minecraft-pcg/

gdpc/
  gdpc Python framework (local copy)

  Myriana_Miltiadous/
    Generator implementation
    myhomes.py
      Main house generation script
    Mincraft_mgai_Myriana_Miltiadous_report.pdf
      Report
    Readme.docx

  examples/
    GDPC example scripts
    emerald_city.py
    quick_example.py
    visualize_map.py
    tutorials/
      Step-by-step GDPC tutorials (1–8)

  gdpc/
    GDPC library source

  requirements.txt
  setup.py

gdmc_http_interface-1.0.0.jar
  GDMC HTTP Interface Minecraft mod

mgai_a1.pdf
  Assignment

 
## Overview
 
A procedural house generator that places a randomized, terrain-adaptive elevated house within a 100×100 Minecraft build area. The house is raised on four circular 3×3 pillars, adapts its height and materials to the environment, and includes interior decoration, a garden, and a circular staircase for access. Communication between Python and Minecraft happens via the GDMC HTTP Interface mod.
 
## Requirements
 
See mgai_a1.pdf for full setup and requirements details.

## Usage
 
1. Open a Minecraft world with the GDMC HTTP mod enabled.
2. Set the build area in the Minecraft chat, e.g.:
   ```
   /setbuildarea 0 100 0 100 100 100
   ```
3. Run the generator:
   ```bash
   python gdpc/Myriana_Miltiadous/myhomes.py
   ```
 
**Optional tweaks inside `myhomes.py`:**
- To skip the border, comment out `createborder()` (line 578).
- For better terrain adaptation (slower), uncomment lines 183, 186, 189, 192.
- To visualise the heightmaps for terrain evaluation, uncomment lines 451–479.
 
## How It Works
 
The generator (`myhomes.py`) is organised around four main functions:
 
- `createoutside()` : builds the exterior shell: walls, roof, windows, door, and fence
- `decorateinside()` : furnishes the interior with carpet, bed, lighting, and job objects
- `createstairs()` : generates a circular staircase to reach the elevated house
- `createborder()` : places a decorative border around the build area
### Randomness & Variation
Every generated house is unique. Randomised elements include: house height (10–15 blocks), side length (7–12 blocks), wall/roof/pillar/ground materials, number and material of windows (1–4), door placement, presence and position of a garden (with a named owner sign and optional chest), interior furniture positions, and fence/entry placement.
 
### Terrain Adaptation
The generator compares two heightmaps (`MOTION_BLOCKING_NO_LEAVES` and `WORLD_SURFACE`) to detect trees and avoid destroying them. Pillar placement is chosen from tree-free locations. For varied ground levels, the first rows of each pillar check for non-air/snow/grass blocks before placing. For ocean terrain, pillars are built from the ocean floor upward using the ocean heightmap.
 
### Believability
The circular staircase direction varies based on house height, adding further visual variety. Houses include lighting, a bed, and an optional garden to feel lived-in. All materials are drawn from curated lists of realistic Minecraft block types.
 
