import React, { createContext, useEffect, useMemo, useState } from "react";

import {
  getPredictionRat,
  IPredictionItem,
  IPredictionInputItem,
} from "../data/oracle";

export interface IChildren {
  children?: React.ReactNode;
}

export interface IProviderValue {
  loading: boolean;
  predictionList: IPredictionItem[];
  makePrediction: ({}: IPredictionInputItem) => void;
}

export const ApplicationContext = createContext({} as IProviderValue);

export function ApplicationProvider({ children }: IChildren) {
  const [loading, setLoading] = useState(false);
  const [predictionList, setPredictionList] = useState([] as IPredictionItem[]);

  async function makePrediction({
    data_hora,
    feriado,
    categoria,
  }: IPredictionInputItem) {
    const data_rat = await getPredictionRat({ data_hora, feriado, categoria });

    const allPredictions = [];
    allPredictions.push(...data_rat.predictions);

    setPredictionList(allPredictions);
  }

  const memoedValue = useMemo(
    () => ({
      loading,
      predictionList,
      makePrediction,
    }),
    [predictionList]
  );

  return (
    <ApplicationContext.Provider value={memoedValue}>
      {children}
    </ApplicationContext.Provider>
  );
}
