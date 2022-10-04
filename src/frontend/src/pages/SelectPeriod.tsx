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

//Styling
import "../styles/pages/SelectPeriod.css";
import { FaArrowLeft, FaArrowRight } from "react-icons/fa";
import {
  useNavigate,
  useSearchParams,
  createSearchParams,
} from "react-router-dom";

// Page Structure
const SelectPeriod = () => {
  const navigation = useNavigate();
  const [searchParams] = useSearchParams();
  const [moment, setMoment] = useState("");
  const [isHoliday, setIsHoliday] = useState(false);

  const category = searchParams.get("category") || "";

  const goBackHandler = () => {
    navigation(-1);
  };
  const goNextHandler = () => {
    navigation({
      pathname: "/results",
      search: createSearchParams({
        category: category,
        moment: moment,
        isHoliday: isHoliday.toString(),
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
            src="assets/img/1.png"
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
              <FormLabel>Momento:</FormLabel>
              <Input
                type={"datetime-local"}
                step={900}
                onChange={(e) => {
                  setMoment(e.target.value);
                }}
              />
              <Checkbox
                onChange={(e) => {
                  setIsHoliday(e.target.checked);
                }}
              >
                Feriado
              </Checkbox>
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

export default SelectPeriod;
