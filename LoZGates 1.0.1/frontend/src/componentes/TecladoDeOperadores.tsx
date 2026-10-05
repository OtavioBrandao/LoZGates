/** Os mesmos operadores do manual (&, |, !, >, <> e parênteses). */
const TECLAS = [
  { texto: '&', nome: 'E (AND)', curto: 'E' },
  { texto: '|', nome: 'OU (OR)', curto: 'OU' },
  { texto: '!', nome: 'NÃO (NOT)', curto: 'NÃO' },
  { texto: '>', nome: 'Implica', curto: 'Implica' },
  { texto: '<>', nome: 'Se e somente se', curto: 'Se e só se' },
  { texto: '(', nome: 'Abre grupo', curto: 'Abre' },
  { texto: ')', nome: 'Fecha grupo', curto: 'Fecha' },
];

/**
 * Legenda dos operadores que também digita: tocar num símbolo o insere no
 * cursor do campo ativo (no celular, &, | e > ficam escondidos no teclado).
 */
export function TecladoDeOperadores({ aoInserir }: { aoInserir: (texto: string) => void }) {
  return (
    <div className="teclado-operadores" role="group" aria-label="Operadores: toque para inserir na expressão">
      {TECLAS.map((tecla) => (
        <button
          key={tecla.texto}
          type="button"
          className="tecla-operador"
          // não tira o foco (nem a posição do cursor) do campo
          onMouseDown={(e) => e.preventDefault()}
          onClick={() => aoInserir(tecla.texto)}
          aria-label={`Inserir ${tecla.texto}: ${tecla.nome}`}
        >
          <kbd className="tecla-operador__simbolo">{tecla.texto}</kbd>
          <span className="tecla-operador__nome" aria-hidden="true">
            {tecla.nome}
          </span>
          <span className="tecla-operador__curto" aria-hidden="true">
            {tecla.curto}
          </span>
        </button>
      ))}
    </div>
  );
}
