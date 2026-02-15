
from PIL import Image, ImageTk
import math

def show_gif_frame(self):
	if not self.gif_frames:
		self.gif_canvas.config(image="")
		self.show_texture()
		return
	frame = self.gif_frames[self.current_frame]
	self.gif_canvas.update_idletasks()
	canvas_w = self.gif_canvas.winfo_width()
	canvas_h = self.gif_canvas.winfo_height()
	self.texture_canvas.update_idletasks()
	texture_w = self.texture_canvas.winfo_width()
	texture_h = self.texture_canvas.winfo_height()
	max_w = min(canvas_w, texture_w) if texture_w > 10 else canvas_w
	max_h = min(canvas_h, texture_h) if texture_h > 10 else canvas_h
	if max_w < 10 or max_h < 10:
		max_w, max_h = 256, 256
	frame = frame.resize((max_w, max_h), Image.Resampling.LANCZOS)
	frame = apply_effects(self, frame, prefix="gif")
	img = ImageTk.PhotoImage(frame)
	self._gif_img_ref = img
	self.gif_canvas.config(image=img)
	self.show_texture()

def show_texture(self):
	if not self.gif_frames:
		self.texture_canvas.config(image="")
		return
	import math, os
	tex_w = self.width_var.get() if self.width_var.get() > 0 else 2048
	tex_h = self.height_var.get() if self.height_var.get() > 0 else 2048
	frame_count = self.frame_count
	tiles_x = math.ceil(math.sqrt(frame_count))
	tiles_y = math.ceil(frame_count / tiles_x)
	tile_w = tex_w // tiles_x
	tile_h = tex_h // tiles_y
	from PIL import ImageColor
	bg_rgba = (0,0,0,0)
	try:
		bg_rgba = ImageColor.getcolor(self.bg_color, "RGBA")
	except Exception:
		pass
	sheet = Image.new("RGBA", (tex_w, tex_h), bg_rgba)
	for idx, frame in enumerate(self.gif_frames):
		tx = idx % tiles_x
		ty = idx // tiles_x
		f = frame.resize((tile_w, tile_h), Image.Resampling.LANCZOS)
		f = apply_effects(self, f, prefix="texture")
		x = tx * tile_w
		y = ty * tile_h
		sheet.paste(f, (x, y))
	if hasattr(self, 'borderless_var') and self.borderless_var.get():
		bbox = sheet.getbbox()
		if bbox:
			sheet = sheet.crop(bbox)
	self.texture_image = sheet
	self.texture_canvas.update_idletasks()
	canvas_w = self.texture_canvas.winfo_width()
	canvas_h = self.texture_canvas.winfo_height()
	if canvas_w < 10 or canvas_h < 10:
		canvas_w, canvas_h = 256, 256
	preview = sheet.resize((canvas_w, canvas_h), Image.Resampling.LANCZOS)
	img = ImageTk.PhotoImage(preview)
	self._texture_img_ref = img
	self.texture_canvas.config(image=img)

def update_previews(self):
	show_gif_frame(self)

def apply_effects(self, img, prefix):
	from PIL import ImageEnhance, ImageFilter
	if self.__dict__[f'{prefix}_grayscale'].get():
		img = img.convert("L").convert("RGBA")
	else:
		if img.mode != "RGBA":
			img = img.convert("RGBA")
	if self.__dict__[f'{prefix}_sharpen'].get():
		factor = self.__dict__[f'{prefix}_sharpen_value'].get()
		img = ImageEnhance.Sharpness(img).enhance(factor)
	if self.__dict__[f'{prefix}_blur'].get():
		radius = self.__dict__[f'{prefix}_blur_value'].get()
		if radius > 0:
			img = img.filter(ImageFilter.GaussianBlur(radius))
	if self.__dict__[f'{prefix}_transparency'].get():
		value = self.__dict__[f'{prefix}_transparency_value'].get()
		alpha = img.split()[-1].point(lambda p: int(p * value))
		img.putalpha(alpha)
	if self.__dict__[f'{prefix}_colorintensity_active'].get():
		colorint = self.__dict__[f'{prefix}_colorintensity'].get()
		if colorint != 0.5:
			if colorint < 0.5:
				import numpy as np
				arr = np.array(img).astype(float)
				factor = colorint * 2
				arr[..., :3] = arr[..., :3] * factor + 255 * (1 - factor)
				if img.mode == "RGBA" or (arr.shape[-1] == 4):
					img = Image.fromarray(np.clip(arr, 0, 255).astype('uint8'), "RGBA")
				else:
					img = Image.fromarray(np.clip(arr, 0, 255).astype('uint8'), "RGB")
			else:
				from PIL import ImageEnhance
				factor = 1.0 + (colorint - 0.5) * 2
				img = ImageEnhance.Color(img).enhance(factor)
	return img
