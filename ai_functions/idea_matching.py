import json
import urllib.request
import urllib.error
import math
import re

def calculate_distance_meters(lat1, lon1, lat2, lon2):
    R = 6371000
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

def parse_coordinates(loc_str):
    if not loc_str: return None
    # Look for a pattern like 28.50, 77.04
    match = re.search(r'(-?\d+\.\d+)[^\d-]+(-?\d+\.\d+)', loc_str)
    if match:
        try:
            return (float(match.group(1)), float(match.group(2)))
        except:
            return None
    return None

def format_prompt(list_of_ideas):
    prompt = "You are an expert at analyzing civic feedback and clustering similar reports. The reports are often written in Hinglish, Hindi, or English.\n\n"
    prompt += "Task: Read the following list of reports. Group them as duplicates ONLY IF they are conceptually similar (talking about the exact same underlying civic issue).\n"
    prompt += "Return the result as a JSON object containing a list of 'merge_groups'. Each group should contain the indices of the duplicate reports and a short explanation of why they are grouped.\n\n"
    prompt += "Format expected (This is just an example structure, provide your own accurate reasons based on the actual input text):\n"
    prompt += "{\n"
    prompt += '  "merge_groups": [\n'
    prompt += '    {"ideas": [0, 1], "reason": "Both complain about XYZ issue"}\n'
    prompt += "  ]\n"
    prompt += "}\n\n"
    
    prompt += "List of reports (Text and Location):\n"
    for i, idea in enumerate(list_of_ideas):
        prompt += f"{i}: Text: '{idea['text']}', Location: '{idea['location']}'\n"
        
    prompt += "\nOutput JSON:"
    return prompt

def find_similar_ideas_llm(list_of_ideas: list) -> dict:
    if len(list_of_ideas) < 2:
        return {"merge_groups": []}
        
    prompt = format_prompt(list_of_ideas)
    
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": "llama3.1:8b",
        "prompt": prompt,
        "format": "json",
        "stream": False
    }
    
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
    
    try:
        response = urllib.request.urlopen(req, timeout=180)
        result = json.loads(response.read().decode("utf-8"))
        
        response_text = result.get("response", "{}")
        parsed_json = json.loads(response_text)
        
        # POST-PROCESSING: Filter out groups that are > 500m apart geographically
        valid_merge_groups = []
        if "merge_groups" in parsed_json:
            for group in parsed_json["merge_groups"]:
                ideas = group.get("ideas", [])
                if len(ideas) >= 2:
                    # Collect coordinates for these ideas
                    coords_list = []
                    for idx in ideas:
                        if 0 <= idx < len(list_of_ideas):
                            c = parse_coordinates(list_of_ideas[idx].get("location", ""))
                            coords_list.append((idx, c))
                    
                    # Very simple logic: if any pair in the group is > 500m apart, we don't merge them.
                    # A better way is to create valid subgroups.
                    valid_subgroups = []
                    
                    # Union-Find / Connected components approach based on < 500m edges
                    parent = {idx: idx for idx, _ in coords_list}
                    def find(i):
                        if parent[i] == i: return i
                        parent[i] = find(parent[i])
                        return parent[i]
                    def union(i, j):
                        root_i = find(i)
                        root_j = find(j)
                        if root_i != root_j:
                            parent[root_i] = root_j
                    
                    for i in range(len(coords_list)):
                        for j in range(i+1, len(coords_list)):
                            idx1, c1 = coords_list[i]
                            idx2, c2 = coords_list[j]
                            if c1 and c2:
                                dist = calculate_distance_meters(c1[0], c1[1], c2[0], c2[1])
                                if dist <= 500:
                                    union(idx1, idx2)
                            # Missing coordinates cannot establish geographic proximity.
                    
                    # Group by parent
                    clusters = {}
                    for idx, _ in coords_list:
                        root = find(idx)
                        if root not in clusters:
                            clusters[root] = []
                        clusters[root].append(idx)
                    
                    for sub_ideas in clusters.values():
                        if len(sub_ideas) >= 2:
                            valid_merge_groups.append({
                                "ideas": sub_ideas,
                                "reason": group.get("reason", "") + " (Distance <= 500m verified)"
                            })

            parsed_json["merge_groups"] = valid_merge_groups

        return parsed_json
    except urllib.error.URLError as e:
        return {"error": f"Failed to connect to Ollama server: {str(e)}"}
    except json.JSONDecodeError:
        return {"error": "LLM returned invalid JSON"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}
