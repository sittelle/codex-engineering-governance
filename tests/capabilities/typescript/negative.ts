// Deliberately capability-free TypeScript: local-only logic, no network,
// persistence, auth, subprocess, cloud, or mail. Used by
// scripts/test-registration-conformance.py to confirm the capability rules
// produce zero false positives on ordinary application code (precision).

interface Invoice {
  amount: number;
  taxRate: number;
}

function total(invoice: Invoice): number {
  return Math.round(invoice.amount * (1 + invoice.taxRate) * 100) / 100;
}

function parseInvoices(raw: string): Invoice[] {
  const data = JSON.parse(raw) as { amount: number; tax_rate: number }[];
  return data.map((item) => ({ amount: item.amount, taxRate: item.tax_rate }));
}

function summarize(invoices: Invoice[]) {
  const totals = invoices.map(total);
  const sum = totals.reduce((a, b) => a + b, 0);
  return { count: invoices.length, total: sum, average: sum / Math.max(invoices.length, 1) };
}

function standardDeviation(values: number[]): number {
  if (values.length === 0) return 0;
  const mean = values.reduce((a, b) => a + b, 0) / values.length;
  const variance = values.reduce((acc, v) => acc + (v - mean) ** 2, 0) / values.length;
  return Math.sqrt(variance);
}
