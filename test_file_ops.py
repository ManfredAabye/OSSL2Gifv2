import unittest
from unittest.mock import MagicMock, patch
from PIL import Image
import file_ops

class DummyApp:
    def __init__(self):
        # Mindestens 1 Frame, um Division-by-Zero zu vermeiden
        frame = Image.new("RGBA", (32, 32), (255, 0, 0, 255))
        self.gif_frames = [frame]
        self.frame_count = 1
        self.current_frame = 0
        self.playing = False
        self.width_var = MagicMock(get=MagicMock(return_value=32))
        self.height_var = MagicMock(get=MagicMock(return_value=32))
        self.framerate_var = MagicMock(get=MagicMock(return_value=100))
        self.export_format_var = MagicMock(get=MagicMock(return_value="PNG"))
        self.texture_image = Image.new("RGBA", (32, 32), (255, 0, 0, 255))
        self.gif_image = None
        self.status = MagicMock()
        self.maxframes_var = MagicMock()
        self.frame_select_var = MagicMock()
        self.frame_select_spin = MagicMock()
        self.add_frame_btn = MagicMock()
        self.play_btn = MagicMock()
        self.texture_canvas = MagicMock()
        self.gif_canvas = MagicMock()
    def _update_status(self):
        pass
    def _update_preview(self):
        pass
    def _reset_play_button(self):
        pass
    def _setup_frame_select(self):
        pass
    def _update_texture(self):
        pass

class TestFileOps(unittest.TestCase):
    @patch("file_ops.filedialog.askopenfilename", return_value=None)
    def test_load_gif_cancel(self, mock_dialog):
        app = DummyApp()
        initial_frames = len(app.gif_frames)
        file_ops.load_gif(app)  # Sollte einfach abbrechen
        self.assertEqual(len(app.gif_frames), initial_frames)

    @patch("file_ops.filedialog.asksaveasfilename", return_value=None)
    def test_save_gif_cancel(self, mock_dialog):
        app = DummyApp()
        initial_frames = len(app.gif_frames)
        file_ops.save_gif(app)  # Sollte einfach abbrechen
        self.assertEqual(len(app.gif_frames), initial_frames)

    @patch("file_ops.filedialog.asksaveasfilename", return_value=None)
    def test_save_texture_cancel(self, mock_dialog):
        app = DummyApp()
        file_ops.save_texture(app)  # Sollte einfach abbrechen
        self.assertIsNotNone(app.texture_image)

if __name__ == "__main__":
    unittest.main()
