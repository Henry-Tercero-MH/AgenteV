#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Launcher para FalconEPSA
Ejecuta la app GUI sin conflictos
"""

if __name__ == '__main__':
    import tkinter as tk
    from app_gui import FalconEPSAApp
    
    root = tk.Tk()
    app = FalconEPSAApp(root)
    root.mainloop()
