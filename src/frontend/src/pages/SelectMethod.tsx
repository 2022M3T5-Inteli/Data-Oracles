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
} from "@chakra-ui/react";

//Styling
import "../styles/pages/SelectMethod.css";
import { FaArrowLeft, FaArrowRight } from "react-icons/fa";
import { useNavigate } from "react-router-dom";

import { FontAwesomeIcon } from "@fortawesome/react-fontawesome";
import { faFileCsv, faKeyboard } from "@fortawesome/free-solid-svg-icons";

// Page Structure
const SelectMethod = () => {
  const navigation = useNavigate();

  const goBackHandler = () => {
    navigation(-1);
  };
  const goNextHandler = () => {
    navigation("/selectPeriod");
  };

  const goManualHandler = () => {
    navigation("/selectMethodManual");
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
            <Flex
              h={40}
              w={40}
              justifyContent={"center"}
              direction={"column"}
              align={"center"}
              className={"option-block"}
            >
              <FontAwesomeIcon
                icon={faFileCsv}
                className={"option-block-icon"}
              />
              <Text
                fontSize={"2xl"}
                textAlign={"center"}
                className="option-block-text"
              >
                Abrir CSV
              </Text>
            </Flex>
            <Flex
              h={40}
              w={40}
              justifyContent={"center"}
              direction={"column"}
              align={"center"}
              className={"option-block"}
              onClick={goManualHandler}
            >
              <FontAwesomeIcon
                icon={faKeyboard}
                className={"option-block-icon"}
              />
              <Text
                fontSize={"2xl"}
                textAlign={"center"}
                className="option-block-text"
              >
                Inserir Programa
              </Text>
            </Flex>
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

export default SelectMethod;
