#!/usr/bin/env python3

import os
import json
import glob
import shutil
from PIL import Image

outputs = [
  { "name": "EMOJI_14", "suffix": "sm", "size": 14, "top": 0 },
  { "name": "EMOJI_18", "suffix": "sm", "size": 18, "top": 2 },
  { "name": "EMOJI_24", "suffix": "lg", "size": 24, "top": 0 },
  { "name": "EMOJI_28", "suffix": "lg", "size": 28, "top": 2 }
]

if not os.path.exists("emoji.json"):
  print("You are in a wrong directory to build the fonts, run this from the root of the repository")
  quit()

if os.path.exists("merged"):
  shutil.rmtree("merged")
shutil.copytree("base", "merged")

os.makedirs("build", exist_ok=True)
emojis_file = open("emoji.json")
emojis_json = json.load(emojis_file)
for folder in ["sm", "lg"]:
  files = glob.glob("emoji/*-%s.png" % folder)
  os.makedirs("build/%s" % folder, exist_ok=True)
  for file in files:
    shutil.copyfile(file, "build/%s/%05X.png" % (folder, int(file[file.find('/')+1 : file.find('-')], 16)))
for output in outputs:
  output_name = output["name"]
  suffix = output["suffix"]
  
  output_folder = "merged/%s" % output_name
  glyphs_folder = os.path.join(output_folder, "glyphs")
  os.makedirs(glyphs_folder, exist_ok=True)
  
  json_path = os.path.join(output_folder, "font.json")
  if os.path.exists(json_path):
    with open(json_path, 'r') as f:
      output_json = json.load(f)
  else:
    output_json = {'glyphs': []}
  
  glyphs_dict = {glyph['codepoint']: glyph for glyph in output_json.get('glyphs', [])}
  
  for emoji in emojis_json:
    codepoint = ord(emoji["character"])
    image = Image.open("build/%s/%05X.png" % (suffix, codepoint))
    metrics = emoji[suffix]
    width, height = image.size
    
    hex_codepoint = "%X" % codepoint
    final_image_path = os.path.join(glyphs_folder, "U+%s.png" % hex_codepoint)
    shutil.copyfile("build/%s/%05X.png" % (suffix, codepoint), final_image_path)
    
    glyphs_dict[codepoint] = {
      'codepoint': codepoint,
      'char': emoji["character"],
      'file': "glyphs/U+%s.png" % hex_codepoint,
      'width': width,
      'height': height,
      'left_offset': 1,
      'top_offset': metrics["top"] + output["top"],
      'advance': width + 2
    }
  
  output_json['glyphs'] = sorted(glyphs_dict.values(), key=lambda x: x['codepoint'])
  
  with open(json_path, 'w') as f:
    json.dump(output_json, f, indent=2)

print("\nPacking into PBF files...")
for output in outputs:
  output_name = output["name"]
  json_path = os.path.join("merged", output_name, "font.json")
  pbf_path = os.path.join("merged", "%s.pbf" % output_name)
  
  os.system("python autogen/pbf_repack.py %s -o %s" % (json_path, pbf_path))
  print("Generated %s" % pbf_path)
