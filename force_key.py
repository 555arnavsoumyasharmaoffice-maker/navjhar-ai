import os
import re

with open("ai_functions/gemini_helper.py", "r") as f:
    code = f.read()

# Force ignore environment variable
code = code.replace('os.environ.get("GEMINI_API_KEY", key1 + key2)', 'key1 + key2')

with open("ai_functions/gemini_helper.py", "w") as f:
    f.write(code)

with open("ai_functions/voice_to_text.py", "r") as f:
    code2 = f.read()
code2 = code2.replace('os.environ.get("GEMINI_API_KEY", "AQ.Ab8RN6KG-fwYzup2QrE" + "Xx0HulRQTqGtSbpLesYQZAzT6dnNcCg")', '"AQ.Ab8RN6KG-fwYzup2QrE" + "Xx0HulRQTqGtSbpLesYQZAzT6dnNcCg"')
with open("ai_functions/voice_to_text.py", "w") as f:
    f.write(code2)

with open("main.py", "r") as f:
    code3 = f.read()
code3 = code3.replace('os.environ.get("GEMINI_API_KEY", "AQ.Ab8RN6KG-fwYzup2QrE" + "Xx0HulRQTqGtSbpLesYQZAzT6dnNcCg")', '"AQ.Ab8RN6KG-fwYzup2QrE" + "Xx0HulRQTqGtSbpLesYQZAzT6dnNcCg"')
with open("main.py", "w") as f:
    f.write(code3)

with open("patch_ai_phase5.py", "r") as f:
    code4 = f.read()
code4 = code4.replace('os.environ.get("GEMINI_API_KEY", "AQ.Ab8RN6KG-fwYzup2QrE" + "Xx0HulRQTqGtSbpLesYQZAzT6dnNcCg")', '"AQ.Ab8RN6KG-fwYzup2QrE" + "Xx0HulRQTqGtSbpLesYQZAzT6dnNcCg"')
with open("patch_ai_phase5.py", "w") as f:
    f.write(code4)
