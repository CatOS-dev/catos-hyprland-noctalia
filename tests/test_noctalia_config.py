from pathlib import Path
import tomllib
import unittest


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "usr/share/catos-hyprland-noctaliav5/.config/noctalia/config.toml"


class NoctaliaConfigTests(unittest.TestCase):
    def test_builtin_template_ids_include_hyprland(self) -> None:
        data = tomllib.loads(CONFIG.read_text(encoding="utf-8"))
        self.assertIn("hyprland", data["theme"]["templates"]["builtin_ids"])


if __name__ == "__main__":
    unittest.main()
