"use client"
import React, { useEffect, useState } from 'react';
import { Badge } from './Badge';

export function HealthCheck() {
  const [status, setStatus] = useState<"loading" | "ok" | "error">("loading");

  useEffect(() => {
    fetch("http://localhost:8000/health")
      .then(res => res.json())
      .then(data => {
        if (data.status === "ok") {
          setStatus("ok");
        } else {
          setStatus("error");
        }
      })
      .catch(() => setStatus("error"));
  }, []);

  if (status === "loading") return <Badge variant="infoSoft">Connecting...</Badge>;
  if (status === "error") return <Badge variant="pro" className="bg-accent-red-soft text-accent-red">Backend Offline</Badge>;
  return <Badge variant="infoSoft" className="bg-accent-green-soft text-accent-green">Backend OK</Badge>;
}
