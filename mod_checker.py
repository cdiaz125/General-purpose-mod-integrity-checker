import os
import zipfile
import ast

MODS_FOLDER = r"C:Enter path of mods folder here"

# -------------------------------
# Utility: scan Mods directory
# -------------------------------
def get_mod_files():
    mod_files = []
    for root, _, files in os.walk(MODS_FOLDER):
        for file in files:
            if file.lower().endswith((".package", ".ts4script")):
                mod_files.append(os.path.join(root, file))
    return mod_files

# -------------------------------
# Check if .ts4script file is valid
# -------------------------------
def check_ts4script(path):
    # Must be a valid ZIP
    if not zipfile.is_zipfile(path):
        return "Invalid .ts4script (not a ZIP archive)"

    try:
        with zipfile.ZipFile(path, "r") as z:
            for name in z.namelist():
                # Sims 4 script mods contain .py or .pyc
                if name.endswith(".py"):
                    try:
                        data = z.read(name).decode("utf-8")
                        ast.parse(data)  # try parsing Python code
                    except Exception as e:
                        return f"Python error inside script: {e}"
    except Exception as e:
        return f"Cannot read .ts4script: {e}"

    return None  # valid


# -------------------------------
# Check if .package file is valid
# -------------------------------
def check_package(path):
    try:
        with open(path, "rb") as f:
            header = f.read(4)
            if header != b"DBPF":
                return "Invalid .package header (missing DBPF)"
            
            # Attempt to read first 1MB (detects truncated/corrupt files)
            f.seek(0)
            chunk = f.read(1_000_000)
            if len(chunk) == 0:
                return "Empty or unreadable .package file"

    except Exception as e:
        return f".package read error: {e}"

    return None  # valid

# -------------------------------
# Main detector
# -------------------------------

def detect_broken_mods():
    files = get_mod_files()
    issues = [];

    for mod in files: 
        if mod.endswith(".ts4script"):
            result = check_ts4script(mod)
            if result:
                issues.append((mod,result))


        elif mod.endswith(".package"):
            result = check_package(mod)
            if result:
                issues.append((mod,result))

    return issues

# -------------------------------
# Run scan
# -------------------------------
if __name__ == "__main__":
    print("\n=== Sims 4 Broken Mod Detector ===\n")
    print("Scanning Mods folder...\n")

    problems = detect_broken_mods()

    if not problems:
        print("No broken mods detected!")
    else:
        print(" BROKEN MODS FOUND:\n")
        for path, issue in problems:
            print(f"[BROKEN] {path}")
            print(f"   → Reason: {issue}\n")

    print("\nScan complete.\n")
