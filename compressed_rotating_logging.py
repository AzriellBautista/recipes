from logging.handlers import RotatingFileHandler
from typing import override, Literal
import os
import shutil
import bz2
import gzip
import lzma
import zipfile
import tarfile


__all__ = [
    "CompressedRotatingFileHandler",
]


"""
Implements a custom rotating file handler that automatically compresses log 
files. This is achieved by overriding the `doRollover` method and adding a new 
parameter `compression` to the constructor. The `compression` parameter 
determines the compression method used for the log files. The supported 
compression methods are:

- `zip`: Zip compression
- `gz`: Gzip compression
- `bz2`: Bzip2 compression
- `xz` or `lzma`: Xz and Lzma compression
- `tar`: Tar archive without compression
- `tar.gz`, `tar.bz2`, `tar.xz`, or `tar.lzma`: Tar archive with compression
"""

# Valid compression literals
Compression = Literal[
    "zip", 
    "gz", "bz2", "xz", "lzma",
    "tar", "tar.gz", "tar.bz2", "tar.xz", "tar.lzma"
]


class CompressedRotatingFileHandler(RotatingFileHandler):
    """
    A custom rotating file handler that automatically compresses backup log files.
    """
    # # Below __init__ removes function signature hints in editors
    # def __init__(self, *args, compression: Compression = "gz", **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.compression = compression

    def __init__(
            self, 
            filename: str | os.PathLike[str], 
            compression: Compression = "tar.gz",  # new parameter
            mode: str = "a", 
            maxBytes: int = 0, 
            backupCount: int = 0, 
            encoding: str | None = None, 
            delay: bool = False, 
            errors: str | None = None,
        ) -> None:

        super().__init__(
            filename, mode, maxBytes, backupCount, encoding, delay, errors
        )

        if compression not in Compression.__args__:
            raise ValueError(
                f"Invalid compression mode: {compression}. " +
                "Expected one of the following: {}" 
                .format(", ".join(Compression.__args__))
            )

        self.compression = compression


    @override
    def doRollover(self) -> None:
        """
        Overridden to compress the log file after rotation.
        """
        
        if self.stream:
            self.stream.close()
            self.stream = None  # type: ignore

        if self.backupCount > 0:
            for i in range(self.backupCount - 1, 0, -1):
                src = f"{self.baseFilename}.{i}.{self.compression}"
                dest_file = f"{self.baseFilename}.{i + 1}.{self.compression}"

                if os.path.exists(src):
                    if os.path.exists(dest_file):
                        os.remove(dest_file)
                    os.rename(src, dest_file)

            # The base log file (not compressed yet)
            log_file = self.baseFilename

            dest_file = f"{self.baseFilename}.1.{self.compression}"
            
            # Compress the base log file
            if os.path.exists(log_file):
                self._compress_log_file(log_file, dest_file)
                os.remove(log_file)

        if not self.delay:
            self.stream = self._open()


    def _compress_log_file(self, src: str, dest: str) -> None:
        """
        Compresses the log file using the specified compression method.
        """
        self.compression: str # type hint as str

        if self.compression == "zip":
            with zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(src, arcname=os.path.basename(src))

        elif self.compression == "gz":
            with open(src, "rb") as f_in, gzip.open(dest, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)

        elif self.compression == "bz2":
            with open(src, "rb") as f_in, bz2.open(dest, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)

        elif self.compression == "xz" or self.compression == "lzma":
            with open(src, "rb") as f_in, lzma.open(dest, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)

        elif self.compression.startswith("tar"):
            mode = self._get_tar_mode()
            with tarfile.open(dest, mode) as tarf:
                tarf.add(src, arcname=os.path.basename(src))

        else:
            raise ValueError(f"Unsupported compression: {self.compression}")
        
        
    def _get_tar_mode(self) -> str:
        """
        Helper function to get the appropriate tar mode based on the compression
        type.
        """
        match self.compression:
            case "tar":
                return "w"
            case "tar.gz":
                return "w:gz"
            case "tar.bz2":
                return "w:bz2"
            case "tar.xz" | "tar.lzma":
                return "w:xz"
            case _:
                raise ValueError(
                    "Unsupported tar compression: {}"
                    .format(self.compression)
                )