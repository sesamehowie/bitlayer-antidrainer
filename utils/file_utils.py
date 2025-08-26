from pathlib import Path


def read_txt(file_name: str | Path) -> list[str]:
    with open(file=file_name, mode="r") as f:
        data = f.read().splitlines()
    return data


def write_txt(
    new_filename: Path | str, data_list: list | tuple, mode: str = "w"
) -> bool | None:
    with open(new_filename, mode=mode) as file:
        for item in data_list:
            file.write(item + "\n")
        return
