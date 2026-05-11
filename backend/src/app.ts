import express, { Application, Request, Response, NextFunction } from "express";
import cors from "cors";
import authRoutes from "./routes/auth.routes";
import candidateRoutes from "./routes/candidate.routes";
import jobRoutes from "./routes/job.routes";
import uploadRoutes from "./routes/upload.routes";
import resumeRoutes from "./routes/resume.routes";
import matchingRoutes from "./routes/matching.routes";
import labelingRoutes from "./routes/labeling.routes";

const app: Application = express();

// CORS configuration
const getOrigins = () => {
  const staticOrigins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:4173",
    "https://lakshya-llm-resume-parser-ated.vercel.app",
    "https://frontend-one-nu-47.vercel.app",
  ];
  
  const envOrigins = process.env.CORS_ORIGINS ? process.env.CORS_ORIGINS.split(",") : [];
  const frontendUrl = process.env.FRONTEND_URL ? [process.env.FRONTEND_URL] : [];
  
  return [...new Set([...staticOrigins, ...envOrigins, ...frontendUrl])].filter(Boolean);
};

const allowedOrigins = getOrigins();

const corsOptions = {
  origin: (origin: string | undefined, callback: (err: Error | null, allow?: boolean) => void) => {
    // In development or if ALLOW_ALL_ORIGINS is set, allow everything
    if (!origin || process.env.NODE_ENV === "development" || process.env.ALLOW_ALL_ORIGINS === "true") {
      callback(null, true);
      return;
    }

    if (allowedOrigins.includes(origin) || origin.endsWith(".vercel.app")) {
      callback(null, true);
    } else {
      console.warn("🚫 CORS blocked for origin:", origin);
      callback(null, false);
    }
  },
  credentials: true,
  methods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
  allowedHeaders: ["Content-Type", "Authorization", "X-Requested-With"],
};

// Middleware
app.use(cors(corsOptions));
app.use(express.json({ limit: "10mb" }));
app.use(express.urlencoded({ extended: true, limit: "10mb" }));

// Health check endpoint
app.get("/health", (req: Request, res: Response) => {
  res.json({
    status: "healthy",
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    environment: process.env.NODE_ENV || "development",
  });
});

// Routes
app.use("/api/auth", authRoutes);
app.use("/api/candidates", candidateRoutes);
app.use("/api/jobs", jobRoutes);
app.use("/api/upload", uploadRoutes);
app.use("/api/resume", resumeRoutes);
app.use("/api/matching", matchingRoutes);
app.use("/api/labeling", labelingRoutes);

// 404 handler
app.use("*", (req: Request, res: Response) => {
  res.status(404).json({
    error: "Route not found",
    path: req.originalUrl,
    method: req.method,
  });
});

// Global error handler
app.use((err: Error, req: Request, res: Response, next: NextFunction) => {
  console.error("Unhandled error:", err);

  // JWT errors
  if (err.name === "JsonWebTokenError") {
    return res.status(401).json({
      error: "Invalid token",
    });
  }

  if (err.name === "TokenExpiredError") {
    return res.status(401).json({
      error: "Token expired",
    });
  }

  // Database errors
  if (err.message.includes("duplicate key")) {
    return res.status(409).json({
      error: "Resource already exists",
    });
  }

  // Default error
  return res.status(500).json({
    error: "Internal server error",
    message:
      process.env.NODE_ENV === "development"
        ? err.message
        : "Something went wrong",
  });
});

export default app;
