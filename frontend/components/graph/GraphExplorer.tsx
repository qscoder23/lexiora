"use client";

import { useMemo, useState } from "react";
import { evidenceItems, graphEdges, graphNodes } from "@/lib/data";

export function GraphExplorer() {
  const [selectedId, setSelectedId] = useState("issue");
  const [showCases, setShowCases] = useState(true);
  const selected = graphNodes.find((node) => node.id === selectedId) ?? graphNodes[0];
  const visibleNodes = useMemo(
    () => graphNodes.filter((node) => showCases || node.type !== "case"),
    [showCases],
  );
  const visibleIds = new Set(visibleNodes.map((node) => node.id));

  return (
    <div className="graph-layout">
      <aside className="panel graph-filter">
        <div className="panel-title">Graph filters</div>
        <label className="field">
          <span>Entity search</span>
          <input placeholder="Search issue, law, case..." />
        </label>
        <label className="check-row">
          <input checked readOnly type="checkbox" />
          Law and issues
        </label>
        <label className="check-row">
          <input checked={showCases} onChange={(event) => setShowCases(event.target.checked)} type="checkbox" />
          Cases
        </label>
        <label className="field">
          <span>Depth</span>
          <input max="3" min="1" readOnly type="range" value="2" />
        </label>
        <div className="legend">
          {["issue", "law", "case", "behavior", "responsibility"].map((type) => (
            <span key={type}>
              <i className={`dot ${type}`} />
              {type}
            </span>
          ))}
        </div>
      </aside>

      <section className="graph-canvas" aria-label="Knowledge graph">
        <svg viewBox="0 0 100 100" role="img" aria-label="Graph relationships">
          {graphEdges
            .filter((edge) => visibleIds.has(edge.from) && visibleIds.has(edge.to))
            .map((edge) => {
              const from = graphNodes.find((node) => node.id === edge.from)!;
              const to = graphNodes.find((node) => node.id === edge.to)!;
              return <line key={edge.id} x1={from.x} x2={to.x} y1={from.y} y2={to.y} />;
            })}
          {visibleNodes.map((node) => (
            <g
              className={`graph-node ${node.type} ${selectedId === node.id ? "selected" : ""}`}
              key={node.id}
              onClick={() => setSelectedId(node.id)}
              role="button"
              tabIndex={0}
            >
              <circle cx={node.x} cy={node.y} r={selectedId === node.id ? 8 : 6} />
              <text x={node.x} y={node.y + 12}>
                {node.label}
              </text>
            </g>
          ))}
        </svg>
        <div className="canvas-controls">
          <button className="button secondary" type="button">
            Fit
          </button>
          <button className="button secondary" type="button">
            Reset
          </button>
        </div>
      </section>

      <aside className="panel node-inspector">
        <div className="panel-title">Node inspector</div>
        <span className={`source-type ${selected.type}`}>{selected.type}</span>
        <h2>{selected.label}</h2>
        <p>{selected.summary}</p>
        <div className="metadata-grid">
          <div>
            <dt>Linked evidence</dt>
            <dd>{evidenceItems.length}</dd>
          </div>
          <div>
            <dt>Relations</dt>
            <dd>{graphEdges.filter((edge) => edge.from === selected.id || edge.to === selected.id).length}</dd>
          </div>
        </div>
        <button className="button primary" type="button">
          Open evidence
        </button>
      </aside>
    </div>
  );
}
