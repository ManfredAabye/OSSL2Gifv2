
import math
import os
from tkinter import filedialog, messagebox, ttk
from PIL import Image
from translations import tr
from image_processing import update_previews, apply_effects

def load_gif_compat(self):
	"""
	Kompatibilitäts-Wrapper für alte Aufrufe: Lädt ein GIF und aktualisiert alle GUI-Elemente wie früher in einer Methode.
	"""
	file = filedialog.askopenfilename(filetypes=[("GIF", "*.gif")])
	if not file:
		return
	self._load_gif_frames(file)
	self._setup_frame_select()
	self._reset_play_button()
	self._update_status()
	self._update_preview()
	# Textur erst nach vollständigem Laden und Setup anzeigen
	if hasattr(self, '_update_texture'):
		self._update_texture()

def load_gif(self):
	"""
	Öffnet einen Dialog, lädt ein GIF und initialisiert die GUI über Hilfsmethoden.
	"""
	file = filedialog.askopenfilename(filetypes=[("GIF", "*.gif")])
	if not file:
		return
	self._load_gif_frames(file)
	self._setup_frame_select()
	self._reset_play_button()
	self._update_status()
	self._update_preview()
	# Textur nach GIF-Ladevorgang immer anzeigen
	if hasattr(self, '_update_texture'):
		self._update_texture()

def _load_gif_frames(self, file):
	"""Lädt die Frames aus einer GIF-Datei und setzt gif_image, gif_frames, frame_count, current_frame."""
	self.gif_image = Image.open(file)
	frames = []
	try:
		while True:
			frames.append(self.gif_image.copy())
			self.gif_image.seek(len(frames))
	except EOFError:
		pass
	if not frames:
		frames.append(self.gif_image.copy())
	print(f"[DEBUG] Frames geladen: {len(frames)}")
	self.gif_frames = frames
	self.frame_count = len(frames)
	self.current_frame = 0
	self.playing = False

def _setup_frame_select(self):
	"""Initialisiert die Spinbox für die Frame-Auswahl."""
	value = 0
	if hasattr(self, 'frame_select_spin') and self.frame_select_spin is not None:
		self.frame_select_spin.destroy()
	self.frame_select_spin = ttk.Spinbox(self.add_frame_btn.master, from_=0, to=max(0, self.frame_count-1), textvariable=self.frame_select_var, width=5, state="readonly")
	self.frame_select_spin.pack(side="right")
	self.frame_select_var.set(value)
	self.current_frame = 0

def _reset_play_button(self):
	"""Setzt den Play-Button auf den Startwert zurück."""
	self.play_btn.config(text=tr('play', self.lang) or "Play ▶")

def _update_status(self):
	"""Aktualisiert die Statusleiste mit der Frame-Anzahl."""
	self.maxframes_var.set(self.frame_count)
	self.status.config(text=f"{tr('frame_count', self.lang)}: {self.frame_count}")

def _update_preview(self):
	"""Aktualisiert die GIF-Vorschau in der GUI."""
	if hasattr(self, 'root') and self.root is not None:
		self.root.update_idletasks()
		update_previews(self)

def delete_gif(self):
	"""
	Setzt alle GIF- und Textur-bezogenen Attribute und GUI-Elemente zurück.
	Wird z.B. aufgerufen, wenn ein GIF entladen oder ein neues geladen werden soll.
	"""
	self.gif_image = None
	self.gif_frames = []
	self.frame_count = 0
	self.current_frame = 0
	self.playing = False
	self.texture_image = None
	self.texture_canvas.config(image="")
	self.gif_canvas.config(image="")
	self.status.config(text="")
	self.maxframes_var.set(0)
	if hasattr(self, 'frame_select_spin') and self.frame_select_spin is not None:
		self.frame_select_spin.destroy()
		self.frame_select_spin = None
	if hasattr(self, 'add_frame_btn') and self.add_frame_btn is not None:
		self.add_frame_btn.config(state="disabled")
	if hasattr(self, 'play_btn') and self.play_btn is not None:
		self.play_btn.config(text=tr('play', self.lang) or "Play ▶", state="disabled")

def save_gif(self):
	if not self.gif_frames:
		messagebox.showerror("Fehler", "Kein GIF geladen.")
		return
	file = filedialog.asksaveasfilename(defaultextension=".gif", filetypes=[("GIF", "*.gif")])
	if not file:
		return
	try:
		frames = [apply_effects(self, f.resize((self.width_var.get(), self.height_var.get())), "gif") for f in self.gif_frames]
		duration = self.framerate_var.get()
		frames[0].save(file, save_all=True, append_images=frames[1:], loop=0, duration=duration)
		messagebox.showinfo("Info", "GIF gespeichert.")
	except Exception as e:
		messagebox.showerror("Fehler", str(e))

