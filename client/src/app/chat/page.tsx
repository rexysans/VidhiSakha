"use client";

import dynamic from "next/dynamic";

const JurisprudenceChat = dynamic(
  () => import("@/components/chat/jurisprudence-chat").then((mod) => mod.JurisprudenceChat),
  { ssr: false }
);

export default function ChatPage() {
  return <JurisprudenceChat />;
}
