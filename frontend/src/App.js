import React from "react";
import { Provider } from "react-redux";
import store from "./store";
import LogInteractionScreen from "./pages/LogInteractionScreen";
import "./styles/global.css";

function App() {
  return (
    <Provider store={store}>
      <div className="app">
        <LogInteractionScreen />
      </div>
    </Provider>
  );
}

export default App;
