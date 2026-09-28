import '@fontsource/ibm-plex-sans/400.css';
import '@fontsource/ibm-plex-sans/500.css';
import '@fontsource/ibm-plex-sans/600.css';
import '@fontsource/ibm-plex-sans/700.css';
import '@fontsource/ibm-plex-mono/400.css';
import '@fontsource/ibm-plex-mono/600.css';
import { createRoot } from 'react-dom/client';
import { App } from './App';
import './estilos/global.css';

// Sem <StrictMode>: ele executa efeitos duas vezes em desenvolvimento, o que duplicaria
// chamadas ao Python com efeito colateral (ex.: registros do DetailedUserLogger).
createRoot(document.getElementById('root')!).render(<App />);
