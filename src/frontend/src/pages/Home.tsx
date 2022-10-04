import * as React from "react";

import {
  Box,
  Container,
  Flex,
  Grid,
  GridItem,
  Heading,
  Image,
} from "@chakra-ui/react";

//Styling
import "../styles/pages/Home.css";
import { FaArrowRight } from "react-icons/fa";
import { useNavigate } from "react-router-dom";

// Page Structure
const Home = () => {
  const navigation = useNavigate();

  const nextClickHandler = () => {
    navigation("/selectMethod");
  };

  return (
    <Grid
      templateRows="1fr 4fr"
      height={"100vh"}
      p={5}
      width={"full"}
      position={"absolute"}
    >
      <GridItem
        colSpan={12}
        fontSize="7xl"
        fontWeight={"semibold"}
        float="left"
        paddingLeft={10}
        bg={"#fefefe"}
      >
        <h1>O Oráculo</h1>
      </GridItem>
      <GridItem colSpan={7}>
        <Flex h={"full"} justify={"start"} align={"flex-end"}>
          <Image
            src="assets/img/0.png"
            h={[0, 0, 400, 500, "3xl"]}
            objectFit={"contain"}
            className={"bottom-img"}
          />
        </Flex>
      </GridItem>
      <GridItem rowSpan={2} colSpan={5} padding={10} display={"flex"}>
        <Flex p={3} h={"full"} w={"full"} justify={"end"} align={"center"}>
          <Flex
            w={60}
            justify={"space-around"}
            align={"center"}
            className={"next-button"}
            onClick={nextClickHandler}
          >
            <Heading padding={0} margin={0} fontSize={"6xl"}>
              Iniciar
            </Heading>
            <FaArrowRight fontSize={40} />
          </Flex>
        </Flex>
      </GridItem>
    </Grid>
  );
};

export default Home;
