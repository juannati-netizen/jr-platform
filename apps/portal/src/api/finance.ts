import { apiRequest } from './client'
import type {
  Invoice,
  InvoiceStatus,
  PaymentMethod,
  Quote,
  QuoteStatus,
} from './types'

export interface LineItemInput {
  description: string
  quantity: string
  unit_price: string
  tax_rate: string
}

export interface QuoteInput {
  client_id: string
  work_order_id?: string | null
  valid_until?: string | null
  notes?: string
  items: LineItemInput[]
}

export interface InvoiceInput {
  client_id: string
  work_order_id?: string | null
  due_date?: string | null
  notes?: string
  items: LineItemInput[]
}

export interface PaymentInput {
  amount: string
  method: PaymentMethod
  paid_at?: string | null
  reference?: string
  notes?: string
}

export function getQuotes(): Promise<Quote[]> {
  return apiRequest<Quote[]>('/quotes')
}

export function createQuote(payload: QuoteInput): Promise<Quote> {
  return apiRequest<Quote>('/quotes', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function updateQuote(
  quoteId: string,
  payload: { status?: QuoteStatus; valid_until?: string | null; notes?: string },
): Promise<Quote> {
  return apiRequest<Quote>(`/quotes/${quoteId}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  })
}

export function convertQuoteToInvoice(quoteId: string, dueDate?: string): Promise<Invoice> {
  const query = dueDate ? `?due_date=${encodeURIComponent(dueDate)}` : ''
  return apiRequest<Invoice>(`/quotes/${quoteId}/convert-to-invoice${query}`, {
    method: 'POST',
  })
}

export function getInvoices(): Promise<Invoice[]> {
  return apiRequest<Invoice[]>('/invoices')
}

export function createInvoice(payload: InvoiceInput): Promise<Invoice> {
  return apiRequest<Invoice>('/invoices', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function updateInvoice(
  invoiceId: string,
  payload: { status?: InvoiceStatus; due_date?: string | null; notes?: string },
): Promise<Invoice> {
  return apiRequest<Invoice>(`/invoices/${invoiceId}`, {
    method: 'PATCH',
    body: JSON.stringify(payload),
  })
}

export function addInvoicePayment(invoiceId: string, payload: PaymentInput): Promise<Invoice> {
  return apiRequest<Invoice>(`/invoices/${invoiceId}/payments`, {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}
