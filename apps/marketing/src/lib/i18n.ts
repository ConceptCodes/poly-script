export const locales = ["en", "de", "es", "fr", "jp"] as const;
export type Locale = (typeof locales)[number];

type Copy = {
  nav: {
    features: string;
    pricing: string;
    docs: string;
    blog: string;    legal: string;
    contact: string;
    legal: string;
    cta: string;
  };
  hero: {
    eyebrow: string;
    title: string;
    subtitle: string;
    primary: string;
    secondary: string;
  };
  trust: string;
  features: {
    title: string;
    items: { title: string; body: string }[];
  };
  workflow: {
    title: string;
    steps: { title: string; body: string }[];
  };
  pricing: {
    title: string;
    subtitle: string;
    plans: { name: string; price: string; summary: string; bullets: string[] }[];
  };
  contact: {
    title: string;
    subtitle: string;
    submit: string;
    name: string;
    email: string;
    message: string;
    company: string;
  };
  footer: {
    tagline: string;
    rights: string;
  };
};

const copy: Record<Locale, Copy> = {
  en: {
    nav: {
      features: "Features",
      pricing: "Pricing",
      docs: "Docs",
      blog: "Blog",
      contact: "Contact",
    legal: "Legal",
      cta: "Start Free",
    },
    hero: {
      eyebrow: "Multi-language transcription that feels instant",
      title: "Turn messy audio into clean, searchable transcripts.",
      subtitle:
        "PolyScript gives teams a reliable STT pipeline with live progress, exports, and real-time collaboration.",
      primary: "Create a job",
      secondary: "See the platform",
    },
    trust: "Trusted by global teams shipping audio at scale.",
    features: {
      title: "Built for product teams, ops, and researchers",
      items: [
        {
          title: "Live job telemetry",
          body: "Watch transcription progress in real time with SSE updates, stage tracking, and retries.",
        },
        {
          title: "Normalized outputs",
          body: "Every engine returns identical segments, timestamps, and metadata for seamless export.",
        },
        {
          title: "Team-ready workflows",
          body: "Invite roles, enforce plan limits, and keep every transcript scoped to its team.",
        },
      ],
    },
    workflow: {
      title: "From upload to export in minutes",
      steps: [
        { title: "Upload", body: "Drag audio or paste a URL. Plan limits are enforced upfront." },
        { title: "Process", body: "Background worker handles decoding, STT, and formatting." },
        { title: "Deliver", body: "Download TXT, JSON, SRT, or VTT with a single click." },
      ],
    },
    pricing: {
      title: "Pricing that scales with your team",
      subtitle: "Start free. Upgrade only when your workload grows.",
      plans: [
        {
          name: "Free",
          price: "$0",
          summary: "Ideal for early experiments.",
          bullets: ["5 uploads / month", "2 languages", "1 team member"],
        },
        {
          name: "Standard",
          price: "$10",
          summary: "For growing teams.",
          bullets: ["25 uploads / month", "5 languages", "Up to 5 members"],
        },
        {
          name: "Pro",
          price: "$30",
          summary: "Unlimited scale.",
          bullets: ["Unlimited uploads", "5 languages", "Unlimited members"],
        },
      ],
    },
    contact: {
      title: "Talk to the PolyScript team",
      subtitle: "Let us know what you’re building and we’ll help you launch.",
      submit: "Send message",
      name: "Name",
      email: "Email",
      message: "What do you want to transcribe?",
      company: "Company",
    },
    footer: {
      tagline: "PolyScript — a calm, reliable transcription engine for teams.",
      rights: "All rights reserved.",
    },
  },
  de: {
    nav: {
      features: "Funktionen",
      pricing: "Preise",
      docs: "Docs",
      blog: "Blog",
      contact: "Kontakt",
    legal: "Rechtliches",
      cta: "Kostenlos starten",
    },
    hero: {
      eyebrow: "Mehrsprachige Transkription in Echtzeit",
      title: "Verwandle Audio in klare, durchsuchbare Transkripte.",
      subtitle:
        "PolyScript liefert Teams eine verlässliche STT‑Pipeline mit Live‑Status, Exporten und Kollaboration.",
      primary: "Job erstellen",
      secondary: "Plattform ansehen",
    },
    trust: "Vertraut von globalen Teams mit großen Audio‑Workloads.",
    features: {
      title: "Gemacht für Produkt‑ und Ops‑Teams",
      items: [
        {
          title: "Live‑Telemetrie",
          body: "Fortschritt in Echtzeit mit SSE‑Updates, Stages und Retries.",
        },
        {
          title: "Normalisierte Outputs",
          body: "Einheitliche Segmente, Timecodes und Metadaten für einfache Exporte.",
        },
        {
          title: "Team‑Workflows",
          body: "Rollen, Planlimits und Team‑Isolation sind eingebaut.",
        },
      ],
    },
    workflow: {
      title: "Von Upload bis Export in Minuten",
      steps: [
        { title: "Upload", body: "Audio hochladen oder URL einfügen. Limits prüfen wir vorher." },
        { title: "Verarbeiten", body: "Worker dekodiert, transkribiert und formatiert." },
        { title: "Liefern", body: "TXT, JSON, SRT oder VTT sofort exportieren." },
      ],
    },
    pricing: {
      title: "Preise, die mitwachsen",
      subtitle: "Starte gratis, upgrade wenn nötig.",
      plans: [
        {
          name: "Free",
          price: "€0",
          summary: "Für erste Tests.",
          bullets: ["5 Uploads / Monat", "2 Sprachen", "1 Mitglied"],
        },
        {
          name: "Standard",
          price: "€10",
          summary: "Für wachsende Teams.",
          bullets: ["25 Uploads / Monat", "5 Sprachen", "Bis 5 Mitglieder"],
        },
        {
          name: "Pro",
          price: "€30",
          summary: "Für große Workloads.",
          bullets: ["Unbegrenzt", "5 Sprachen", "Unbegrenzte Mitglieder"],
        },
      ],
    },
    contact: {
      title: "Sprich mit dem PolyScript‑Team",
      subtitle: "Erzähl uns von deinem Projekt — wir helfen beim Start.",
      submit: "Nachricht senden",
      name: "Name",
      email: "E‑Mail",
      message: "Was möchtest du transkribieren?",
      company: "Firma",
    },
    footer: {
      tagline: "PolyScript — ruhige, verlässliche Transkription für Teams.",
      rights: "Alle Rechte vorbehalten.",
    },
  },
  es: {
    nav: {
      features: "Funciones",
      pricing: "Precios",
      docs: "Docs",
      blog: "Blog",
      contact: "Contacto",
    legal: "Legal",
      cta: "Empezar gratis",
    },
    hero: {
      eyebrow: "Transcripción multilingüe en tiempo real",
      title: "Convierte audio en transcripciones limpias y buscables.",
      subtitle:
        "PolyScript ofrece una canalización STT confiable con progreso en vivo, exportaciones y colaboración.",
      primary: "Crear trabajo",
      secondary: "Ver plataforma",
    },
    trust: "Equipos globales confían en PolyScript.",
    features: {
      title: "Hecho para producto y operaciones",
      items: [
        {
          title: "Telemetría en vivo",
          body: "Progreso en tiempo real con SSE, etapas y reintentos.",
        },
        {
          title: "Salidas normalizadas",
          body: "Segmentos y metadatos consistentes para exportación inmediata.",
        },
        {
          title: "Flujos de equipo",
          body: "Roles, límites y aislamiento por equipo incluidos.",
        },
      ],
    },
    workflow: {
      title: "De la carga al exporte en minutos",
      steps: [
        { title: "Carga", body: "Sube audio o pega una URL. Validamos límites al inicio." },
        { title: "Procesa", body: "El worker decodifica, transcribe y formatea." },
        { title: "Entrega", body: "Descarga TXT, JSON, SRT o VTT al instante." },
      ],
    },
    pricing: {
      title: "Precios que escalan contigo",
      subtitle: "Empieza gratis y actualiza cuando crezcas.",
      plans: [
        {
          name: "Free",
          price: "$0",
          summary: "Para experimentar.",
          bullets: ["5 cargas / mes", "2 idiomas", "1 miembro"],
        },
        {
          name: "Standard",
          price: "$10",
          summary: "Para equipos en crecimiento.",
          bullets: ["25 cargas / mes", "5 idiomas", "Hasta 5 miembros"],
        },
        {
          name: "Pro",
          price: "$30",
          summary: "Escala ilimitada.",
          bullets: ["Cargas ilimitadas", "5 idiomas", "Miembros ilimitados"],
        },
      ],
    },
    contact: {
      title: "Hablemos",
      subtitle: "Cuéntanos qué estás construyendo.",
      submit: "Enviar mensaje",
      name: "Nombre",
      email: "Correo",
      message: "¿Qué quieres transcribir?",
      company: "Empresa",
    },
    footer: {
      tagline: "PolyScript — transcripción confiable para equipos.",
      rights: "Todos los derechos reservados.",
    },
  },
  fr: {
    nav: {
      features: "Fonctionnalités",
      pricing: "Tarifs",
      docs: "Docs",
      blog: "Blog",
      contact: "Contact",
    legal: "Legal",
      cta: "Commencer gratuitement",
    },
    hero: {
      eyebrow: "Transcription multilingue en temps réel",
      title: "Transformez l’audio en transcriptions propres et consultables.",
      subtitle:
        "PolyScript offre un pipeline STT fiable avec progression en direct, exports et collaboration.",
      primary: "Créer un job",
      secondary: "Voir la plateforme",
    },
    trust: "Adopté par des équipes internationales.",
    features: {
      title: "Conçu pour produit et opérations",
      items: [
        {
          title: "Télémétrie en direct",
          body: "Suivi en temps réel avec SSE, étapes et relances.",
        },
        {
          title: "Sorties normalisées",
          body: "Segments et métadonnées homogènes pour l’export.",
        },
        {
          title: "Workflows d’équipe",
          body: "Rôles, limites et isolation par équipe intégrés.",
        },
      ],
    },
    workflow: {
      title: "De l’upload à l’export en minutes",
      steps: [
        { title: "Uploader", body: "Chargez un audio ou collez une URL." },
        { title: "Traiter", body: "Le worker décode, transcrit et formate." },
        { title: "Livrer", body: "Export TXT, JSON, SRT ou VTT en un clic." },
      ],
    },
    pricing: {
      title: "Des tarifs qui suivent votre rythme",
      subtitle: "Commencez gratuitement, évoluez ensuite.",
      plans: [
        {
          name: "Free",
          price: "0€",
          summary: "Pour tester.",
          bullets: ["5 uploads / mois", "2 langues", "1 membre"],
        },
        {
          name: "Standard",
          price: "10€",
          summary: "Pour les équipes en croissance.",
          bullets: ["25 uploads / mois", "5 langues", "Jusqu’à 5 membres"],
        },
        {
          name: "Pro",
          price: "30€",
          summary: "Échelle illimitée.",
          bullets: ["Uploads illimités", "5 langues", "Membres illimités"],
        },
      ],
    },
    contact: {
      title: "Parlons de votre projet",
      subtitle: "Nous vous aidons à lancer rapidement.",
      submit: "Envoyer",
      name: "Nom",
      email: "Email",
      message: "Que voulez‑vous transcrire ?",
      company: "Entreprise",
    },
    footer: {
      tagline: "PolyScript — transcription fiable pour équipes modernes.",
      rights: "Tous droits réservés.",
    },
  },
  jp: {
    nav: {
      features: "機能",
      pricing: "料金",
      docs: "ドキュメント",
      blog: "ブログ",
      contact: "お問い合わせ",
    legal: "法的情報",
      cta: "無料で開始",
    },
    hero: {
      eyebrow: "リアルタイム多言語トランスクリプション",
      title: "音声をクリーンで検索可能な文字起こしへ。",
      subtitle:
        "PolyScript はライブ進捗、エクスポート、コラボを備えた信頼性の高い STT パイプラインです。",
      primary: "ジョブ作成",
      secondary: "プラットフォームを見る",
    },
    trust: "世界中のチームに採用されています。",
    features: {
      title: "プロダクト/運用チーム向け",
      items: [
        {
          title: "ライブテレメトリ",
          body: "SSE で進捗をリアルタイムに可視化。",
        },
        {
          title: "正規化された出力",
          body: "統一されたセグメントとタイムコード。",
        },
        {
          title: "チーム運用",
          body: "ロール管理とプラン制御を標準搭載。",
        },
      ],
    },
    workflow: {
      title: "アップロードからエクスポートまで数分",
      steps: [
        { title: "アップロード", body: "音声を選択、または URL を貼付。" },
        { title: "処理", body: "バックグラウンドで変換と整形。" },
        { title: "配信", body: "TXT/JSON/SRT/VTT で即エクスポート。" },
      ],
    },
    pricing: {
      title: "チーム成長に合わせた料金",
      subtitle: "まずは無料。必要に応じてアップグレード。",
      plans: [
        {
          name: "Free",
          price: "¥0",
          summary: "お試し向け。",
          bullets: ["月5件", "2言語", "1メンバー"],
        },
        {
          name: "Standard",
          price: "¥10",
          summary: "成長チーム向け。",
          bullets: ["月25件", "5言語", "最大5メンバー"],
        },
        {
          name: "Pro",
          price: "¥30",
          summary: "無制限スケール。",
          bullets: ["無制限", "5言語", "無制限メンバー"],
        },
      ],
    },
    contact: {
      title: "PolyScript に相談する",
      subtitle: "プロジェクト内容を教えてください。",
      submit: "送信",
      name: "お名前",
      email: "メール",
      message: "どの音声を文字起こししますか？",
      company: "会社名",
    },
    footer: {
      tagline: "PolyScript — チーム向けの信頼できる文字起こし。",
      rights: "All rights reserved.",
    },
  },
};

export function getStaticPaths() {
  return locales.map((lang) => ({ params: { lang } }));
}

export function getCopy(lang: string): Copy {
  const key = locales.includes(lang as Locale) ? (lang as Locale) : "en";
  return copy[key];
}
