"""Materials Project API Retriever for materials science research.

Searches the Materials Project database for material properties including
metals, alloys, ceramics, and other inorganic materials using the free
Materials Project API (materialsproject.org).

Requires: MATERIALS_PROJECT_API_KEY environment variable (free at materialsproject.org).
Falls back to web-based material property search if no API key is set.
"""

import json
import logging
import os
import urllib.parse
import urllib.request

logger = logging.getLogger(__name__)

MP_API_BASE = "https://api.materialsproject.org"
MP_WEBSITE_BASE = "https://materialsproject.org/materials"


class MaterialsProjectSearch:
    """Materials Project database search retriever.

    Uses the Materials Project API to search for materials by formula,
    elements, or keywords and retrieve their properties.
    """

    def __init__(self, query, query_domains=None):
        self.query = query
        self.api_key = os.getenv("MATERIALS_PROJECT_API_KEY", "")

    def search(self, max_results=5):
        """Search for materials matching the query.

        Args:
            max_results: Maximum number of results to return.

        Returns:
            List of dicts with title, href, and body keys.
        """
        results = []

        if self.api_key:
            results = self._search_api(max_results)

        if not results:
            results = self._search_fallback(max_results)

        return results

    def _search_api(self, max_results):
        """Search using the Materials Project API v2."""
        results = []

        # Try formula-based search first
        formula_results = self._search_by_formula(max_results)
        if formula_results:
            return formula_results

        # Try element-based search
        element_results = self._search_by_elements(max_results)
        if element_results:
            return element_results

        return results

    def _search_by_formula(self, max_results):
        """Search Materials Project by chemical formula."""
        formula = self._extract_formula(self.query)
        if not formula:
            return []

        url = (
            f"{MP_API_BASE}/materials/summary/"
            f"?formula={urllib.parse.quote(formula)}"
            f"&_limit={max_results}"
            f"&_fields=material_id,formula_pretty,symmetry,density,"
            f"band_gap,formation_energy_per_atom,energy_above_hull,"
            f"is_stable,theoretical"
        )

        return self._fetch_and_format(url)

    def _search_by_elements(self, max_results):
        """Search Materials Project by elements contained in materials."""
        elements = self._extract_elements(self.query)
        if not elements:
            return []

        elements_str = ",".join(elements)
        url = (
            f"{MP_API_BASE}/materials/summary/"
            f"?elements={urllib.parse.quote(elements_str)}"
            f"&_limit={max_results}"
            f"&_fields=material_id,formula_pretty,symmetry,density,"
            f"band_gap,formation_energy_per_atom,energy_above_hull,"
            f"is_stable,theoretical"
        )

        return self._fetch_and_format(url)

    def _fetch_and_format(self, url):
        """Fetch data from Materials Project API and format results."""
        results = []
        try:
            req = urllib.request.Request(url, headers={
                "X-API-KEY": self.api_key,
                "Accept": "application/json",
            })
            with urllib.request.urlopen(req, timeout=15) as resp:
                data = json.loads(resp.read().decode())

            for entry in data.get("data", []):
                material_id = entry.get("material_id", "")
                formula = entry.get("formula_pretty", "Unknown")
                symmetry = entry.get("symmetry", {})
                crystal_system = symmetry.get("crystal_system", "N/A") if isinstance(symmetry, dict) else "N/A"
                space_group = symmetry.get("symbol", "N/A") if isinstance(symmetry, dict) else "N/A"
                density = entry.get("density", "N/A")
                band_gap = entry.get("band_gap", "N/A")
                formation_energy = entry.get("formation_energy_per_atom", "N/A")
                e_above_hull = entry.get("energy_above_hull", "N/A")
                is_stable = entry.get("is_stable", "N/A")
                theoretical = entry.get("theoretical", False)

                title = f"{formula} ({material_id})"
                if theoretical:
                    title += " [Theoretical]"

                body_parts = [
                    f"Formula: {formula}",
                    f"Crystal System: {crystal_system}",
                    f"Space Group: {space_group}",
                ]
                if density != "N/A" and density is not None:
                    body_parts.append(f"Density: {density:.3f} g/cm³")
                if band_gap != "N/A" and band_gap is not None:
                    body_parts.append(f"Band Gap: {band_gap:.3f} eV")
                if formation_energy != "N/A" and formation_energy is not None:
                    body_parts.append(f"Formation Energy: {formation_energy:.4f} eV/atom")
                if e_above_hull != "N/A" and e_above_hull is not None:
                    stability = "Stable" if is_stable else f"Metastable ({e_above_hull:.4f} eV/atom above hull)"
                    body_parts.append(f"Stability: {stability}")

                results.append({
                    "title": title,
                    "href": f"{MP_WEBSITE_BASE}/{material_id}",
                    "body": ". ".join(body_parts),
                })

        except Exception as e:
            logger.warning(f"Materials Project API search failed: {e}")

        return results

    def _search_fallback(self, max_results):
        """Fallback search using Materials Project website text search.

        When no API key is available, constructs search URLs and returns
        useful reference links for common material types.
        """
        results = []
        query_lower = self.query.lower()

        # Map common material terms to Materials Project search URLs and descriptions
        material_db_entries = [
            {
                "keywords": ["steel", "iron", "fe", "stainless", "aisi", "martensite", "austenite", "ferrite"],
                "title": "Iron-based Alloys & Steels - Materials Project Database",
                "href": f"https://materialsproject.org/#search/materials/{{Fe}}",
                "body": "Materials Project database for iron-based materials including steels, "
                        "stainless steels, and iron alloys. Contains crystal structures, phase stability, "
                        "density, electronic properties, and thermodynamic data for Fe-based compounds.",
            },
            {
                "keywords": ["titanium", "ti-6al-4v", "ti6al4v", "ti ", "titanium alloy"],
                "title": "Titanium Alloys - Materials Project Database",
                "href": f"https://materialsproject.org/#search/materials/{{Ti}}",
                "body": "Materials Project database for titanium-based materials including Ti alloys. "
                        "Contains crystal structures, density, band gap, formation energies, and phase "
                        "stability data for Ti-based compounds used in aerospace and biomedical applications.",
            },
            {
                "keywords": ["aluminum", "aluminium", "al ", "al2o3", "alumina", "duralumin"],
                "title": "Aluminum & Alumina Materials - Materials Project Database",
                "href": f"https://materialsproject.org/#search/materials/{{Al}}",
                "body": "Materials Project database for aluminum-based materials including Al alloys "
                        "and alumina (Al2O3) ceramics. Contains structural, thermodynamic, and electronic "
                        "properties for lightweight structural and ceramic applications.",
            },
            {
                "keywords": ["nickel", "inconel", "ni ", "superalloy", "hastelloy", "monel"],
                "title": "Nickel Superalloys - Materials Project Database",
                "href": f"https://materialsproject.org/#search/materials/{{Ni}}",
                "body": "Materials Project database for nickel-based materials including superalloys "
                        "(Inconel, Hastelloy). Contains high-temperature stability data, crystal structures, "
                        "and thermodynamic properties for turbine and corrosion-resistant applications.",
            },
            {
                "keywords": ["ceramic", "sic", "silicon carbide", "zirconia", "zro2", "si3n4", "boron nitride", "bn"],
                "title": "Advanced Ceramics - Materials Project Database",
                "href": f"https://materialsproject.org/#search/materials/{{Si,C}}",
                "body": "Materials Project database for ceramic materials including SiC, ZrO2, Si3N4, "
                        "BN, and other advanced ceramics. Contains hardness-related electronic data, thermal "
                        "stability, crystal structures, and phase information for high-temperature applications.",
            },
            {
                "keywords": ["copper", "cu ", "brass", "bronze", "cupronickel"],
                "title": "Copper Alloys - Materials Project Database",
                "href": f"https://materialsproject.org/#search/materials/{{Cu}}",
                "body": "Materials Project database for copper-based materials including brasses, bronzes, "
                        "and cupronickel alloys. Contains electrical conductivity-related data, crystal structures, "
                        "and thermodynamic properties for electrical and thermal applications.",
            },
            {
                "keywords": ["tungsten", "carbide", "wc", "cobalt", "cemented"],
                "title": "Tungsten & Carbide Materials - Materials Project Database",
                "href": f"https://materialsproject.org/#search/materials/{{W}}",
                "body": "Materials Project database for tungsten and tungsten carbide materials. "
                        "Contains ultra-high melting point data, hardness-related properties, crystal structures, "
                        "and stability data for cutting tools and high-temperature applications.",
            },
        ]

        # Always add a general search result
        encoded_query = urllib.parse.quote(self.query)
        results.append({
            "title": f"Materials Project Search: {self.query}",
            "href": f"https://materialsproject.org/#search/materials/{encoded_query}",
            "body": f"Search the Materials Project database for materials related to: {self.query}. "
                    "The Materials Project provides open access to computed properties of over 150,000 "
                    "inorganic materials including crystal structure, stability, electronic structure, "
                    "and thermodynamic properties.",
        })

        # Add matching specific entries
        for entry in material_db_entries:
            if any(kw in query_lower for kw in entry["keywords"]):
                results.append({
                    "title": entry["title"],
                    "href": entry["href"],
                    "body": entry["body"],
                })

        # Add ASM International reference
        results.append({
            "title": f"ASM International Materials Database: {self.query}",
            "href": f"https://www.asminternational.org/search#q={encoded_query}",
            "body": f"ASM International reference for: {self.query}. ASM provides comprehensive "
                    "materials property data, phase diagrams, alloy composition data, heat treatment "
                    "guidelines, and failure analysis for metals, alloys, and engineered materials.",
        })

        # Add MatWeb reference
        results.append({
            "title": f"MatWeb Material Property Data: {self.query}",
            "href": f"https://www.matweb.com/search/QuickText.aspx?SearchText={encoded_query}",
            "body": f"MatWeb material property database search for: {self.query}. MatWeb contains "
                    "property data for over 100,000 materials including metals, plastics, ceramics, "
                    "and composites with mechanical, thermal, and physical property values.",
        })

        return results[:max_results]

    @staticmethod
    def _extract_formula(query):
        """Try to extract a chemical formula from the query."""
        import re
        # Match patterns like Fe2O3, Ti-6Al-4V, SiC, Al2O3, NaCl
        formula_pattern = re.findall(r'\b([A-Z][a-z]?\d*(?:[A-Z][a-z]?\d*)*)\b', query)
        for match in formula_pattern:
            # Must have at least one uppercase letter and look like a formula
            if len(match) >= 2 and any(c.isupper() for c in match):
                # Filter out common English words that match the pattern
                if match.lower() not in {"the", "and", "for", "are", "was", "has", "its", "can"}:
                    return match
        return None

    @staticmethod
    def _extract_elements(query):
        """Try to extract element symbols from the query."""
        # Common element keyword mapping
        element_map = {
            "iron": "Fe", "steel": "Fe", "titanium": "Ti", "aluminum": "Al",
            "aluminium": "Al", "nickel": "Ni", "copper": "Cu", "zinc": "Zn",
            "chromium": "Cr", "manganese": "Mn", "silicon": "Si", "carbon": "C",
            "tungsten": "W", "molybdenum": "Mo", "vanadium": "V", "cobalt": "Co",
            "tin": "Sn", "lead": "Pb", "gold": "Au", "silver": "Ag",
            "platinum": "Pt", "palladium": "Pd", "zirconium": "Zr",
            "niobium": "Nb", "tantalum": "Ta", "magnesium": "Mg",
            "lithium": "Li", "boron": "B", "nitrogen": "N", "oxygen": "O",
        }

        query_lower = query.lower()
        elements = []
        for keyword, symbol in element_map.items():
            if keyword in query_lower and symbol not in elements:
                elements.append(symbol)

        return elements if elements else None
