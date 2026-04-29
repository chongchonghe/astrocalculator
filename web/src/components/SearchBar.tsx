// web/src/components/SearchBar.tsx
import type { SidebarTab } from '../types';

interface SearchBarProps {
  value: string;
  onChange: (q: string) => void;
  inputRef: React.RefObject<HTMLInputElement | null>;
  activeTab: SidebarTab;
}

const PLACEHOLDERS: Record<SidebarTab, string> = {
  equations: 'Search equations...',
  constants: 'Search constants...',
  units: 'Search units...',
  history: 'Search history...',
};

export default function SearchBar({ value, onChange, inputRef, activeTab }: SearchBarProps) {
  return (
    <input
      ref={inputRef}
      type="text"
      value={value}
      onChange={e => onChange(e.target.value)}
      placeholder={PLACEHOLDERS[activeTab]}
      style={{
        width: '100%',
        padding: '6px 10px',
        border: '1px solid var(--color-border)',
        borderRadius: 'var(--radius)',
        fontSize: 'var(--font-base)',
        outline: 'none',
      }}
      onFocus={e => e.currentTarget.style.borderColor = 'var(--color-accent)'}
      onBlur={e => e.currentTarget.style.borderColor = 'var(--color-border)'}
    />
  );
}
