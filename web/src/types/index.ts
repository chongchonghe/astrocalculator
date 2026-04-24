export interface ConstantEntry {
  symbol: string;
  name: string;
  value: number;
  unit: string;
  uncertainty: number;
  ref: string;
}

export interface UnitEntry {
  name: string;
  category: string;
}

export interface EquationParam {
  symbol: string;
  default: string;
  description: string;
}

export interface EquationExpression {
  name: string;
  expression: string;
  latex?: string;
  description?: string;
}

export interface Equation {
  slug: string;
  title: string;
  category: string;
  tags: string[];
  params: EquationParam[];
  expressions: EquationExpression[];
  body?: string;
}

export interface CalculatorResult {
  parsed: string;
  si: string;
  cgs: string;
  converted?: string;
  targetUnit?: string;
}

export interface HistoryEntry {
  id: number;
  input: string;
  result: CalculatorResult;
  timestamp: number;
}

export type SidebarTab = 'constants' | 'units' | 'equations' | 'history';

export interface CalculatorWorkerAPI {
  evaluate: (expression: string) => Promise<CalculatorResult>;
  convert: (quantityStr: string, unit: string) => Promise<string>;
  ready: Promise<void>;
}
