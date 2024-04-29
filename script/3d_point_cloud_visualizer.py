import open3d as o3d
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox
import matplotlib.pyplot as plt

def apply_color_by_attribute(cloud, attribute):
    colors = plt.get_cmap('viridis')(attribute)[:, :3]
    cloud.colors = o3d.utility.Vector3dVector(colors)

def voxel_downsample(cloud, voxel_size=0.05):
    return cloud.voxel_down_sample(voxel_size)

def compute_statistics(cloud, options):
    results = {}
    points = np.asarray(cloud.points)
    
    if options['mean']:
        results['mean'] = np.mean(points, axis=0)
    if options['standard_deviation']:
        results['standard_deviation'] = np.std(points, axis=0)
    
    if options['density']:
        bounding_box = cloud.get_axis_aligned_bounding_box()
        volume = bounding_box.volume()
        results['density'] = len(points) / volume if volume > 0 else 0

    return results

def compute_geometric_properties(cloud, options):
    results = {}
    
    if options['centroid']:
        results['centroid'] = cloud.get_center()
    if options['bounding_box']:
        bounding_box = cloud.get_axis_aligned_bounding_box()
        results['bounding_box'] = str(bounding_box)
        results['volume'] = bounding_box.volume()

    return results

def visualize_ply(file_path, downsample=False, color_map=None, stats_options=None, geom_options=None):
    cloud = o3d.io.read_point_cloud(file_path)
    if downsample:
        cloud = voxel_downsample(cloud)

    if color_map == 'depth' and cloud.has_points():
        zs = np.asarray(cloud.points)[:, 2]
        zs_normalized = (zs - zs.min()) / (zs.max() - zs.min())
        apply_color_by_attribute(cloud, zs_normalized)

    stats_results = compute_statistics(cloud, stats_options)
    geom_results = compute_geometric_properties(cloud, geom_options)

    o3d.visualization.draw_geometries([cloud])

    output_info = '\n'.join([f"{key}: {value}" for key, value in {**stats_results, **geom_results}.items()])
    messagebox.showinfo("Point Cloud Analysis Results", output_info)

def gui():
    root = tk.Tk()
    root.title("3D Point Cloud Visualizer")
    root.geometry("400x400")

    downsample_var = tk.BooleanVar()
    color_map_var = tk.StringVar(value='none')

    open_button = tk.Button(root, text="Open PLY File", command=lambda: open_file_dialog())
    open_button.pack(pady=10)

    downsample_check = tk.Checkbutton(root, text="Apply Downsampling", variable=downsample_var)
    downsample_check.pack(anchor='w')

    color_map_label = tk.Label(root, text="Color Map:")
    color_map_label.pack(anchor='w')

    color_map_menu = tk.OptionMenu(root, color_map_var, 'none', 'depth')
    color_map_menu.pack(anchor='w')

    # Options for statistics and geometric properties
    stats_options = {'mean': tk.BooleanVar(), 'standard_deviation': tk.BooleanVar(), 'density': tk.BooleanVar()}
    geom_options = {'centroid': tk.BooleanVar(), 'bounding_box': tk.BooleanVar(), 'volume': tk.BooleanVar()}

    # Creating checkboxes for each option
    for key in stats_options:
        tk.Checkbutton(root, text=f"{key.replace('_', ' ').title()}", variable=stats_options[key]).pack(anchor='w')
    for key in geom_options:
        tk.Checkbutton(root, text=f" {key.replace('_', ' ').title()}", variable=geom_options[key]).pack(anchor='w')

    def open_file_dialog():
        file_path = filedialog.askopenfilename(title='Select a PLY File', filetypes=[('PLY Files', '*.ply')])
        if file_path:
            visualize_ply(file_path, downsample_var.get(), color_map_var.get(),
                          {k: v.get() for k, v in stats_options.items()},
                          {k: v.get() for k, v in geom_options.items()})

    root.mainloop()

if __name__ == "__main__":
    gui()
