"""Create expendable fixtures only. Re-running preserves every existing file."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SAMPLES = {
    "lecture-notes.txt": b"VETO GENERATED SAMPLE ONLY\nWeek 1: Python basics.\n",
    "study-plan.md": b"# Sample study plan\n- Read notes\n- Practise Python\n",
    "demo-preferences.json": b'{"sample_only": true, "sort_by": "file_type"}\n',
    "sample-screenshot.svg": b'<svg xmlns="http://www.w3.org/2000/svg" width="320" height="180"><rect width="320" height="180" fill="#173e38"/><text x="20" y="90" fill="white">Veto sample image only</text></svg>',
    "unknown-file.dat": b"Expendable sample with unknown extension.\n",
}


def is_link_or_reparse(path: Path) -> bool:
    try:
        attributes = getattr(path.lstat(), 'st_file_attributes', 0)
    except FileNotFoundError:
        attributes = 0
    return path.is_symlink() or bool(attributes & 0x400)


def generate(project_root: Path = ROOT) -> int:
    root = project_root.resolve()
    target = root / "data" / "demo" / "Veto Demo Inbox"
    for candidate in (root, *reversed(target.relative_to(root).parents), target):
        path = candidate if candidate.is_absolute() else root / candidate
        if is_link_or_reparse(path):
            raise RuntimeError("Refusing sample generation through a link or junction.")
    target.mkdir(parents=True, exist_ok=True)
    created = 0
    for name, content in SAMPLES.items():
        destination = target / name
        # Restarting after sorting must not recreate original paths and break undo.
        moved = False
        for category in ('Documents', 'Notes', 'Images', 'Data'):
            folder = target / category
            if is_link_or_reparse(folder):
                raise RuntimeError('Refusing sample generation through a linked output folder.')
            if (folder / name).exists():
                moved = True
                break
        if moved:
            continue
        try:
            with destination.open("xb") as stream:
                stream.write(content)
            created += 1
        except FileExistsError:
            pass  # Never overwrite an existing sample or follow an existing link.
    return created


if __name__ == "__main__":
    print(f"Created {generate()} new sample files in data/demo/Veto Demo Inbox; existing files preserved.")
