"use client";

import { useEffect, useRef, useState, useTransition } from "react";
import { chatAction } from "@/lib/actions";
import ErrorAlert from "@/components/ui/ErrorAlert";
import GlassCard from "@/components/ui/GlassCard";

const SUGGESTIONS = [
  "How did Arsenal perform in the 2023-24 Premier League season?",
  "How is Liverpool at home vs away in 2024-25?",
  "What is the head-to-head between Man City and Chelsea?",
  "What was Arsenal's worst season in the last 5 years?",
];

function MessageBubble({ role, content }) {
  const isUser = role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[90%] border-2 border-black px-4 py-3 shadow-[3px_3px_0px_0px_#121212] sm:max-w-[80%] ${
          isUser ? "bg-[#1040C0] text-white" : "bg-white text-[#121212]"
        }`}
      >
        <p className="mb-1 text-[0.65rem] font-black uppercase tracking-widest opacity-70">
          {isUser ? "You" : "FootyIntel"}
        </p>
        <p className="whitespace-pre-wrap text-sm font-medium leading-relaxed">{content}</p>
      </div>
    </div>
  );
}

export default function ChatPanel() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [conversationId, setConversationId] = useState("");
  const [error, setError] = useState("");
  const [isPending, startTransition] = useTransition();
  const bottomRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [messages, isPending]);

  function sendMessage(rawMessage) {
    const message = rawMessage.trim();
    if (!message || isPending) {
      return;
    }

    setError("");
    setInput("");
    setMessages((current) => [...current, { role: "user", content: message }]);

    startTransition(async () => {
      const result = await chatAction({
        message,
        conversation_id: conversationId || undefined,
      });

      if (result.error) {
        setError(result.error);
        setMessages((current) => [
          ...current,
          {
            role: "assistant",
            content: "I couldn't answer that right now. Please try again.",
          },
        ]);
        return;
      }

      setConversationId(result.data.conversation_id);
      setMessages((current) => [
        ...current,
        { role: "assistant", content: result.data.reply },
      ]);
    });
  }

  function handleSubmit(event) {
    event.preventDefault();
    sendMessage(input);
  }

  function handleClear() {
    setMessages([]);
    setConversationId("");
    setError("");
    setInput("");
    inputRef.current?.focus();
  }

  return (
    <div className="space-y-6">
      <GlassCard accent="yellow" padding="p-0" className="overflow-hidden">
        <div className="flex items-center justify-between border-b-4 border-black bg-[#F0C020] px-4 py-3 sm:px-6">
          <div>
            <p className="text-xs font-black uppercase tracking-widest">RAG Assistant</p>
            <p className="text-sm font-medium text-[#121212]/70">
              Ask about Premier League form, matches, and seasons
            </p>
          </div>
          {messages.length > 0 ? (
            <button
              type="button"
              className="bauhaus-btn bauhaus-btn-outline px-3 py-2 text-xs"
              onClick={handleClear}
              disabled={isPending}
            >
              Clear
            </button>
          ) : null}
        </div>

        <div className="flex h-[min(60vh,32rem)] flex-col bg-[#F0F0F0]">
          <div className="min-h-0 flex-1 space-y-4 overflow-y-auto px-4 py-5 sm:px-6">
            {messages.length === 0 ? (
              <div className="space-y-4">
                <p className="text-sm font-medium text-[#121212]/60">
                  Try one of these questions to get started:
                </p>
                <div className="flex flex-col gap-2">
                  {SUGGESTIONS.map((suggestion) => (
                    <button
                      key={suggestion}
                      type="button"
                      className="border-2 border-black bg-white px-4 py-3 text-left text-sm font-semibold shadow-[3px_3px_0px_0px_#121212] transition hover:bg-[#1040C0] hover:text-white disabled:opacity-50"
                      onClick={() => sendMessage(suggestion)}
                      disabled={isPending}
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              messages.map((message, index) => (
                <MessageBubble key={`${message.role}-${index}`} {...message} />
              ))
            )}

            {isPending ? (
              <div className="flex justify-start">
                <div className="border-2 border-black bg-white px-4 py-3 shadow-[3px_3px_0px_0px_#121212]">
                  <span className="flex items-center gap-2 text-sm font-bold uppercase tracking-wider">
                    <span className="loading loading-spinner loading-sm" />
                    Thinking...
                  </span>
                </div>
              </div>
            ) : null}

            <div ref={bottomRef} />
          </div>

          <form
            onSubmit={handleSubmit}
            className="border-t-4 border-black bg-white p-4 sm:p-5"
          >
            <div className="flex flex-col gap-3 sm:flex-row">
              <label className="sr-only" htmlFor="chat-message">
                Message
              </label>
              <input
                ref={inputRef}
                id="chat-message"
                type="text"
                className="input-bauhaus w-full flex-1 px-4 py-3 text-sm font-semibold"
                placeholder="Ask about a team, season, or match..."
                value={input}
                onChange={(event) => setInput(event.target.value)}
                disabled={isPending}
                autoComplete="off"
              />
              <button
                type="submit"
                className="bauhaus-btn bauhaus-btn-yellow w-full sm:w-auto"
                disabled={isPending || !input.trim()}
              >
                {isPending ? "Sending..." : "Send"}
              </button>
            </div>
          </form>
        </div>
      </GlassCard>

      {error ? <ErrorAlert message={error} /> : null}
    </div>
  );
}
