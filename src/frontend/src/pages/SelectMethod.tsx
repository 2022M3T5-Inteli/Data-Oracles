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
  SimpleGrid,
  Text,
} from "@chakra-ui/react";

//Styling
import "../styles/pages/SelectMethod.css";
import { FaArrowLeft, FaArrowRight, FaMagic } from "react-icons/fa";
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
          <Flex gap={5}>
            <Heading size={"xl"}>Selecione Uma Opção</Heading>
            <FaMagic fontSize={40} />
          </Flex>
        </Flex>
      </GridItem>
      <GridItem colSpan={5} h="full" className="right-section">
        <Flex
          p={3}
          h={"full"}
          w={"full"}
          justify={"space-between"}
          direction={"column"}
          align={"end"}
        >
          <HStack w={"full"} h="full" justify={"center"}>
            <Flex
              h={60}
              w={60}
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
                Modo Manual
              </Text>
            </Flex>
          </HStack>
        </Flex>
      </GridItem>
    </SimpleGrid>
  );
};

export default SelectMethod;
