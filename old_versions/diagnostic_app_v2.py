#!/usr/bin/env python3
"""
Diagnostic app_v2 - Liste tous les callbacks et leurs IDs
"""

print("\n" + "="*70)
print("  📋 APP_V2 CALLBACKS DIAGNOSTIC")
print("="*70)

print("\n🔍 Recherche des IDs dans app_v2.py...")

import re

with open('app_v2.py', 'r') as f:
    content = f.read()

# Extract all Output IDs
outputs = re.findall(r"Output\('([^']+)'", content)
print(f"\n✅ {len(set(outputs))} Output IDs trouvés:")
for output_id in sorted(set(outputs)):
    print(f"   - {output_id}")

# Extract all Input IDs
inputs = re.findall(r"Input\('([^']+)'", content)
print(f"\n✅ {len(set(inputs))} Input IDs trouvés:")
for input_id in sorted(set(inputs)):
    print(f"   - {input_id}")

# Extract all modal IDs
modals = re.findall(r"id='(modal-[^']+)'", content)
print(f"\n✅ {len(set(modals))} Modal IDs trouvés:")
for modal_id in sorted(set(modals)):
    print(f"   - {modal_id}")

# Extract all dropdown IDs
dropdowns = re.findall(r"id='(dropdown-[^']+)'", content)
print(f"\n✅ {len(set(dropdowns))} Dropdown IDs trouvés:")
for dropdown_id in sorted(set(dropdowns)):
    print(f"   - {dropdown_id}")

# Extract all button IDs
buttons = re.findall(r"id='(btn-[^']+)'", content)
print(f"\n✅ {len(set(buttons))} Button IDs trouvés:")
for btn_id in sorted(set(buttons)):
    print(f"   - {btn_id}")

print("\n" + "="*70)
print("  🔍 VÉRIFICATION DES CORRESPONDANCES")
print("="*70)

# Vérifier que chaque Input/Output a un ID correspondant dans les composants
all_component_ids = set()
all_component_ids.update(modals)
all_component_ids.update(dropdowns)
all_component_ids.update(buttons)

# Extract tous les id='...'
all_ids_in_layout = re.findall(r"id='([^']+)'", content)
all_component_ids.update(all_ids_in_layout)

print("\n📊 Callbacks vs Composants:")
print(f"   - Total composants avec IDs: {len(all_component_ids)}")
print(f"   - Total Outputs: {len(set(outputs))}")
print(f"   - Total Inputs: {len(set(inputs))}")

# Check for orphan callbacks (Output sans composant)
orphan_outputs = set(outputs) - all_component_ids
if orphan_outputs:
    print(f"\n⚠️  {len(orphan_outputs)} Output(s) ORPHELINS (pas de composant correspondant):")
    for orphan in sorted(orphan_outputs):
        print(f"   - {orphan}")
else:
    print("\n✅ Tous les Outputs ont un composant correspondant")

# Check for orphan inputs
orphan_inputs = set(inputs) - all_component_ids
if orphan_inputs:
    print(f"\n⚠️  {len(orphan_inputs)} Input(s) ORPHELINS:")
    for orphan in sorted(orphan_inputs):
        print(f"   - {orphan}")
else:
    print("\n✅ Tous les Inputs ont un composant correspondant")

# Count callbacks
callback_count = content.count('@app.callback')
print(f"\n📋 Total callbacks: {callback_count}")

print("\n" + "="*70 + "\n")
