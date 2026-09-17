import argparse
import io
import json
import tarfile
import uuid
from pathlib import Path

import tomli

from reptor.lib.plugins.Base import Base


def dir_or_file(path):
    p = Path(path)
    if not p.exists() and not p.is_dir() and not p.is_file():
        raise argparse.ArgumentTypeError(f"readable_dir:{path} is not a valid path")
    return p


def build_tarinfo(name, size):
    info = tarfile.TarInfo(name=name)
    info.size = size
    return info


class PackArchive(Base):
    meta = {
        "name": "PackArchive",
        "summary": "Pack directories into a .tar.gz file",
    }

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.directories: list[Path] = kwargs.get("directories") or []
        self.output = kwargs.get("output")

    @classmethod
    def add_arguments(cls, parser, plugin_filepath=None):
        super().add_arguments(parser, plugin_filepath=plugin_filepath)

        parser.add_argument("directories", nargs="+", type=dir_or_file)
        parser.add_argument(
            "-o",
            "--output",
            type=argparse.FileType("wb"),
            default="packed_archive.tar.gz",
        )

    def load_file(self, path_input: Path):
        if not path_input.exists() or not path_input.is_file():
            return None
        elif path_input.suffix == ".toml":
            data_dict = tomli.loads(path_input.read_text(encoding='utf-8'))
        else:
            data_dict = json.loads(path_input.read_text(encoding='utf-8'))
        if not isinstance(data_dict, dict) or not isinstance(data_dict.get('format'), str):
            return None
        self.normalize_notes(data_dict)
        return data_dict

    def normalize_notes(self, data_dict: dict):
        """TOML cannot represent null; restore parent/checked nulls expected by the UI."""
        for notes in (
            data_dict.get("default_notes"),
            data_dict.get("notes"),
            (data_dict.get("project_type") or {}).get("default_notes"),
        ):
            if not isinstance(notes, list):
                continue
            for note in notes:
                if not isinstance(note, dict) or note.get("file"):
                    continue
                note.setdefault("parent", None)
                note.setdefault("checked", None)

    def reassign_toplevel_note_order(self, notes_list: list):
        """Set consecutive order values on top-level notes based on list order."""
        order = 1
        for note in notes_list:
            if isinstance(note, dict) and not note.get("parent"):
                note["order"] = order
                order += 1

    def resolve_note_includes(
        self,
        data_dict: dict,
        key: str,
        base_dir: Path,
        _stack: set[Path] | None = None,
    ) -> list[tuple[Path, dict]]:
        """Expand file references in a notes list (recursively). Returns included pairs."""
        notes_list = data_dict.get(key)
        if not isinstance(notes_list, list):
            return []

        stack = _stack if _stack is not None else set()
        merged = []
        included: list[tuple[Path, dict]] = []
        for item in notes_list:
            if isinstance(item, dict) and item.get("file"):
                notes_path = (base_dir / item["file"]).resolve()
                if notes_path in stack:
                    raise ValueError(f"Circular notes include: {notes_path}")
                loaded = self.load_file(notes_path)
                if not loaded:
                    raise ValueError(f"Invalid reference to notes file: {notes_path}")
                if loaded.get("format") != "notes/v1":
                    raise ValueError(
                        f'Notes file must have format "notes/v1": {notes_path}'
                    )
                stack.add(notes_path)
                try:
                    nested = self.resolve_note_includes(
                        loaded, "notes", notes_path.parent, stack
                    )
                finally:
                    stack.discard(notes_path)
                if isinstance(loaded.get("notes"), list):
                    merged.extend(loaded["notes"])
                included.append((notes_path, loaded))
                included.extend(nested)
            else:
                merged.append(item)

        data_dict[key] = merged
        if included:
            self.reassign_toplevel_note_order(merged)
        return included

    def _sidecar_sources(
        self,
        included: list[tuple[Path, dict]],
        dest_images: str,
        dest_files: str,
    ) -> list[tuple[Path, str]]:
        sources = []
        for notes_path, notes_data in included:
            prefixes = {notes_path.stem}
            if notes_data.get("id"):
                prefixes.add(str(notes_data["id"]))
            for prefix in prefixes:
                sources.append((notes_path.parent / f"{prefix}-images", dest_images))
                sources.append((notes_path.parent / f"{prefix}-files", dest_files))
        return sources

    def _id_stem_sources(
        self, path_input: Path, resource_id: str, kinds: tuple[str, ...]
    ) -> list[tuple[Path, str]]:
        parent, stem = path_input.parent, path_input.stem
        sources = []
        for kind in kinds:
            dest = f"{resource_id}-{kind}"
            sources.append((parent / f"{resource_id}-{kind}", dest))
            sources.append((parent / f"{stem}-{kind}", dest))
        return sources

    def add_to_archive(self, tar: tarfile.TarFile, path_input: Path, data_dict: dict, is_subresource=False):
        if not data_dict.get("id"):
            data_dict["id"] = str(uuid.uuid4())

        included = self.resolve_note_includes(
            data_dict, "notes", path_input.parent
        ) + self.resolve_note_includes(data_dict, "default_notes", path_input.parent)

        file_sources: list[tuple[Path, str]] = []
        format = data_dict.get('format', '')
        rid = data_dict["id"]
        if format.startswith("projects/"):
            dest_images, dest_files = f"{rid}-images", f"{rid}-files"
            file_sources += self._id_stem_sources(path_input, rid, ("images", "files"))
            file_sources += self._sidecar_sources(included, dest_images, dest_files)

            project_type = data_dict.get("project_type")
            projecttype_path_input = path_input
            if not project_type:
                raise ValueError(f'Project type is missing in project: {path_input}')
            elif project_type.get('file'):
                projecttype_path_input = path_input.parent / project_type['file']
                project_type = self.load_file(projecttype_path_input)
                if not project_type:
                    raise ValueError(f'Invlaid reference to project type file: {projecttype_path_input}')
                data_dict['project_type'] = project_type
            self.add_to_archive(tar=tar, path_input=projecttype_path_input, data_dict=project_type, is_subresource=True)
        elif format.startswith("projecttypes/"):
            dest_assets = f"{rid}-assets"
            file_sources += self._id_stem_sources(path_input, rid, ("assets",))
            file_sources += self._sidecar_sources(included, dest_assets, dest_assets)
        elif format.startswith("templates/"):
            file_sources += self._id_stem_sources(path_input, rid, ("images",))
        elif format.startswith("notes/"):
            dest_images, dest_files = f"{rid}-images", f"{rid}-files"
            file_sources += self._id_stem_sources(path_input, rid, ("images", "files"))
            file_sources += self._sidecar_sources(included, dest_images, dest_files)

        self.normalize_notes(data_dict)

        # Add files to archive
        # Translate human-friendly names to archive names based on IDs
        for d_dir, dd in file_sources:
            # Always add file list to data_dict
            data_key = dd.split("-")[-1]
            data_dict.setdefault(data_key, [])

            # Add directory contents to archive
            if d_dir.exists() and d_dir.is_dir():
                tar.add(d_dir, arcname=dd, recursive=True)
                for path_file in d_dir.glob("*"):
                    # Add file entry to data_dict
                    data_file = next(filter(lambda f: f.get('name') == path_file.name, data_dict.get(data_key, [])), None)
                    if not data_file:
                        data_file = {
                            'name': path_file.name,
                        }
                        data_dict[data_key].append(data_file)
                    if not data_file.get('id'):
                        data_file['id'] = str(uuid.uuid4())
                     
        # Add to archive
        if not is_subresource:
            data_json = json.dumps(data_dict, indent=2)
            tar.addfile(
                build_tarinfo(
                    name=data_dict["id"] + ".json", size=len(data_json)
                ),
                fileobj=io.BytesIO(data_json.encode()),
            )
        return True


    def run(self):
        if not self.directories:
            return
        with tarfile.open(fileobj=self.output, mode="w:gz") as tar:
            for path_dir in self.directories:
                if path_dir.exists() and path_dir.is_dir():
                    # Add NOTICE files at top level
                    notice_path = path_dir / "NOTICE"
                    if notice_path.exists() and notice_path.is_file():
                        notice_filename = "NOTICE"
                        if notice_filename in tar.getnames():
                            i = 0
                            while True:
                                i += 1
                                notice_filename = f"NOTICE ({str(i)})"
                                if notice_filename not in tar.getnames():
                                    break
                        tar.add(notice_path, arcname=notice_filename)

                    # Add files to archive
                    for path_input in list(path_dir.glob("*.toml")) + list(
                        path_dir.glob("*.json")
                    ):
                        data_dict = self.load_file(path_input)
                        if not data_dict:
                            continue
                        self.add_to_archive(tar=tar, path_input=path_input, data_dict=data_dict)
                elif path_dir.exists() and path_dir.is_file():
                    data_dict = self.load_file(path_dir)
                    if not data_dict:
                        raise ValueError(f"Could not load file: {path_dir}")
                    self.add_to_archive(tar=tar, path_input=path_dir, data_dict=data_dict)

        self.success(f"Packed contents to {self.output.name}")


loader = PackArchive
