import axios from "axios";

const BASE_URL = "http://10.254.18.71:5000";

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
    `${BASE_URL}/api/lgbm/rat`,
    {
      data_hora,
      feriado,
      categoria,
    },
    { headers: { "Content-Type": "application/json" } }
  );

  return data.data;
}
export async function getPredictionFid({
  data_hora,
  feriado,
  categoria,
}: IPredictionInputItem) {
  const data: IPredictionRequestt = await axios.post(
    `${BASE_URL}/api/lgbm/fid`,
    {
      data_hora,
      feriado,
      categoria,
    },
    { headers: { "Content-Type": "application/json" } }
  );

  return data.data;
}
export async function getPredictionShare({
  data_hora,
  feriado,
  categoria,
}: IPredictionInputItem) {
  const data: IPredictionRequestt = await axios.post(
    `${BASE_URL}/api/lgbm/share`,
    {
      data_hora,
      feriado,
      categoria,
    },
    { headers: { "Content-Type": "application/json" } }
  );

  return data.data;
}
