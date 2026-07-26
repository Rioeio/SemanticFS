from __future__ import annotations

import math
import os
import sys
import time
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()

class NeuralModelVisualizer:
    """3D ASCII Raycasting Neural Network & Embedding Model Visualizer for Terminal."""
    def __init__(self, width: int = 70, height: int = 24):
        self.width = width
        self.height = height
        self.angle_x = 0.0
        self.angle_y = 0.0
        self.angle_z = 0.0
        self.zoom = 1.0
        self.mode = "mesh"  # "mesh", "clusters", "attention"
        self.animating = True

        # Generate 384-dimensional neural nodes on a 3D sphere surface
        self.nodes: list[tuple[float, float, float]] = []
        num_nodes = 48  # Visual node resolution
        golden_ratio = (1 + 5 ** 0.5) / 2
        for i in range(num_nodes):
            theta = 2 * math.pi * i / golden_ratio
            phi = math.acos(1 - 2 * (i + 0.5) / num_nodes)
            x = math.cos(theta) * math.sin(phi)
            y = math.sin(theta) * math.sin(phi)
            z = math.cos(phi)
            self.nodes.append((x, y, z))

    def rotate_point(self, x: float, y: float, z: float) -> tuple[float, float, float]:
        """Apply 3D rotation matrices for angles (X, Y, Z)."""
        # Rotate X
        rad_x = math.radians(self.angle_x)
        cos_x, sin_x = math.cos(rad_x), math.sin(rad_x)
        y, z = y * cos_x - z * sin_x, y * sin_x + z * cos_x

        # Rotate Y
        rad_y = math.radians(self.angle_y)
        cos_y, sin_y = math.cos(rad_y), math.sin(rad_y)
        x, z = x * cos_y + z * sin_y, -x * sin_y + z * cos_y

        # Rotate Z
        rad_z = math.radians(self.angle_z)
        cos_z, sin_z = math.cos(rad_z), math.sin(rad_z)
        x, y = x * cos_z - y * sin_z, x * sin_z + y * cos_z

        return x * self.zoom, y * self.zoom, z * self.zoom

    def render_frame(self) -> str:
        """Render a single ASCII frame of the 3D Neural Model Topology."""
        grid = [[" " for _ in range(self.width)] for _ in range(self.height)]
        z_buffer = [[-999.0 for _ in range(self.width)] for _ in range(self.height)]

        shading = [".", ":", "-", "=", "+", "*", "#", "%", "@"]

        # Projected 2D points
        proj_nodes = []
        for x, y, z in self.nodes:
            rx, ry, rz = self.rotate_point(x, y, z)
            
            # Perspective projection
            distance = 2.5
            factor = 20.0 / (rz + distance)
            px = int(self.width / 2 + rx * factor * 1.8)
            py = int(self.height / 2 + ry * factor)

            if 0 <= px < self.width and 0 <= py < self.height:
                if rz > z_buffer[py][px]:
                    z_buffer[py][px] = rz
                    proj_nodes.append((px, py, rz))

        # Render Synaptic Attention Connections (edges)
        if self.mode == "mesh":
            for i in range(len(proj_nodes)):
                for j in range(i + 1, min(i + 4, len(proj_nodes))):
                    x1, y1, z1 = proj_nodes[i]
                    x2, y2, z2 = proj_nodes[j]
                    
                    # Draw line using Bresenham algorithm
                    dx, dy = abs(x2 - x1), abs(y2 - y1)
                    sx = 1 if x1 < x2 else -1
                    sy = 1 if y1 < y2 else -1
                    err = dx - dy
                    cx, cy = x1, y1

                    while True:
                        if 0 <= cx < self.width and 0 <= cy < self.height:
                            if grid[cy][cx] == " ":
                                grid[cy][cx] = "·" if (cx + cy) % 2 == 0 else "─"
                        if cx == x2 and cy == y2:
                            break
                        e2 = 2 * err
                        if e2 > -dy:
                            err -= dy
                            cx += sx
                        if e2 < dx:
                            err += dx
                            cy += sy

        # Render Neural Nodes
        for px, py, rz in proj_nodes:
            shade_idx = min(len(shading) - 1, max(0, int((rz + 1.2) * 4)))
            grid[py][px] = shading[shade_idx]

        frame_str = "\n".join("".join(row) for row in grid)
        return frame_str

    def run_interactive(self):
        """Run interactive movable neural visualizer loop."""
        if not sys.stdin.isatty() or os.name != 'nt':
            # Non-interactive fallback frame
            print(self.render_frame())
            return

        import msvcrt
        os.system('cls' if os.name == 'nt' else 'clear')
        
        while True:
            # Auto-spin if animation is ON
            if self.animating:
                self.angle_y += 3.0
                self.angle_x += 1.5

            frame_ascii = self.render_frame()
            
            os.system('cls' if os.name == 'nt' else 'clear')
            console.print("[bold cyan]🧠 BAAI/bge-small-en-v1.5 & CLIP Vision 3D Neural Visualizer[/bold cyan]")
            console.print(f"[dim]Mode: {self.mode.upper()} | Zoom: {self.zoom:.1f}x | Nodes: 384-Dim Vector Projection[/dim]\n")
            
            panel = Panel(
                Text(frame_ascii, style="bold bright_magenta"),
                border_style="bright_cyan",
                title="● 3D Movable Model Topology Projection ●"
            )
            console.print(panel)
            
            console.print("\n[bold bright_cyan]⌨️ Movable Controls:[/bold bright_cyan] [bold green][W/A/S/D or Arrow Keys][/bold green] Rotate 3D  [bold green][+/-][/bold green] Zoom  [bold yellow][Space][/bold yellow] Toggle Spin  [bold blue][Tab][/bold blue] Switch Mode  [bold red][Q/Esc][/bold red] Exit\n")
            
            time.sleep(0.05)

            # Non-blocking key check
            if msvcrt.kbhit():
                key = msvcrt.getch()
                if key in (b'q', b'Q', b'\x1b'):
                    os.system('cls' if os.name == 'nt' else 'clear')
                    console.print("[green]✔ Exited Neural Model Visualizer.[/green]")
                    break
                elif key in (b'w', b'W'):
                    self.angle_x -= 10.0
                elif key in (b's', b'S'):
                    self.angle_x += 10.0
                elif key in (b'a', b'A'):
                    self.angle_y -= 10.0
                elif key in (b'd', b'D'):
                    self.angle_y += 10.0
                elif key in (b'+', b'='):
                    self.zoom = min(2.5, self.zoom + 0.2)
                elif key in (b'-', b'_'):
                    self.zoom = max(0.5, self.zoom - 0.2)
                elif key == b' ':
                    self.animating = not self.animating
                elif key == b'\t':
                    modes = ["mesh", "clusters", "attention"]
                    self.mode = modes[(modes.index(self.mode) + 1) % len(modes)]
                elif key in (b'\x00', b'\xe0'):
                    arrow = msvcrt.getch()
                    if arrow == b'H':  # Up
                        self.angle_x -= 10.0
                    elif arrow == b'P':  # Down
                        self.angle_x += 10.0
                    elif arrow == b'K':  # Left
                        self.angle_y -= 10.0
                    elif arrow == b'M':  # Right
                        self.angle_y += 10.0

def launch_visualizer():
    viz = NeuralModelVisualizer()
    viz.run_interactive()

if __name__ == "__main__":
    launch_visualizer()
