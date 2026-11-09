import * as React from "react";
import {
  ChakraProvider,
  Box,
  Text,
  Link,
  VStack,
  Code,
  Grid,
  theme,
} from "@chakra-ui/react";
import { ColorModeSwitcher } from "./ColorModeSwitcher";
import { Logo } from "./Logo";

import { BrowserRouter } from "react-router-dom";
import MainRoute from "./Routes";
import { ApplicationProvider } from "./context/ModelContext";

export const App = () => (
  <ChakraProvider theme={theme}>
    <ApplicationProvider>
      <BrowserRouter>
        <MainRoute />
      </BrowserRouter>
    </ApplicationProvider>
  </ChakraProvider>
);
