/** Uma expressão com um trecho destacado (a subexpressão em análise, o ponto onde a lei agiu...). */
export function TextoComTrecho({ texto, trecho, classe = 'trecho' }: { texto: string; trecho?: [number, number] | null; classe?: string }) {
  if (!trecho) return <>{texto}</>;
  const [inicio, fim] = trecho;
  return (
    <>
      {texto.slice(0, inicio)}
      <mark className={classe}>{texto.slice(inicio, fim)}</mark>
      {texto.slice(fim)}
    </>
  );
}
