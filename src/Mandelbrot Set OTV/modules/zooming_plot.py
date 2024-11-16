import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import hsv_to_rgb
from numba import njit
from modules.config import *

# Numba JIT function to plot the fractal
@njit(parallel=True)
def plot_frac(frac_size, maxIter, frac_xStep, frac_yStep):
    (frac_x0, frac_y0), (frac_x1, frac_y1) = frac_size

    for row in range(img_h):
        for col in range(img_w):
            x = frac_x0 + col * frac_xStep
            y = frac_y0 + row * frac_yStep
            c = x + y * 1j
            z = 0 + 0j
            for i in range(maxIter):
                z = z**2 + c
                if abs(z) > 2:
                    iteration_count[row, col] = i
                    break
            else:
                iteration_count[row, col] = maxIter

            if iteration_count[row, col] < maxIter:
                img[row, col, 0] = iteration_count[row, col] / (maxIter - 1)  # Red channel
                img[row, col, 1] = 1  # Green channel is constant at 1
                img[row, col, 2] = 1 - (iteration_count[row, col] / (maxIter - 1))  # Blue channel
            else:
                img[row, col] = 0  # Black for points in the set

    return img

def show_img(ax, img):
    ax.imshow(img)
    xlen = len(ax.get_xticks())
    ylen = len(ax.get_yticks())
    xlen += (xlen + 1) % 2
    ylen += (ylen + 1) % 2
    xticks = np.linspace(img_x0, img_x1 - 1, xlen)
    yticks = np.linspace(img_y0, img_y1 - 1, ylen)
    xlabels = np.round(np.linspace(frac_x0, frac_x1, xlen), 2)
    ylabels = np.round(np.linspace(frac_y1, frac_y0, ylen), 2)
    ylabels = [str(l) + 'i' for l in ylabels]

    ax.set_xticks(xticks)
    ax.set_xticklabels(xlabels)
    ax.set_yticks(yticks)
    ax.set_yticklabels(ylabels)
    ax.set_xlabel("Real")
    ax.set_ylabel("Imaginary")
    ax.set_frame_on(False)
    ax.set_xlim([img_x0, img_x1 - 1])
    ax.set_ylim([img_y0, img_y1 - 1])
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')

def zoom(event):
    global frac_x0, frac_y0, frac_x1, frac_y1, frac_xStep, frac_yStep, maxIter

    # Calculate the mouse position in fractal coordinates
    mouse_x, mouse_y = event.xdata, event.ydata
    if mouse_x is None or mouse_y is None:
        return

    scale_factor = 1.6  # Adjust the zoom factor
    if event.button == 'up':
        scale = 1 / scale_factor
        maxIter *= 1.1  # Increase maxIter when zooming in
    elif event.button == 'down':
        scale = scale_factor
        maxIter /= 1  # Decrease maxIter when zooming out
    else:
        return

    # Ensure maxIter stays within a reasonable range
    maxIter = int(np.clip(maxIter, 10, 2000))  # Min and max iteration limits
    print(f"Max iterations: {maxIter}")

    # Calculate the new fractal boundaries
    mouse_frac_x = frac_x0 + (mouse_x / img_w) * (frac_x1 - frac_x0)
    mouse_frac_y = frac_y0 + (mouse_y / img_h) * (frac_y1 - frac_y0)

    # Adjust the fractal dimensions based on the zoom scale
    frac_x0 = mouse_frac_x - (mouse_frac_x - frac_x0) * scale
    frac_y0 = mouse_frac_y - (mouse_frac_y - frac_y0) * scale
    frac_x1 = mouse_frac_x + (frac_x1 - mouse_frac_x) * scale
    frac_y1 = mouse_frac_y + (frac_y1 - mouse_frac_y) * scale

    # Recalculate step sizes for the new dimensions
    frac_xStep = (frac_x1 - frac_x0) / img_w
    frac_yStep = (frac_y1 - frac_y0) / img_h

    # Recalculate the fractal image with the new dimensions
    img = plot_frac(((frac_x0, frac_y0), (frac_x1, frac_y1)), maxIter, frac_xStep, frac_yStep)
    img_rgb = hsv_to_rgb(img)

    # Clear the old plot and display the new one
    ax.clear()
    ax.set_facecolor("black")
    show_img(ax, img_rgb)
    plt.draw()

def on_press(event):
    global dragging, start_x, start_y
    if event.button == 1:  # Left mouse button
        dragging = True
        start_x = event.xdata
        start_y = event.ydata

def on_release(event):
    global dragging
    dragging = False

def on_motion(event):
    global frac_x0, frac_y0, frac_x1, frac_y1, frac_xStep, frac_yStep, start_x, start_y

    if dragging:
        # Calculate the amount of movement in the fractal coordinates
        dx = event.xdata - start_x
        dy = event.ydata - start_y

        # Adjust the fractal coordinates based on mouse movement
        frac_x0 -= dx * (frac_x1 - frac_x0) / img_w
        frac_y0 -= dy * (frac_y1 - frac_y0) / img_h
        frac_x1 -= dx * (frac_x1 - frac_x0) / img_w
        frac_y1 -= dy * (frac_y1 - frac_y0) / img_h

        # Recalculate step sizes for the new fractal size
        frac_xStep = (frac_x1 - frac_x0) / img_w
        frac_yStep = (frac_y1 - frac_y0) / img_h

        # Recalculate the fractal image with the new dimensions
        img = plot_frac(((frac_x0, frac_y0), (frac_x1, frac_y1)), maxIter, frac_xStep, frac_yStep)
        img_rgb = hsv_to_rgb(img)

        # Clear the old plot and display the new one
        ax.clear()
        ax.set_facecolor("black")
        show_img(ax, img_rgb)
        plt.draw()

        # Update the starting position for the next drag movement
        start_x = event.xdata
        start_y = event.ydata


def main():
    # Initialize the plot
    fig, ax = plt.subplots(figsize=(15, 10))
    ax.set_facecolor("black")

    # Initial fractal plot
    img = plot_frac(((frac_x0, frac_y0), (frac_x1, frac_y1)), maxIter, frac_xStep, frac_yStep)
    img_rgb = hsv_to_rgb(img)
    show_img(ax, img_rgb)
    
    # Connect the zoom and dragging functions to the appropriate events
    fig.canvas.mpl_connect('scroll_event', zoom)
    fig.canvas.mpl_connect('button_press_event', on_press)
    fig.canvas.mpl_connect('button_release_event', on_release)
    fig.canvas.mpl_connect('motion_notify_event', on_motion)

    plt.show()
    
main()