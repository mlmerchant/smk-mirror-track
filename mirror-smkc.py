import sys
import os

def is_map_data_line(line):
    return line.startswith("#") and len(line.strip()) == 65

def extract_map_data(lines):
    in_map = False
    start_index = 0
    map_lines = []

    for i, line in enumerate(lines):
        if line.strip() == "#MAP":
            in_map = True
            start_index = i + 1
            continue
        if in_map:
            if is_map_data_line(line):
                map_lines.append(line.strip()[1:])  # skip the '#'
            else:
                break

    return start_index, map_lines

def reverse_full_map(map_lines):
    if len(map_lines) % 4 != 0:
        raise ValueError("MAP section not aligned to 4-line rows")

    reversed_lines = []
    for i in range(0, len(map_lines), 4):
        # Each group of 4 lines = one 128-tile row (each line is 32 tiles = 64 hex chars)
        row_tiles = []
        for line in map_lines[i:i+4]:
            row_tiles.extend([line[j:j+2] for j in range(0, 64, 2)])

        assert len(row_tiles) == 128

        # Mirror the row
        row_tiles.reverse()

        # Re-split into 4 lines of 32 tiles (64 hex chars)
        for j in range(0, 128, 32):
            reversed_line = "#" + ''.join(row_tiles[j:j+32]) + "\n"
            reversed_lines.append(reversed_line)

    return reversed_lines

def replace_map_section(original_lines, start_index, new_map_lines):
    out = original_lines[:start_index] + new_map_lines

    # Skip original 512 MAP lines
    remaining = original_lines[start_index + len(new_map_lines):]
    out += remaining
    return out

def main():
    if len(sys.argv) != 2:
        print("Usage: python reverse_track.py <file.smkc>")
        sys.exit(1)

    path = sys.argv[1]
    if not os.path.isfile(path):
        print("File not found:", path)
        sys.exit(1)

    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    start_index, map_lines = extract_map_data(lines)

    if len(map_lines) != 512:
        print(f"Unexpected MAP line count: {len(map_lines)}. Expected 512.")
        sys.exit(2)

    reversed_map = reverse_full_map(map_lines)
    updated = replace_map_section(lines, start_index, reversed_map)

    out_path = path.replace(".smkc", "-reversed.smkc")
    with open(out_path, 'w', encoding='utf-8') as f:
        f.writelines(updated)

    print("Reversed MAP saved to:", out_path)

if __name__ == "__main__":
    main()
