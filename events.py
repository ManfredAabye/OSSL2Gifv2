
from tkinter import messagebox, colorchooser, ttk
from PIL import Image
from translations import tr

def reset_settings(self):
	self.width_var.set(2048)
	self.height_var.set(2048)
	self.bg_color = "#00000000"
	self.bg_box_color = "#000000"
	self.bg_color_box.config(bg=self.bg_box_color)
	self.borderless_var.set(0)
	# Label und Tooltip für Randlos explizit zurücksetzen/übersetzen
	if hasattr(self, 'borderless_label') and self.borderless_label is not None:
		self.borderless_label.config(text=tr('borderless', self.lang) or "Randlos")
	if hasattr(self, 'tooltips') and 'borderless_label' in self.tooltips:
		self.tooltips['borderless_label'].set_text(tr('tt_borderless', self.lang))
	self.framerate_var.set(10)
	self.export_format_var.set("PNG")
	self.maxframes_var.set(64)
	self.lang_var.set("de")
	for prefix in ("gif", "texture"):
		self.__dict__[f'{prefix}_grayscale'].set(0)
		self.__dict__[f'{prefix}_sharpen'].set(0)
		self.__dict__[f'{prefix}_blur'].set(0)
		self.__dict__[f'{prefix}_transparency'].set(0)
		self.__dict__[f'{prefix}_sharpen_value'].set(2.5)
		self.__dict__[f'{prefix}_blur_value'].set(3.5)
		self.__dict__[f'{prefix}_transparency_value'].set(0.5)
		self.__dict__[f'{prefix}_colorintensity'].set(0.5)
		self.__dict__[f'{prefix}_colorintensity_active'].set(0)
	self.update_language()
	self.current_frame = 0
	self.playing = False
	if self.gif_image and hasattr(self.gif_image, 'filename'):
		file = self.gif_image.filename
		try:
			self.gif_image = Image.open(file)
			self.gif_frames = []
			while True:
				self.gif_frames.append(self.gif_image.copy())
				self.gif_image.seek(len(self.gif_frames))
		except EOFError:
			pass
		except Exception:
			self.gif_frames = []
		self.frame_count = len(self.gif_frames)
		self.current_frame = 0
		if self.gif_frames:
			self.show_gif_frame()
	else:
		self.update_previews()

def on_maxframes_changed(self, *args):
	max_frames = self.maxframes_var.get()
	if hasattr(self, 'gif_frames') and len(self.gif_frames) > max_frames:
		removed = len(self.gif_frames) - max_frames
		self.gif_frames = self.gif_frames[:max_frames]
		self.frame_count = len(self.gif_frames)
		self.status.config(text=f"{removed} Bilder entfernt. Gesamt: {self.frame_count}")
		value = self.frame_select_var.get()
		self.frame_select_spin.destroy()
		self.frame_select_spin = ttk.Spinbox(self.add_frame_btn.master, from_=0, to=max(0, self.frame_count-1), textvariable=self.frame_select_var, width=5, state="readonly")
		self.frame_select_spin.pack(side="left", padx=2, before=self.add_frame_btn)
		self.frame_select_var.set(min(value, self.frame_count-1))
		self.update_previews()

def choose_bg_color(self, event=None):
	color = colorchooser.askcolor(color=self.bg_box_color, title="Hintergrundfarbe wählen")
	if color and color[1]:
		self.bg_box_color = color[1]
		if self.bg_box_color.lower() == "#000000":
			self.bg_color = "#00000000"
		else:
			self.bg_color = self.bg_box_color
		self.bg_color_box.config(bg=self.bg_box_color)
		self.update_previews()

def add_selected_frame_to_texture(self):
	idx = self.frame_select_var.get()
	if not self.gif_frames or idx < 0 or idx >= len(self.gif_frames):
		messagebox.showerror("Fehler", "Ungültige Bildnummer.")
		return
	max_frames = self.maxframes_var.get()
	if len(self.gif_frames) >= max_frames:
		messagebox.showerror("Fehler", f"Maximale Bildanzahl ({max_frames}) erreicht.")
		return
	frame = self.gif_frames[idx].copy()
	self.gif_frames.append(frame)
	self.frame_count = len(self.gif_frames)
	value = self.frame_select_var.get()
	self.frame_select_spin.destroy()
	self.frame_select_spin = ttk.Spinbox(self.add_frame_btn.master, from_=0, to=max(0, self.frame_count-1), textvariable=self.frame_select_var, width=5, state="readonly")
	self.frame_select_spin.pack(side="left", padx=2, before=self.add_frame_btn)
	self.frame_select_var.set(value)
	self.status.config(text=f"Bild {idx} hinzugefügt. Gesamt: {self.frame_count}")
	self.update_previews()

def change_language(self, event=None):
	self.lang = self.lang_var.get()
	self.update_language()  # Tooltips und Labels übersetzen
	self.update_previews()  # Previews ggf. neu zeichnen
