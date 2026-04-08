from articles.enrich.tree_slicer import TreeSlicer


class WebTreeSlicer(TreeSlicer):
    """
    Slices a nested commodity tree dict down to the relevant branch
    for a given article's group/classification context.

    tree shape: {sector: {group: {classification: [instruments]}}}
    """

    def __init__(self, tree: dict) -> None:
        self.tree = tree

    def slice(self, commodity_group: str | None, commodity_classification: str | None) -> str:
        lines = []

        for _sector, groups in self.tree.items():
            group_items = (
                {commodity_group: groups[commodity_group]}
                if commodity_group and commodity_group in groups
                else groups
            )

            for group, classifications in group_items.items():
                lines.append(f"Group: {group}")

                cls_items = (
                    {commodity_classification: classifications[commodity_classification]}
                    if commodity_classification and commodity_classification in classifications
                    else classifications
                )

                for cls, instruments in cls_items.items():
                    lines.append(f"  Classification: {cls}")
                    lines.append(f"    Instruments: {', '.join(instruments)}")

        return "\n".join(lines)
