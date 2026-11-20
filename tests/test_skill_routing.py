import importlib.util
import json
import os
from pathlib import Path
import tempfile
import subprocess
import unittest
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("skill_router", REPO / "discovery/project-skill-router/scripts/skills.py")
router = importlib.util.module_from_spec(spec)
spec.loader.exec_module(router)


class RoutingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records = router.load_catalog()

    def setUp(self):
        parent = REPO / ".local-backups" / "routing-tests"
        parent.mkdir(parents=True, exist_ok=True)
        self.project = Path(tempfile.mkdtemp(prefix="project-", dir=parent))

    def test_search_does_not_read_instruction_bodies(self):
        original = Path.read_text

        def guarded(path, *args, **kwargs):
            if path.name == "SKILL.md":
                raise AssertionError("Search attempted to read a skill body")
            return original(path, *args, **kwargs)

        with patch.object(Path, "read_text", guarded):
            result = router.search(router.load_catalog(), "JUCE DSP", limit=4)
            self.assertLessEqual(len(result), 4)
            self.assertTrue(any("audio" == r["category"] for r in result))
            unreal = router.search(router.load_catalog(), "Unreal Niagara", limit=6)
            self.assertEqual(unreal[0]["id"], "unreal-niagara")
            self.assertNotIn("unreal-behavior-trees", [r["id"] for r in unreal])

    def test_catalog_covers_canonical_skills_and_exclusions(self):
        expected = {p.relative_to(router.LIBRARY).parent.as_posix()
                    for p in router.LIBRARY.rglob("SKILL.md") if "_shared" not in p.parts}
        self.assertEqual(expected, {r["id"] for r in self.records})
        self.assertFalse(any(router.excluded(r["id"]) for r in self.records))
        self.assertFalse(router.excluded("brand-guidelines-community"))

    def test_name_alias_and_dependency_closure(self):
        self.assertEqual(router.lookup(self.records, "vercel-react-best-practices")["id"], "react-best-practices")
        result = router.expand_selection(self.records, ["blender-animation"])
        self.assertIn("blender-core", result)
        self.assertIn("blender-animation", result)

    def test_recommendation_preserves_stack(self):
        (self.project / "package.json").write_text(json.dumps({"dependencies": {"express": "5"}}))
        self.assertEqual(router.recommend(self.project, "")["profiles"], ["general"])
        (self.project / "CMakeLists.txt").write_text("find_package(JUCE CONFIG REQUIRED)")
        self.assertEqual(router.recommend(self.project, "fix audio processing")["profiles"], ["juce"])

    def test_preview_is_read_only(self):
        result = router.selection(self.records, self.project, ["web"], [], apply=False)
        self.assertFalse(result["applied"])
        self.assertFalse((self.project / ".agents").exists())

    def test_links_repeat_replace_and_restore_without_copies(self):
        first = router.selection(self.records, self.project, ["web"], [], apply=True)
        self.assertEqual(len(first["skills"]), 3)
        root = self.project / ".agents/skills"
        source = router.LIBRARY / "frontend-design"
        self.assertEqual((root / "frontend-design").resolve(), source.resolve())
        self.assertTrue(router.is_link(root / "frontend-design"))
        repeat = router.selection(self.records, self.project, [], [], apply=True)
        self.assertEqual(first["skills"], repeat["skills"])
        foreign = root / "project-owned"
        foreign.mkdir()
        (foreign / "SKILL.md").write_text("local authored instructions")
        second = router.selection(self.records, self.project, ["audio"], [], apply=True, replace=True)
        self.assertEqual(len(second["skills"]), 2)
        self.assertFalse((root / "frontend-design").exists())
        self.assertTrue((source / "SKILL.md").is_file())
        self.assertTrue((foreign / "SKILL.md").is_file())
        ignored = (root / ".gitignore").read_text()
        self.assertIn("/audio-dsp-review/", ignored)
        self.assertNotIn("/project-owned/", ignored)
        # Simulate a fresh clone: portable manifest remains; machine-local links/state do not.
        state = json.loads((self.project / ".agents/.skill-links.local.json").read_text())
        for name in state["links"]:
            path = root / name
            self.assertEqual(path.parent.resolve(), root.resolve())
            if path.is_symlink():
                path.unlink()
            else:
                os.rmdir(path)
        (self.project / ".agents/.skill-links.local.json").unlink()
        restored = router.selection(self.records, self.project, [], [], apply=True)
        self.assertEqual(second["skills"], restored["skills"])

    def test_unmanaged_collision_is_detected_before_any_mutation(self):
        occupied = self.project / ".agents/skills/frontend-design"
        occupied.mkdir(parents=True)
        (occupied / "SKILL.md").write_text("user-owned")
        with self.assertRaisesRegex(ValueError, "collision"):
            router.selection(self.records, self.project, ["web"], [], apply=True)
        self.assertFalse((occupied.parent / "frontend-ui-engineering").exists())
        self.assertEqual((occupied / "SKILL.md").read_text(), "user-owned")

    def test_redirected_project_root_is_not_modified(self):
        agents = self.project / ".agents"
        agents.mkdir()
        router.link_directory(REPO / "discovery", agents / "skills")
        with self.assertRaisesRegex(ValueError, "redirected"):
            router.selection(self.records, self.project, ["web"], [], apply=True)
        self.assertFalse((REPO / "discovery/frontend-design").exists())

    @unittest.skipUnless(os.name == "nt", "Windows junction installer")
    def test_installer_replaces_junction_without_moving_target(self):
        # Default TEMP is commonly C:, while the shared library/backup is on D:.
        home = Path(tempfile.mkdtemp(prefix="skill-routing-installer-"))
        sentinel = self.project / "canonical-library"
        sentinel.mkdir()
        (sentinel / "preserve.txt").write_text("canonical files must not move")
        (home / ".agents").mkdir()
        router.link_directory(sentinel, home / ".agents/skills")
        env = {**os.environ, "ROUTING_INSTALLER": str(REPO / "setup-shared-skills.ps1"), "ROUTING_TEST_HOME": str(home)}
        subprocess.run(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command",
                        "& $env:ROUTING_INSTALLER -UserRoot $env:ROUTING_TEST_HOME"],
                       env=env, check=True, capture_output=True)
        self.assertEqual((sentinel / "preserve.txt").read_text(), "canonical files must not move")
        self.assertEqual((home / ".agents/skills").resolve(), (REPO / "discovery").resolve())


if __name__ == "__main__":
    unittest.main()
