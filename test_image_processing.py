import unittest
from PIL import Image
import numpy as np
from image_processing import apply_effects

from typing import Any, Optional

class TestImageProcessing(unittest.TestCase):
    def setUp(self):
        # Erzeuge ein einfaches RGBA-Testbild (rot)
        self.img = Image.new("RGBA", (32, 32), (255, 0, 0, 255))
        class Dummy:
            gif_grayscale: Any  # type: ignore
            texture_grayscale: Any  # type: ignore
            gif_sharpen: Any  # type: ignore
            texture_sharpen: Any  # type: ignore
            gif_sharpen_value: Any  # type: ignore
            texture_sharpen_value: Any  # type: ignore
            gif_blur: Any  # type: ignore
            texture_blur: Any  # type: ignore
            gif_blur_value: Any  # type: ignore
            texture_blur_value: Any  # type: ignore
            gif_transparency: Any  # type: ignore
            texture_transparency: Any  # type: ignore
            gif_transparency_value: Any  # type: ignore
            texture_transparency_value: Any  # type: ignore
            gif_colorintensity_active: Any  # type: ignore
            texture_colorintensity_active: Any  # type: ignore
            gif_colorintensity: Any  # type: ignore
            texture_colorintensity: Any  # type: ignore
        self.dummy = Dummy()
        # Simuliere GUI-Variablen für Filter
        # explizit deklarieren für Pylance
        self.dummy.gif_grayscale = type('V', (), {'get': lambda s: False})()
        self.dummy.texture_grayscale = type('V', (), {'get': lambda s: False})()
        self.dummy.gif_sharpen = type('V', (), {'get': lambda s: False})()
        self.dummy.texture_sharpen = type('V', (), {'get': lambda s: False})()
        self.dummy.gif_sharpen_value = type('V', (), {'get': lambda s: 1.0})()
        self.dummy.texture_sharpen_value = type('V', (), {'get': lambda s: 1.0})()
        self.dummy.gif_blur = type('V', (), {'get': lambda s: False})()
        self.dummy.texture_blur = type('V', (), {'get': lambda s: False})()
        self.dummy.gif_blur_value = type('V', (), {'get': lambda s: 0})()
        self.dummy.texture_blur_value = type('V', (), {'get': lambda s: 0})()
        self.dummy.gif_transparency = type('V', (), {'get': lambda s: False})()
        self.dummy.texture_transparency = type('V', (), {'get': lambda s: False})()
        self.dummy.gif_transparency_value = type('V', (), {'get': lambda s: 1.0})()
        self.dummy.texture_transparency_value = type('V', (), {'get': lambda s: 1.0})()
        self.dummy.gif_colorintensity_active = type('V', (), {'get': lambda s: False})()
        self.dummy.texture_colorintensity_active = type('V', (), {'get': lambda s: False})()
        self.dummy.gif_colorintensity = type('V', (), {'get': lambda s: 0.5})()
        self.dummy.texture_colorintensity = type('V', (), {'get': lambda s: 0.5})()

    def test_apply_effects_identity(self):
        # Ohne Filter bleibt das Bild gleich
        out = apply_effects(self.dummy, self.img.copy(), "gif")
        self.assertEqual(out.size, self.img.size)
        self.assertTrue(np.array_equal(np.array(out), np.array(self.img)))

    def test_apply_grayscale(self):
        self.dummy.gif_grayscale.get = lambda: True
        out = apply_effects(self.dummy, self.img.copy(), "gif")
        arr = np.array(out)
        self.assertTrue((arr[...,0] == arr[...,1]).all() and (arr[...,1] == arr[...,2]).all())

if __name__ == "__main__":
    unittest.main()
