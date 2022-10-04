import { useContext, useEffect } from "react";

import { Flex, Grid, GridItem, Heading, Image } from "@chakra-ui/react";

//Styling
import "../styles/pages/Results.css";
import ResultTable from "../components/ResultTable";
import { useNavigate, useSearchParams } from "react-router-dom";
import { ApplicationContext } from "../context/ModelContext";

// Page Structure

const Results = () => {
  const { makePrediction, predictionList } = useContext(ApplicationContext);
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

  const closeHandler = () => {
    navigation("/home");
  };

  return (
    <Grid
      templateRows="0fr 4fr"
      height={"100vh"}
      width={"full"}
      position={"absolute"}
    >
      <GridItem
        colSpan={12}
        fontSize="7xl"
        fontWeight={"semibold"}
        float="left"
        padding={5}
        paddingLeft={10}
        bg={"#fefefe"}
      >
        <Flex p={3} h={"full"} w={"full"} justify={"start"} align={"center"}>
          <Flex w={"full"} justify={"space-between"} align={"center"}>
            <Heading padding={0} margin={0} fontSize={"5xl"}>
              Resultados
            </Heading>
            <Heading
              fontSize={"4xl"}
              className={"next-button"}
              onClick={closeHandler}
            >
              X
            </Heading>
          </Flex>
        </Flex>
      </GridItem>
      <GridItem colSpan={8}>
        <Flex h={"full"} justify={"start"} align={"flex-end"}>
          <Image
            src="assets/img/3.png"
            h={[0, 0, 400, 500, "3xl"]}
            objectFit={"contain"}
            className={"bottom-img"}
          />
        </Flex>
      </GridItem>
      <GridItem rowSpan={2} colSpan={4} padding={10} display={"flex"}>
        <Flex p={3} h={"full"} w={"full"} justify={"center"} align={"center"}>
          <ResultTable items={predictionList} />
        </Flex>
      </GridItem>
    </Grid>
  );
};

export default Results;
