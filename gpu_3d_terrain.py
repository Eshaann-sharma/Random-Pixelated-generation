import numpy as np
import cupy as cp
import glfw
from OpenGL.GL import *
from OpenGL.GLU import *
import noise
import time

# ============================================================
# Terrain generation functions
# ============================================================
def generate_terrain_cpu(size=128, scale=40.0, height_scale=10.0,
                         octaves=4, persistence=0.5, lacunarity=2.0, offset_x=0):
    terrain = np.zeros((size, size), dtype=np.float32)
    for i in range(size):
        for j in range(size):
            height = noise.pnoise2(
                (i + offset_x) / scale,
                j / scale,
                octaves=octaves,
                persistence=persistence,
                lacunarity=lacunarity,
                repeatx=1024,
                repeaty=1024,
                base=0
            )
            terrain[i][j] = height
    terrain = (terrain - terrain.min()) / (terrain.max() - terrain.min()) * 2 - 1
    return terrain * height_scale


def generate_terrain_gpu(size=128, scale=40.0, height_scale=10.0,
                         octaves=4, persistence=0.5, lacunarity=2.0, offset_x=0):
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
                xx_cpu[i, j],
                yy_cpu[i, j],
                octaves=octaves,
                persistence=persistence,
                lacunarity=lacunarity,
                repeatx=1024,
                repeaty=1024,
                base=0
            )

    terrain = (terrain - terrain.min()) / (terrain.max() - terrain.min()) * 2 - 1
    return terrain * height_scale


# ============================================================
# Mesh creation
# ============================================================
def create_terrain_mesh(terrain):
    size = terrain.shape[0]
    verts, colors, indices = [], [], []

    for i in range(size):
        for j in range(size):
            x = i - size / 2
            y = terrain[i][j]
            z = j - size / 2
            verts.append([x, y, z])

            h = (y + 10) / 20
            colors.append([0.0, 0.3 + h * 0.4, 0.0])

    for i in range(size - 1):
        for j in range(size - 1):
            a = i * size + j
            b = a + 1
            c = a + size
            d = c + 1
            indices.extend([a, b, c, b, d, c])

    return np.array(verts, np.float32), np.array(colors, np.float32), np.array(indices, np.uint32)


# ============================================================
# Rendering
# ============================================================
def render_terrain(vertices, colors, indices):
    glBegin(GL_TRIANGLES)
    for idx in indices:
        glColor3fv(colors[idx])
        glVertex3fv(vertices[idx])
    glEnd()


def render_water_plane(size=128, level=-2.0, alpha=0.6):
    half = size / 2
    glColor4f(0.0, 0.3, 0.8, alpha)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    glBegin(GL_QUADS)
    glVertex3f(-half, level, -half)
    glVertex3f(half, level, -half)
    glVertex3f(half, level, half)
    glVertex3f(-half, level, half)
    glEnd()
    glDisable(GL_BLEND)


# ============================================================
# Main benchmark + render loop
# ============================================================
def main():
    gpu_available = False
    try:
        cp.cuda.Device(0).compute_capability
        gpu_available = True
        print("GPU Mode Enabled (CuPy)")
    except Exception:
        print("GPU not available, falling back to CPU mode")

    if not glfw.init():
        raise Exception("GLFW initialization failed")

    window = glfw.create_window(900, 700, "GPU Terrain Flythrough (Left to Right)", None, None)
    glfw.make_context_current(window)

    glEnable(GL_DEPTH_TEST)
    glClearColor(0.53, 0.81, 0.98, 1.0)
    gluPerspective(30, 900 / 700, 0.2, 500)

    # Base camera view
    glTranslatef(0.0, -10.0, -120.0)
    glRotatef(40, 1, 0, 0)

    # camera state
    terrain_offset_x = 0.0
    total_offset = 0.0
    speed = 15.0
    last_time = time.time()

    # initial terrain
    start = time.time()
    terrain = generate_terrain_gpu(offset_x=terrain_offset_x) if gpu_available else generate_terrain_cpu(offset_x=terrain_offset_x)
    terrain_cpu = cp.asnumpy(terrain) if gpu_available else terrain
    vertices, colors, indices = create_terrain_mesh(terrain_cpu)
    print(f"[Initial Terrain] Generated in {time.time() - start:.3f}s")

    while not glfw.window_should_close(window):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        current_time = time.time()
        delta_time = current_time - last_time
        last_time = current_time

        move_distance = speed * delta_time
        total_offset += move_distance

        glPushMatrix()
        # continuous smooth camera motion (no bounce)
        glTranslatef(-total_offset, 0.0, 0.0)
        render_terrain(vertices, colors, indices)
        render_water_plane(size=128, level=-2.0, alpha=0.6)
        glPopMatrix()

        glfw.swap_buffers(window)
        glfw.poll_events()

        # regenerate terrain every 100 units
        if total_offset > 50:
            total_offset = 0.0
            terrain_offset_x += 16.0
            start = time.time()
            terrain = generate_terrain_gpu(offset_x=terrain_offset_x) if gpu_available else generate_terrain_cpu(offset_x=terrain_offset_x)
            terrain_cpu = cp.asnumpy(terrain) if gpu_available else terrain
            vertices, colors, indices = create_terrain_mesh(terrain_cpu)
            print(f"[Regenerated] time={time.time() - start:.3f}s")

    glfw.terminate()


if __name__ == "__main__":
    main()
