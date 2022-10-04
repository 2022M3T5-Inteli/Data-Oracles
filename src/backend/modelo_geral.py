class ModelTools:
    def __init__(self) -> None:
        pass

    def _parse_predict(self, pred_map, prediction_val):
        prediction_list = []
        for i in range(0, len(prediction_val[0])):
            pred_map[list(pred_map.keys())[i]] = prediction_val[0][i]

        for key in list(pred_map.keys()):
            prediction_list.append({"type": key, "prediction": pred_map[key]})
        return prediction_list

    def parse_predict_rat(self, rat_prediction):
        rat_map = {'Total Domicílios | Rat%': 0, 'AB | Rat%': 0,
                   'C1 | Rat%': 0, 'C2 | Rat%': 0, 'DE | Rat%': 0, 'Masculino | Rat%': 0,
                   'Feminino | Rat%': 0, '4-11 anos | Rat%': 0, '12-17 anos | Rat%': 0,
                   '18-24 anos | Rat%': 0, '25-34 anos | Rat%': 0, '35-49 anos | Rat%': 0,
                   '50-59 anos | Rat%': 0, '60+ anos | Rat%': 0}
        return self._parse_predict(rat_map, rat_prediction)

    def parse_predict_fid(self, fid_prediction):
        prediction_list = []

        fid_map = {'Total Indivíduos | Fid%': 0, 'AB | Fid%': 0, 'C1 | Fid%': 0, 'C2 | Fid%': 0,
                   'DE | Fid%': 0, 'Masculino | Fid%': 0, 'Feminino | Fid%': 0, '4-11 anos | Fid%': 0,
                   '12-17 anos | Fid%': 0, '18-24 anos | Fid%': 0, '25-34 anos | Fid%': 0,
                   '35-49 anos | Fid%': 0, '50-59 anos | Fid%': 0, '60+ anos | Fid%': 0}
        return self._parse_predict(fid_map, fid_prediction)

    def parse_predict_share(self, share_prediction):
        share_map = {'Total Domicílios | Shr%': 0, 'AB | Shr%': 0, 'C1 | Shr%': 0, 'C2 | Shr%': 0,
                     'DE | Shr%': 0, 'Masculino | Shr%': 0, 'Feminino | Shr%': 0, '4-11 anos | Shr%': 0,
                     '12-17 anos | Shr%': 0, '18-24 anos | Shr%': 0, '25-34 anos | Shr%': 0,
                     '35-49 anos | Shr%': 0, '50-59 anos | Shr%': 0, '60+ anos | Shr%': 0}
        return self._parse_predict(share_map, share_prediction)

    def transform_input(self, X, scaler):
        return scaler.transform(X)


class ModeloGeral:
    def __init__(self, modelo_base_rat, modelo_base_fid, modelo_base_share):
        self.modelo_rat = modelo_base_rat
        self.modelo_fid = modelo_base_fid
        self.modelo_share = modelo_base_share

    def predict_rat(self, X):
        return self.modelo_rat.predict(X)

    def predict_fid(self, X):
        return self.modelo_fid.predict(X)

    def predict_share(self, X):
        return self.modelo_share.predict(X)
