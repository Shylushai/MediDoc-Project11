import { ThemeProvider, createTheme } from "@mui/material/styles";
import "./App.css";
import SignIn from "./pages/SignIn";
import { Route, BrowserRouter as Router, Routes } from "react-router-dom";
import Dashboard from "./pages/Patient/Dashboard";
import ProtectedRoute from "./pages/ProtectedRoute";
import { useState } from "react";
import { CssBaseline } from "@mui/material";
import MedicalHistory from "./pages/Patient/MedicalHistory/main";
import PatientRoot from "./pages/Patient/PatientRoot";
import Account from "./pages/Patient/Account/main";

function App() {
  const defaultTheme = createTheme();
  const [user, setUser] = useState(null);
  const handleLogin = (user) => setUser(user);
  const handleLogout = () => setUser(null);

  return (
    <>
      <CssBaseline />
      <ThemeProvider theme={defaultTheme}>
        <Router>
          <Routes>
            <Route path="/" element={<SignIn callback={handleLogin} />} />
            <Route element={<ProtectedRoute user={user} />}>
              <Route
                path="patient"
                element={<PatientRoot user={user} onLogout={handleLogout} />}
              >
                <Route index element={<Dashboard user={user} />} />
                <Route path="dashboard" element={<Dashboard user={user} />} />
                <Route path="account" element={<Account user={user} />} />
                <Route
                  path="medHistory"
                  element={<MedicalHistory user={user} />}
                />
              </Route>
            </Route>
          </Routes>
        </Router>
      </ThemeProvider>
    </>
  );
}

export default App;
