"""PubChem API Retriever for chemistry research.

Searches the PubChem database for chemical compounds, substances,
and bioassay data using the PUG REST API.
"""

import logging
import urllib.parse
import json

logger = logging.getLogger(__name__)

PUBCHEM_BASE_URL = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
PUBCHEM_COMPOUND_URL = "https://pubchem.ncbi.nlm.nih.gov/compound"


class PubChemSearch:
    """PubChem compound search retriever.

    Uses the PubChem PUG REST API to search for chemical compounds
    by name and retrieve their properties and descriptions.
    """

    def __init__(self, query, query_domains=None):
        self.query = query

    def search(self, max_results=5):
        """Search PubChem for compounds matching the query.

        Args:
            max_results: Maximum number of results to return.

        Returns:
            List of dicts with title, href, and body keys.
        """
        try:
            return self._search_compounds(max_results)
        except Exception as e:
            logger.warning(f"PubChem search failed: {e}")
            return []

    def _search_compounds(self, max_results):
        """Search PubChem compounds using the PUG REST API."""
        import urllib.request

        # Step 1: Search for compound CIDs by name/keyword
        encoded_query = urllib.parse.quote(self.query)
        search_url = (
            f"{PUBCHEM_BASE_URL}/compound/name/{encoded_query}/cids/JSON"
        )

        cids = []
        try:
            req = urllib.request.Request(search_url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
                cids = data.get("IdentifierList", {}).get("CID", [])
        except Exception:
            # Fallback: use autocomplete/search API for broader keyword matching
            cids = self._autocomplete_search(max_results)

        if not cids:
            return []

        cids = cids[:max_results]
        return self._get_compound_details(cids)

    def _autocomplete_search(self, max_results):
        """Fallback search using PubChem's autocomplete endpoint."""
        import urllib.request

        encoded_query = urllib.parse.quote(self.query)
        url = (
            f"https://pubchem.ncbi.nlm.nih.gov/rest/autocomplete/compound/{encoded_query}/json"
            f"?limit={max_results}"
        )

        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
                terms = data.get("dictionary_terms", {}).get("compound", [])

            # Resolve each term to a CID
            cids = []
            for term in terms[:max_results]:
                cid = self._resolve_name_to_cid(term)
                if cid:
                    cids.append(cid)
            return cids
        except Exception as e:
            logger.warning(f"PubChem autocomplete search failed: {e}")
            return []

    def _resolve_name_to_cid(self, name):
        """Resolve a compound name to a PubChem CID."""
        import urllib.request

        encoded_name = urllib.parse.quote(name)
        url = f"{PUBCHEM_BASE_URL}/compound/name/{encoded_name}/cids/JSON"
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())
                cids = data.get("IdentifierList", {}).get("CID", [])
                return cids[0] if cids else None
        except Exception:
            return None

    def _get_compound_details(self, cids):
        """Fetch detailed properties for a list of compound CIDs."""
        import urllib.request

        results = []
        properties = "MolecularFormula,MolecularWeight,IUPACName,InChI,CanonicalSMILES"

        # Batch property request
        cid_str = ",".join(str(c) for c in cids)
        url = (
            f"{PUBCHEM_BASE_URL}/compound/cid/{cid_str}/property/{properties}/JSON"
        )

        props_by_cid = {}
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())
                for prop in data.get("PropertyTable", {}).get("Properties", []):
                    props_by_cid[prop["CID"]] = prop
        except Exception as e:
            logger.warning(f"PubChem property fetch failed: {e}")

        # Get descriptions for each compound
        for cid in cids:
            prop = props_by_cid.get(cid, {})
            iupac = prop.get("IUPACName", "Unknown compound")
            formula = prop.get("MolecularFormula", "")
            weight = prop.get("MolecularWeight", "")
            smiles = prop.get("CanonicalSMILES", "")

            title = f"{iupac} (CID: {cid})"
            if formula:
                title = f"{iupac} [{formula}] (CID: {cid})"

            body_parts = []
            if formula:
                body_parts.append(f"Molecular Formula: {formula}")
            if weight:
                body_parts.append(f"Molecular Weight: {weight} g/mol")
            if smiles:
                body_parts.append(f"SMILES: {smiles}")

            # Try to get a description
            description = self._get_compound_description(cid)
            if description:
                body_parts.append(f"Description: {description}")

            results.append({
                "title": title,
                "href": f"{PUBCHEM_COMPOUND_URL}/{cid}",
                "body": ". ".join(body_parts) if body_parts else f"PubChem compound CID {cid}",
            })

        return results

    def _get_compound_description(self, cid):
        """Fetch a text description for a compound from PubChem."""
        import urllib.request

        url = f"{PUBCHEM_BASE_URL}/compound/cid/{cid}/description/JSON"
        try:
            req = urllib.request.Request(url, headers={"Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())
                descriptions = data.get("InformationList", {}).get("Information", [])
                for desc in descriptions:
                    text = desc.get("Description", "")
                    if text and len(text) > 20:
                        return text[:500]
        except Exception:
            pass
        return ""
