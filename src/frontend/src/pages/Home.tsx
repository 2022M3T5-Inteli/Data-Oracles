import * as React from "react";

import {
  Box,
  Center,
  Container,
  Flex,
  Grid,
  GridItem,
  Heading,
  Image,
  Text,
  SimpleGrid,
  Img,
  Button,
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
    <Flex
      className="container"
      grow={1}
      h={"100vh"}
      width="full"
      justify={"center"}
      align={"center"}
      direction={"column"}
      position="absolute"
    >
      <Heading p={6} size={"2xl"}>
        Seja Bem-Vindo ao Oráculo
      </Heading>
      <Box
        m={4}
        w={200}
        className={"go-next-button"}
        onClick={nextClickHandler}
      >
        Iniciar
      </Box>
    </Flex>
  );
};

export default Home;
