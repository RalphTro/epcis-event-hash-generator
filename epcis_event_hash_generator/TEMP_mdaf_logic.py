#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys
from typing import Any, Dict, Tuple

# Print IDs with JSON-LD keyword 'id' (NOT a GS1 URI).
ID_KEY_STYLE = "keyword"
GS1_PREFIX = "https://ref.gs1.org/voc/"

def load_json(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def is_uri(value: Any) -> bool:
    return isinstance(value, str) and (value.startswith("http://") or value.startswith("https://"))

def is_curie(value: Any) -> bool:
    return isinstance(value, str) and (":" in value) and not is_uri(value)

def build_prefix_map(ctx: Dict[str, Any]) -> Dict[str, str]:
    """Collect prefix -> IRI base from the top-level @context."""
    prefixes = {}
    for k, v in ctx.items():
        if isinstance(v, str) and is_uri(v):
            prefixes[k] = v
    return prefixes

def resolve_curie(curie: str, prefixes: Dict[str, str]) -> str:
    """Expand CURIE using available prefixes; if unknown prefix, return as-is."""
    if not is_curie(curie):
        return curie
    prefix, suffix = curie.split(":", 1)
    base = prefixes.get(prefix)
    return (base + suffix) if base else curie

def get_term_mapping(term: str, context_map: Dict[str, Any]) -> Tuple[str, Dict[str, Any]]:
    """
    Return (mapped_identifier, raw_entry) for a term name found in @context.
    mapped_identifier can be a CURIE (e.g., 'gs1:foo') or IRI (if context uses that).
    raw_entry is the raw context entry (dict or string).
    Raises if term not in context.
    """
    if term not in context_map:
        raise ValueError(f"Error: Bare property '{term}' not found in context.")
    entry = context_map[term]
    if isinstance(entry, dict):
        mid = entry.get("@id")
        if isinstance(mid, str):
            return mid, entry
        raise ValueError(f"Error: Context entry for '{term}' is invalid (missing '@id').")
    elif isinstance(entry, str):
        return entry, {"@id": entry}
    else:
        raise ValueError(f"Error: Context entry for '{term}' must be a string or object.")

def resolve_property_identifier(prop: str, context_map: Dict[str, Any], prefixes: Dict[str, str]) -> str:
    """
    Resolve a property name to a printable identifier according to rules:
      - 'id' / '@id' and 'type' / '@type' are handled elsewhere (not expanded)
      - Full IRI -> print as-is
      - CURIE:
          - If 'gs1:*' -> expand to full IRI for printing
          - Else (non-GS1) -> print as provided CURIE (allowed)
      - Bare name:
          - Must be in context: get '@id'
          - If '@id' is 'gs1:*' -> expand to full IRI
          - If '@id' is non-GS1 -> bare non-GS1 not allowed -> error
    """
    if prop in ("id", "@id", "type", "@type"):
        return prop

    if is_uri(prop):
        return prop

    if is_curie(prop):
        if prop.startswith("gs1:"):
            return resolve_curie(prop, prefixes)
        return prop  # non-GS1 CURIE permitted as-is

    mapped, _entry = get_term_mapping(prop, context_map)
    if mapped.startswith("gs1:"):
        return resolve_curie(mapped, prefixes)
    raise ValueError(
        f"Error: Bare property '{prop}' resolves to non-GS1 identifier '{mapped}'. "
        "Non-GS1 properties must be provided as CURIEs or full URIs."
    )

def is_code_list_property(prop: str, context_map: Dict[str, Any]) -> bool:
    entry = context_map.get(prop)
    if not isinstance(entry, dict) or "@context" not in entry:
        entry = context_map.get(f"gs1:{prop}")
    return isinstance(entry, dict) and isinstance(entry.get("@context"), dict)

def get_code_enumeration(prop: str, context_map: Dict[str, Any]) -> Dict[str, str]:
    entry = context_map.get(prop)
    if not isinstance(entry, dict) or "@context" not in entry:
        entry = context_map.get(f"gs1:{prop}")
    enum_map = entry.get("@context", {}) if isinstance(entry, dict) else {}
    return {k: v for k, v in enum_map.items() if isinstance(v, str)}

def normalize_code_value(prop: str, value: Any, context_map: Dict[str, Any], prefixes: Dict[str, str]) -> Any:
    """
    For code-list properties:
      Accept and validate any of the following forms, then return full GS1 IRI:
        - The code key (e.g., 'UN_LOCODE')
        - The local name (e.g., 'LocationID_Type-UN_LOCODE')
        - The CURIE (e.g., 'gs1:LocationID_Type-UN_LOCODE')
        - The full IRI (e.g., 'https://ref.gs1.org/voc/LocationID_Type-UN_LOCODE')
    """
    if not isinstance(value, str):
        return value

    enum_map = get_code_enumeration(prop, context_map)
    if not enum_map:
        return value  # not a code-list property

    allowed_full_iris = set()
    code_to_full_iri = {}

    for code_key, mapped in enum_map.items():
        full_iri = resolve_curie(mapped, prefixes)
        allowed_full_iris.add(full_iri)
        code_to_full_iri[code_key] = full_iri

    if is_uri(value):
        if value in allowed_full_iris:
            return value
        raise ValueError(f"Error: Code '{value}' not found in enumeration for '{prop}'.")

    if is_curie(value):
        full_iri = resolve_curie(value, prefixes)
        if full_iri in allowed_full_iris:
            return full_iri
        raise ValueError(f"Error: Code '{value}' not found in enumeration for '{prop}'.")

    if value in code_to_full_iri:
        return code_to_full_iri[value]

    as_curie = f"gs1:{value}"
    full_iri = resolve_curie(as_curie, prefixes)
    if full_iri in allowed_full_iris:
        return full_iri

    raise ValueError(f"Error: Code '{value}' not found in enumeration for '{prop}'.")

def print_kv(key: str, value: Any):
    if isinstance(value, list):
        for v in value:
            print_kv(key, v)
    else:
        print(f"{key}={value}")

def print_key_only(key: str):
    print(key)

def id_key_label() -> str:
    """Return the key label to use when printing IDs."""
    # Per your instruction: print 'id=<value>' exactly.
    return "id"

def process_object(obj: Dict[str, Any], context_map: Dict[str, Any], prefixes: Dict[str, str]):
    """
    Traverse a master-data object:
      - Print the object's id/@id FIRST (key 'id', value unchanged).
      - Then print type if present.
      - For nested dicts: print the parent property's resolved identifier (no '='),
        then recurse into the dict.
      - Resolve GS1 properties to full IRIs via context/prefixes.
      - Non-GS1 bare properties -> error; non-GS1 CURIE/IRI -> allowed.
      - Normalize code-list values to full GS1 IRIs.
      - Lists: if list of dicts, print the parent key (no '=') before each dict.
    """
    # 1) Print id first (value unchanged)
    if "id" in obj:
        print_kv(id_key_label(), obj["id"])
    elif "@id" in obj:
        print_kv(id_key_label(), obj["@id"])

    # 2) Print type next (value unchanged)
    if "type" in obj:
        print_kv("type", obj["type"])
    elif "@type" in obj:
        print_kv("type", obj["@type"])

    # 3) Print the remaining properties
    for prop, value in obj.items():
        if prop in ("id", "@id", "type", "@type"):
            continue

        if isinstance(value, dict):
            resolved_prop = resolve_property_identifier(prop, context_map, prefixes)
            print_key_only(resolved_prop)  # parent container line
            process_object(value, context_map, prefixes)
            continue

        if isinstance(value, list):
            resolved_prop = resolve_property_identifier(prop, context_map, prefixes)
            any_obj = any(isinstance(v, dict) for v in value)
            if any_obj:
                for v in value:
                    if isinstance(v, dict):
                        print_key_only(resolved_prop)  # parent container per dict element
                        process_object(v, context_map, prefixes)
                    else:
                        print_kv(resolved_prop, v)
            else:
                for v in value:
                    print_kv(resolved_prop, v)
            continue

        # Leaf value
        resolved_prop = resolve_property_identifier(prop, context_map, prefixes)
        if is_code_list_property(prop, context_map) and isinstance(value, str):
            value = normalize_code_value(prop, value, context_map, prefixes)
        print_kv(resolved_prop, value)

def main():
    if len(sys.argv) != 3:
        print("Usage: python normalize_epcis.py <context.json> <epcis.json>")
        sys.exit(1)

    context_path = sys.argv[1]
    epcis_path = sys.argv[2]

    context_doc = load_json(context_path)
    epcis_doc = load_json(epcis_path)

    context_map = context_doc.get("@context")
    if not isinstance(context_map, dict):
        raise ValueError("Error: Invalid context: '@context' must be an object.")

    prefixes = build_prefix_map(context_map)

    events = epcis_doc.get("epcisBody", {}).get("eventList", [])
    if not isinstance(events, list):
        raise ValueError("Error: epcisBody.eventList must be a list.")

    found_any = False
    for event in events:
        if "gs1:masterDataAvailableFor" not in event:
            continue

        found_any = True

        # Print the header (parent container) for the block as a full GS1 URI
        header = resolve_property_identifier("gs1:masterDataAvailableFor", context_map, prefixes)
        print_key_only(header)

        md_list = event.get("gs1:masterDataAvailableFor")
        if not isinstance(md_list, list):
            raise ValueError("Error: gs1:masterDataAvailableFor must be a list of objects.")

        for item in md_list:
            if not isinstance(item, dict):
                raise ValueError("Error: Items in gs1:masterDataAvailableFor must be objects.")
            process_object(item, context_map, prefixes)

    if not found_any:
        print("No gs1:masterDataAvailableFor found. Exiting.")

if __name__ == "__main__":
    main()