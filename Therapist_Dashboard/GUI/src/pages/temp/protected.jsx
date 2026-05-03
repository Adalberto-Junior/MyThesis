import { useEffect, useState } from "react";
import api from "../../api";

export default function Protected() {
  const [message, setMessage] = useState("");

  useEffect(() => {
    api.get("/protected")
      .then(res => setMessage(res.data.message))
      .catch(() => setMessage("Acesso negado"));
  }, []);

  return <div><h2>{message}</h2></div>;
}