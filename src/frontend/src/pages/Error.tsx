import { useContext, useEffect } from "react";

import {
  Box,
  Flex,
  GridItem,
  Heading,
  Text,
  SimpleGrid,
} from "@chakra-ui/react";

//Styling
import "../styles/pages/Error.css";

import { ApplicationContext } from "../context/ModelContext";
import { useNavigate } from "react-router-dom";
import { FaArrowLeft, FaCloudShowersHeavy } from "react-icons/fa";

// Page Structure

const Error = () => {
  const { errorMessage, cleanErrors, hasError } =
    useContext(ApplicationContext);
  const navigation = useNavigate();

  const closeHandler = () => {
    cleanErrors();
    navigation("/home");
  };

  useEffect(() => {
    if (!hasError) {
      navigation("/home");
    }
  }, [hasError]);

  return (
    <SimpleGrid
      height={"100vh"}
      width={"full"}
      position={"absolute"}
      columns={12}
      className={"result-container"}
    >
      <GridItem colSpan={12} h="full">
        <Flex flexDir={"column"} height="full">
          <Flex
            w={60}
            p={20}
            justify={"start"}
            align={"center"}
            className={"next-button"}
            zIndex={1}
            onClick={closeHandler}
          >
            <Box className="icon-button icon-button-left">
              <FaArrowLeft fontSize={40} className={"next-icon"} />
            </Box>
          </Flex>
          <Flex
            grow={1}
            justify={"center"}
            position={"absolute"}
            height="full"
            width={"full"}
            align={"center"}
            direction={"column"}
            gap={10}
          >
            <FaCloudShowersHeavy
              fontSize={120}
              className={"next-icon"}
              color={"white"}
            />
            <Heading size={"xl"} color={"white"}>
              Erro ao gerar predição :(
            </Heading>
            <Text color={"white"}>"{errorMessage}"</Text>
          </Flex>
        </Flex>
      </GridItem>
    </SimpleGrid>
  );
};

export default Error;
