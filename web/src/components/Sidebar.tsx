// web/src/components/Sidebar.tsx
import type { SidebarTab } from '../types';
import SearchBar from './SearchBar';
import ConstantsTable from './ConstantsTable';
import UnitsTable from './UnitsTable';
import EquationTemplates from './EquationTemplates';
import HistoryPanel from './HistoryPanel';

interface SidebarProps {
  activeTab: SidebarTab;
  onTabChange: (tab: SidebarTab) => void;
  searchQuery: string;
  onSearchChange: (q: string) => void;
  onConstantClick: (symbol: string) => void;
  onEquationAdd: (params: { symbol: string; default: string }[], expression: string) => void;
  onHistoryClick: (input: string) => void;
  searchBarRef: React.RefObject<HTMLInputElement | null>;
}

const TABS: { key: SidebarTab; label: string }[] = [
  { key: 'equations', label: 'Equations' },
  { key: 'constants', label: 'Constants' },
  { key: 'units', label: 'Units' },
  { key: 'history', label: 'History' },
];

export default function Sidebar({
  activeTab, onTabChange, searchQuery, onSearchChange,
  onConstantClick, onEquationAdd, onHistoryClick, searchBarRef,
}: SidebarProps) {
  return (
    <aside style={{
      width: 'var(--sidebar-width)',
      borderRight: '1px solid var(--color-border)',
      background: 'var(--color-surface)',
      display: 'flex',
      flexDirection: 'column',
      height: '100%',
    }}>
      <div style={{ padding: '8px 12px' }}>
        <SearchBar
          value={searchQuery}
          onChange={onSearchChange}
          inputRef={searchBarRef}
          activeTab={activeTab}
        />
      </div>
      <div style={{
        display: 'flex',
        borderBottom: '1px solid var(--color-border)',
        padding: '0 12px',
      }}>
        {TABS.map(tab => (
          <button
            key={tab.key}
            onClick={() => onTabChange(tab.key)}
            style={{
              padding: '6px 10px',
              border: 'none',
              background: 'none',
              borderBottom: activeTab === tab.key ? '2px solid var(--color-accent)' : '2px solid transparent',
              color: activeTab === tab.key ? 'var(--color-accent)' : 'var(--color-text-muted)',
              fontWeight: activeTab === tab.key ? 600 : 400,
              cursor: 'pointer',
              fontSize: 'var(--font-sm)',
            }}
          >
            {tab.label}
          </button>
        ))}
      </div>
      <div style={{ flex: 1, overflow: 'hidden' }}>
        {activeTab === 'constants' && (
          <ConstantsTable query={searchQuery} onClick={onConstantClick} />
        )}
        {activeTab === 'units' && (
          <UnitsTable query={searchQuery} onClick={onConstantClick} />
        )}
        {activeTab === 'equations' && (
          <EquationTemplates query={searchQuery} onAdd={onEquationAdd} />
        )}
        {activeTab === 'history' && (
          <HistoryPanel onClick={onHistoryClick} query={searchQuery} />
        )}
      </div>
    </aside>
  );
}
