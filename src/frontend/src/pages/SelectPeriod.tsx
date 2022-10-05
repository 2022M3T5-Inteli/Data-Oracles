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

//Styling
import "../styles/pages/SelectPeriod.css";
import {
  FaArrowLeft,
  FaArrowRight,
  FaCalendar,
  FaCalendarAlt,
} from "react-icons/fa";
import {
  useNavigate,
  useSearchParams,
  createSearchParams,
} from "react-router-dom";

// Page Structure
const SelectPeriod = () => {
  const navigation = useNavigate();
  const [searchParams] = useSearchParams();
  const [date, setDate] = useState("");
  const [time, setTime] = useState("");
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
        moment: `${date}T${time}`,
        isHoliday: isHoliday.toString(),
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
          <Flex gap={5}>
            <Heading size={"xl"}>Selecione o Período</Heading>
            <FaCalendarAlt fontSize={40} />
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
              <FormLabel>Data:</FormLabel>
              <Input
                type={"date"}
                onChange={(e) => {
                  setDate(e.target.value);
                }}
              />
              <FormLabel>Faixa Horária:</FormLabel>
              <Select
                onChange={(e) => {
                  setTime(e.target.value);
                }}
                placeholder="Faixa"
              >
                <option value="00:00">00:00 - 01:00</option>
                <option value="01:00">01:00 - 02:00</option>
                <option value="02:00">02:00 - 03:00</option>
                <option value="03:00">03:00 - 04:00</option>
                <option value="04:00">04:00 - 05:00</option>
                <option value="05:00">05:00 - 06:00</option>
                <option value="06:00">06:00 - 07:00</option>
                <option value="07:00">07:00 - 08:00</option>
                <option value="08:00">08:00 - 09:00</option>
                <option value="09:00">09:00 - 10:00</option>
                <option value="10:00">10:00 - 11:00</option>
                <option value="11:00">11:00 - 12:00</option>
                <option value="12:00">12:00 - 13:00</option>
                <option value="13:00">13:00 - 14:00</option>
                <option value="14:00">14:00 - 15:00</option>
                <option value="15:00">15:00 - 16:00</option>
                <option value="16:00">16:00 - 17:00</option>
                <option value="17:00">17:00 - 18:00</option>
                <option value="18:00">18:00 - 19:00</option>
                <option value="19:00">19:00 - 20:00</option>
                <option value="20:00">20:00 - 21:00</option>
                <option value="21:00">21:00 - 22:00</option>
                <option value="22:00">22:00 - 23:00</option>
                <option value="23:00">23:00 - 00:00</option>
              </Select>
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

export default SelectPeriod;
