import plan from "./site-plan.json";

/* The only place for business data. Replace each marked value from facts.md.
   Leave an optional field empty if the client does not have it. */
export const site = {
  name: "__FILL_PUBLIC_NAME__",
  legalName: "__FILL_LEGAL_NAME__",
  tagline: "__FILL_TAGLINE__",
  description: "__FILL_COMPANY_DESCRIPTION__",
  url: plan.domain,
  /* Use the most exact schema.org subtype, such as GeneralContractor. */
  schemaType: "LocalBusiness",
  logo: "/logo.webp",
  ogImage: "/og.webp",
  email: "__FILL_EMAIL__",
  phone: "__FILL_PHONE_DISPLAY__",
  phoneHref: "tel:__FILL_PHONE_DIGITS__",
  /* Digits only, with the country code. Empty if the client has no WhatsApp. */
  whatsapp: { number: "", message: "" },
  address: {
    street: "__FILL_STREET__",
    city: "__FILL_CITY__",
    region: "",
    postalCode: "",
    country: "__FILL_COUNTRY_CODE__",
  },
  /* Schema.org format, such as "Mo-Fr 08:30-17:30". */
  openingHours: [] as string[],
  areaServed: [] as string[],
  foundingDate: "",
  social: [] as string[],
  gaId: "",
  clarityId: "",
};

export function waLink(message?: string) {
  const text = message ?? site.whatsapp.message;
  const base = `https://wa.me/${site.whatsapp.number}`;
  return text ? `${base}?text=${encodeURIComponent(text)}` : base;
}
