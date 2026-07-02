import { View, Text } from "@tarojs/components";
import { healthResponseSchema } from "@changsu/shared";
import "./index.scss";

const placeholderHealth = healthResponseSchema.parse({ status: "ok" });

export default function IndexPage() {
  return (
    <View className="index">
      <Text className="title">Changsu 个人助手</Text>
      <Text className="subtitle">账单 · 跑步 · 喝酒 · 知识管理</Text>
      <Text className="status">API 占位状态: {placeholderHealth.status}</Text>
    </View>
  );
}
