from modules.config import *  # If any additional config is needed
import sys

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