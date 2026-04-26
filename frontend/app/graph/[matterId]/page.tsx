import { GraphExplorer } from "@/components/graph/GraphExplorer";
import { MatterHeader } from "@/components/matter/MatterHeader";
import { AppShell } from "@/components/shell/AppShell";
import { currentMatter } from "@/lib/data";

export default function GraphPage() {
  return (
    <AppShell active="Graph">
      <div className="page-stack">
        <MatterHeader matter={currentMatter} />
        <GraphExplorer />
      </div>
    </AppShell>
  );
}
