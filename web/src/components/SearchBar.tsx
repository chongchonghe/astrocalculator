// web/src/components/SearchBar.tsx

interface SearchBarProps {
  value: string;
  onChange: (q: string) => void;
  inputRef: React.RefObject<HTMLInputElement | null>;
}

export default function SearchBar({ value, onChange, inputRef }: SearchBarProps) {
  return (
    <input
      ref={inputRef}
      type="text"
      value={value}
      onChange={e => onChange(e.target.value)}
      placeholder="Search (G, Planck, energy...)"
      style={{
        width: '100%',
        padding: '6px 10px',
        border: '1px solid var(--color-border)',
        borderRadius: 'var(--radius)',
        fontSize: 13,
        outline: 'none',
      }}
      onFocus={e => e.currentTarget.style.borderColor = 'var(--color-accent)'}
      onBlur={e => e.currentTarget.style.borderColor = 'var(--color-border)'}
    />
  );
}
