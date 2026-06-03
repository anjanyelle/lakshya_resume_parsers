import { Router } from "express";
import { matchJobDescription } from "../controllers/jdMatch.controller";

const router = Router();

// POST /api/jd/match
router.post("/match", matchJobDescription);

export default router;
