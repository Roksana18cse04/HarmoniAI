from symspellpy import SymSpell, Verbosity
from pathlib import Path

sym_spell = SymSpell(max_dictionary_edit_distance=2)
# Base path is the project root
base_path = Path(__file__).resolve().parents[1]
dict_path = base_path / "data" / "frequency_dictionary_en_82_765.txt"
sym_spell.load_dictionary(str(dict_path), term_index=0, count_index=1)

def correct_spelling(prompt: str) -> str:
    suggestions = sym_spell.lookup_compound(prompt, max_edit_distance=2)
    corrected = suggestions[0].term if suggestions else prompt
    print(f"Corrected: {corrected}")
    return corrected
