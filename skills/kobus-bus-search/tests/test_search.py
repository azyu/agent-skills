import importlib.util
import pathlib
import sys
import types
import unittest


DEPARTURE_HTML = """
<ul class="clear" id="tableTrmList">
  <li><button type="button" onclick="fnDeprChc('010','서울경부');">서울경부</button></li>
  <li><button type="button" onclick="fnDeprChc('021','센트럴시티(서울)');">센트럴시티(서울)</button></li>
  <li><button type="button" onclick="fnDeprChc('300','대전복합');">대전복합</button></li>
  <li><button type="button" onclick="fnDeprChc('400','청주고속터미널');">청주고속터미널</button></li>
  <li><button type="button" onclick="fnDeprChc('111','용인신갈(고가밑)');">용인신갈(고가밑)</button></li>
  <li><button type="button" onclick="fnDeprChc('703','서부산(사상)');">서부산(사상)</button></li>
</ul>
"""


def load_search_module():
    fetchers_module = types.ModuleType("scrapling.fetchers")
    fetchers_module.Fetcher = type("Fetcher", (), {})

    scrapling_module = types.ModuleType("scrapling")
    scrapling_module.fetchers = fetchers_module

    sys.modules["scrapling"] = scrapling_module
    sys.modules["scrapling.fetchers"] = fetchers_module

    module_path = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "search.py"
    spec = importlib.util.spec_from_file_location("kobus_search", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ResolveTerminalTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.search = load_search_module()
        cls.candidates = cls.search.parse_terminal_candidates(DEPARTURE_HTML)

    def test_parses_terminal_codes_from_html(self):
        self.assertEqual(self.candidates["서울경부"], "010")
        self.assertEqual(self.candidates["용인신갈(고가밑)"], "111")

    def test_resolves_alias_to_official_terminal_name(self):
        name, code = self.search.resolve_terminal("서울", self.candidates)
        self.assertEqual((name, code), ("서울경부", "010"))

    def test_resolves_normalized_terminal_name(self):
        name, code = self.search.resolve_terminal("센트럴시티서울", self.candidates)
        self.assertEqual((name, code), ("센트럴시티(서울)", "021"))

    def test_resolves_fuzzy_terminal_name(self):
        name, code = self.search.resolve_terminal("부산사상", self.candidates)
        self.assertEqual((name, code), ("서부산(사상)", "703"))

    def test_rejects_ambiguous_terminal_name(self):
        with self.assertRaises(ValueError):
            self.search.resolve_terminal(
                "용인유",
                {
                    "용인": "150",
                    "용인신갈(고가밑)": "111",
                    "용인유림": "149",
                },
            )


if __name__ == "__main__":
    unittest.main()
