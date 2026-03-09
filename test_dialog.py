import tkinter as tk
from tkinter import filedialog
root = tk.Tk()
root.withdraw()

try:
    # Try different namespaces or variables
    root.tk.eval('catch {namespace eval ::tk::dialog::file { variable showHiddenVar 0; variable showHiddenBtn 1 }}')
    root.tk.eval('set ::tk::dialog::file::showHiddenVar 0')
    print("Variables set")
except Exception as e:
    print("Error:", e)
    
print("Showing dialog...")
# We can't actually show it and check, but we can dump the tk variables.
print(root.tk.eval('info vars ::tk::dialog::file::*'))
