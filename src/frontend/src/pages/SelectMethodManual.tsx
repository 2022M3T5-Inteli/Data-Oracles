import * as React from "react";

import {
  Box,
  Container,
  Flex,
  Grid,
  GridItem,
  Heading,
  HStack,
  Image,
  Text,
  Input,
  FormControl,
  FormLabel,
  Select,
  Checkbox,
} from "@chakra-ui/react";

import { useState } from "react";

import "../styles/pages/SelectMethodManual.css";
import { FaArrowLeft, FaArrowRight } from "react-icons/fa";
import { useNavigate, createSearchParams } from "react-router-dom";

// Page Structure
const SelectMethodManual = () => {
  const navigation = useNavigate();

  const [category, setCategory] = useState("");

  const goBackHandler = () => {
    navigation(-1);
  };
  const goNextHandler = () => {
    navigation({
      pathname: "/selectPeriod",
      search: createSearchParams({
        category: category,
      }).toString(),
    });
  };

  return (
    <Grid templateRows="1fr 4fr" height={"100vh"} width={"full"} position={"absolute"}>
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
          <Flex
            w={60}
            justify={"space-around"}
            align={"center"}
            className={"next-button"}
            onClick={goBackHandler}
          >
            <FaArrowLeft fontSize={40} />
            <Heading padding={0} margin={0} fontSize={"5xl"}>
              Voltar
            </Heading>
          </Flex>
        </Flex>
      </GridItem>
      <GridItem colSpan={7}>
        <Flex h={"full"} justify={"start"} align={"flex-end"}>
          <Image
            src="assets/img/2.png"
            h={[0, 0, 400, 500, "3xl"]}
            objectFit={"contain"}
            className={"bottom-img"}
          />
        </Flex>
      </GridItem>
      <GridItem rowSpan={2} colSpan={5} padding={10} display={"flex"}>
        <Flex
          p={3}
          h={"full"}
          w={"full"}
          justify={"space-between"}
          direction={"column"}
          align={"end"}
        >
          <HStack w={"full"} h="full" justify={"end"}>
            <FormControl>
              <FormLabel>Categoria</FormLabel>

              <Select
                onChange={(e) => {
                  setCategory(e.target.value);
                }}
                placeholder="Selecionar Categoria"
              >
                <option value="CARROS E MOTORES">CARROS E MOTORES</option>
                <option value="CULINARIO">CULINARIO</option>
                <option value="DEBATE">DEBATE</option>
                <option value="DOCUMENTARIO">DOCUMENTARIO</option>
                <option value="EDUCATIVO">EDUCATIVO</option>
                <option value="ENTREVISTA">ENTREVISTA</option>
                <option value="ESPORTE">ESPORTE</option>
                <option value="FEMININO">FEMININO</option>
                <option value="FILME">FILME</option>
                <option value="FUTEBOL">FUTEBOL</option>
                <option value="GAME SHOW">GAME SHOW</option>
                <option value="HUMORISTICO">HUMORISTICO</option>
                <option value="JORNALISMO">JORNALISMO</option>
                <option value="MINISSERIE">MINISSERIE</option>
                <option value="MUSICAL">MUSICAL</option>
                <option value="NOVELA">NOVELA</option>
                <option value="OUTROS">OUTROS</option>
                <option value="POLITICO">POLITICO</option>
                <option value="PREMIACAO">PREMIACAO</option>
                <option value="REALITY SHOW">REALITY SHOW</option>
                <option value="RELIGIOSO">RELIGIOSO</option>
                <option value="REPORTAGEM">REPORTAGEM</option>
                <option value="RURAL">RURAL</option>
                <option value="SERIES">SERIES</option>
                <option value="SHOW">SHOW</option>
                <option value="SORTEIO">SORTEIO</option>
                <option value="TELE VENDAS">TELE VENDAS</option>
              </Select>
            </FormControl>
          </HStack>
          <Flex
            w={60}
            justify={"space-around"}
            align={"center"}
            className={"next-button"}
            onClick={goNextHandler}
          >
            <Heading padding={0} margin={0} fontSize={"5xl"}>
              Próximo
            </Heading>
            <FaArrowRight fontSize={40} />
          </Flex>
        </Flex>
      </GridItem>
    </Grid>
  );
};

export default SelectMethodManual;
