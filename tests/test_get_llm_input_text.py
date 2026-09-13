import asyncio
import sys
import types


# The tested branch only parses HTML and does not call either renderer. Keeping
# these lightweight fallbacks lets the parser test run without native wheels.
sys.modules.setdefault(
    "minify_html", types.SimpleNamespace(minify=lambda html: html)
)
sys.modules.setdefault(
    "inscriptis", types.SimpleNamespace(get_text=lambda html: html)
)

from url_to_llm_text.get_llm_input_text import get_processed_text


def test_skips_empty_table_rows_when_building_markdown(capsys):
    html = """
    <table>
      <tr><th>Name</th></tr>
      <tr></tr>
      <tr><td>Ada</td></tr>
    </table>
    """

    result = asyncio.run(
        get_processed_text(
            html,
            "https://example.test/",
            html_parser="html.parser",
            extract=True,
        )
    )

    assert "| Name |" in result
    assert "| Ada |" in result
    assert "|  |" not in result
    assert "Error while getting individual table" not in capsys.readouterr().out
