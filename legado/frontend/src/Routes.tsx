import { useTransition } from "react-spring";
import { Routes, Route, Navigate, useLocation } from "react-router-dom";
import Home from "./pages/Home";
import Results from "./pages/Results";
import SelectMethod from "./pages/SelectMethod";
import SelectPeriod from "./pages/SelectPeriod";
import "./styles/root.css";

import { animated } from "react-spring";
import SelectMethodManual from "./pages/SelectMethodManual";
import Error from "./pages/Error";

// Pages

// Routes

function MainRoute() {
  const location = useLocation();
  const transitions = useTransition(location, {
    from: {
      position: "absolute",
      transform: "translate3d(-1000px,0,0)",
      opacity: 0,
    },
    enter: {
      position: "relative",
      opacity: 1,

      transform: "translate3d(0px,0px,0)",
    },
    leave: {
      position: "absolute",
      opacity: 0,
      overflow: "hidden",
      transform: "translate3d(1000px,0,0)",
    },
  });
  return (
    <>
      {transitions((styles: any, item, key: any) => (
        <animated.div style={styles} key={key}>
          <Routes location={item}>
            <Route path="/" element={<Navigate to={"/home"} />}></Route>
            <Route path="/home" element={<Home />}></Route>
            <Route path="/SelectMethod" element={<SelectMethod />}></Route>
            <Route
              path="/SelectMethodManual"
              element={<SelectMethodManual />}
            ></Route>
            <Route path="/SelectPeriod" element={<SelectPeriod />}></Route>
            <Route path="/Results" element={<Results />}></Route>
            <Route path="/Error" element={<Error />}></Route>
          </Routes>
        </animated.div>
      ))}
    </>
  );
}

export default MainRoute;
