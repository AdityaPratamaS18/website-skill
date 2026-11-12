import { site, waLink } from "@/lib/site";

/* A fixed WhatsApp button. It shows only if site.whatsapp.number is set.
   It uses logical properties (end-4), so it moves to the left in RTL.
   The GA4 listener in Analytics.tsx counts each click as click_whatsapp. */
export default function WhatsAppButton({ message }: { message?: string }) {
  if (!site.whatsapp.number) return null;
  return (
    <a
      href={waLink(message)}
      target="_blank"
      rel="noopener"
      aria-label={`Chat with ${site.name} on WhatsApp`}
      className="fixed bottom-4 end-4 z-50 flex h-14 w-14 items-center justify-center rounded-full bg-[#25D366] text-white shadow-lg focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2"
    >
      <svg viewBox="0 0 32 32" width="30" height="30" fill="currentColor" aria-hidden="true">
        <path d="M16 3C8.8 3 3 8.7 3 15.8c0 2.5.7 4.9 2 7L3 29l6.4-2c2 1.1 4.3 1.7 6.6 1.7 7.2 0 13-5.7 13-12.8S23.2 3 16 3Zm0 23.4c-2.1 0-4.1-.6-5.9-1.7l-.4-.3-3.8 1.2 1.2-3.7-.3-.4a10.4 10.4 0 0 1-1.8-5.8C5 9.9 9.9 5.2 16 5.2s11 4.7 11 10.6-4.9 10.6-11 10.6Zm6-7.9c-.3-.2-2-1-2.3-1.1-.3-.1-.5-.2-.8.2-.2.3-.9 1.1-1.1 1.3-.2.2-.4.3-.7.1-.3-.2-1.4-.5-2.7-1.6-1-.9-1.7-2-1.9-2.3-.2-.3 0-.5.1-.7l.5-.6.3-.6c.1-.2 0-.4 0-.6l-1-2.5c-.3-.7-.6-.6-.8-.6h-.7c-.2 0-.6.1-.9.4-.3.3-1.2 1.1-1.2 2.8s1.2 3.2 1.4 3.5c.2.2 2.4 3.6 5.8 5 .8.4 1.4.6 1.9.7.8.3 1.6.2 2.2.1.7-.1 2-.8 2.3-1.6.3-.8.3-1.4.2-1.6-.1-.1-.3-.2-.6-.4Z" />
      </svg>
    </a>
  );
}
