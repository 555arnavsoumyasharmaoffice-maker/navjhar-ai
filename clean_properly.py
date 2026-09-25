import sys

with open("main.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
skip = False
for line in lines:
    if "def generate_impact_report_endpoint(request:" in line:
        # We also need to remove the @app.post above it
        if new_lines and "@app.post(\"/generate-impact-report\")" in new_lines[-1]:
            new_lines.pop()
        skip = True
        continue
    
    if skip:
        # wait until the end of the function.
        # the function ends right before `class MatchSolversRequest(BaseModel):`
        if "class MatchSolversRequest(BaseModel):" in line:
            skip = False
            new_lines.append(line)
        continue
    
    new_lines.append(line)

with open("main.py", "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("Old route removed cleanly!")
