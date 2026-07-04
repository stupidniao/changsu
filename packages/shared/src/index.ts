import { z } from "zod";

export const healthResponseSchema = z.object({
  status: z.literal("ok"),
});

export type HealthResponse = z.infer<typeof healthResponseSchema>;

export const agentDebugOptionsSchema = z.object({
  dry_run: z.boolean().default(false),
  explain: z.boolean().default(false),
});

export const agentMessageRequestSchema = z.object({
  message: z.string().min(1).max(1000),
  conversation_id: z.string().optional(),
  debug: agentDebugOptionsSchema.default({ dry_run: false, explain: false }),
});

export const traceStepSchema = z.object({
  kind: z.string(),
  message: z.string(),
  data: z.record(z.unknown()).default({}),
});

export const toolCallTraceSchema = z.object({
  name: z.string(),
  args: z.record(z.unknown()).default({}),
  result: z.record(z.unknown()).nullable().optional(),
  error: z.string().nullable().optional(),
});

export const agentDebugTraceSchema = z.object({
  trace_id: z.string(),
  conversation_id: z.string().nullable().optional(),
  intent: z.string(),
  candidate_tools: z.array(z.string()).default([]),
  tool_calls: z.array(toolCallTraceSchema).default([]),
  steps: z.array(traceStepSchema).default([]),
  dry_run: z.boolean(),
  explain: z.boolean(),
});

export const agentMessageResponseSchema = z.object({
  trace_id: z.string(),
  reply: z.string(),
  debug_trace: agentDebugTraceSchema.nullable().optional(),
});

export type AgentMessageRequest = z.infer<typeof agentMessageRequestSchema>;
export type AgentMessageResponse = z.infer<typeof agentMessageResponseSchema>;

export const billDirectionSchema = z.union([z.literal("expense"), z.literal("income")]);

export const billCreateSchema = z.object({
  amount: z.number().positive(),
  currency: z.string().default("CNY"),
  direction: billDirectionSchema.default("expense"),
  occurred_at: z.string().optional(),
  category: z.string().default("uncategorized"),
  account: z.string().default("default"),
  merchant: z.string().nullable().optional(),
  note: z.string().nullable().optional(),
  raw_text: z.string().nullable().optional(),
  trace_id: z.string().nullable().optional(),
});

export const billReadSchema = billCreateSchema.extend({
  id: z.number().nullable().optional(),
  occurred_at: z.string(),
  dry_run: z.boolean().default(false),
});

export const billSummarySchema = z.object({
  period: z.string(),
  total_expense: z.number(),
  total_income: z.number(),
  count: z.number(),
});

export const debugBillCreateResponseSchema = z.object({
  dry_run: z.boolean(),
  bill: billReadSchema,
});

export const debugBillListResponseSchema = z.object({
  dry_run: z.boolean(),
  bills: z.array(billReadSchema),
});

export const debugBillSummaryResponseSchema = z.object({
  dry_run: z.boolean(),
  summary: billSummarySchema,
});

export type BillCreate = z.infer<typeof billCreateSchema>;
export type BillRead = z.infer<typeof billReadSchema>;
export type BillSummary = z.infer<typeof billSummarySchema>;
