"""
This script serves as the entry point for the Mandelbrot Set application. It performs different actions based on the value of `user_action`.
Modules:
    modules.config: Imports all configurations needed for the application.
    modules.mandelbrot_calculator: Contains functions for calculating and loading Mandelbrot set images.
    modules.visualizer: Contains functions for visualizing the Mandelbrot set.
    modules.zooming_plot: Contains the main function for generating zooming plots of the Mandelbrot set.
Actions:
    If `user_action` is 1:
        Imports `memmap_img` from `modules.mandelbrot_calculator` and calls it to generate a memory-mapped image of the Mandelbrot set.
    If `user_action` is 2:
        Imports `load_memmap_img` from `modules.mandelbrot_calculator` and `display_fractal` from `modules.visualizer`, then calls `display_fractal` with the loaded image to display the Mandelbrot set.
    If `user_action` is 3:
        Imports and calls the `main` function from `modules.zooming_plot` to generate a zooming plot of the Mandelbrot set.
    Otherwise:
        Exits the program.
"""
import sys
from modules.config import *  # If any additional config is needed

if user_action == 1:
    from modules.mandelbrot_calculator import memmap_img
    memmap_img()
elif user_action == 2:
    from modules.mandelbrot_calculator import load_memmap_img
    from modules.visualizer import display_fractal
    display_fractal(load_memmap_img())
elif user_action == 3:
    from modules.zooming_plot import main
    main()
else:
    sys.exit()