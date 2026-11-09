import React, { createContext, useEffect, useMemo, useState } from "react";

import {
  getPredictionRat,
  IPredictionItem,
  IPredictionInputItem,
  getPredictionFid,
  getPredictionShare,
} from "../data/oracle";

export interface IChildren {
  children?: React.ReactNode;
}

export interface IProviderValue {
  loading: boolean;
  predictionList: IPredictionItem[];
  makePrediction: ({}: IPredictionInputItem) => void;
  cleanErrors: () => void;
  hasError: boolean;
  errorMessage: string;
}

export const ApplicationContext = createContext({} as IProviderValue);

export function ApplicationProvider({ children }: IChildren) {
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [hasError, setHasError] = useState(false);
  const [predictionList, setPredictionList] = useState([] as IPredictionItem[]);

  async function makePrediction({
    data_hora,
    feriado,
    categoria,
  }: IPredictionInputItem) {
    try {
      const data_rat = await getPredictionRat({
        data_hora,
        feriado,
        categoria,
      });
      // const data_fid = await getPredictionFid({
      //   data_hora,
      //   feriado,
      //   categoria,
      // });
      const data_share = await getPredictionShare({
        data_hora,
        feriado,
        categoria,
      });

      const allPredictions = [];
      allPredictions.push(
        ...data_rat.predictions,
        // ...data_fid.predictions,
        ...data_share.predictions
      );

      setPredictionList(allPredictions);
    } catch (error) {
      setPredictionList([]);
      setErrorMessage("Erro na Requisição");
      setHasError(true);
    }
  }

  function cleanErrors() {
    // setErrorMessage("");
    setHasError(false);
  }

  const memoedValue = useMemo(
    () => ({
      loading,
      predictionList,
      makePrediction,
      cleanErrors,
      hasError,
      errorMessage,
    }),
    [predictionList]
  );

  return (
    <ApplicationContext.Provider value={memoedValue}>
      {children}
    </ApplicationContext.Provider>
  );
}
