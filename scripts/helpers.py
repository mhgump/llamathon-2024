from requirements_detector import from_requirements_txt
from requirements_detector import from_requirements_dir
from requirements_detector import from_requirements_blob
from requirements_detector import from_pyproject_toml
from requirements_detector import from_setup_py
from requirements_detector import CouldNotParseRequirements
from requirements_detector import RequirementsNotFound
from requirements_detector.requirement import DetectedRequirement
from pathlib import Path
from typing import List, Tuple


def detected_requirements_to_str(req: DetectedRequirement) -> Tuple[str, str]:
    return req.name, req.pip_format()


def find_requirements(path: str) -> List[DetectedRequirement]:
    """Adapted from https://github.com/landscapeio/requirements-detector/blob/master/requirements_detector/detect.py
    """
    requirements = []
    path = Path(path)
    setup_py = path / "setup.py"
    if setup_py.exists() and setup_py.is_file():
        try:
            requirements = from_setup_py(setup_py)
            requirements.sort()
            return requirements
        except CouldNotParseRequirements:
            pass
    poetry_toml = path / "pyproject.toml"
    if poetry_toml.exists() and poetry_toml.is_file():
        try:
            requirements = from_pyproject_toml(poetry_toml)
            if len(requirements) > 0:
                requirements.sort()
                return requirements
        except CouldNotParseRequirements:
            pass

    for reqfile_name in ("requirements.txt", "requirements.pip"):
        reqfile = path / reqfile_name
        if reqfile.exists and reqfile.is_file():
            try:
                requirements += from_requirements_txt(reqfile)
            except CouldNotParseRequirements as e:
                pass

    requirements_dir = path / "requirements"
    if requirements_dir.exists() and requirements_dir.is_dir():
        from_dir = from_requirements_dir(requirements_dir)
        if from_dir is not None:
            requirements += from_dir

    from_blob = from_requirements_blob(path)
    if from_blob is not None:
        requirements += from_blob

    requirements = list(set(requirements))
    if len(requirements) > 0:
        requirements.sort()
        return requirements

    return []