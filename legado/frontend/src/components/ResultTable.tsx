import * as React from "react";

import {
  Box,
  Container,
  Flex,
  Grid,
  GridItem,
  Heading,
  Image,
  Table,
  TableCaption,
  TableContainer,
  Tbody,
  Td,
  Tfoot,
  Th,
  Thead,
  Tr,
} from "@chakra-ui/react";

//Styling
import "../styles/components/ResultTable.css";
import { FaArrowLeft, FaArrowRight } from "react-icons/fa";
import { IPredictionItem } from "../data/oracle";

interface IProps {
  items: IPredictionItem[];
}
// Page Structure
const ResultTable: React.FC<IProps> = ({ items }) => {
  return (
    <Flex p={3} className={"table-result"}>
      <TableContainer height={600} overflowY={"scroll"}>
        <Table variant="simple">
          <TableCaption>Predição de Valores</TableCaption>
          <Thead>
            <Tr>
              <Th>Medição</Th>
              <Th isNumeric>Valor%</Th>
            </Tr>
          </Thead>
          <Tbody>
            {items.map((item) => {
              return (
                <Tr>
                  <Td>{item.type}</Td>
                  <Td>{item.prediction}</Td>
                </Tr>
              );
            })}
          </Tbody>
          <Tfoot>
            <Tr>
              <Th>Medição</Th>
              <Th isNumeric>Valor%</Th>
            </Tr>
          </Tfoot>
        </Table>
      </TableContainer>
    </Flex>
  );
};

export default ResultTable;
