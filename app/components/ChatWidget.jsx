"use client";

import { useState } from "react";

export default function ChatWidget() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(event) {
    event.preventDefault();

    setLoading(true);
    setAnswer("");

    const response = await fetch(
      "http://127.0.0.1:8000/chat",
      {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: question,
        }),
      }
    );

    const data = await response.json();

    setAnswer(data.answer);
    setLoading(false);
  }

  return (
    <div>
      <h2>Mission Control AI Assistant</h2>

      <form onSubmit={handleSubmit}>
        <input
          type="text"
          value={question}
          onChange={(event) =>
            setQuestion(event.target.value)
          }
          placeholder="Ask about SpaceX..."
        />

        <button type="submit">
          Ask
        </button>
      </form>

      {loading && <p>Thinking...</p>}

      {answer && (
        <div>
          <h3>Answer</h3>
          <p>{answer}</p>
        </div>
      )}
    </div>
  );
}