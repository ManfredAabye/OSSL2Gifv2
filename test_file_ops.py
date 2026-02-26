import unittest
from unittest.mock import MagicMock, patch
from typing import Any, Optional
import os
import tempfile
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
        self.gif_image: Optional[Any] = None
        self.status = MagicMock()
        self.maxframes_var = MagicMock()
        self.lsl_effect_loop_var = MagicMock(get=MagicMock(return_value=True))
        self.lsl_effect_smooth_var = MagicMock(get=MagicMock(return_value=True))
        self.lsl_effect_reverse_var = MagicMock(get=MagicMock(return_value=False))
        self.lsl_effect_ping_pong_var = MagicMock(get=MagicMock(return_value=False))
        self.lsl_movement_var = MagicMock(get=MagicMock(return_value='ROTATE'))
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

    @patch("file_ops.filedialog.asksaveasfilename", return_value=None)
    def test_save_texture_uses_plain_base_filename(self, mock_dialog):
        app = DummyApp()
        app.framerate_var = MagicMock(get=MagicMock(return_value=10))
        gif_stub = type("GifStub", (), {"filename": "Feuer.gif"})()
        app.gif_image = gif_stub
        file_ops.save_texture(app)
        self.assertTrue(mock_dialog.called)
        initialfile = mock_dialog.call_args.kwargs.get("initialfile", "")
        self.assertEqual(initialfile, "Feuer.png")

    def test_generate_lsl_script_enhanced_contains_new_format_and_flags(self):
        app = DummyApp()
        script = file_ops.generate_lsl_script_v2(app, "Feuer", 4, 3, 10.0)
        self.assertIn("Texture-Animation-Script.lsl", script)
        self.assertIn("list defaultEffects = [LOOP, SMOOTH];", script)
        self.assertIn("integer defaultMovement = ROTATE;", script)
        self.assertIn("collectNotecardPlaylist()", script)
        self.assertIn("parseLegacyTextureName", script)
        self.assertIn("dataserver(key query_id, string data)", script)
        self.assertIn("parseConfigLine(data);", script)

    def test_generate_lsl_notecard_contains_values(self):
        content = file_ops.generate_lsl_notecard("Feuer", 4, 3, 10.0, ["LOOP", "SMOOTH"], "ROTATE")
        self.assertIn("columns=4", content)
        self.assertIn("rows=3", content)
        self.assertIn("fps=10.0", content)
        self.assertIn("effects=LOOP, SMOOTH", content)
        self.assertIn("movement=ROTATE", content)
        self.assertIn("Texture Notecard: Feuer.notecard", content)

    def test_save_texture_creates_notecard_named_like_texture(self):
        app = DummyApp()
        app.framerate_var = MagicMock(get=MagicMock(return_value=10))
        with tempfile.TemporaryDirectory() as tmpdir:
            texture_path = os.path.join(tmpdir, "bildname2.png")
            with patch("file_ops.filedialog.asksaveasfilename", return_value=texture_path):
                file_ops.save_texture(app)
            self.assertTrue(os.path.exists(texture_path))
            self.assertTrue(os.path.exists(os.path.join(tmpdir, "bildname2.notecard")))

    def test_export_lsl_does_not_create_notecard(self):
        app = DummyApp()
        app.framerate_var = MagicMock(get=MagicMock(return_value=10))
        gif_stub = type("GifStub", (), {"filename": "bildname.gif"})()
        app.gif_image = gif_stub
        with tempfile.TemporaryDirectory() as tmpdir:
            script_path = os.path.join(tmpdir, "Texture-Animation-Script.lsl")
            with patch("file_ops.filedialog.asksaveasfilename", return_value=script_path):
                file_ops.export_lsl(app)
            self.assertTrue(os.path.exists(script_path))
            self.assertFalse(os.path.exists(os.path.join(tmpdir, "bildname.notecard")))

if __name__ == "__main__":
    unittest.main()
