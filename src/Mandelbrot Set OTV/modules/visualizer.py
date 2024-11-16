from matplotlib.animation import FuncAnimation
import numpy as np
import matplotlib.pyplot as plt
from modules.config import *
from numba import njit
from modules.mandelbrot_calculator import *

def show_img(ax, img):
    """
    Displays an image on the given Axes object with custom tick labels.
    Parameters:
    ax (matplotlib.axes.Axes): The Axes object on which to display the image.
    img (numpy.ndarray): The image data to display.
    Notes:
    - The function customizes the x and y ticks based on the image dimensions and fractional coordinates.
    - The x-axis represents the real part (Re) and the y-axis represents the imaginary part (Im) of the complex plane.
    - The y-axis labels are formatted with an 'i' to denote imaginary numbers.
    - The function sets the frame off and adjusts the x and y limits to match the image dimensions.
    """
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
    ax.set_aspect('equal')  # Maintain the aspect ratio
        
def mouse_move(event):
    """
    Handles the mouse movement event on the Mandelbrot plot.
    This function is triggered when the mouse is moved over the plot. It updates
    the current mouse position in fractal coordinates, computes the orbit of the
    Mandelbrot function for the current mouse position, and updates the plot with
    the computed orbit.
    Parameters:
    event (matplotlib.backend_bases.MouseEvent): The mouse event containing the
        coordinates of the mouse pointer.
    Returns:
    tuple: A tuple containing the updated line1 and lines objects for the plot.
    """
    x, y = event.xdata, event.ydata  
    if x is None or y is None:
        return  

    x, y = imgToFrac(frac_size, img_size, (x, y))
    animate.current_mouse_position = (x, y)  

    orbit = []
    c = x + y * 1j
    z = c
    for i in range(maxIter):
        orbit.append(fracToImg(frac_size, img_size, (z.real, z.imag)))
        z = z**2 + c
        if abs(z) > 2:
            break

    if orbit:
        orbit = np.array(orbit)
        x, y = orbit[:, 0], orbit[:, 1]
        line1.set_data(x, y)

        u = np.diff(x)
        v = np.diff(y)
        angles = np.arctan2(v, u) * 180 / np.pi - 90

        for i in range(maxIter):
            line2, line3 = lines[i]
            if i < len(x) - 1:
                line2.set_data(x[i:i + 1], y[i:i + 1])
                line3.set_data(x[i:i + 1], y[i:i + 1])
                line2.set_marker((2, 0, angles[i]))
                line3.set_marker((3, 0, angles[i]))
                line2.set_markerfacecolor("black")
                line3.set_markerfacecolor("black")
                line2.set_markeredgecolor("yellow")
                line3.set_markeredgecolor("yellow")
            elif i == len(x) - 1:
                line2.set_data(x[i:i + 1], y[i:i + 1])
                line3.set_data(x[i:i + 1], y[i:i + 1])
                line2.set_marker('o')
                line3.set_marker('o')
                line2.set_markerfacecolor("black")
                line3.set_markerfacecolor("black")
                line2.set_markeredgecolor("white")
                line3.set_markeredgecolor("white")
            else:
                line2.set_data([], [])
                line3.set_data([], [])  
    else:
        for line2, line3 in lines:
            line2.set_data([], [])
            line3.set_data([], [])

    return line1, lines

def init():
    """
    Initializes the data for the lines and sets them to empty lists.

    This function sets the data for `line1`, `line4`, and each line in the `lines` list to empty lists.
    It returns `line1`, all items in the `lines` list, and `line4`.

    Returns:
        tuple: A tuple containing `line1`, all items in the `lines` list, and `line4`.
    """
    line1.set_data([], [])
    for line2, line3 in lines:
        line2.set_data([], [])
        line3.set_data([], [])
    line4.set_data([], [])
    return line1, *[item for sublist in lines for item in sublist], line4

def animate(i): 
    """
    Updates the animation frame for the Mandelbrot set visualization.
    Parameters:
    i (int): The current frame index (unused in the function).
    Returns:
    tuple: A tuple containing the updated line data for the animation.
    Notes:
    - The function uses the current mouse position stored in `animate.current_mouse_position`
      to compute the orbit of the complex number `c`.
    - The orbit is computed by iterating the function `z = z**2 + c` until the magnitude of `z`
      exceeds 2 or the maximum number of iterations (`maxIter`) is reached.
    - The function updates the line data for the animation using the computed orbit.
    """
    if hasattr(animate, 'current_mouse_position'):
        x, y = animate.current_mouse_position
        orbit = []
        c = x + y * 1j
        z = c
        for i in range(maxIter):
            orbit.append(fracToImg(frac_size, img_size, (z.real, z.imag)))
            z = z**2 + c
            if abs(z) > 2:
                break

        if orbit:
            orbit = np.array(orbit)
            x, y = orbit[:, 0], orbit[:, 1]
            line1.set_data(x, y)  
            line4.set_data(x[-1:], y[-1:])  

    return line1, *[item for sublist in lines for item in sublist], line4

def display_fractal(img):
    show_img(ax, img)
    cid = fig.canvas.mpl_connect('motion_notify_event', mouse_move)
    ani = FuncAnimation(fig, animate, frames=165, init_func=init, blit=True, interval=50)
    plt.show()