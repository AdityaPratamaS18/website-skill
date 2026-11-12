"use client";

import { useState } from "react";

/* The form for a static site. Web3Forms sends each message to the email of
   the account that owns the key. Pass site.web3formsKey from a Server
   Component: do not import site.ts here, or the plan goes into the browser bundle.
   The hidden botcheck field is the honeypot. A person never sees it, so a
   value in it means a bot. Web3Forms drops those messages.
   The GA4 listener in Analytics.tsx sends generate_lead on submit. */
type Status = "idle" | "sending" | "sent" | "error";

export default function ContactForm({ accessKey, subject }: { accessKey: string; subject: string }) {
  const [status, setStatus] = useState<Status>("idle");
  if (!accessKey) return null;

  async function onSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const form = event.currentTarget;
    const data = new FormData(form);
    if (data.get("botcheck")) return;
    setStatus("sending");
    try {
      const response = await fetch("https://api.web3forms.com/submit", {
        method: "POST",
        headers: { "Content-Type": "application/json", Accept: "application/json" },
        body: JSON.stringify(Object.fromEntries(data)),
      });
      const result = await response.json();
      if (!response.ok || !result.success) throw new Error(result.message);
      form.reset();
      setStatus("sent");
    } catch {
      setStatus("error");
    }
  }

  return (
    <form id="contact-form" onSubmit={onSubmit}>
      <input type="hidden" name="access_key" value={accessKey} />
      <input type="hidden" name="subject" value={subject} />
      <input
        type="checkbox"
        name="botcheck"
        tabIndex={-1}
        autoComplete="off"
        aria-hidden="true"
        style={{ position: "absolute", left: "-9999px" }}
      />
      <label htmlFor="cf-name">Name</label>
      <input id="cf-name" name="name" required autoComplete="name" />
      <label htmlFor="cf-email">Email</label>
      <input id="cf-email" name="email" type="email" required autoComplete="email" />
      <label htmlFor="cf-phone">Phone</label>
      <input id="cf-phone" name="phone" type="tel" autoComplete="tel" />
      <label htmlFor="cf-message">Message</label>
      <textarea id="cf-message" name="message" required rows={5} />
      <button type="submit" disabled={status === "sending"}>
        {status === "sending" ? "Sending" : "Send message"}
      </button>
      <p role="status" aria-live="polite">
        {status === "sent" && "Thank you. We received your message and will reply soon."}
        {status === "error" && "The message did not send. Please call or WhatsApp us."}
      </p>
    </form>
  );
}
