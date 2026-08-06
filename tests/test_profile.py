from __future__ import annotations

import os
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile
import tomllib
import unittest


ROOT = Path(__file__).resolve().parents[1]
PROFILE_ID = "catos-hyprland-noctaliav5"
MANIFEST = ROOT / "usr/share/catdot/profiles" / PROFILE_ID / "profile.toml"
CONTENT = ROOT / "usr/share" / PROFILE_ID


class CatdotProfileTests(unittest.TestCase):
    def setUp(self) -> None:
        catdot = os.environ.get("CATDOT_BIN")
        if not catdot:
            self.fail("CATDOT_BIN must point to the real catdot executable")
        self.catdot = Path(catdot)
        self.assertTrue(self.catdot.is_file(), self.catdot)

    def stage_profile(self, root: Path) -> tuple[Path, Path]:
        metadata = root / "usr/share/catdot/profiles" / PROFILE_ID
        content = root / "usr/share" / PROFILE_ID
        metadata.mkdir(parents=True)
        shutil.copy2(MANIFEST, metadata / "profile.toml")
        shutil.copytree(CONTENT, content)
        return root / "usr/share/catdot/profiles", content

    def fake_pacman(self, root: Path, packages: list[str]) -> Path:
        bindir = root / "bin"
        bindir.mkdir()
        installed = root / "installed-packages"
        installed.write_text("\n".join(packages) + "\n", encoding="utf-8")
        pacman = bindir / "pacman"
        pacman.write_text(
            "#!/bin/sh\n"
            "if [ \"$1\" = -Qq ]; then cat \"$CATDOT_TEST_INSTALLED\"; exit 0; fi\n"
            "if [ \"$1\" = -S ]; then exit 0; fi\n"
            "printf 'unexpected pacman invocation: %s\\n' \"$*\" >&2\n"
            "exit 64\n",
            encoding="utf-8",
        )
        pacman.chmod(pacman.stat().st_mode | stat.S_IXUSR)
        sudo = bindir / "sudo"
        sudo.write_text("#!/bin/sh\nexec \"$@\"\n", encoding="utf-8")
        sudo.chmod(sudo.stat().st_mode | stat.S_IXUSR)
        return bindir

    def run_catdot(
        self,
        temp: Path,
        home: Path,
        profile_root: Path,
        bindir: Path,
        *args: str,
    ) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env.update(
            {
                "CATDOT_PROFILE_ROOT": str(profile_root),
                "CATDOT_TEST_INSTALLED": str(temp / "installed-packages"),
                "HOME": str(home),
                "XDG_STATE_HOME": str(home / ".local/state"),
                "PATH": f"{bindir}:/usr/bin:/bin",
            }
        )
        return subprocess.run(
            [str(self.catdot), *args],
            input="y\n",
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env,
            check=False,
        )

    def test_manifest_is_accepted_by_catdot(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            temp = Path(tmpdir)
            profile_root, _ = self.stage_profile(temp)
            result = subprocess.run(
                [str(self.catdot), "validate", str(profile_root)],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_select_and_update_preserve_custom_and_dconf_seeds(self) -> None:
        manifest = tomllib.loads(MANIFEST.read_text(encoding="utf-8"))
        packages = manifest["packages"]
        managed = set(manifest["manage"])
        self.assertNotIn(".config/hypr/custom/catos-hyprland-noctaliav5/input.lua", managed)
        self.assertNotIn(".config/dconf/user", managed)

        with tempfile.TemporaryDirectory() as tmpdir:
            temp = Path(tmpdir)
            home = temp / "home"
            home.mkdir()
            profile_root, staged_content = self.stage_profile(temp)
            bindir = self.fake_pacman(temp, packages)

            selected = self.run_catdot(
                temp,
                home,
                profile_root,
                bindir,
                "select",
                PROFILE_ID,
                "--packages=verify",
            )
            self.assertEqual(selected.returncode, 0, selected.stderr)

            managed_hypr = home / ".config/hypr/hyprland.lua"
            managed_noctalia = home / ".config/noctalia/config.toml"
            custom_seed = home / ".config/hypr/custom/catos-hyprland-noctaliav5/input.lua"
            dconf_seed = home / ".config/dconf/user"
            for path in (managed_hypr, managed_noctalia, custom_seed, dconf_seed):
                self.assertTrue(path.is_file(), path)

            custom_seed.write_text("user input settings\n", encoding="utf-8")
            dconf_seed.write_bytes(b"user dconf database")
            (staged_content / ".config/hypr/hyprland.lua").write_text(
                managed_hypr.read_text(encoding="utf-8") + "\n-- managed-update\n",
                encoding="utf-8",
            )
            (staged_content / ".config/noctalia/config.toml").write_text(
                managed_noctalia.read_text(encoding="utf-8") + "\n# managed-update\n",
                encoding="utf-8",
            )
            (staged_content / ".config/hypr/custom/catos-hyprland-noctaliav5/input.lua").write_text(
                "profile input update\n", encoding="utf-8"
            )
            (staged_content / ".config/dconf/user").write_bytes(b"profile dconf update")

            updated = self.run_catdot(
                temp,
                home,
                profile_root,
                bindir,
                "update",
                PROFILE_ID,
            )
            self.assertEqual(updated.returncode, 0, updated.stderr)
            self.assertIn("managed-update", managed_hypr.read_text(encoding="utf-8"))
            self.assertIn("managed-update", managed_noctalia.read_text(encoding="utf-8"))
            self.assertEqual(custom_seed.read_text(encoding="utf-8"), "user input settings\n")
            self.assertEqual(dconf_seed.read_bytes(), b"user dconf database")

    def test_profile_has_no_display_manager_payload_or_hard_dependency(self) -> None:
        manifest = tomllib.loads(MANIFEST.read_text(encoding="utf-8"))
        self.assertNotIn("greetd", manifest["packages"])
        self.assertNotIn("noctalia-greeter", manifest["packages"])
        self.assertFalse((ROOT / "catos-hyprland-noctaliav5.install").exists())
        self.assertFalse(any("greetd" in str(path) for path in CONTENT.rglob("*")))

    def test_installed_profile_payload_is_readable_by_regular_users(self) -> None:
        files = [MANIFEST, *(path for path in CONTENT.rglob("*") if path.is_file())]
        for path in files:
            self.assertTrue(
                path.stat().st_mode & stat.S_IROTH,
                f"profile payload is not world-readable: {path.relative_to(ROOT)}",
            )


if __name__ == "__main__":
    unittest.main()
