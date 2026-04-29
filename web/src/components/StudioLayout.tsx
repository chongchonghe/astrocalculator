// web/src/components/StudioLayout.tsx
import { useState } from 'react';
import type { ReactNode } from 'react';
import Sidebar from './Sidebar';
import type { SidebarTab } from '../types';

interface StudioLayoutProps {
  editor: ReactNode;
  results: ReactNode;
  onConstantClick: (symbol: string) => void;
  onEquationAdd: (params: { symbol: string; default: string }[], expression: string) => void;
  onHistoryClick: (input: string) => void;
  onSearchFocus: () => void;
  searchBarRef: React.RefObject<HTMLInputElement | null>;
  editorRef: React.RefObject<HTMLTextAreaElement | null>;
}

export default function StudioLayout({
  editor, results, onConstantClick, onEquationAdd,
  onHistoryClick, onSearchFocus: _onSearchFocus, searchBarRef, editorRef: _editorRef,
}: StudioLayoutProps) {
  const [activeTab, setActiveTab] = useState<SidebarTab>('equations');
  const [searchQuery, setSearchQuery] = useState('');

  return (
    <div style={{
      display: 'flex',
      height: '100%',
    }}>
      <Sidebar
        activeTab={activeTab}
        onTabChange={setActiveTab}
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        onConstantClick={onConstantClick}
        onEquationAdd={onEquationAdd}
        onHistoryClick={onHistoryClick}
        searchBarRef={searchBarRef}
      />
      <main style={{
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        padding: 16,
        gap: 12,
        minWidth: 0,
      }}>
        {editor}
        {results}
      </main>
    </div>
  );
}
