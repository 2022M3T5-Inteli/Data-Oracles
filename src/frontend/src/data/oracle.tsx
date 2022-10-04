import axios from "axios";

export interface IPredictionInputItem {
  data_hora: string;
  feriado: boolean;
  categoria: string;
}

export interface IPredictionItem {
  prediction: number;
  type: string;
}

export interface IPredictionRequestt {
  data: { predictions: IPredictionItem[] };
}

export async function getPredictionRat({
  data_hora,
  feriado,
  categoria,
}: IPredictionInputItem) {
  const data: IPredictionRequestt = await axios.post(
    `http://127.0.0.1:5000/api/knn/rat`,
    {
      data_hora,
      feriado,
      categoria,
    },
    { headers: { "Content-Type": "application/json" } }
  );

  return data.data;
}
