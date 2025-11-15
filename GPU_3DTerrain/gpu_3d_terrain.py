import numpy as np
import cupy as cp
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import noise
import time

# ============================================================
# Terrain generation (CPU & GPU, scrolling in X direction)
# ============================================================
def generate_terrain_cpu(size=128, scale=40.0, height_scale=17.0,
                         octaves=8, persistence=0.5, lacunarity=2.1, offset_x=0):
    terrain = np.zeros((size, size), dtype=np.float32)
    for i in range(size):
        for j in range(size):
            height = noise.pnoise2(
                (i + offset_x) / scale,
                j / scale,
                octaves=octaves,
                persistence=persistence,
                lacunarity=lacunarity,
                repeatx=1024, repeaty=1024
            )
            terrain[i][j] = height

    terrain = (terrain - terrain.min()) / (terrain.max() - terrain.min()) * 2 - 1
    return terrain * height_scale


def generate_terrain_gpu(size=128, scale=40.0, height_scale=17.0,
                         octaves=16, persistence=0.5, lacunarity=2.1, offset_x=0):

    x = cp.arange(size, dtype=cp.float32)
    y = cp.arange(size, dtype=cp.float32)
    xx, yy = cp.meshgrid(x, y)

    xx = (xx + offset_x) / scale
    yy = yy / scale

    terrain = cp.zeros_like(xx)
    xx_cpu = xx.get()
    yy_cpu = yy.get()

    for i in range(size):
        for j in range(size):
            terrain[i, j] = noise.pnoise2(
                xx_cpu[i, j], yy_cpu[i, j],
                octaves=octaves,
                persistence=persistence,
                lacunarity=lacunarity,
                repeatx=1024, repeaty=1024
            )

    terrain = (terrain - terrain.min()) / (terrain.max() - terrain.min()) * 2 - 1
    return terrain * height_scale

# ============================================================
# Mesh
# ============================================================
def create_terrain_mesh(terrain):
    size = terrain.shape[0]
    verts, colors, indices = [], [], []

    for i in range(size):
        for j in range(size):
            x = i - size/2
            y = terrain[i][j]
            z = j - size/2
            verts.append([x, y, z])

            h = (y + 7) / 20
            colors.append([0.0, 0.3 + h * 0.4, 0.0])

    for i in range(size-1):
        for j in range(size-1):
            a = i*size + j
            b = a+1
            c = a+size
            d = c+1
            indices.extend([a,b,c,b,d,c])

    return np.array(verts, np.float32), np.array(colors,np.float32), np.array(indices,np.uint32)

# ============================================================
# Rendering
# ============================================================
def render_terrain(verts, cols, idxs):
    glBegin(GL_TRIANGLES)
    for i in idxs:
        glColor3fv(cols[i])
        glVertex3fv(verts[i])
    glEnd()

def render_water(size=128, y=-2.0, alpha=0.6):
    half = size/2
    glEnable(GL_BLEND); glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glColor4f(0.0, 0.3, 0.8, alpha)

    glBegin(GL_QUADS)
    glVertex3f(-half, y, -half)
    glVertex3f(half, y, -half)
    glVertex3f(half, y, half)
    glVertex3f(-half, y, half)
    glEnd()

    glDisable(GL_BLEND)

# ============================================================
# Main
# ============================================================
def main():
    gpu = False
    try:
        cp.cuda.Device(0).compute_capability; gpu=True
        print("GPU Mode")
    except: print("CPU Mode")

    if not glfw.init(): raise Exception("Could not init GLFW")

    win = glfw.create_window(900, 700, "GPU Infinite Terrain ", None, None)
    glfw.make_context_current(win)

    glEnable(GL_DEPTH_TEST)
    glClearColor(0.53,0.81,0.98,1.0)
    gluPerspective(30, 900/700, 0.2, 500)

    # Camera fixed
    glTranslatef(0, -15, -85)  
    glRotatef(200,100,0,0)

    # Initial terrain
    terrain = generate_terrain_gpu() if gpu else generate_terrain_cpu()
    cpu_map = cp.asnumpy(terrain) if gpu else terrain
    verts, cols, idxs = create_terrain_mesh(cpu_map)

    # Simulation state
    offset = 0.0
    speed = 7.0
    last = time.time()

    while not glfw.window_should_close(win):
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)

        now = time.time()
        dt = now - last
        last = now

        offset += speed * dt

        # Update heights only (true infinite scrolling)
        terrain = generate_terrain_gpu(offset_x=offset) if gpu else generate_terrain_cpu(offset_x=offset)
        cpu_map = cp.asnumpy(terrain) if gpu else terrain
        verts[:,1] = cpu_map.flatten()

        glPushMatrix()
        render_terrain(verts, cols, idxs)
        render_water(128, -2.0, 0.6)
        glPopMatrix()

        glfw.swap_buffers(win)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()
