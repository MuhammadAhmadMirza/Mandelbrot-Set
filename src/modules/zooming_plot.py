'''makes a plot that you can zoom into indefinitely by clicking and dragging the mouse unlike the otv one'''
# i couldn't merge the otv one with zooming capabilities due to my lack of knowledge in matplotlib

# you cannot technically zoom indefinitely because the mex iterations are limited so the detail will be lost in high zoom due to performance limitations

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import hsv_to_rgb
from numba import njit
from matplotlib.animation import FuncAnimation
from modules.resource_path import resource_path as rp

# Define parameters for image and fractal size
width = 450
height = 300
maxIter = 50

# Define initial parameters
img_size = ((0, 0), (width, height))
frac_size = ((-2.2, -1.2), (1.2, 1.2))  # The region of the fractal
(frac_x0, frac_y0), (frac_x1, frac_y1) = frac_size
(img_x0, img_y0), (img_x1, img_y1) = img_size
img_w = img_x1 - img_x0
img_h = img_y1 - img_y0

frac_xStep = (frac_x1 - frac_x0) / img_w
frac_yStep = (frac_y1 - frac_y0) / img_h

# Numba JIT function to plot the fractal
@njit(parallel=True)
def plot_frac(frac_size, maxIter, frac_xStep, frac_yStep):
    """
    Plots the Mandelbrot fractal for a given region and returns the image.
    Parameters:
    frac_size (tuple): A tuple containing two tuples, each with two floats. 
                       The first tuple represents the bottom-left corner (frac_x0, frac_y0) 
                       and the second tuple represents the top-right corner (frac_x1, frac_y1) 
                       of the region to be plotted.
    maxIter (int): The maximum number of iterations to determine if a point is in the Mandelbrot set.
    frac_xStep (float): The step size in the x-direction for each pixel.
    frac_yStep (float): The step size in the y-direction for each pixel.
    Returns:
    numpy.ndarray: A 3D numpy array representing the RGB image of the Mandelbrot fractal.
    """
    (frac_x0, frac_y0), (frac_x1, frac_y1) = frac_size
    img = np.zeros((img_h, img_w, 3), dtype=np.float32)
    iteration_count = np.zeros((img_h, img_w), dtype=np.int32)

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

    # Add grid lines
    ax.grid(True, color='gray', linestyle='--', linewidth=0.5)

    # Create a text object for mouse coordinates (initially empty)
    ax.mouse_coord_text = ax.text(0.95, 0.05, "", transform=ax.transAxes, ha="right", va="bottom", 
                                  fontsize=12, color='white', backgroundcolor='black', 
                                  bbox=dict(facecolor='black', edgecolor='none', boxstyle='round,pad=0.5'))
  
def zoom(event):
    """
    Handles zooming in and out on a fractal plot based on mouse events.
    Parameters:
    event (matplotlib.backend_bases.MouseEvent): The mouse event that triggers the zoom action. 
        The event should have the following attributes:
        - xdata (float): The x-coordinate of the mouse event in data coordinates.
        - ydata (float): The y-coordinate of the mouse event in data coordinates.
        - button (str): The mouse button pressed ('up' for zoom in, 'down' for zoom out).
    Returns:
    None
    """
    global frac_x0, frac_y0, frac_x1, frac_y1, frac_xStep, frac_yStep, maxIter

    mouse_x, mouse_y = event.xdata, event.ydata
    if mouse_x is None or mouse_y is None:
        return

    scale_factor = 0.8  # Adjust the zoom factor
    if event.button == 'up':
        scale = scale_factor  # Zoom in
        maxIter *= 1.1  # Increase maxIter when zooming out
    elif event.button == 'down':
        scale = 1 / scale_factor  # Zoom out
        maxIter /= 1.1  # Decrease maxIter when zooming out
    else:
        return

    maxIter = min(maxIter, 2000)  # Limit the maximum number of iterations

    # Calculate new fractal bounds centered on the mouse position
    mouse_frac_x = frac_x0 + (mouse_x / img_w) * (frac_x1 - frac_x0)
    mouse_frac_y = frac_y0 + (mouse_y / img_h) * (frac_y1 - frac_y0)

    frac_x0 = mouse_frac_x - (mouse_frac_x - frac_x0) * scale
    frac_x1 = mouse_frac_x + (frac_x1 - mouse_frac_x) * scale
    frac_y0 = mouse_frac_y - (mouse_frac_y - frac_y0) * scale
    frac_y1 = mouse_frac_y + (frac_y1 - mouse_frac_y) * scale

    frac_xStep = (frac_x1 - frac_x0) / img_w
    frac_yStep = (frac_y1 - frac_y0) / img_h

    # Trigger an animation update
    fig.canvas.draw_idle()

def update(frame):
    """
    Update the plot for each frame in the animation.
    """
    global img
    img = plot_frac(((frac_x0, frac_y0), (frac_x1, frac_y1)), maxIter, frac_xStep, frac_yStep)
    img_rgb = hsv_to_rgb(img)
    img_rgb = np.clip(img_rgb, 0, 1)  # Clip the values to [0, 1]
    ax.clear()
    ax.set_facecolor("black")
    ax.set_title("Mandelbrot Set", fontsize=24)  # Add the title back here
    show_img(ax, img_rgb)

