import tkinter as tk
try:
	import ttkbootstrap as tb
	THEME_AVAILABLE = True
except ImportError:
	tb = None
	THEME_AVAILABLE = False
from main import ModernApp

def main():
	if THEME_AVAILABLE and tb is not None:
		root = tb.Window(themename="superhero")
	else:
		root = tk.Tk()
	app = ModernApp(root)
	root.mainloop()

if __name__ == "__main__":
	main()
