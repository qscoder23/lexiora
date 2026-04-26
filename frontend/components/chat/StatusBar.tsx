import clsx from "clsx";

const STEPS = [
  { key: "intent", label: "识别意图", icon: "🔍" },
  { key: "retrieve", label: "检索知识", icon: "📚" },
  { key: "generate", label: "生成回答", icon: "✍️" },
];

interface StatusBarProps {
  currentStep: string | null;
}

export function StatusBar({ currentStep }: StatusBarProps) {
  const stepIndex = STEPS.findIndex((s) => s.key === currentStep);

  return (
    <div className="flex items-center gap-2 py-2">
      {STEPS.map((step, idx) => {
        const isDone = stepIndex > idx;
        const isActive = stepIndex === idx;

        return (
          <div key={step.key} className="flex items-center gap-2">
            <div
              className={clsx(
                "flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium border transition-all",
                isDone && "bg-accent-gold/15 text-accent-gold border-accent-gold/30",
                isActive && "bg-accent-gold/10 text-accent-gold border-accent-gold/20 animate-pulse",
                !isDone && !isActive && "bg-card text-text-muted border-border"
              )}
            >
              <span>{step.icon}</span>
              <span>{step.label}</span>
            </div>
            {idx < STEPS.length - 1 && (
              <div className="w-4 h-px bg-border" />
            )}
          </div>
        );
      })}
    </div>
  );
}
