'''contains some necessary global variables for the application like fig size axes etc.'''

import tkinter as tk
from tkinter import simpledialog
import matplotlib.pyplot as plt
from modules.resource_path import resource_path as rp

# Create a Tkinter window for input
root = tk.Tk()
root.withdraw()  # Hide the main window

user_action = simpledialog.askinteger("What would you like to do:", "1: Render Image\n2: Display Orbit trap visualization\n3: Display Zooming Plot")

if user_action == 1:
    # Ask for width and height using dialog boxes
    height = simpledialog.askinteger("Resolution Input(=1600)", "Enter height resolution in pixels:")
    width = int(height * 1.5)  # Set width based on height proportionally
    maxIter = simpledialog.askinteger("Max Iteration Input(=100)", "Enter maximum iterations for fractal calculation:")
    
    with open(rp("assets/fractal/metadata.txt"), "w") as f:
        f.write(f"{width}\n{height}\n{maxIter}")
        
elif user_action == 2:
    with open(rp("assets/fractal/metadata.txt"), "r") as f:
        data = f.readlines()
        width, height, maxIter = int(data[0]), int(data[1]), int(data[2])
        dimensions = (width, height)
    
    print("Image dimensions: ", dimensions)
    width, height = dimensions[0], dimensions[1]

elif user_action == 3:
    height = 500
    width = height * 1.5  # width is a float here
    maxIter = 75

else:
    print("Invalid input. Exiting...")
    exit()

if user_action != 3:
    # Define size
    img_size = ((0, 0), (width, height))   
    frac_size = ((-2.2, -1.2), (1.2, 1.2))
    (frac_x0, frac_y0), (frac_x1, frac_y1) = frac_size
    (img_x0, img_y0), (img_x1, img_y1) = img_size
    img_w = img_x1 - img_x0
    img_h = img_y1 - img_y0

    # Define parameters
    frac_xStep = (frac_x1 - frac_x0) / img_w
    frac_yStep = (frac_y1 - frac_y0) / img_h

    # Visualization
    fig, ax = plt.subplots(1, figsize=(18, 12))
    ax.set_title("Mandelbrot Fractal Orbit trap Visualization", fontsize=24)  # Add title here
    fig.canvas.manager.window.title("Mandelbrot Fractal")  # Set the window title
    fig.canvas.manager.window.iconbitmap(rp("assets/images/icon.ico"))  # Set the window icon

    if user_action == 2:
        # Animation setup (optional, if you want to include interaction)
        line1, = ax.plot([], [], linewidth=1, color="blue")  
        lines = []  
        for _ in range(maxIter):
            line2, = ax.plot([], [], alpha=0.8)
            line3, = ax.plot([], [], alpha=0.8)
            lines.append((line2, line3))
        line4, = ax.plot([], [], marker='o', markersize=1, color="white")  