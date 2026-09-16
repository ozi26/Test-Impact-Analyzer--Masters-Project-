# ============================================================================== 
# Configuration parsing and exact configuration-change detection.
# ============================================================================== 

import json  # Import JSON support for JSON configuration files.
import xml.etree.ElementTree as ET  # Import Python's built-in XML parser.
from pathlib import Path  # Import Path for file extension handling.
import yaml  # Import PyYAML for YAML configuration files.
from .text_utils import extract_words  # Import lexical extraction for configuration keys and values.

# ------------------------------------------------------------------------------
# Flatten nested dictionaries into dotted configuration keys.
# ------------------------------------------------------------------------------
def flatten_dictionary(data, parent_key=""):
    """Convert nested dictionaries into dotted configuration keys."""
    result = {}  # Create the flattened result dictionary.
    if not isinstance(data, dict):  # Check whether the input is a dictionary.
        return result  # Return an empty mapping for unsupported top-level values.
    for key, value in data.items():  # Visit every configuration entry.
        full_key = f"{parent_key}.{key}" if parent_key else str(key)  # Build the complete dotted key.
        if isinstance(value, dict):  # Check whether the value contains another dictionary.
            result.update(flatten_dictionary(value, full_key))  # Flatten the nested dictionary.
        else:  # Handle a normal configuration value.
            result[full_key] = value  # Store the final value under its dotted key.
    return result  # Return all flattened settings.

# ------------------------------------------------------------------------------
# Parse YAML text.
# ------------------------------------------------------------------------------
def parse_yaml_text(text):
    """Parse YAML text and return flattened settings."""
    data = yaml.safe_load(text) or {}  # Convert YAML text into Python data.
    return flatten_dictionary(data)  # Return the flattened settings.

# ------------------------------------------------------------------------------
# Parse JSON text.
# ------------------------------------------------------------------------------
def parse_json_text(text):
    """Parse JSON text and return flattened settings."""
    data = json.loads(text) or {}  # Convert JSON text into Python data.
    return flatten_dictionary(data)  # Return the flattened settings.

# ------------------------------------------------------------------------------
# Parse Java-style properties text.
# ------------------------------------------------------------------------------
def parse_properties_text(text):
    """Parse simple key=value and key:value property lines."""
    result = {}  # Create the properties result.
    for raw_line in text.splitlines():  # Visit every line in the file.
        line = raw_line.strip()  # Remove surrounding whitespace.
        if not line or line.startswith("#") or line.startswith("!"):  # Ignore blanks and comments.
            continue  # Move to the next line.
        if "=" in line:  # Check for the common key=value form.
            key, value = line.split("=", 1)  # Split only at the first equals sign.
        elif ":" in line:  # Check for the key:value form.
            key, value = line.split(":", 1)  # Split only at the first colon.
        else:  # Handle a key without a value separator.
            key, value = line, ""  # Treat the complete line as an empty-value key.
        result[key.strip()] = value.strip()  # Store the cleaned property.
    return result  # Return all parsed properties.

# ------------------------------------------------------------------------------
# Convert XML elements into dotted configuration keys.
# ------------------------------------------------------------------------------
def _xml_element_to_dict(element, parent_key=""):
    """Convert an XML element tree into a flat key-value dictionary."""
    result = {}  # Create the output mapping.
    current_key = f"{parent_key}.{element.tag}" if parent_key else element.tag  # Build the current element path.
    for name, value in element.attrib.items():  # Visit every XML attribute.
        result[f"{current_key}.@{name}"] = value  # Store the attribute as a setting.
    children = list(element)  # Collect the element's children.
    text_value = (element.text or "").strip()  # Read the element text safely.
    if text_value and not children:  # Store text only for leaf elements.
        result[current_key] = text_value  # Save the leaf value.
    for child in children:  # Visit every child element.
        result.update(_xml_element_to_dict(child, current_key))  # Add child settings recursively.
    return result  # Return the flattened XML mapping.

# ------------------------------------------------------------------------------
# Parse XML text.
# ------------------------------------------------------------------------------
def parse_xml_text(text):
    """Parse XML text and return flattened settings."""
    root = ET.fromstring(text)  # Build the XML element tree.
    return _xml_element_to_dict(root)  # Convert the tree to dotted keys.

