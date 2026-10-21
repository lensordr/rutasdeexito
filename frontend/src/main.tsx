import React from "react";
import ReactDOM from "react-dom/client";
import { createBrowserRouter, RouterProvider } from "react-router-dom";
import "./index.css";
import App from "./App";
import ProjectsPage from "./pages/ProjectsPage";
import ProjectDetailPage from "./pages/ProjectDetailPage";
import StyleProfilePage from "./pages/StyleProfilePage";
import ClipsPage from "./pages/ClipsPage";
import RenderPage from "./pages/RenderPage";
import ConnectorsPage from "./pages/ConnectorsPage";

const router = createBrowserRouter([
  {
    path: "/",
    element: <App />,
    children: [
      { index: true, element: <ProjectsPage /> },
      { path: "projects/:projectId", element: <ProjectDetailPage /> },
      { path: "projects/:projectId/style", element: <StyleProfilePage /> },
      { path: "projects/:projectId/clips", element: <ClipsPage /> },
      { path: "projects/:projectId/render", element: <RenderPage /> },
      { path: "connectors", element: <ConnectorsPage /> },
    ],
  },
]);

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>,
);
