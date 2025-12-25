# PIXEL GENERATION

This repo demonstartes 2D Random Map generation and 3D Terrain generation using perlin noise and GPU.

## 2D RANDOM MAP GENERATION

2D map generation using Pygame and sprites involves creating a grid based world where each cell represents a tile such as grass, 
water, forest, or mountains, and the map is generated programmatically rather than designed manually. The map is typically stored as
a 2D array that is first filled with a default tile and then modified using procedural techniques like patch-based generation, where randomly
sized and positioned regions are replaced with specific terrain types to create natural-looking clusters. Each tile corresponds to a sprite in Pygame,
with an image and position calculated from its grid coordinates, and during rendering, these sprites are drawn to the screen in a loop.
This separation of map data and visual representation makes the system efficient, scalable, and well-suited for simulations, games, and 
performance comparisons such as CPU vs GPU-based world generation.

## 3D RANDOM TERRAIN GENERATION

![PHOTO-2025-11-06-01-33-31](https://github.com/user-attachments/assets/4723b678-a8df-468e-94f9-79e1e7b2f7e8)

### PERLIN NOISE

Perlin Noise generates a smooth, pseudorandom pattern that transitions gradually between values. Unlike white noise, which changes abruptly, Perlin noise creates coherent textures ideal for landscapes, clouds, or terrain in games.

How It Works :
- Divides space into a grid of gradient vectors.
- Computes dot products between gradients and the position of each point.
- Applies interpolation (usually fade curves) to smooth the transitions.
- The result is a continuous field of noise values between -1 and 1.

https://github.com/user-attachments/assets/710c232d-c753-4b35-b057-8847c079114b


