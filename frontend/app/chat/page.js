import ChatPanel from "@/components/chat/ChatPanel";
import PageShell from "@/components/ui/PageShell";

export const metadata = {
  title: "Chat — FootyIntel",
  description: "Ask questions about Premier League teams, form, and seasons using RAG.",
};

export default function ChatPage() {
  return (
    <PageShell
      kicker="Retrieval Augmented Generation"
      title="Match Chat"
      description="Ask about team form, season performance, and past Premier League matches. Answers are grounded in indexed match and season documents."
    >
      <ChatPanel />
    </PageShell>
  );
}
