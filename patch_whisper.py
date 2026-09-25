with open("ai_functions/voice_to_text.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if "WHISPER_MODEL_NAME = \"small\"" in line:
        lines[i] = line.replace("\"small\"", "\"medium\"")
        break

with open("ai_functions/voice_to_text.py", "w", encoding="utf-8") as f:
    f.writelines(lines)
