interface UserMessageProps {
  content: string;
}

export function UserMessage({ content }: UserMessageProps) {
  return (
    <div className="flex justify-end animate-fade-in-up">
      <div className="bg-accent-blue text-white px-4 py-3 rounded-2xl rounded-br-md max-w-xl text-sm leading-relaxed">
        {content}
      </div>
    </div>
  );
}
