"""
Symétrise un fichier relations.txt (format: "A: B, C, D").

Règles:
- Pour chaque relation A -> B, ajoute la relation B -> A si absente
- Déduplique les cibles par personne, conserve l'ordre d'apparition
- Ignore les auto-boucles (A -> A)
- Par défaut, réécrit le fichier en place en sauvegardant une copie .bak

Utilisation:
    python symmetrize_relations.py --input relations.txt [--output relations.sym.txt]
    # En place (avec sauvegarde relations.txt.bak):
    python symmetrize_relations.py --input relations.txt
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Tuple
import argparse

# Réutilise le parseur robuste déjà présent dans graph.py
from graph import parse_relations_txt


def remove_diacritics(s: str) -> str:
    import unicodedata as ud
    return "".join(c for c in ud.normalize("NFKD", s) if not ud.combining(c))


def diacritic_count(s: str) -> int:
    import unicodedata as ud
    return sum(1 for c in s if ud.category(c) == "Ll" and ud.normalize("NFD", c) != c)


def canonical_key(name: str) -> str:
    # Trim, collapse spaces, remove diacritics, lowercase
    tokens = [t for t in name.strip().split() if t]
    base = " ".join(tokens)
    base = remove_diacritics(base)
    return base.casefold()


def titlecase_name(name: str) -> str:
    # Title-case each token; keep single-letter tokens uppercase (initials)
    parts = [p for p in name.strip().split() if p]
    def tc(tok: str) -> str:
        if len(tok) == 1:
            return tok.upper()
        # Handle hyphenated names: jean-luc -> Jean-Luc
        return "-".join(sub.capitalize() if sub else sub for sub in tok.split("-"))
    return " ".join(tc(p) for p in parts)


def merge_display_name(curr: str, cand: str) -> str:
    """Choose preferred display between two variants of same canonical key.

    Heuristics:
    - Prefer one with more diacritics
    - Else prefer the one with more characters (assume more explicit)
    - Else keep current (first seen)
    Also apply a gentle titlecase normalization.
    """
    c_curr = diacritic_count(curr)
    c_cand = diacritic_count(cand)
    chosen = curr
    if c_cand > c_curr:
        chosen = cand
    elif c_cand == c_curr and len(cand) > len(curr):
        chosen = cand
    return titlecase_name(chosen)


def normalize_relations(rel: Dict[str, List[str]]) -> Tuple[Dict[str, List[str]], Dict[str, str]]:
    """Normalize names (spacing, case) and merge variants by canonical key.

    Returns (normalized_relations, key_to_display) where keys and targets
    are the chosen display names.
    """
    # 1) Build mapping canonical -> preferred display
    key_to_display: Dict[str, str] = {}
    # Consider both sources and targets to pick the best display variant
    def consider(name: str):
        if not name:
            return
        key = canonical_key(name)
        disp = titlecase_name(name)
        if key in key_to_display:
            key_to_display[key] = merge_display_name(key_to_display[key], disp)
        else:
            key_to_display[key] = disp

    for src, targets in rel.items():
        consider(src)
        for t in targets:
            consider(t)

    # 2) Rebuild relations using canonical keys then re-map to display names
    tmp: Dict[str, List[str]] = {}
    for src, targets in rel.items():
        ksrc = canonical_key(src)
        if ksrc not in tmp:
            tmp[ksrc] = []
        seen: set = set()
        for t in targets:
            kt = canonical_key(t)
            if kt != ksrc and kt not in seen:
                seen.add(kt)
                tmp[ksrc].append(kt)

    # 3) Map canonical -> preferred display
    out: Dict[str, List[str]] = {}
    for ksrc, kt_targets in tmp.items():
        src_disp = key_to_display.get(ksrc, titlecase_name(ksrc))
        if src_disp not in out:
            out[src_disp] = []
        seen_disp: set = set()
        for kt in kt_targets:
            t_disp = key_to_display.get(kt, titlecase_name(kt))
            if t_disp not in seen_disp:
                seen_disp.add(t_disp)
                out[src_disp].append(t_disp)

    return out, key_to_display


def symmetrize(rel: Dict[str, List[str]]) -> Dict[str, List[str]]:
    """Retourne une version symétrisée du mapping {src: [dst,...]}.

    - Conserve l'ordre d'insertion des clés et des cibles existantes
    - Ajoute les clés manquantes pour les cibles qui n'avaient pas de ligne
    - Ajoute les relations inverses manquantes
    """
    # Copie superficielle pour préserver l'ordre et éviter de muter l'original
    sym: Dict[str, List[str]] = {k: list(v) for k, v in rel.items()}

    # 1) S'assurer que toutes les cibles existent en tant que clés (ajoutées à la fin)
    for src, targets in rel.items():
        for dst in targets:
            if dst not in sym:
                sym[dst] = []

    # 2) Ajouter les relations inverses manquantes
    for src, targets in rel.items():
        for dst in targets:
            if src == dst:
                continue
            if src not in sym[dst]:
                sym[dst].append(src)

    # 3) Nettoyer d'éventuelles auto-boucles
    for k in list(sym.keys()):
        sym[k] = [t for t in sym[k] if t != k]

    return sym


def write_relations_txt(rel: Dict[str, List[str]], path: Path) -> None:
    """Écrit le mapping au format `A: B, C, D` par ligne.

    - Conserve l'ordre des clés tel que fourni par `rel` (dict insertion order)
    - Conserve l'ordre des cibles déjà présent
    """
    lines: List[str] = []
    for person, targets in rel.items():
        # Dédupliquer par sécurité (en conservant l'ordre)
        seen = set()
        dedup_targets: List[str] = []
        for t in targets:
            if t and t not in seen and t != person:
                seen.add(t)
                dedup_targets.append(t)
        if dedup_targets:
            lines.append(f"{person}: {', '.join(dedup_targets)}")
        else:
            # Laisser une ligne vide de cibles si nécessaire, c'est plus explicite
            lines.append(f"{person}:")

    content = "\n".join(lines) + "\n"
    path.write_text(content, encoding="utf-8")


def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Symétriser un fichier relations.txt")
    parser.add_argument("--input", "-i", type=str, default="relations.txt", help="Chemin du fichier d'entrée")
    parser.add_argument("--output", "-o", type=str, default=None, help="Chemin du fichier de sortie (par défaut: réécriture en place)")
    args = parser.parse_args(argv)

    in_path = Path(args.input).resolve()
    if not in_path.exists():
        raise FileNotFoundError(f"Fichier introuvable: {in_path}")

    rel = parse_relations_txt(in_path)
    if not rel:
        raise ValueError(f"Aucune relation valide trouvée dans {in_path}")

    # Normaliser les noms et fusionner les variantes
    norm_rel, key_to_display = normalize_relations(rel)
    # Puis symétriser
    sym = symmetrize(norm_rel)

    out_path: Path
    if args.output:
        out_path = Path(args.output).resolve()
    else:
        # Sauvegarde en .bak et réécriture en place
        bak = in_path.with_suffix(in_path.suffix + ".bak")
        bak.write_text(in_path.read_text(encoding="utf-8"), encoding="utf-8")
        out_path = in_path

    write_relations_txt(sym, out_path)
    print(f"Relations normalisées + symétrisées écrites dans: {out_path}")


if __name__ == "__main__":
    main()
