import json
import anthropic
import appsettings

from articles.enrich.tree_slicer import TreeSlicer


class ClaudeSummariser:
    """
    LLM-based summariser using Claude.
    tree_slicer is injected so each web runner can scope classification to its domain.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "claude-haiku-4-5-20251001",
        tree_slicer: TreeSlicer | None = None,
    ) -> None:
        self.client = anthropic.Anthropic(api_key=api_key or appsettings.ANTHROPIC_API_KEY)
        self.model = model
        self.tree_slicer = tree_slicer
        self.last_usage: dict = {}

    def _system_prompt(self, tree_section: str) -> str:
        tree_block = f"\nCommodity tree:\n{tree_section}" if tree_section else ""
        return (
            "You are a commodity market analyst. Given a news article, return a JSON object with:\n"
            "- short_summary: 2-3 sentence summary of the key market implications\n"
            "- commodity_group: single best matching group string from the commodity tree, or null\n"
            "- commodity_classification: single best matching classification string from the commodity tree, or null\n"
            "- commodity_name: single best matching instrument name string from the commodity tree, or null\n"
            f"{tree_block}\n"
            "All fields must be a single string value, never an array. Return only the JSON object."
        )

    def summarise(
        self,
        title: str,
        body_text: str,
        commodity_group: str | None = None,
        commodity_classification: str | None = None,
        **_,
    ) -> dict:
        tree_section = (
            self.tree_slicer.slice(commodity_group, commodity_classification)
            if self.tree_slicer
            else ""
        )

        user_content = f"Title: {title}\n\n{body_text or ''}"
        if commodity_group:
            user_content += f"\n\nCommodity group context: {commodity_group}"
        if commodity_classification:
            user_content += f"\nCommodity classification (use this value): {commodity_classification}"

        message = self.client.messages.create(
            model=self.model,
            max_tokens=256,
            system=self._system_prompt(tree_section),
            messages=[{"role": "user", "content": user_content}],
        )

        self.last_usage = {
            "provider":      "anthropic",
            "model":         self.model,
            "input_tokens":  message.usage.input_tokens,
            "output_tokens": message.usage.output_tokens,
        }

        raw = message.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
            raw = raw.strip()
        return json.loads(raw)
