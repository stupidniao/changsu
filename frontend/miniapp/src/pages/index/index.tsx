import { Button, Input, Text, View } from "@tarojs/components";
import Taro from "@tarojs/taro";
import { useState } from "react";
import {
  agentMessageResponseSchema,
  debugBillCreateResponseSchema,
  debugBillListResponseSchema,
  debugBillSummaryResponseSchema,
} from "@changsu/shared";
import "./index.scss";

const API_BASE_URL = "http://localhost:8000";

type DebugMode = "agent" | "create-bill" | "recent-bills" | "bill-summary";

const modeLabels: Record<DebugMode, string> = {
  agent: "Agent",
  "create-bill": "Create Bill API",
  "recent-bills": "Recent API",
  "bill-summary": "Summary API",
};

export default function IndexPage() {
  const [mode, setMode] = useState<DebugMode>("agent");
  const [message, setMessage] = useState("");
  const [reply, setReply] = useState("选择调试模式后输入内容，例如：今天午饭 38 元。");
  const [trace, setTrace] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function submitDebugRequest() {
    const trimmed = message.trim();
    if (loading || (mode !== "recent-bills" && mode !== "bill-summary" && !trimmed)) {
      return;
    }

    setLoading(true);
    setReply(`${modeLabels[mode]} 请求中...`);
    setTrace(null);
    try {
      if (mode === "agent") {
        await callAgent(trimmed);
      } else if (mode === "create-bill") {
        await callCreateBill(trimmed);
      } else if (mode === "recent-bills") {
        await callRecentBills();
      } else {
        await callBillSummary();
      }
    } catch (error) {
      setReply(`请求失败：${error instanceof Error ? error.message : "未知错误"}`);
    } finally {
      setLoading(false);
    }
  }

  async function callAgent(input: string) {
    const requestBody = {
      message: input,
      debug: {
        dry_run: true,
        explain: true,
      },
    };
    const url = `${API_BASE_URL}/agent/messages`;
    const response = await Taro.request({
      url,
      method: "POST",
      data: requestBody,
    });
    const parsed = agentMessageResponseSchema.parse(response.data);
    setReply(parsed.reply);
    setTrace(formatDebugPayload({ method: "POST", url, body: requestBody, response: parsed }));
  }

  async function callCreateBill(input: string) {
    const amount = Number(input.match(/\d+(?:\.\d+)?/)?.[0]);
    if (!Number.isFinite(amount) || amount <= 0) {
      setReply("Create Bill API 需要输入一个金额，例如：38 或 午饭 38。");
      return;
    }

    const requestBody = {
      amount,
      currency: "CNY",
      direction: "expense",
      category: inferCategory(input),
      account: "debug",
      note: input,
      raw_text: input,
      trace_id: "miniapp-debug",
    };
    const url = `${API_BASE_URL}/debug/bills/create?dry_run=true`;
    const response = await Taro.request({
      url,
      method: "POST",
      data: requestBody,
    });
    const parsed = debugBillCreateResponseSchema.parse(response.data);
    setReply(`Create Bill API 返回：${parsed.bill.category} ${parsed.bill.amount} ${parsed.bill.currency}`);
    setTrace(formatDebugPayload({ method: "POST", url, body: requestBody, response: parsed }));
  }

  async function callRecentBills() {
    const url = `${API_BASE_URL}/debug/bills/recent?limit=10&dry_run=true`;
    const response = await Taro.request({ url, method: "GET" });
    const parsed = debugBillListResponseSchema.parse(response.data);
    setReply(`Recent API 返回 ${parsed.bills.length} 条账单。dry_run=${parsed.dry_run}`);
    setTrace(formatDebugPayload({ method: "GET", url, response: parsed }));
  }

  async function callBillSummary() {
    const url = `${API_BASE_URL}/debug/bills/summary?dry_run=true`;
    const response = await Taro.request({ url, method: "GET" });
    const parsed = debugBillSummaryResponseSchema.parse(response.data);
    setReply(`Summary API 返回：${parsed.summary.period} 支出 ${parsed.summary.total_expense} CNY。`);
    setTrace(formatDebugPayload({ method: "GET", url, response: parsed }));
  }

  return (
    <View className="index">
      <Text className="title">Changsu 个人助手</Text>
      <Text className="subtitle">可通过 Agent 或 direct API 调试 bill domain。</Text>

      <View className="mode-switcher">
        {Object.entries(modeLabels).map(([key, label]) => (
          <Button
            key={key}
            className={mode === key ? "mode-button mode-button-active" : "mode-button"}
            onClick={() => {
              setMode(key as DebugMode);
              setTrace(null);
              setReply(`${label} 调试模式已选择。`);
            }}
          >
            {label}
          </Button>
        ))}
      </View>

      <View className="composer">
        <Input
          className="message-input"
          value={message}
          placeholder={mode === "agent" ? "例如：今天午饭 38 元" : "API create 输入金额；recent/summary 可留空"}
          confirmType="send"
          onInput={(event) => setMessage(event.detail.value)}
          onConfirm={submitDebugRequest}
        />
        <Button className="send-button" loading={loading} onClick={submitDebugRequest}>
          调试
        </Button>
      </View>

      <View className="reply-card">
        <Text className="reply-title">{modeLabels[mode]} 回复</Text>
        <Text className="reply">{reply}</Text>
      </View>

      {trace ? (
        <View className="trace-card">
          <Text className="reply-title">Debug Trace</Text>
          <Text className="trace">{trace}</Text>
        </View>
      ) : null}
    </View>
  );
}

function formatDebugPayload(payload: unknown) {
  return JSON.stringify(payload, null, 2);
}

function inferCategory(input: string) {
  if (["饭", "午饭", "晚饭", "早餐", "咖啡", "奶茶", "餐", "吃"].some((keyword) => input.includes(keyword))) {
    return "food";
  }
  if (["打车", "地铁", "公交", "高铁", "机票"].some((keyword) => input.includes(keyword))) {
    return "transport";
  }
  return "uncategorized";
}
