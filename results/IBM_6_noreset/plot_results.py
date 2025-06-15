import json
import matplotlib.pyplot as plt
import numpy as np
import sys

# --- 1. Load Data from JSON File ---
filename = 'grover_known_solutions_results.json'
try:
    with open(filename, 'r') as f:
        counts_data = json.load(f)
    print(f"Successfully loaded data from '{filename}'")
except FileNotFoundError:
    print(f"Error: The file '{filename}' was not found.")
    print("Please make sure the JSON file is in the same directory as this script.")
    sys.exit() # Exit the script if the file can't be found
except json.JSONDecodeError:
    print(f"Error: Could not decode JSON. The file '{filename}' may be corrupted or not in valid JSON format.")
    sys.exit()


# --- 2. Define Plotting Parameters ---
# The states you want to highlight
highlight_keys = ["11111100", "11011100", "01111100", "01011100"]

# --- 3. Sort the data for a clean, ordered plot ---
sorted_items = sorted(counts_data.items())
sorted_keys = [item[0] for item in sorted_items]
sorted_values = [item[1] for item in sorted_items]

# --- 4. Create lists for colors and labels based on the highlight keys ---
highlight_color = '#ff7f0e'  # A vibrant orange
default_color = '#1f77b4'   # A standard blue
colors = [highlight_color if key in highlight_keys else default_color for key in sorted_keys]
xtick_labels = [key if key in highlight_keys else '' for key in sorted_keys]

# --- 5. Create the plot ---
fig, ax = plt.subplots(figsize=(20, 10))
ax.bar(range(len(sorted_keys)), sorted_values, color=colors)

# --- 6. Customize the plot ---
ax.set_title("Measurement Outcomes from Grover's Algorithm", fontsize=20, pad=20)
ax.set_xlabel('Quantum States', fontsize=16)
ax.set_ylabel('Counts', fontsize=16)
ax.set_xticks(np.arange(len(sorted_keys)))
ax.set_xticklabels(xtick_labels, rotation=75, ha='right', fontsize=12)
ax.tick_params(axis='x', which='major', pad=5)
ax.margins(x=0.01)  # Add a little padding to the sides

# --- 7. Create a custom legend ---
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor=highlight_color, edgecolor='black', label='Target Solutions'),
                   Patch(facecolor=default_color, edgecolor='black', label='Other Outcomes')]
ax.legend(handles=legend_elements, fontsize=14)

plt.tight_layout()
# You can uncomment the next line to save the plot as a file
plt.savefig('highlighted_histogram.png')
#plt.show()