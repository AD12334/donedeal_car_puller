input_file = "unmatched_titles.log"

with open(input_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

chunk_size = 300  # number of lines per batch
for i in range(0, len(lines), chunk_size):
    chunk = lines[i:i + chunk_size]
    with open(f"batch_{i//chunk_size + 1}.txt", "w", encoding="utf-8") as out:
        out.writelines(chunk)

print("✅ Split complete.")
