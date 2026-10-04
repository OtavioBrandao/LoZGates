/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** Onde estão os arquivos do Pyodide (padrão: CDN jsDelivr). Ex.: "./pyodide/" quando hospedado junto. */
  readonly VITE_PYODIDE_URL?: string;
  /** Chave da API Groq usada pelo assistente de IA (opcional; fica visível no navegador). */
  readonly VITE_GROQ_API_KEY?: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}
