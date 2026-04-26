import Link from "next/link";

export function Header() {
  return (
    <header className="border-b border-border bg-secondary px-4 sm:px-6 py-3 sm:py-4 flex items-center justify-between">
      <div className="flex items-center gap-2">
        <span className="text-lg sm:text-xl">⚖️</span>
        <span className="font-semibold text-text-primary text-sm sm:text-base">Lexiora</span>
        <span className="text-text-muted text-xs sm:text-sm ml-2 hidden sm:inline">法律咨询助手</span>
      </div>
      <nav className="flex items-center gap-3 sm:gap-4">
        <Link
          href="/"
          className="text-text-secondary hover:text-text-primary text-xs sm:text-sm transition-colors"
        >
          对话
        </Link>
        <Link
          href="/about"
          className="text-text-secondary hover:text-text-primary text-xs sm:text-sm transition-colors"
        >
          关于
        </Link>
      </nav>
    </header>
  );
}
