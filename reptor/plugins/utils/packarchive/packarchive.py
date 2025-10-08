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
        return data_dict

    def add_to_archive(self, tar: tarfile.TarFile, path_input: Path, data_dict: dict, is_subresource=False):
        if not data_dict.get("id"):
            data_dict["id"] = str(uuid.uuid4())

        # Include file directories
        file_dirs = {}
        format = data_dict.get('format', '')
        if format.startswith("projects/"):
            file_dirs |= {
                f"{data_dict['id']}-images": f"{data_dict['id']}-images",
                f"{data_dict['id']}-files": f"{data_dict['id']}-files",
                f"{path_input.stem}-images": f"{data_dict['id']}-images",
                f"{path_input.stem}-files": f"{data_dict['id']}-files",
            }

            # Add project type
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
            file_dirs |= {
                f"{data_dict['id']}-assets": f"{data_dict['id']}-assets",
                f"{path_input.stem}-assets": f"{data_dict['id']}-assets",
            }
        elif format.startswith("templates/"):
            file_dirs |= {
                f"{data_dict['id']}-images": f"{data_dict['id']}-images",
                f"{path_input.stem}-images": f"{data_dict['id']}-images",
            }
        elif format.startswith("notes/"):
            file_dirs |= {
                f"{data_dict['id']}-images": f"{data_dict['id']}-images",
                f"{data_dict['id']}-files": f"{data_dict['id']}-files",
                f"{path_input.stem}-images": f"{data_dict['id']}-images",
                f"{path_input.stem}-files": f"{data_dict['id']}-files",
            }

        # Add files to archive
        # Translate human-friendly names to archive names based on IDs
        for ds, dd in file_dirs.items():
            # Always add file list to data_dict
            data_key = dd.split("-")[-1]
            data_dict.setdefault(data_key, [])

            # Add directory contents to archive
            d_dir = Path(path_input).parent / ds
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
