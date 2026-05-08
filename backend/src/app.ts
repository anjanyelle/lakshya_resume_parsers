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
const rawOrigins = process.env.CORS_ORIGINS || "";
const envOrigins = rawOrigins.split(',').map(o => o.trim()).filter(o => o);

const allowedOrigins = [
  "http://localhost:3000",
  "http://localhost:5173",
  "https://lakshya-llm-resume-parser-ated.vercel.app",
  ...envOrigins.map(o => o.startsWith('http') ? o : `https://${o}`),
  ...envOrigins.map(o => o.startsWith('http') ? `${o}/` : `https://${o}/`) // Allow with trailing slash
];

console.log("🔒 Allowed CORS Origins:", allowedOrigins);

const corsOptions = {
  origin: (origin: string | undefined, callback: (err: Error | null, allow?: boolean) => void) => {
    // Allow requests with no origin (like mobile apps or curl requests)
    if (!origin) return callback(null, true);
    
    if (allowedOrigins.indexOf(origin) !== -1 || allowedOrigins.includes("*")) {
      callback(null, true);
    } else {
      console.log("🚫 CORS blocked for origin:", origin);
      callback(new Error("Not allowed by CORS"));
    }
  },
  credentials: true,
  methods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
  allowedHeaders: ["Content-Type", "Authorization"],
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
