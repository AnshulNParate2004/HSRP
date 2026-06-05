/** Renders assistant text with basic markdown (bold, lists) — no streaming. */

function renderInline(text: string) {
  const parts = text.split(/(\*\*[^*]+\*\*)/g);
  return parts.map((part, i) => {
    if (part.startsWith("**") && part.endsWith("**")) {
      return (
        <strong key={i} className="font-semibold text-foreground">
          {part.slice(2, -2)}
        </strong>
      );
    }
    return <span key={i}>{part}</span>;
  });
}

interface AssistantAnswerProps {
  text: string;
}

export function AssistantAnswer({ text }: AssistantAnswerProps) {
  const lines = text.split("\n");

  return (
    <div className="space-y-2 text-sm leading-relaxed text-foreground/90">
      {lines.map((line, i) => {
        const trimmed = line.trim();
        if (!trimmed) return <div key={i} className="h-1" />;

        const numbered = trimmed.match(/^(\d+)\.\s+\*\*(.+?)\*\*(.*)$/);
        if (numbered) {
          return (
            <p key={i}>
              <span className="font-semibold">{numbered[1]}.</span>{" "}
              <strong>{numbered[2]}</strong>
              {renderInline(numbered[3])}
            </p>
          );
        }

        const bullet = trimmed.match(/^[-•]\s+(.*)$/);
        if (bullet) {
          return (
            <p key={i} className="pl-3 border-l-2 border-primary/20">
              {renderInline(bullet[1])}
            </p>
          );
        }

        const numberedPlain = trimmed.match(/^(\d+)\.\s+(.*)$/);
        if (numberedPlain) {
          return (
            <p key={i}>
              <span className="font-semibold">{numberedPlain[1]}.</span> {renderInline(numberedPlain[2])}
            </p>
          );
        }

        return <p key={i}>{renderInline(trimmed)}</p>;
      })}
    </div>
  );
}
