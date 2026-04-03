import os
import re
from bs4 import BeautifulSoup

def parse_artisan_html_recipe(file_path):
    """Parses ingredients from ANY table in the HTML, regardless of Phase naming."""
    if not os.path.exists(file_path):
        return None

    # Terms that indicate a row is NOT an ingredient
    IGNORE_LIST = ["total", "phase total", "ingredients", "formulation", "saponifiables", "heat phase", "water", "lye"]

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f.read(), 'html.parser')

        # Get the title
        title_tag = soup.select_one('h1')
        recipe_data = {
            "title": title_tag.get_text(strip=True) if title_tag else "Unknown Recipe",
            "phases": {}, # We will fill this with ingredients
            "extended_data": extract_extended_notes(soup)
        }

        # Find ALL tables in the document
        all_tables = soup.find_all('table')

        for i, table in enumerate(all_tables):
            # Try to find a heading for this table (Phase A, Phase B, etc.)
            header = table.find_previous(['h2', 'h3', 'h4', 'div'])
            phase_name = f"Phase {i+1}"
            if header:
                header_text = header.get_text(strip=True)
                if "Phase" in header_text or "Stage" in header_text:
                    phase_name = header_text.split(':')[0].strip()

            ingredients = []
            for row in table.find_all('tr'):
                cols = row.find_all(['td', 'th'])
                if len(cols) >= 2:
                    name = cols[0].get_text(strip=True)

                    # Filter out headers and totals
                    if not name or any(term in name.lower() for term in IGNORE_LIST) or name == "Ingredient":
                        continue

                    try:
                        weight_raw = cols[1].get_text(strip=True)
                        # Extract only numbers and decimals (handles "20.41g", "20.41 oz", etc.)
                        weight_match = re.search(r"(\d+\.?\d*)", weight_raw)
                        if weight_match:
                            ingredients.append({
                                "name": name,
                                "weight": float(weight_match.group(1))
                            })
                    except (ValueError, IndexError):
                        continue

            if ingredients:
                recipe_data["phases"][phase_name] = ingredients

        return recipe_data
    except Exception as e:
        print(f"Error parsing ingredients: {e}")
        return None

def extract_extended_notes(soup_or_html):
    """
    Extracts Process, Notes, and Scent Profile.
    FIX: Automatically converts string to BeautifulSoup if needed.
    """
    data = {
        "instructions": "",
        "notes": "",
        "scent_top": {"name": "", "description": ""},
        "scent_mid": {"name": "", "description": ""},
        "scent_base": {"name": "", "description": ""}
    }

    # CRITICAL FIX: Ensure we are working with a BeautifulSoup object
    if isinstance(soup_or_html, str):
        soup = BeautifulSoup(soup_or_html, 'html.parser')
    else:
        soup = soup_or_html

    if not soup:
        return data

    # 1. Extract Process
    # The template uses .process-content (or we can look for "The Process" heading)
    process_div = soup.select_one('.process-content')
    if not process_div:
        # Fallback: Find the div containing the process steps
        process_header = None
        for h3 in soup.select('h3'):
            if "The Process" in h3.get_text():
                process_header = h3
                break
        if process_header:
            # Get the parent container text
            process_div = process_header.find_parent('div')

    if process_div:
        data["instructions"] = process_div.get_text(separator="\n", strip=True)

    # 2. Extract Artisan Note
    for h4 in soup.select('h4'):
        if "Artisan's Note" in h4.get_text():
            note_p = h4.find_next('p')
            if note_p:
                data["notes"] = note_p.get_text(strip=True).strip('"')
            break

    # 3. Extract Scent Profile (Matches the 'group' structure in the HTML)
    for group in soup.select('.group'):
        label_tag = group.select_one('span')
        if not label_tag: continue

        label = label_tag.get_text().lower()
        p_tags = group.select('p')

        # In the provided HTML:
        # p[0] is the name (e.g., "Sweet Orange")
        # p[1] is the description (e.g., "Bright, citrusy bursts...")
        name_val = p_tags[0].get_text(strip=True) if len(p_tags) > 0 else ""
        desc_val = p_tags[1].get_text(strip=True) if len(p_tags) > 1 else ""

        if "top" in label:
            data["scent_top"] = {"name": name_val, "description": desc_val}
        elif "middle" in label or "mid" in label:
            data["scent_mid"] = {"name": name_val, "description": desc_val}
        elif "base" in label:
            data["scent_base"] = {"name": name_val, "description": desc_val}

    return data