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
  SimpleGrid,
} from "@chakra-ui/react";

import { useState } from "react";

import "../styles/pages/SelectMethodManual.css";
import { FaArrowLeft, FaArrowRight, FaList } from "react-icons/fa";
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
    <SimpleGrid
      height={"100vh"}
      width={"full"}
      position={"absolute"}
      columns={12}
    >
      <GridItem colSpan={7} h="full" className="left-section">
        <Flex
          grow={1}
          h={"full"}
          justify={"space-between"}
          p={20}
          align={"center"}
        >
          <Box className="icon-button icon-button-left" onClick={goBackHandler}>
            <FaArrowLeft fontSize={40} className={"next-icon"} />
          </Box>
          <Flex gap={5} align={"center"}>
            <Heading size={"xl"}>Selecione a Categoria</Heading>
            <FaList fontSize={40} />
          </Flex>
        </Flex>
      </GridItem>
      <GridItem colSpan={5} h="full" className="right-section">
        <Flex
          p={10}
          h={"full"}
          w={"full"}
          justify={"center"}
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
            justify={"end"}
            align={"center"}
            className={"next-button"}
            onClick={goNextHandler}
          >
            <Box className="icon-button icon-button-right">
              <FaArrowRight fontSize={40} className={"next-icon"} />
            </Box>
          </Flex>
        </Flex>
      </GridItem>
    </SimpleGrid>
  );
};

export default SelectMethodManual;
