import { useContext, useEffect } from "react";

import {
  Box,
  Flex,
  Grid,
  GridItem,
  Heading,
  Image,
  SimpleGrid,
} from "@chakra-ui/react";

//Styling
import "../styles/pages/Results.css";
import ResultTable from "../components/ResultTable";
import { useNavigate, useSearchParams } from "react-router-dom";
import { ApplicationContext } from "../context/ModelContext";

// Page Structure

const Results = () => {
  const { makePrediction, predictionList, hasError, cleanErrors } =
    useContext(ApplicationContext);
  const navigation = useNavigate();

  const [searchParams] = useSearchParams();

  const category = searchParams.get("category") || "";
  const datetime = searchParams.get("moment") || "";
  const isHoliday = Boolean(searchParams.get("isHoliday")) || false;

  useEffect(() => {
    makePrediction({
      data_hora: datetime,
      categoria: category,
      feriado: isHoliday,
    });
  }, []);

  useEffect(() => {
    if (hasError) {
      navigation("/Error");
    }
  }, [hasError]);

  const closeHandler = () => {
    navigation("/home");
  };

  return (
    <SimpleGrid
      height={"100vh"}
      width={"full"}
      position={"absolute"}
      columns={12}
      className={"result-container"}
    >
      <GridItem colSpan={7} h="full">
        <Flex
          grow={1}
          h={"full"}
          justify={"center"}
          align={"center"}
          direction={"column"}
        >
          <Heading size={"xl"} color={"white"}>
            Resultados
          </Heading>
        </Flex>
      </GridItem>
      <GridItem colSpan={5} h="full">
        <Flex
          h={"full"}
          w={"full"}
          justify={"start"}
          direction={"column"}
          align={"center"}
        >
          <Flex w={"full"} justify={"end"} align={"center"} p={10}>
            <Heading
              fontSize={"4xl"}
              className={"next-button"}
              onClick={closeHandler}
            >
              X
            </Heading>
          </Flex>
          <Flex
            height={"full"}
            width={"full"}
            justify={"center"}
            align={"center"}
          >
            <Box>
              <ResultTable items={predictionList} />
            </Box>
          </Flex>
        </Flex>
      </GridItem>
    </SimpleGrid>
  );
};

export default Results;
