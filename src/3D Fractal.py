import turtle
import math
from collections import defaultdict

# --- Configuration ---
focal_length = 200
observer_distance = 400
alpha_deg = 30
beta_deg = 30
depth = 2
quantize_precision = 0.001  # snap coordinates to remove inner seams

alpha = math.radians(alpha_deg)
beta = math.radians(beta_deg)

# --- Rotation and Projection ---
def rotate_x(p, angle):
    x, y, z = p
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    return [x, y * cos_a - z * sin_a, y * sin_a + z * cos_a]

def rotate_y(p, angle):
    x, y, z = p
    cos_b, sin_b = math.cos(angle), math.sin(angle)
    return [x * cos_b + z * sin_b, y, -x * sin_b + z * cos_b]

def project_point(p):
    x, y, z = p
    z += observer_distance
    if z == 0:
        z = 0.0001
    return (focal_length * x / z, focal_length * y / z)

# --- Edge Collection ---
edge_counts = defaultdict(int)

def quantize_point(p, precision):
    return tuple(round(coord / precision) * precision for coord in p)

def normalize_edge(p1, p2):
    qp1 = quantize_point(p1, quantize_precision)
    qp2 = quantize_point(p2, quantize_precision)
    return tuple(sorted((qp1, qp2)))

def collect_cube_edges(center, size):
    x0, y0, z0 = center
    s = size / 2
    vertices = [
        [-s, -s, -s], [ s, -s, -s], [ s,  s, -s], [-s,  s, -s],
        [-s, -s,  s], [ s, -s,  s], [ s,  s,  s], [-s,  s,  s]
    ]
    world_vertices = [[x + x0, y + y0, z + z0] for x, y, z in vertices]
    edges = [
        (0, 1), (1, 2), (2, 3), (3, 0),
        (4, 5), (5, 6), (6, 7), (7, 4),
        (0, 4), (1, 5), (2, 6), (3, 7)
    ]
    for i, j in edges:
        edge = normalize_edge(world_vertices[i], world_vertices[j])
        edge_counts[edge] += 1

# --- Draw Only Unique (Outer) Edges ---
def draw_collected_edges():
    t.pencolor("black")
    t.pensize(1)
    for edge, count in edge_counts.items():
        if count == 1:
            p1, p2 = edge
            p1_rot = rotate_y(rotate_x(p1, alpha), beta)
            p2_rot = rotate_y(rotate_x(p2, alpha), beta)
            p1_proj = project_point(p1_rot)
            p2_proj = project_point(p2_rot)
            t.penup()
            t.goto(p1_proj)
            t.pendown()
            t.goto(p2_proj)

# --- Draw Cube Faces Only (No Outline) ---
def draw_cube_fill(center, size):
    x0, y0, z0 = center
    s = size / 2
    vertices = [
        [-s, -s, -s], [ s, -s, -s], [ s,  s, -s], [-s,  s, -s],
        [-s, -s,  s], [ s, -s,  s], [ s,  s,  s], [-s,  s,  s]
    ]
    translated = [[x + x0, y + y0, z + z0] for x, y, z in vertices]
    rotated = [rotate_y(rotate_x(p, alpha), beta) for p in translated]
    projected = [project_point(p) for p in rotated]
    faces = [
        [0, 1, 2, 3], [4, 5, 6, 7],
        [0, 1, 5, 4], [2, 3, 7, 6],
        [1, 2, 6, 5], [0, 3, 7, 4]
    ]
    t.fillcolor("lightblue")
    t.pencolor("lightblue")  # hide fill outlines
    for face in faces:
        t.penup()
        t.goto(projected[face[0]])
        t.begin_fill()
        for idx in face[1:]:
            t.goto(projected[idx])
        t.goto(projected[face[0]])
        t.end_fill()

# --- Recursive Sierpiński Cube ---
def sierpinski_cube(center, size, depth):
    if depth == 0:
        draw_cube_fill(center, size)
        collect_cube_edges(center, size)
        return
    step = size / 3
    x0, y0, z0 = center
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            for dz in [-1, 0, 1]:
                if abs(dx) + abs(dy) + abs(dz) <= 1:
                    continue
                new_center = (x0 + dx * step, y0 + dy * step, z0 + dz * step)
                sierpinski_cube(new_center, step, depth - 1)

# --- Turtle Setup ---
screen = turtle.Screen()
screen.setup(width=800, height=800)
screen.setworldcoordinates(-400, -400, 400, 400)
screen.tracer(0)

cv = screen.getcanvas()
root = cv.winfo_toplevel()
root.geometry("+300+200")

t = turtle.Turtle()
t.hideturtle()
t.speed(0)
turtle.delay(0)

# --- Run the Drawing ---
sierpinski_cube(center=(0, 0, 0), size=200, depth=depth)
draw_collected_edges()
screen.update()
turtle.done()
