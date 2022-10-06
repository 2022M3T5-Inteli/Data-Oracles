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
      textAlign={"end"}
      align={["center", "center", "center", "end", "center", "center"]}
      direction={"column"}
      position="absolute"
    >
      <Heading
        p={6}
        size={"2xl"}
        color={"white"}
        zIndex={1}
        width={[0, 0, 0, 550, 0, 680]}
      >
        Seja Bem-Vindo ao Oráculo
      </Heading>
      <Box
        m={4}
        w={200}
        className={"go-next-button"}
        onClick={nextClickHandler}
        zIndex={1}
      >
        Iniciar
      </Box>
      <Img
        src="/assets/img/robothead.png"
        position={"absolute"}
        left={-100}
        bottom={-10}
        height={[800, 800, 800, 800, 900]}
      />
    </Flex>
  );
};

export default Home;
