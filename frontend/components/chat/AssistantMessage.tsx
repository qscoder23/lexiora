import { useState } from "react";
import { DomainBadge } from "@/components/ui/Badge";

interface AssistantMessageProps {
  content: string;
  domain?: string;
  domain_zh?: string;
  sources?: string[];
}

export function AssistantMessage({
  content,
  domain,
  domain_zh,
  sources = [],
}: AssistantMessageProps) {
  const [sourcesOpen, setSourcesOpen] = useState(false);

  return (
    <div className="flex flex-col gap-2 animate-fade-in-up">
      {domain && domain_zh && (
        <DomainBadge domain={domain} domain_zh={domain_zh} />
      )}
      <div className="bg-card border border-border px-4 py-3 rounded-2xl rounded-bl-md max-w-xl text-sm leading-relaxed text-text-primary">
        {content}
      </div>
      {sources.length > 0 && (
        <div>
          <button
            onClick={() => setSourcesOpen(!sourcesOpen)}
            className="text-xs text-text-muted hover:text-accent-gold transition-colors"
          >
            📖 引用来源 ({sources.length})
          </button>
          {sourcesOpen && (
            <ul className="mt-2 space-y-1">
              {sources.map((src, i) => (
                <li
                  key={i}
                  className="text-xs text-text-secondary bg-secondary px-3 py-1.5 rounded-lg border border-border"
                >
                  {src}
                </li>
              ))}
            </ul>
          )}
        </div>
      )}
    </div>
  );
}
