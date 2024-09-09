from dataclasses import dataclass, field
from functools import total_ordering, singledispatchmethod
from re import match as _match
from typing import Self


__all__ = ["InvalidSemanticVersionError", "SemanticVersionInfo"]
__version__ = "1.0.0"


SV_PATTERN_PR = r"(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
SV_PATTERN_BM = r"(?:\+(?P<build>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?"
SV_PATTERN = r"^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)" + SV_PATTERN_PR + SV_PATTERN_BM + "$"


class InvalidSemanticVersionError(ValueError):
    pass


@total_ordering
@dataclass(slots=True, frozen=True, repr=True)
class SemanticVersionInfo:
    major: int = 0
    minor: int = 0
    patch: int = 0
    prerelease: str = field(default="", compare=False)
    build: str = field(default="", compare=False)

    # Validation of arguments occurs post init of class
    def __post_init__(self) -> None:
        for key, val in self.as_dict().items():
            if key in ("major", "minor", "patch"):
                if not isinstance(val, int):
                    raise TypeError(
                        "Version `{}` number must be a positive integer. Got `{}` of type `{}`."
                        .format(key, val, type(val).__name__)
                    )
                
                if val < 0:
                    raise ValueError(
                        "Version number must be positive. Got `{}` for key `{}`."
                        .format(val, key)
                    )
                                    
            elif key in ("prerelease", "build"):
                if not isinstance(val, str):
                    raise TypeError("Version `{}` identifier must be a string. Got `{}` of type `{}`."
                                    .format(key, val, type(val).__name__))

                pattern = SV_PATTERN_PR if key == "prerelease" else SV_PATTERN_BM
                if _match(pattern, val) is None:
                    raise ValueError(
                        f"Invalid version `{key}` identifier. Got `{val}`."
                    ) 

            else:
                raise ValueError(
                    "Invalid key `{}`. Expected major, minor, patch, prerelease, or build."
                    .format(key)
                )
        
    @singledispatchmethod
    @classmethod
    def parse(cls, version: str | dict[str, int | str], /) -> Self:
        raise NotImplementedError("Unable to parse type `{}` into `{}`"
                        .format(type(version).__name__, cls.__name__))
    
    @parse.register
    @classmethod
    def _(cls, version: str):
        semver_match = _match(SV_PATTERN, version)

        if semver_match is None:
            raise InvalidSemanticVersionError("Unable to parse string. Invalid semantic versioning: `{}`"
                                    .format(version))

        return cls(
            int(semver_match.group("major")),
            int(semver_match.group("minor")),
            int(semver_match.group("patch")),
            semver_match.group("prerelease") or "",
            semver_match.group("build") or "",
        )

    @parse.register
    @classmethod
    def _(cls, version: dict):
        return cls(
            int(version.get("major", 0)),
            int(version.get("minor", 0)),
            int(version.get("patch", 0)),
            str(version.get("prerelease", "")),
            str(version.get("build", ""))
        )


    # Return as tuple, dict, or str types
    
    def as_tuple(self, no_id: bool = False) -> tuple[int, int, int] | tuple[int, int, int, str, str]:
        if no_id:
            return (self.major, self.minor, self.patch)
        return (self.major, self.minor, self.patch, self.prerelease, self.build)
    
    def as_dict(self, no_id: bool = False) -> dict[str, int | str]:
        version_dict = {
            "major": self.major,
            "minor": self.minor,
            "patch": self.patch,
            "prerelease": self.prerelease,
            "build": self.build 
        }

        if no_id:
            version_dict.pop("prerelease")
            version_dict.pop("build")

        return version_dict

    def as_str(self) -> str:
        semver = f"{self.major}.{self.minor}.{self.patch}"

        if self.prerelease:
            semver += f"-{self.prerelease}"
        
        if self.build:
            semver += f"+{self.build}"

        return semver

    # Bump versions, return new class instance    

    def bump_major(self) -> Self:
        return self.__class__(self.major + 1, 0, 0)
    
    def bump_minor(self) -> Self:
        return self.__class__(self.major, self.minor + 1, 0)
    
    def bump_patch(self) -> Self:
        return self.__class__(self.major, self.minor, self.patch + 1)
    

    def __str__(self) -> str:
        return self.as_str()
    
    # Comparison operators
    # The rest are filled in by functools.total_ordering
    # Only compare major, minor, and patch values
    def __eq__(self, other: Self | str | tuple[int, int, int] | dict[str, int | str]) -> bool:
        if not isinstance(other, type(self)):
            return NotImplemented
            # raise TypeError("Cannot compare `{}` with `{}`."
                            # .format(type(self).__name__, type(other).__name__))
        if isinstance(other, tuple):
            if len(other) != 3:
                raise ValueError("Semantic version tuple must be of length 3. Got `{}`"
                                 .format(other))

            return (self.major, self.minor, self.patch) == other
        
        if isinstance(other, str) or isinstance(other, dict):
            return (self.major, self.minor, self.patch) == self.parse(other)

        return self.as_tuple(no_id=False) == other.as_tuple(no_id=False)
        
    
    def __lt__(self, other: Self | str | tuple[int, int, int] | dict[str, int | str]) -> bool:
        if isinstance(other, tuple):
            if len(other) != 3:
                raise ValueError("Semantic version tuple must be of length 3. Got `{}` with length `{}`"
                                 .format(other, len(other)))

            return (self.major, self.minor, self.patch) < other
        
        if isinstance(other, str) or isinstance(other, dict):
            return (self.major, self.minor, self.patch) < self.parse(other)
        
        if not isinstance(other, type(self)):
            return NotImplemented
            # raise TypeError("Cannot compare `{}` with `{}`."
            #                 .format(type(self).__name__, type(other).__name__))
        
        return self.as_tuple(no_id=False) < other.as_tuple(no_id=False)
    
    
    def compare_strict(self, other: Self | str | tuple[int, int, int, str, str] | dict[str, int | str]) -> bool:
        if isinstance(other, str):
            return self.as_str() == other
        
        elif isinstance(other, dict):
            return self.as_dict() == other
        
        elif isinstance(other, tuple):
            return self.as_tuple() == other

        else:
            raise TypeError("Cannot compare `{}` with `{}`."
                            .format(type(self).__name__, type(other).__name__))

if __name__ == "__main__":
    version1 = SemanticVersionInfo.parse("1.2.3")

    print(version1.as_str())
    print(version1.as_tuple())
    print(version1.as_tuple(no_id=True))
    print(version1.as_dict())
    print(version1.as_dict(no_id=True))
    print(version1.bump_major())
    print(version1.bump_minor())
    print(version1.bump_patch())

    version2 = SemanticVersionInfo(1, 3, 2)

    print(version1 == version2)
    print(version1 > version2)
    print(version1 < version2)

    print(version1 == (1, 2, 3))
    print(version1 == "1.2.3")
    print(version1 == {"major": 1, "minor": 2, "patch": 3})
    
    print(version1.compare_strict("1.2.3")) 
    print(version1.compare_strict("1.2.3-rc1"))
    print(version1.compare_strict((1, 2, 3, '', '')))

    print([str(_) for _ in sorted([
        SemanticVersionInfo(1, 2, 3),
        SemanticVersionInfo(1, 3, 0),
        SemanticVersionInfo(2, 0, 0),
        SemanticVersionInfo(1, 2, 4),
    ])])

    # TODO: Add unit test cases