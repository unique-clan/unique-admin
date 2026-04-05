#!/usr/bin/env python3
import os
import sys
import re
from pathlib import Path

# map-name_name_0.999.demo
demo_pattern = re.compile(r'^(.+?)_(.+?)_(\d+\.\d{3})\.demo$')


def check_demo_name(file_path: Path, map_name: str) -> (str, float):
    demo_name = file_path.stem
    if demo_pattern.match(file_path.name):
        demo_map_name = demo_name[:len(map_name)]
        player_name, time_str = demo_name[len(map_name) + 1:].rsplit('_', 1)
        if demo_map_name != file_path.parent.name:
            print(f"WARNING: demo {file_path} is misplaced in the wrong map directory")
            return "error", -1

        time = float(time_str)
        return player_name, time
    else:
        print(f"WARNING: demo {file_path} does not follow naming convention, ignored")
    return "error", -1


def tidy_up_map_demos(path: Path, noop: bool) -> bool:
    map_name = path.name
    best_records_per_player = {}
    error_list = []

    # find the best demo per player
    for file_path in path.glob("*.demo"):
        player_name, time = check_demo_name(file_path, map_name)

        # ignore errored demos
        if time < 0:
            error_list.append(file_path)
            continue

        # check if a better demo already exists
        if player_name in best_records_per_player and best_records_per_player[player_name][0] < time:
            continue
        best_records_per_player[player_name] = (time, file_path)

    # sort demos by time and just keep top 10
    top_10_list = list(best_records_per_player.values())

    def sort_by_time(info):
        return info[0]

    top_10_list.sort(key=sort_by_time)
    top_10_list = top_10_list[:10]
    top_10_paths = [path for _, path in top_10_list]

    print("Successes:")
    print(f"Number of records present: {len(top_10_paths)}")
    print(f"Top 10 players: {[p.name for _, p in top_10_list]}")

    # delete slower demos
    for file_path in path.glob("*.demo"):
        if file_path in error_list or file_path in top_10_paths:
            continue

        if noop:
            print(f"Script would delete {file_path}")
        else:
            pass
    return len(error_list) > 0


def check_maps(path: str, noop: bool):
    """Assume that we have directories with map-names"""
    errors_happened: bool = False
    try:
        # List only directories
        directories = [d for d in os.listdir(path) if os.path.isdir(os.path.join(path, d))]
        for directory in directories:
            directory_path = Path(os.path.join(path, directory))
            print(f"### Map: {directory_path.name} ###")
            error = tidy_up_map_demos(directory_path, noop)
            errors_happened = errors_happened or error

    except FileNotFoundError:
        print(f"Error: The path '{path}' does not exist.")
    except PermissionError:
        print(f"Error: Permission denied for '{path}'.")
    except Exception as e:
        print(f"Unexpected error: {e}")

    return sys.exit(int(errors_happened))


def main():
    if len(sys.argv) >= 4:
        print(f"Usage: python {sys.argv[0]} <path> [--noop]")
        sys.exit(1)

    path = sys.argv[1]
    noop: bool = False
    if sys.argv[2] and sys.argv[2].endswith("noop"):
        noop = True
    check_maps(path, noop)


if __name__ == "__main__":
    main()
