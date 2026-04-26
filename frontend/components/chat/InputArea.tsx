import { useState } from "react";

interface InputAreaProps {
  onSend: (question: string) => void;
  disabled?: boolean;
}

export function InputArea({ onSend, disabled }: InputAreaProps) {
  const [input, setInput] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || disabled) return;
    onSend(input.trim());
    setInput("");
  };

  return (
    <form onSubmit={handleSubmit} className="flex gap-2">
      <input
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        disabled={disabled}
        placeholder="输入法律问题..."
        className="flex-1 bg-card border border-border rounded-xl px-3 sm:px-4 py-2.5 sm:py-3 text-sm text-text-primary placeholder:text-text-muted focus:outline-none focus:border-accent-gold transition-colors disabled:opacity-50"
      />
      <button
        type="submit"
        disabled={disabled || !input.trim()}
        className="bg-accent-gold text-primary px-4 sm:px-5 py-2.5 sm:py-3 rounded-xl font-medium text-sm hover:bg-accent-gold transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        发送
      </button>
    </form>
  );
}