def save_texture(self):
	if self.texture_image is None:
		messagebox.showerror("Fehler", "Keine Textur vorhanden.")
		return
	name = "texture"
	if self.gif_image and hasattr(self.gif_image, 'filename'):
		name = os.path.splitext(os.path.basename(self.gif_image.filename))[0]
	frame_count = self.frame_count
	tiles_x = math.ceil(math.sqrt(frame_count))
	tiles_y = math.ceil(frame_count / tiles_x)
	speed_val = self.framerate_var.get()
	speed = f"{speed_val};0"
	ext = self.export_format_var.get().lower()
	defext = f".{ext}"
	filetypes = [(ext.upper(), f"*.{ext}") for ext in ["png", "jpg", "bmp"]]
	file = filedialog.asksaveasfilename(defaultextension=defext, initialfile=f"{name};{tiles_x};{tiles_y};{speed}.{ext}", filetypes=filetypes)
	if not file:
		return
	fmt = self.export_format_var.get().upper()
	if fmt == "JPG":
		fmt = "JPEG"
	try:
		img = self.texture_image
		if fmt == "JPEG":
			img = img.convert("RGB")
		img.save(file, format=fmt)
		messagebox.showinfo("Info", "Textur gespeichert.")
	except Exception as e:
		messagebox.showerror("Fehler", str(e))

def export_lsl(self):
	if not self.gif_frames:
		messagebox.showerror("Fehler", "Kein GIF geladen.")
		return
	frame_count = self.frame_count
	tiles_x = math.ceil(math.sqrt(frame_count))
	tiles_y = math.ceil(frame_count / tiles_x)
	name = "texture"
	if self.gif_image and hasattr(self.gif_image, 'filename'):
		name = os.path.splitext(os.path.basename(self.gif_image.filename))[0]
	speed = 10.0
	lsl = generate_lsl_script(self, name, tiles_x, tiles_y, speed)
	file = filedialog.asksaveasfilename(defaultextension=".lsl", initialfile=f"{name}.lsl", filetypes=[("LSL", "*.lsl"), ("Text", "*.txt")])
	if not file:
		return
	try:
		with open(file, "w", encoding="utf-8") as f:
			f.write(lsl)
		messagebox.showinfo("Info", "LSL-Skript exportiert.")
	except Exception as e:
		messagebox.showerror("Fehler", str(e))

def generate_lsl_script(self, name, tiles_x, tiles_y, speed):
		length = tiles_x * tiles_y
		return f'''// LSL Texture Animation Script\n// Generated by OSSL2Gif\n// Texture: {name};{tiles_x};{tiles_y};{speed}\n\ninteger animOn = TRUE;\nlist effects = [LOOP];\ninteger movement = 0;\ninteger face = ALL_SIDES;\ninteger sideX = {tiles_x};\ninteger sideY = {tiles_y};\nfloat start = 0.0;\nfloat length = {length};\nfloat speed = {speed};\n\ninitAnim() {{\n    if(animOn) {{\n        integer effectBits;\n        integer i;\n        for(i = 0; i < llGetListLength(effects); i++) {{\n            effectBits = (effectBits | llList2Integer(effects,i));\n        }}\n        integer params = (effectBits|movement);\n        llSetTextureAnim(ANIM_ON|params,face,sideX,sideY,start,length,speed);\n    }}\n    else {{\n        llSetTextureAnim(0,face,sideX,sideY,start,length,speed);\n    }}\n}}\n\nfetch() {{\n     string texture = llGetInventoryName(INVENTORY_TEXTURE,0);\n            llSetTexture(texture,face);\n            // llParseString2List braucht als Trennzeichen eine Liste!\n            list data  = llParseString2List(texture,[";"],[]);\n            string X = llList2String(data,1);\n            string Y = llList2String(data,2);\n            string Z = llList2String(data,3);\n            sideX = (integer) X;\n            sideY = (integer) Y;\n            speed = (float) Z;\n            length = (float)(sideX * sideY);\n            if (speed) \n                initAnim();\n}}\n\ndefault\n{{\n    state_entry()\n    {{\n        llSetTextureAnim(FALSE, face, 0, 0, 0.0, 0.0, 1.0);\n        fetch();\n    }}\n    changed(integer what)\n    {{\n        if (what & CHANGED_INVENTORY)\n        {{\n            fetch();\n        }}\n    }}\n}}\n'''