# ------------------------------------------------------------------------------
# Parse configuration text using its file extension.
# ------------------------------------------------------------------------------
def parse_configuration_text(text, extension):
    """Parse supported configuration text and return a flat mapping."""
    suffix = str(extension).lower()  # Normalize the extension before selecting a parser.
    if suffix in {".yaml", ".yml"}:  # Check for YAML.
        return parse_yaml_text(text)  # Parse YAML settings.
    if suffix == ".json":  # Check for JSON.
        return parse_json_text(text)  # Parse JSON settings.
    if suffix == ".properties":  # Check for Java properties.
        return parse_properties_text(text)  # Parse properties settings.
    if suffix == ".xml":  # Check for XML.
        return parse_xml_text(text)  # Parse XML settings.
    return {}  # Return an empty mapping for unsupported extensions.

# ------------------------------------------------------------------------------
# Parse one configuration file from disk.
# ------------------------------------------------------------------------------
def parse_configuration(file_path):
    """Read and parse one supported configuration file."""
    path = Path(file_path)  # Convert the file path into a Path object.
    text = path.read_text(encoding="utf-8", errors="replace")  # Read the configuration text.
    return parse_configuration_text(text, path.suffix)  # Parse the text using its extension.

# ------------------------------------------------------------------------------
# Convert changed configuration settings into lexical terms.
# ------------------------------------------------------------------------------
def configuration_terms(changes):
    """Extract searchable words from changed keys and values."""
    terms = set()  # Create an empty term set.
    for key, values in changes.items():  # Visit every changed configuration key.
        if key == "__parse_error__":  # Ignore the internal parser-error entry.
            continue  # Move to the next setting.
        terms.update(extract_words(str(key)))  # Add words from the configuration key.
        terms.update(extract_words(str(values.get("old"))))  # Add words from the old value.
        terms.update(extract_words(str(values.get("new"))))  # Add words from the new value.
    return terms  # Return all configuration terms.

# ------------------------------------------------------------------------------
# Compare two configuration texts exactly.
# ------------------------------------------------------------------------------
def find_configuration_changes_from_text(old_text, new_text, extension):
    """Return added, removed, and modified configuration keys."""
    old_config = parse_configuration_text(old_text, extension)  # Parse the old configuration.
    new_config = parse_configuration_text(new_text, extension)  # Parse the new configuration.
    changes = {}  # Create the exact change result.
    all_keys = sorted(set(old_config) | set(new_config))  # Include keys from both versions.
    for key in all_keys:  # Visit every possible configuration key.
        old_exists = key in old_config  # Check whether the old version contains the key.
        new_exists = key in new_config  # Check whether the new version contains the key.
        old_value = old_config.get(key)  # Read the old value when present.
        new_value = new_config.get(key)  # Read the new value when present.
        if not old_exists:  # Detect a newly added key.
            changes[key] = {"type": "added", "old": None, "new": new_value}  # Record the added setting.
        elif not new_exists:  # Detect a removed key.
            changes[key] = {"type": "removed", "old": old_value, "new": None}  # Record the removed setting.
        elif old_value != new_value:  # Detect a changed value.
            changes[key] = {"type": "modified", "old": old_value, "new": new_value}  # Record the modified setting.
    return changes  # Return all exact changes.

# ------------------------------------------------------------------------------
# Compare two configuration files from disk.
# ------------------------------------------------------------------------------
def find_configuration_changes(old_file, new_file):
    """Return exact configuration changes between two files."""
    old_path = Path(old_file)  # Convert the old file path into a Path object.
    new_path = Path(new_file)  # Convert the new file path into a Path object.
    old_text = old_path.read_text(encoding="utf-8", errors="replace") if old_path.exists() else ""  # Read the old text or use an empty value.
    new_text = new_path.read_text(encoding="utf-8", errors="replace") if new_path.exists() else ""  # Read the new text or use an empty value.
    extension = new_path.suffix or old_path.suffix  # Prefer the new extension and fall back to the old extension.
    return find_configuration_changes_from_text(old_text, new_text, extension)  # Compare the two configurations.
