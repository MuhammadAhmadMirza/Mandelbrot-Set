import numpy as np
from numba import njit
from modules.config import *  # If any additional config is needed
from matplotlib.colors import hsv_to_rgb
import time

### Plot fractal using Numba
@njit(parallel=True)
def plot_frac(frac_size, img_size, maxIter, frac_xStep, frac_yStep):
    """
    Plots the Mandelbrot fractal.
    Parameters:
    frac_size (tuple): A tuple containing two tuples, each with two floats representing the 
                       coordinates of the top-left and bottom-right corners of the fractal region.
    img_size (tuple): A tuple containing two integers representing the height and width of the image.
    maxIter (int): The maximum number of iterations to determine if a point is in the Mandelbrot set.
    frac_xStep (float): The step size in the x-direction for each pixel.
    frac_yStep (float): The step size in the y-direction for each pixel.
    Returns:
    np.ndarray: A 3D numpy array representing the RGB image of the Mandelbrot fractal.
    """
    (frac_x0, frac_y0), (frac_x1, frac_y1) = frac_size
    img = np.zeros((img_h, img_w, 3), dtype=np.float32)
    iteration_count = np.zeros((img_h, img_w), dtype=np.int32)

    total_pixels = img_h * img_w
    pixel_count = 0

    for row in range(img_h):
        for col in range(img_w):
            x = frac_x0 + col * frac_xStep
            y = frac_y0 + row * frac_yStep
            c = x + y * 1j
            z = 0 + 0j
            for i in range(maxIter):
                z = z**2 + c
                if abs(z) > 2:  # Early escape condition
                    iteration_count[row, col] = i
                    break
            else:
                iteration_count[row, col] = maxIter  # Point is in the set

            # Update pixel count and print progress
            pixel_count += 1
            if pixel_count % (total_pixels // 100) == 0:
                print("Rendering progress: ", pixel_count * 100 // total_pixels, "%")

    # Color mapping
    for row in range(img_h):
        for col in range(img_w):
            if iteration_count[row, col] < maxIter:
                img[row, col, 0] = iteration_count[row, col] / (maxIter - 1)  # Red channel
                img[row, col, 1] = 1  # Green channel is constant at 1
                img[row, col, 2] = 1 - (iteration_count[row, col] / (maxIter - 1))  # Blue channel
            else:
                img[row, col] = 0  # Set black for points in the set

    return img

def imgToFrac(frac_size, img_size, point):
    """
    Converts a point from image coordinates to fractal coordinates.
    Parameters:
    frac_size (tuple): A tuple containing two tuples, each with two floats, representing the 
                       bottom-left and top-right corners of the fractal coordinate system.
                       Example: ((frac_x0, frac_y0), (frac_x1, frac_y1))
    img_size (tuple): A tuple containing two tuples, each with two floats, representing the 
                      bottom-left and top-right corners of the image coordinate system.
                      Example: ((img_x0, img_y0), (img_x1, img_y1))
    point (tuple): A tuple with two floats representing the coordinates of the point in the 
                   image coordinate system.
                   Example: (x0, y0)
    Returns:
    tuple: A tuple with two floats representing the coordinates of the point in the fractal 
           coordinate system.
           Example: (x1, y1)
    """
    (frac_x0, frac_y0), (frac_x1, frac_y1) = frac_size
    (img_x0, img_y0), (img_x1, img_y1) = img_size
    img_x1 -= 1.0; img_y1 -= 1.0

    x0, y0 = point
    x1 = (x0 - img_x0) * (frac_x1 - frac_x0) / (img_x1 - img_x0) + frac_x0
    y1 = (y0 - img_y0) * (frac_y0 - frac_y1) / (img_y1 - img_y0) + frac_y1
    return x1, y1

def fracToImg(frac_size, img_size, points):
    """
    Converts points from fractal coordinates to image coordinates.
    Parameters:
    frac_size (tuple): A tuple containing two tuples, each with two floats, representing the 
                       bottom-left and top-right corners of the fractal region 
                       ((frac_x0, frac_y0), (frac_x1, frac_y1)).
    img_size (tuple): A tuple containing two tuples, each with two integers, representing the 
                      bottom-left and top-right corners of the image region 
                      ((img_x0, img_y0), (img_x1, img_y1)).
    points (tuple): A tuple containing two numpy arrays, representing the x and y coordinates 
                    of the points in the fractal region (x0, y0).
    Returns:
    tuple: A tuple containing two numpy arrays, representing the x and y coordinates of the 
           points in the image region (x1, y1).
    """
    (frac_x0, frac_y0), (frac_x1, frac_y1) = frac_size
    (img_x0, img_y0), (img_x1, img_y1) = img_size
    img_x1 -= 1; img_y1 -= 1

    x0, y0 = points
    x1 = ((x0 - frac_x0) * (img_x1 - img_x0) / (frac_x1 - frac_x0) + img_x0).astype(int)
    y1 = ((y0 - frac_y0) * (img_y0 - img_y1) / (frac_y1 - frac_y0) + img_y1).astype(int)
    return x1, y1

def memmap_img():
    # Memory-mapping for optimized memory usage
    img_memmap = np.memmap(rp('assets/fractal/fractal_image.dat'), dtype='float32', mode='w+', shape=(img_h, img_w, 3))

    start_time = time.time()
    # Generate fractal image
    img = plot_frac(frac_size, img_size, maxIter, frac_xStep, frac_yStep)
    print("Rendering time: ", time.time() - start_time)

    # Convert to RGB using matplotlib's hsv_to_rgb
    img_rgb = hsv_to_rgb(img)

    start_time = time.time()
    # Store the image in the memory-mapped array
    img_memmap[:] = img_rgb

    # Flush and delete memory-mapped file after use
    img_memmap.flush()
    del img_memmap
    print("Saving time: ", time.time() - start_time)
    
def load_memmap_img():
    start_time = time.time()
    # Load the memory-mapped image back into a NumPy array
    img_memmap = np.memmap(rp('assets/fractal/fractal_image.dat'), dtype='float32', mode='r', shape=(img_h, img_w, 3))

    # Now img_memmap behaves like a NumPy array, and you can access it
    # img_memmap is directly a 3D NumPy array with RGB values
    print("Loading time: ", time.time() - start_time)
    return img_memmap