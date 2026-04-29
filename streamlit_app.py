import os
import sys
import runpy

# Ensure the root directory is in the Python path so imports work correctly
root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.append(root_dir)

# Path to the actual Streamlit app
app_path = os.path.join(root_dir, "dashboards", "app.py")

# Execute the dashboard app seamlessly
if __name__ == "__main__":
    runpy.run_path(app_path, run_name="__main__")
