import unittest
from unittest.mock import MagicMock, patch
from typing import Any, Optional
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
    def test_save_texture_uses_new_underscore_filename_format(self, mock_dialog):
        app = DummyApp()
        app.framerate_var = MagicMock(get=MagicMock(return_value=10))
        gif_stub = type("GifStub", (), {"filename": "Feuer.gif"})()
        app.gif_image = gif_stub
        file_ops.save_texture(app)
        self.assertTrue(mock_dialog.called)
        initialfile = mock_dialog.call_args.kwargs.get("initialfile", "")
        self.assertTrue(initialfile.startswith("Feuer_1_1_10_0_LOOP_SMOOTH_ROTATE"))
        self.assertTrue(initialfile.endswith(".png"))

    def test_generate_lsl_script_enhanced_contains_new_format_and_flags(self):
        app = DummyApp()
        script = file_ops.generate_lsl_script_v2(app, "Feuer", 4, 3, 10.0)
        self.assertIn("New format: Feuer_4_3_10.0_0_LOOP_SMOOTH_ROTATE", script)
        self.assertIn("list defaultEffects = [LOOP, SMOOTH];", script)
        self.assertIn("integer defaultMovement = ROTATE;", script)
        self.assertIn("llParseStringKeepNulls(texture, [\".\", \";\", \"_\"], []);", script)
        self.assertIn("if(token == \"PING\" && (i + 1) < count)", script)
        self.assertIn("if(nextToken == \"PONG\")", script)
        self.assertIn("resolved += [PING_PONG];", script)

    def test_generate_lsl_script_legacy_kept(self):
        app = DummyApp()
        script = file_ops.generate_lsl_script_legacy(app, "Feuer", 4, 3, 10.0)
        self.assertIn("// Texture: Feuer;4;3;10.0", script)
        self.assertIn("llParseString2List(texture,[\";\"],[]);", script)

if __name__ == "__main__":
    unittest.main()