# Add drag functionality
def on_press(event):
    """
    Handles the mouse press event for zooming functionality.

    This function is triggered when a mouse button is pressed. It sets the 
    dragging state to True and records the starting x and y coordinates if 
    the left mouse button is pressed.

    Parameters:
    event (matplotlib.backend_bases.MouseEvent): The mouse event containing 
    information about the mouse button pressed and the coordinates of the 
    cursor.
    """
    global dragging, start_x, start_y
    if event.button == 1:  # Left mouse button
        dragging = True
        start_x = event.xdata
        start_y = event.ydata

def on_release(event):
    """
    Event handler for mouse button release.

    This function is triggered when the mouse button is released. It sets the
    global variable 'dragging' to False, indicating that the dragging action
    has stopped.

    Parameters:
    event (matplotlib.backend_bases.MouseEvent): The mouse event that triggered this handler.
    """
    global dragging
    dragging = False

def on_motion(event):
    """
    Handles the motion event for zooming and panning in the Mandelbrot set plot.
    This function updates the fractal coordinates and redraws the plot when the mouse is dragged.
    Parameters:
    event (matplotlib.backend_bases.MouseEvent): The mouse event containing the current mouse position.
    Global Variables:
    frac_x0 (float): The starting x-coordinate of the fractal.
    frac_y0 (float): The starting y-coordinate of the fractal.
    frac_x1 (float): The ending x-coordinate of the fractal.
    frac_y1 (float): The ending y-coordinate of the fractal.
    frac_xStep (float): The step size in the x-direction for the fractal.
    frac_yStep (float): The step size in the y-direction for the fractal.
    start_x (float): The initial x-coordinate when dragging starts.
    start_y (float): The initial y-coordinate when dragging starts.
    dragging (bool): A flag indicating whether the mouse is being dragged.
    img_w (int): The width of the image.
    img_h (int): The height of the image.
    fig (matplotlib.figure.Figure): The figure object for the plot.
    """
    global frac_x0, frac_y0, frac_x1, frac_y1, frac_xStep, frac_yStep, start_x, start_y

    if dragging and event.xdata is not None and event.ydata is not None:
        dx = event.xdata - start_x
        dy = event.ydata - start_y

        frac_x0 -= dx * (frac_x1 - frac_x0) / img_w
        frac_y0 -= dy * (frac_y1 - frac_y0) / img_h
        frac_x1 -= dx * (frac_x1 - frac_x0) / img_w
        frac_y1 -= dy * (frac_y1 - frac_y0) / img_h

        frac_xStep = (frac_x1 - frac_x0) / img_w
        frac_yStep = (frac_y1 - frac_y0) / img_h

        start_x = event.xdata
        start_y = event.ydata
        fig.canvas.draw_idle()

# Main function
def main():
    """
    Main function to initialize and display the Mandelbrot set plot with interactive zooming and dragging.
    This function performs the following tasks:
    1. Initializes the plot with a black background.
    2. Plots the initial fractal image.
    3. Sets up event handlers for zooming and dragging.
    4. Starts the animation loop to update the plot.
    Global Variables:
    - fig: The figure object for the plot.
    - ax: The axes object for the plot.
    - dragging: Boolean flag to indicate if dragging is in progress.
    - start_x: Starting x-coordinate for dragging.
    - start_y: Starting y-coordinate for dragging.
    Event Handlers:
    - 'scroll_event': Calls the zoom function to handle zooming.
    - 'button_press_event': Calls the on_press function to handle mouse button press.
    - 'button_release_event': Calls the on_release function to handle mouse button release.
    - 'motion_notify_event': Calls the on_motion function to handle mouse movement.
    Animation:
    - Starts an animation loop with a single frame and an interval of 50 milliseconds.
    """
    # Initialize the plot
    global fig, ax
    fig, ax = plt.subplots(figsize=(15, 10))
    ax.set_facecolor("black")
    ax.set_title("Mandelbrot Fractal", fontsize=24)  # Add title here
    fig.canvas.manager.window.title("Mandelbrot Fractal")  # Set the window title
    fig.canvas.manager.window.iconbitmap(rp("assets/images/icon.ico"))  # Set the window icon

    # Initial fractal plot
    img = plot_frac(((frac_x0, frac_y0), (frac_x1, frac_y1)), maxIter, frac_xStep, frac_yStep)
    img_rgb = hsv_to_rgb(img)
    show_img(ax, img_rgb)

    # Initialize variables for dragging
    global dragging, start_x, start_y
    dragging = False
    start_x = 0
    start_y = 0

    fig.canvas.mpl_connect('scroll_event', zoom)
    fig.canvas.mpl_connect('button_press_event', on_press)
    fig.canvas.mpl_connect('button_release_event', on_release)
    fig.canvas.mpl_connect('motion_notify_event', on_motion)

    # Start animation
    ani = FuncAnimation(fig, update, frames=range(1), interval=50)

    plt.show()