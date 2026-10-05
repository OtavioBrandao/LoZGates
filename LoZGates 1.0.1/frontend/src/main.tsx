import '@fontsource-variable/archivo/wdth.css';
import '@fontsource-variable/public-sans';
import '@fontsource-variable/jetbrains-mono';
import { createRoot } from 'react-dom/client';
import { App } from './App';
import './estilos/global.css';
import { aplicarTema, temaSalvo } from './tema';

// Antes de desenhar, para não piscar o tema errado
aplicarTema(temaSalvo());

// Sem <StrictMode>: ele executa efeitos duas vezes em desenvolvimento, o que
// duplicaria chamadas à API com efeito no registro de uso.
createRoot(document.getElementById('root')!).render(<App />);
