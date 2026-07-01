import { Request, Response } from "express";
import { query } from "../database/db";
import { getClient } from "../database/db";
import { AuthenticatedRequest } from "../middleware/auth.middleware";

// Helper to generate minimal valid PDF
const generatePDFBuffer = (data: {
  range: number;
  total: number;
  success: number;
  failed: number;
  success_rate: number;
  avg_time: number;
  avg_confidence: number;
}) => {
  const streamContent = `BT
/F1 12 Tf
70 700 Td
(Analytics Report - Range: ${data.range} days) Tj
0 -20 Td
(Total Resumes Uploaded: ${data.total}) Tj
0 -15 Td
(Successfully Parsed: ${data.success}) Tj
0 -15 Td
(Failed Parsing: ${data.failed}) Tj
0 -15 Td
(Success Rate: ${data.success_rate.toFixed(2)}%) Tj
0 -15 Td
(Average Processing Time: ${data.avg_time.toFixed(2)}s) Tj
0 -15 Td
(Average Confidence Score: ${(data.avg_confidence * 100).toFixed(2)}%) Tj
ET`;

  const content = `%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> >> /MediaBox [0 0 612 792] /Contents 4 0 R >>
endobj
4 0 obj
<< /Length ${streamContent.length} >>
stream
${streamContent}
endstream
endobj
xref
0 5
0000000000 65535 f 
trailer
<< /Size 5 /Root 1 0 R >>
startxref
350
%%EOF`;

  return Buffer.from(content, "utf-8");
};

// GET /api/analytics/parsing-stats
export const getParsingStats = async (req: Request, res: Response): Promise<void> => {
  try {
    const statsResult = await query(`
      SELECT 
        COUNT(*)::int as total,
        COUNT(*) FILTER (WHERE status = 'completed')::int as success,
        COUNT(*) FILTER (WHERE status = 'failed')::int as failed,
        COALESCE(AVG(EXTRACT(EPOCH FROM (completed_at - started_at))), 0)::float as avg_time,
        COALESCE(AVG(confidence_score), 0)::float as avg_conf
      FROM parsing_jobs
    `);

    const { total, success, failed, avg_time, avg_conf } = statsResult.rows[0];
    const success_rate = total > 0 ? (success / total) * 100 : 0;

    res.json({
      total_resumes: total,
      successfully_parsed: success,
      failed_parsing: failed,
      success_rate,
      average_parsing_time: avg_time,
      average_confidence_score: avg_conf * 100, // percentage for UI
    });
  } catch (error) {
    console.error("Get parsing stats error:", error);
    res.status(500).json({ error: "Internal server error", message: "Failed to retrieve parsing stats" });
  }
};

// GET /api/analytics/skill-distribution
export const getSkillDistribution = async (req: Request, res: Response): Promise<void> => {
  try {
    const skillsResult = await query(`
      SELECT s.name, COUNT(cs.candidate_id)::int as count
      FROM skills s
      LEFT JOIN candidate_skills cs ON s.id = cs.skill_id
      GROUP BY s.name
      ORDER BY count DESC
      LIMIT 10
    `);

    res.json(skillsResult.rows);
  } catch (error) {
    console.error("Get skill distribution error:", error);
    // Graceful fallback for skills table if not fully populated or not found
    res.json([]);
  }
};

// GET /api/analytics/metrics
export const getMetrics = async (req: Request, res: Response): Promise<void> => {
  try {
    const totalResult = await query("SELECT COUNT(*)::int as count FROM candidates WHERE status != 'deleted'");
    const parsedResult = await query("SELECT COUNT(DISTINCT candidate_id)::int as count FROM parsing_jobs WHERE status = 'completed'");
    const validatedResult = await query("SELECT COUNT(DISTINCT candidate_id)::int as count FROM labeled_data WHERE action = 'approved'");
    const reviewedResult = await query("SELECT COUNT(DISTINCT candidate_id)::int as count FROM labeled_data");
    const matchedResult = await query("SELECT COUNT(DISTINCT candidate_id)::int as count FROM match_scores");
    
    // For shortlisted, query candidates with review_status = 'approved'
    const shortlistedResult = await query(`
      SELECT COUNT(*)::int as count 
      FROM candidates 
      WHERE review_status = 'approved'
    `);

    res.json({
      total_candidates: totalResult.rows[0].count,
      parsed_candidates: parsedResult.rows[0].count,
      validated_candidates: validatedResult.rows[0].count,
      reviewed_candidates: reviewedResult.rows[0].count,
      matched_candidates: matchedResult.rows[0].count,
      shortlisted_candidates: shortlistedResult.rows[0].count,
    });
  } catch (error) {
    console.error("Get metrics error:", error);
    res.status(500).json({ error: "Internal server error", message: "Failed to retrieve metrics" });
  }
};

// GET /api/analytics/upload-trends
export const getUploadTrends = async (req: Request, res: Response): Promise<void> => {
  try {
    const rangeDays = parseInt(req.query.range as string) || 30;

    const trendsResult = await query(`
      SELECT 
        TO_CHAR(started_at, 'YYYY-MM-DD') as date,
        COUNT(*)::int as count,
        COUNT(*) FILTER (WHERE status = 'completed')::int as success_count,
        COUNT(*) FILTER (WHERE status = 'failed')::int as failure_count
      FROM parsing_jobs
      WHERE started_at >= NOW() - CAST($1 || ' days' AS INTERVAL)
      GROUP BY TO_CHAR(started_at, 'YYYY-MM-DD')
      ORDER BY date ASC
    `, [rangeDays]);

    res.json(trendsResult.rows);
  } catch (error) {
    console.error("Get upload trends error:", error);
    res.status(500).json({ error: "Internal server error", message: "Failed to retrieve upload trends" });
  }
};

// GET /api/analytics/recruiter-activity
export const getRecruiterActivity = async (req: Request, res: Response): Promise<void> => {
  try {
    const reviewedResult = await query("SELECT COUNT(*)::int as count FROM labeled_data");
    const shortlistedResult = await query("SELECT COUNT(*)::int as count FROM candidates WHERE review_status = 'approved'");
    const rejectedResult = await query("SELECT COUNT(*)::int as count FROM candidates WHERE review_status = 'rejected'");
    const pendingResult = await query("SELECT COUNT(*)::int as count FROM candidates WHERE review_status = 'pending' AND status = 'success'");

    res.json({
      resumes_reviewed: reviewedResult.rows[0].count,
      candidates_shortlisted: shortlistedResult.rows[0].count,
      candidates_rejected: rejectedResult.rows[0].count,
      pending_reviews: pendingResult.rows[0].count,
    });
  } catch (error) {
    console.error("Get recruiter activity error:", error);
    res.status(500).json({ error: "Internal server error", message: "Failed to retrieve recruiter activity" });
  }
};

// GET /api/analytics/client-performance
export const getClientPerformance = async (req: Request, res: Response): Promise<void> => {
  try {
    const fromDate = req.query.from as string;
    const toDate = req.query.to as string;

    let dateFilter = "";
    const queryParams: any[] = [];
    let paramIndex = 1;

    if (fromDate && toDate) {
      dateFilter = "WHERE p.placed_at BETWEEN $1 AND $2";
      queryParams.push(fromDate, toDate);
      paramIndex = 3;
    } else if (fromDate) {
      dateFilter = "WHERE p.placed_at >= $1";
      queryParams.push(fromDate);
      paramIndex = 2;
    } else if (toDate) {
      dateFilter = "WHERE p.placed_at <= $1";
      queryParams.push(toDate);
      paramIndex = 2;
    }

    const clientPerformanceResult = await query(`
      SELECT 
        c.id as client_id,
        c.company_name,
        COUNT(p.id)::int as total_placements,
        COALESCE(SUM(p.billing_amount), 0) as total_revenue,
        COALESCE(AVG(p.billing_amount), 0) as avg_revenue_per_placement,
        COUNT(DISTINCT p.job_id)::int as unique_jobs_filled,
        COUNT(DISTINCT p.recruiter_id)::int as unique_recruiters_used,
        MIN(p.placed_at) as first_placement_date,
        MAX(p.placed_at) as last_placement_date
      FROM placements p
      JOIN clients c ON p.client_id = c.id
      ${dateFilter}
      GROUP BY c.id, c.company_name
      ORDER BY total_revenue DESC
    `, queryParams);

    res.json(clientPerformanceResult.rows);
  } catch (error) {
    console.error("Get client performance error:", error);
    res.status(500).json({ error: "Internal server error", message: "Failed to retrieve client performance" });
  }
};

// GET /api/analytics/placements
export const getPlacements = async (req: Request, res: Response): Promise<void> => {
  try {
    const fromDate = req.query.from as string;
    const toDate = req.query.to as string;

    let dateFilter = "";
    const queryParams: any[] = [];
    let paramIndex = 1;

    if (fromDate && toDate) {
      dateFilter = "WHERE p.placed_at BETWEEN $1 AND $2";
      queryParams.push(fromDate, toDate);
      paramIndex = 3;
    } else if (fromDate) {
      dateFilter = "WHERE p.placed_at >= $1";
      queryParams.push(fromDate);
      paramIndex = 2;
    } else if (toDate) {
      dateFilter = "WHERE p.placed_at <= $1";
      queryParams.push(toDate);
      paramIndex = 2;
    }

    const placementsResult = await query(`
      SELECT 
        TO_CHAR(p.placed_at, 'YYYY-MM-DD') as date,
        COUNT(*)::int as placements_count,
        COALESCE(SUM(p.billing_amount), 0) as daily_revenue,
        COUNT(DISTINCT p.client_id)::int as unique_clients,
        COUNT(DISTINCT p.recruiter_id)::int as unique_recruiters,
        COUNT(DISTINCT p.job_id)::int as unique_jobs
      FROM placements p
      ${dateFilter}
      GROUP BY TO_CHAR(p.placed_at, 'YYYY-MM-DD')
      ORDER BY date ASC
    `, queryParams);

    res.json(placementsResult.rows);
  } catch (error) {
    console.error("Get placements error:", error);
    res.status(500).json({ error: "Internal server error", message: "Failed to retrieve placements" });
  }
};

// GET /api/analytics/revenue
export const getRevenue = async (req: Request, res: Response): Promise<void> => {
  try {
    const fromDate = req.query.from as string;
    const toDate = req.query.to as string;

    let dateFilter = "";
    const queryParams: any[] = [];
    let paramIndex = 1;

    if (fromDate && toDate) {
      dateFilter = "WHERE p.placed_at BETWEEN $1 AND $2";
      queryParams.push(fromDate, toDate);
      paramIndex = 3;
    } else if (fromDate) {
      dateFilter = "WHERE p.placed_at >= $1";
      queryParams.push(fromDate);
      paramIndex = 2;
    } else if (toDate) {
      dateFilter = "WHERE p.placed_at <= $1";
      queryParams.push(toDate);
      paramIndex = 2;
    }

    const revenueResult = await query(`
      SELECT 
        TO_CHAR(p.placed_at, 'YYYY-MM') as month,
        COALESCE(SUM(p.billing_amount), 0) as monthly_revenue,
        COUNT(*)::int as placements_count,
        COALESCE(AVG(p.billing_amount), 0) as avg_revenue_per_placement,
        COUNT(DISTINCT p.client_id)::int as unique_clients,
        COUNT(DISTINCT p.recruiter_id)::int as unique_recruiters
      FROM placements p
      ${dateFilter}
      GROUP BY TO_CHAR(p.placed_at, 'YYYY-MM')
      ORDER BY month ASC
    `, queryParams);

    // Also get total revenue and other summary stats
    const summaryResult = await query(`
      SELECT 
        COALESCE(SUM(p.billing_amount), 0) as total_revenue,
        COUNT(*)::int as total_placements,
        COALESCE(AVG(p.billing_amount), 0) as avg_revenue_per_placement,
        COALESCE(MIN(p.billing_amount), 0) as min_revenue,
        COALESCE(MAX(p.billing_amount), 0) as max_revenue,
        COUNT(DISTINCT p.client_id)::int as total_unique_clients,
        COUNT(DISTINCT p.recruiter_id)::int as total_unique_recruiters
      FROM placements p
      ${dateFilter}
    `, queryParams);

    res.json({
      monthly_data: revenueResult.rows,
      summary: summaryResult.rows[0] || {
        total_revenue: 0,
        total_placements: 0,
        avg_revenue_per_placement: 0,
        min_revenue: 0,
        max_revenue: 0,
        total_unique_clients: 0,
        total_unique_recruiters: 0
      }
    });
  } catch (error) {
    console.error("Get revenue error:", error);
    res.status(500).json({ error: "Internal server error", message: "Failed to retrieve revenue data" });
  }
};

// GET /api/accuracy/overview and GET /api/analytics/accuracy/overview
export const getAccuracyOverview = async (req: Request, res: Response): Promise<void> => {
  try {
    const jobsResult = await query(`
      SELECT 
        COUNT(*)::int as total,
        COUNT(*) FILTER (WHERE status = 'completed')::int as success,
        COUNT(*) FILTER (WHERE status = 'failed')::int as failed,
        COALESCE(AVG(EXTRACT(EPOCH FROM (completed_at - started_at))), 0)::float as avg_time,
        COALESCE(AVG(confidence_score), 0)::float as avg_conf
      FROM parsing_jobs
    `);

    const { total, success, failed, avg_time, avg_conf } = jobsResult.rows[0];
    const success_rate = total > 0 ? (success / total) * 100 : 100;

    const labeledResult = await query(`
      SELECT 
        COUNT(*)::int as total_labeled,
        COUNT(*) FILTER (WHERE action = 'corrected')::int as corrected,
        COUNT(*) FILTER (WHERE action = 'approved')::int as approved
      FROM labeled_data
    `);

    const { total_labeled, corrected, approved } = labeledResult.rows[0];
    const correction_rate = total_labeled > 0 ? (corrected / total_labeled) * 100 : 0;
    const field_accuracy_percentage = total_labeled > 0 ? (approved / total_labeled) * 100 : 100;

    // Calculate section scores from corrections
    const sectionCorrections = await query(`
      SELECT 
        COUNT(*) FILTER (WHERE action = 'corrected' AND (corrected_fields->>'name' IS NOT NULL OR corrected_fields->>'email' IS NOT NULL OR corrected_fields->>'phone' IS NOT NULL))::int as contact,
        COUNT(*) FILTER (WHERE action = 'corrected' AND corrected_fields->>'skills' IS NOT NULL)::int as skills,
        COUNT(*) FILTER (WHERE action = 'corrected' AND (corrected_fields->>'companies' IS NOT NULL OR corrected_fields->>'job_titles' IS NOT NULL))::int as work,
        COUNT(*) FILTER (WHERE action = 'corrected' AND (corrected_fields->>'education_degrees' IS NOT NULL OR corrected_fields->>'universities' IS NOT NULL))::int as education
      FROM labeled_data
    `);

    const { contact, skills, work, education } = sectionCorrections.rows[0];

    const calculateScore = (correctedCount: number) => {
      return total_labeled > 0 ? (total_labeled - correctedCount) / total_labeled : 1.0;
    };

    const section_scores = [
      { label: "Contact Info", score: calculateScore(contact) },
      { label: "Skills", score: calculateScore(skills) },
      { label: "Work Experience", score: calculateScore(work) },
      { label: "Education", score: calculateScore(education) }
    ];

    // Get recent runs
    const recentRunsResult = await query(`
      SELECT 
        id::text as job_id, 
        status, 
        confidence_score::float as confidence, 
        COALESCE(error_message, filename, 'Parsing completed successfully') as notes 
      FROM parsing_jobs 
      ORDER BY started_at DESC 
      LIMIT 5
    `);

    // Get common error patterns (top fields corrected)
    const allCorrections = await query("SELECT corrected_fields FROM labeled_data WHERE action = 'corrected'");
    const fieldCounts: Record<string, number> = {};
    for (const row of allCorrections.rows) {
      const fields = row.corrected_fields;
      if (fields && typeof fields === "object") {
        for (const key of Object.keys(fields)) {
          fieldCounts[key] = (fieldCounts[key] || 0) + 1;
        }
      }
    }

    const common_error_patterns = Object.entries(fieldCounts)
      .sort((a, b) => b[1] - a[1])
      .map(([key]) => {
        const mapping: Record<string, string> = {
          name: "Contact Name",
          email: "Contact Email",
          phone: "Contact Phone",
          skills: "Skills List",
          companies: "Work Companies",
          job_titles: "Job Titles",
          education_degrees: "Degrees",
          universities: "Universities"
        };
        return mapping[key] || key;
      })
      .slice(0, 3);

    // Return combined object to satisfy both frontend callers
    res.json({
      total_jobs: total,
      success_jobs: success,
      failed_jobs: failed,
      success_rate,
      avg_processing_seconds: avg_time,
      avg_confidence: avg_conf,
      correction_rate,
      section_scores,
      recent_runs: recentRunsResult.rows,
      
      correction_count: corrected,
      field_accuracy_percentage,
      common_error_patterns: common_error_patterns.length > 0 ? common_error_patterns : ["None detected yet"]
    });
  } catch (error) {
    console.error("Get accuracy overview error:", error);
    res.status(500).json({ error: "Internal server error", message: "Failed to retrieve accuracy overview" });
  }
};

// GET /api/analytics/export/csv
export const exportCSV = async (req: Request, res: Response): Promise<void> => {
  try {
    const reportType = req.query.type as string || "parsing";
    const rangeDays = parseInt(req.query.range as string) || 30;
    const fromDate = req.query.from as string;
    const toDate = req.query.to as string;

    let csvContent = "";
    let filename = "";

    if (reportType === "client-performance") {
      let dateFilter = "";
      const queryParams: any[] = [];
      let paramIndex = 1;

      if (fromDate && toDate) {
        dateFilter = "WHERE p.placed_at BETWEEN $1 AND $2";
        queryParams.push(fromDate, toDate);
        paramIndex = 3;
      } else if (fromDate) {
        dateFilter = "WHERE p.placed_at >= $1";
        queryParams.push(fromDate);
        paramIndex = 2;
      } else if (toDate) {
        dateFilter = "WHERE p.placed_at <= $1";
        queryParams.push(toDate);
        paramIndex = 2;
      } else {
        dateFilter = "WHERE p.placed_at >= NOW() - CAST($1 || ' days' AS INTERVAL)";
        queryParams.push(rangeDays);
        paramIndex = 2;
      }

      const csvResult = await query(`
        SELECT 
          c.company_name,
          COUNT(p.id)::int as total_placements,
          COALESCE(SUM(p.billing_amount), 0) as total_revenue,
          COALESCE(AVG(p.billing_amount), 0) as avg_revenue_per_placement,
          COUNT(DISTINCT p.job_id)::int as unique_jobs_filled,
          COUNT(DISTINCT p.recruiter_id)::int as unique_recruiters_used,
          MIN(p.placed_at) as first_placement_date,
          MAX(p.placed_at) as last_placement_date
        FROM placements p
        JOIN clients c ON p.client_id = c.id
        ${dateFilter}
        GROUP BY c.id, c.company_name
        ORDER BY total_revenue DESC
      `, queryParams);

      csvContent = "Client Name,Total Placements,Total Revenue,Avg Revenue Per Placement,Unique Jobs Filled,Unique Recruiters Used,First Placement,Last Placement\n";
      for (const row of csvResult.rows) {
        const fields = [
          `"${(row.company_name || "").replace(/"/g, '""')}"`,
          row.total_placements,
          row.total_revenue,
          row.avg_revenue_per_placement,
          row.unique_jobs_filled,
          row.unique_recruiters_used,
          row.first_placement_date ? row.first_placement_date.toISOString() : "",
          row.last_placement_date ? row.last_placement_date.toISOString() : ""
        ];
        csvContent += fields.join(",") + "\n";
      }
      filename = `client_performance_${fromDate || fromDate || `range_${rangeDays}`}_${toDate || 'now'}.csv`;

    } else if (reportType === "placements") {
      let dateFilter = "";
      const queryParams: any[] = [];
      let paramIndex = 1;

      if (fromDate && toDate) {
        dateFilter = "WHERE p.placed_at BETWEEN $1 AND $2";
        queryParams.push(fromDate, toDate);
        paramIndex = 3;
      } else if (fromDate) {
        dateFilter = "WHERE p.placed_at >= $1";
        queryParams.push(fromDate);
        paramIndex = 2;
      } else if (toDate) {
        dateFilter = "WHERE p.placed_at <= $1";
        queryParams.push(toDate);
        paramIndex = 2;
      } else {
        dateFilter = "WHERE p.placed_at >= NOW() - CAST($1 || ' days' AS INTERVAL)";
        queryParams.push(rangeDays);
        paramIndex = 2;
      }

      const csvResult = await query(`
        SELECT 
          TO_CHAR(p.placed_at, 'YYYY-MM-DD') as date,
          COUNT(*)::int as placements_count,
          COALESCE(SUM(p.billing_amount), 0) as daily_revenue,
          COUNT(DISTINCT p.client_id)::int as unique_clients,
          COUNT(DISTINCT p.recruiter_id)::int as unique_recruiters,
          COUNT(DISTINCT p.job_id)::int as unique_jobs
        FROM placements p
        ${dateFilter}
        GROUP BY TO_CHAR(p.placed_at, 'YYYY-MM-DD')
        ORDER BY date ASC
      `, queryParams);

      csvContent = "Date,Placements Count,Daily Revenue,Unique Clients,Unique Recruiters,Unique Jobs\n";
      for (const row of csvResult.rows) {
        const fields = [
          row.date,
          row.placements_count,
          row.daily_revenue,
          row.unique_clients,
          row.unique_recruiters,
          row.unique_jobs
        ];
        csvContent += fields.join(",") + "\n";
      }
      filename = `placements_${fromDate || fromDate || `range_${rangeDays}`}_${toDate || 'now'}.csv`;

    } else if (reportType === "revenue") {
      let dateFilter = "";
      const queryParams: any[] = [];
      let paramIndex = 1;

      if (fromDate && toDate) {
        dateFilter = "WHERE p.placed_at BETWEEN $1 AND $2";
        queryParams.push(fromDate, toDate);
        paramIndex = 3;
      } else if (fromDate) {
        dateFilter = "WHERE p.placed_at >= $1";
        queryParams.push(fromDate);
        paramIndex = 2;
      } else if (toDate) {
        dateFilter = "WHERE p.placed_at <= $1";
        queryParams.push(toDate);
        paramIndex = 2;
      } else {
        dateFilter = "WHERE p.placed_at >= NOW() - CAST($1 || ' days' AS INTERVAL)";
        queryParams.push(rangeDays);
        paramIndex = 2;
      }

      const csvResult = await query(`
        SELECT 
          TO_CHAR(p.placed_at, 'YYYY-MM') as month,
          COALESCE(SUM(p.billing_amount), 0) as monthly_revenue,
          COUNT(*)::int as placements_count,
          COALESCE(AVG(p.billing_amount), 0) as avg_revenue_per_placement,
          COUNT(DISTINCT p.client_id)::int as unique_clients,
          COUNT(DISTINCT p.recruiter_id)::int as unique_recruiters
        FROM placements p
        ${dateFilter}
        GROUP BY TO_CHAR(p.placed_at, 'YYYY-MM')
        ORDER BY month ASC
      `, queryParams);

      csvContent = "Month,Monthly Revenue,Placements Count,Avg Revenue Per Placement,Unique Clients,Unique Recruiters\n";
      for (const row of csvResult.rows) {
        const fields = [
          row.month,
          row.monthly_revenue,
          row.placements_count,
          row.avg_revenue_per_placement,
          row.unique_clients,
          row.unique_recruiters
        ];
        csvContent += fields.join(",") + "\n";
      }
      filename = `revenue_${fromDate || fromDate || `range_${rangeDays}`}_${toDate || 'now'}.csv`;

    } else {
      // Default parsing analytics
      const csvResult = await query(`
        SELECT 
          pj.id as job_id,
          c.full_name as candidate_name,
          pj.filename,
          pj.status,
          pj.confidence_score,
          pj.started_at,
          pj.completed_at
        FROM parsing_jobs pj
        LEFT JOIN candidates c ON pj.candidate_id = c.id
        WHERE pj.started_at >= NOW() - CAST($1 || ' days' AS INTERVAL)
        ORDER BY pj.started_at DESC
      `, [rangeDays]);

      csvContent = "Job ID,Candidate Name,Filename,Status,Confidence,Started At,Completed At\n";
      for (const row of csvResult.rows) {
        const fields = [
          row.job_id,
          `"${(row.candidate_name || "").replace(/"/g, '""')}"`,
          `"${(row.filename || "").replace(/"/g, '""')}"`,
          row.status,
          row.confidence_score,
          row.started_at ? row.started_at.toISOString() : "",
          row.completed_at ? row.completed_at.toISOString() : ""
        ];
        csvContent += fields.join(",") + "\n";
      }
      filename = `parsing_analytics_range_${rangeDays}.csv`;
    }

    res.setHeader("Content-Type", "text/csv");
    res.setHeader("Content-Disposition", `attachment; filename=${filename}`);
    res.status(200).send(csvContent);
  } catch (error) {
    console.error("Export CSV error:", error);
    res.status(500).json({ error: "Internal server error", message: "Failed to export CSV" });
  }
};

// GET /api/analytics/export/pdf
export const exportPDF = async (req: Request, res: Response): Promise<void> => {
  try {
    const reportType = req.query.type as string || "parsing";
    const rangeDays = parseInt(req.query.range as string) || 30;
    const fromDate = req.query.from as string;
    const toDate = req.query.to as string;

    let pdfBuffer: Buffer;
    let filename = "";

    if (reportType === "client-performance") {
      let dateFilter = "";
      const queryParams: any[] = [];
      let paramIndex = 1;

      if (fromDate && toDate) {
        dateFilter = "WHERE p.placed_at BETWEEN $1 AND $2";
        queryParams.push(fromDate, toDate);
        paramIndex = 3;
      } else if (fromDate) {
        dateFilter = "WHERE p.placed_at >= $1";
        queryParams.push(fromDate);
        paramIndex = 2;
      } else if (toDate) {
        dateFilter = "WHERE p.placed_at <= $1";
        queryParams.push(toDate);
        paramIndex = 2;
      } else {
        dateFilter = "WHERE p.placed_at >= NOW() - CAST($1 || ' days' AS INTERVAL)";
        queryParams.push(rangeDays);
        paramIndex = 2;
      }

      const result = await query(`
        SELECT 
          COUNT(p.id)::int as total_placements,
          COALESCE(SUM(p.billing_amount), 0) as total_revenue,
          COUNT(DISTINCT p.client_id)::int as unique_clients
        FROM placements p
        ${dateFilter}
      `, queryParams);

      const { total_placements, total_revenue, unique_clients } = result.rows[0];

      const streamContent = `BT
/F1 12 Tf
70 700 Td
(Client Performance Report - ${fromDate || fromDate || `Range: ${rangeDays} days`} to ${toDate || 'now'}) Tj
0 -20 Td
(Total Placements: ${total_placements}) Tj
0 -15 Td
(Total Revenue: $${total_revenue.toFixed(2)}) Tj
0 -15 Td
(Unique Clients: ${unique_clients}) Tj
0 -15 Td
(Avg Revenue Per Placement: $${total_placements > 0 ? (total_revenue / total_placements).toFixed(2) : '0.00'}) Tj
ET`;

      pdfBuffer = Buffer.from(`%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> /MediaBox [0 0 612 792] /Contents 4 0 R >>
endobj
4 0 obj
<< /Length ${streamContent.length} >>
stream
${streamContent}
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000010 00000 n 
0000000079 00000 n 
0000000173 00000 n 
0000000301 00000 n 
trailer
<< /Size 5 /Root 1 0 R /Info 1 0 R >>
startxref
321
%%EOF`);

      filename = `client_performance_${fromDate || fromDate || `range_${rangeDays}`}_${toDate || 'now'}.pdf`;

    } else if (reportType === "placements") {
      let dateFilter = "";
      const queryParams: any[] = [];
      let paramIndex = 1;

      if (fromDate && toDate) {
        dateFilter = "WHERE p.placed_at BETWEEN $1 AND $2";
        queryParams.push(fromDate, toDate);
        paramIndex = 3;
      } else if (fromDate) {
        dateFilter = "WHERE p.placed_at >= $1";
        queryParams.push(fromDate);
        paramIndex = 2;
      } else if (toDate) {
        dateFilter = "WHERE p.placed_at <= $1";
        queryParams.push(toDate);
        paramIndex = 2;
      } else {
        dateFilter = "WHERE p.placed_at >= NOW() - CAST($1 || ' days' AS INTERVAL)";
        queryParams.push(rangeDays);
        paramIndex = 2;
      }

      const result = await query(`
        SELECT 
          COUNT(*)::int as total_placements,
          COALESCE(SUM(p.billing_amount), 0) as total_revenue,
          COUNT(DISTINCT p.client_id)::int as unique_clients
        FROM placements p
        ${dateFilter}
      `, queryParams);

      const { total_placements, total_revenue, unique_clients } = result.rows[0];

      const streamContent = `BT
/F1 12 Tf
70 700 Td
(Placements Report - ${fromDate || fromDate || `Range: ${rangeDays} days`} to ${toDate || 'now'}) Tj
0 -20 Td
(Total Placements: ${total_placements}) Tj
0 -15 Td
(Total Revenue: $${total_revenue.toFixed(2)}) Tj
0 -15 Td
(Unique Clients: ${unique_clients}) Tj
0 -15 Td
(Avg Revenue Per Placement: $${total_placements > 0 ? (total_revenue / total_placements).toFixed(2) : '0.00'}) Tj
ET`;

      pdfBuffer = Buffer.from(`%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> /MediaBox [0 0 612 792] /Contents 4 0 R >>
endobj
4 0 obj
<< /Length ${streamContent.length} >>
stream
${streamContent}
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000010 00000 n 
0000000079 00000 n 
0000000173 00000 n 
0000000301 00000 n 
trailer
<< /Size 5 /Root 1 0 R /Info 1 0 R >>
startxref
321
%%EOF`);

      filename = `placements_${fromDate || fromDate || `range_${rangeDays}`}_${toDate || 'now'}.pdf`;

    } else if (reportType === "revenue") {
      let dateFilter = "";
      const queryParams: any[] = [];
      let paramIndex = 1;

      if (fromDate && toDate) {
        dateFilter = "WHERE p.placed_at BETWEEN $1 AND $2";
        queryParams.push(fromDate, toDate);
        paramIndex = 3;
      } else if (fromDate) {
        dateFilter = "WHERE p.placed_at >= $1";
        queryParams.push(fromDate);
        paramIndex = 2;
      } else if (toDate) {
        dateFilter = "WHERE p.placed_at <= $1";
        queryParams.push(toDate);
        paramIndex = 2;
      } else {
        dateFilter = "WHERE p.placed_at >= NOW() - CAST($1 || ' days' AS INTERVAL)";
        queryParams.push(rangeDays);
        paramIndex = 2;
      }

      const result = await query(`
        SELECT 
          COUNT(*)::int as total_placements,
          COALESCE(SUM(p.billing_amount), 0) as total_revenue,
          COUNT(DISTINCT p.client_id)::int as unique_clients
        FROM placements p
        ${dateFilter}
      `, queryParams);

      const { total_placements, total_revenue, unique_clients } = result.rows[0];

      const streamContent = `BT
/F1 12 Tf
70 700 Td
(Revenue Report - ${fromDate || fromDate || `Range: ${rangeDays} days`} to ${toDate || 'now'}) Tj
0 -20 Td
(Total Placements: ${total_placements}) Tj
0 -15 Td
(Total Revenue: $${total_revenue.toFixed(2)}) Tj
0 -15 Td
(Unique Clients: ${unique_clients}) Tj
0 -15 Td
(Avg Revenue Per Placement: $${total_placements > 0 ? (total_revenue / total_placements).toFixed(2) : '0.00'}) Tj
ET`;

      pdfBuffer = Buffer.from(`%PDF-1.4
1 0 obj
<< /Type /Catalog /Pages 2 0 R >>
endobj
2 0 obj
<< /Type /Pages /Kids [3 0 R] /Count 1 >>
endobj
3 0 obj
<< /Type /Page /Parent 2 0 R /Resources << /Font << /F1 << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> >> /MediaBox [0 0 612 792] /Contents 4 0 R >>
endobj
4 0 obj
<< /Length ${streamContent.length} >>
stream
${streamContent}
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000010 00000 n 
0000000079 00000 n 
0000000173 00000 n 
0000000301 00000 n 
trailer
<< /Size 5 /Root 1 0 R /Info 1 0 R >>
startxref
321
%%EOF`);

      filename = `revenue_${fromDate || fromDate || `range_${rangeDays}`}_${toDate || 'now'}.pdf`;

    } else {
      // Default parsing analytics
      const statsResult = await query(`
        SELECT 
          COUNT(*)::int as total,
          COUNT(*) FILTER (WHERE status = 'completed')::int as success,
          COUNT(*) FILTER (WHERE status = 'failed')::int as failed,
          COALESCE(AVG(EXTRACT(EPOCH FROM (completed_at - started_at))), 0)::float as avg_time,
          COALESCE(AVG(confidence_score), 0)::float as avg_conf
        FROM parsing_jobs
        WHERE started_at >= NOW() - CAST($1 || ' days' AS INTERVAL)
      `, [rangeDays]);

      const { total, success, failed, avg_time, avg_conf } = statsResult.rows[0];
      const success_rate = total > 0 ? (success / total) * 100 : 0;

      pdfBuffer = generatePDFBuffer({
        range: rangeDays,
        total,
        success,
        failed,
        success_rate,
        avg_time,
        avg_confidence: avg_conf
      });

      filename = `parsing_analytics_range_${rangeDays}.pdf`;
    }

    res.setHeader("Content-Type", "application/pdf");
    res.setHeader("Content-Disposition", `attachment; filename=${filename}`);
    res.status(200).send(pdfBuffer);
  } catch (error) {
    console.error("Export PDF error:", error);
    res.status(500).json({ error: "Internal server error", message: "Failed to export PDF" });
  }
};

// GET /api/analytics/team-closures?from=&to=
export const getTeamClosures = async (req: Request, res: Response): Promise<void> => {
  try {
    const userId = (req as any).user?.id;
    const userRole = (req as any).user?.role;
    const tenantId = (req as any).user?.tenant_id || "default";
    const fromDate = req.query.from as string;
    const toDate = req.query.to as string;
    const teamLeadId = req.query.teamLeadId as string;

    if (!userId) {
      res.status(401).json({
        error: "Unauthorized",
        message: "User ID is required",
      });
      return;
    }

    // Only team leads and admins can access this endpoint
    if (userRole !== 'team_lead' && userRole !== 'admin') {
      res.status(403).json({
        error: "Forbidden",
        message: "Only team leads and admins can access team closures analytics",
      });
      return;
    }

    // Admins can filter by specific team lead, but team leads can only see their own team
    const effectiveTeamLeadId = (userRole === 'admin' && teamLeadId) ? teamLeadId : userId;

    const client = await getClient();
    try {
      let dateFilter = "";
      const queryParams: any[] = [effectiveTeamLeadId, tenantId];
      let paramIndex = 3;

      if (fromDate && toDate) {
        dateFilter = "AND s.updated_at BETWEEN $3 AND $4";
        queryParams.push(fromDate, toDate);
        paramIndex = 5;
      } else if (fromDate) {
        dateFilter = "AND s.updated_at >= $3";
        queryParams.push(fromDate);
        paramIndex = 4;
      } else if (toDate) {
        dateFilter = "AND s.updated_at <= $3";
        queryParams.push(toDate);
        paramIndex = 4;
      }

      const closuresQuery = `
        SELECT 
          TO_CHAR(s.updated_at, 'YYYY-MM-DD') as date,
          COUNT(*)::int as closures_count,
          COUNT(DISTINCT s.submitted_by)::int as unique_recruiters,
          COUNT(DISTINCT s.job_id)::int as unique_jobs,
          COUNT(DISTINCT s.candidate_id)::int as unique_candidates
        FROM submissions s
        JOIN job_recruiter_assignments jra ON s.job_id = jra.job_id
        JOIN users u ON jra.recruiter_id = u.id
        WHERE u.team_lead_id = $1 
          AND s.tenant_id = $2
          AND s.status = 'Offer Accepted'
          ${dateFilter}
        GROUP BY TO_CHAR(s.updated_at, 'YYYY-MM-DD')
        ORDER BY date ASC
      `;

      const closuresResult = await client.query(closuresQuery, queryParams);

      // Also get summary stats
      const summaryQuery = `
        SELECT 
          COUNT(*)::int as total_closures,
          COUNT(DISTINCT s.submitted_by)::int as total_recruiters,
          COUNT(DISTINCT s.job_id)::int as total_jobs,
          COUNT(DISTINCT s.candidate_id)::int as total_candidates,
          MIN(s.updated_at) as first_closure_date,
          MAX(s.updated_at) as last_closure_date
        FROM submissions s
        JOIN job_recruiter_assignments jra ON s.job_id = jra.job_id
        JOIN users u ON jra.recruiter_id = u.id
        WHERE u.team_lead_id = $1 
          AND s.tenant_id = $2
          AND s.status = 'Offer Accepted'
          ${dateFilter}
      `;

      const summaryResult = await client.query(summaryQuery, queryParams);

      res.json({
        daily_closures: closuresResult.rows,
        summary: summaryResult.rows[0],
      });
    } finally {
      client.release();
    }
  } catch (error) {
    console.error("Get team closures error:", error);
    res.status(500).json({ error: "Internal server error", message: "Failed to retrieve team closures" });
  }
};

// GET /api/analytics/submission-success-rate?from=&to=
export const getSubmissionSuccessRate = async (req: Request, res: Response): Promise<void> => {
  try {
    const userId = (req as any).user?.id;
    const userRole = (req as any).user?.role;
    const tenantId = (req as any).user?.tenant_id || "default";
    const fromDate = req.query.from as string;
    const toDate = req.query.to as string;
    const teamLeadId = req.query.teamLeadId as string;

    if (!userId) {
      res.status(401).json({
        error: "Unauthorized",
        message: "User ID is required",
      });
      return;
    }

    // Only team leads and admins can access this endpoint
    if (userRole !== 'team_lead' && userRole !== 'admin') {
      res.status(403).json({
        error: "Forbidden",
        message: "Only team leads and admins can access submission success rate analytics",
      });
      return;
    }

    // Admins can filter by specific team lead, but team leads can only see their own team
    const effectiveTeamLeadId = (userRole === 'admin' && teamLeadId) ? teamLeadId : userId;

    const client = await getClient();
    try {
      let dateFilter = "";
      const queryParams: any[] = [effectiveTeamLeadId, tenantId];
      let paramIndex = 3;

      if (fromDate && toDate) {
        dateFilter = "AND s.submitted_at BETWEEN $3 AND $4";
        queryParams.push(fromDate, toDate);
        paramIndex = 5;
      } else if (fromDate) {
        dateFilter = "AND s.submitted_at >= $3";
        queryParams.push(fromDate);
        paramIndex = 4;
      } else if (toDate) {
        dateFilter = "AND s.submitted_at <= $3";
        queryParams.push(toDate);
        paramIndex = 4;
      }

      const successRateQuery = `
        SELECT 
          TO_CHAR(s.submitted_at, 'YYYY-MM-DD') as date,
          COUNT(*)::int as total_submissions,
          COUNT(*) FILTER (WHERE s.status IN ('Offer Accepted', 'Interview Scheduled', 'Shortlisted'))::int as successful_submissions,
          COUNT(*) FILTER (WHERE s.status = 'Rejected')::int as rejected_submissions,
          ROUND(
            (COUNT(*) FILTER (WHERE s.status IN ('Offer Accepted', 'Interview Scheduled', 'Shortlisted'))::float / 
             NULLIF(COUNT(*), 0)) * 100, 2
          ) as success_rate
        FROM submissions s
        JOIN job_recruiter_assignments jra ON s.job_id = jra.job_id
        JOIN users u ON jra.recruiter_id = u.id
        WHERE u.team_lead_id = $1 
          AND s.tenant_id = $2
          ${dateFilter}
        GROUP BY TO_CHAR(s.submitted_at, 'YYYY-MM-DD')
        ORDER BY date ASC
      `;

      const successRateResult = await client.query(successRateQuery, queryParams);

      // Also get summary stats
      const summaryQuery = `
        SELECT 
          COUNT(*)::int as total_submissions,
          COUNT(*) FILTER (WHERE s.status IN ('Offer Accepted', 'Interview Scheduled', 'Shortlisted'))::int as total_successful,
          COUNT(*) FILTER (WHERE s.status = 'Rejected')::int as total_rejected,
          COUNT(*) FILTER (WHERE s.status = 'Offer Accepted')::int as total_placed,
          ROUND(
            (COUNT(*) FILTER (WHERE s.status IN ('Offer Accepted', 'Interview Scheduled', 'Shortlisted'))::float / 
             NULLIF(COUNT(*), 0)) * 100, 2
          ) as overall_success_rate
        FROM submissions s
        JOIN job_recruiter_assignments jra ON s.job_id = jra.job_id
        JOIN users u ON jra.recruiter_id = u.id
        WHERE u.team_lead_id = $1 
          AND s.tenant_id = $2
          ${dateFilter}
      `;

      const summaryResult = await client.query(summaryQuery, queryParams);

      // Breakdown by recruiter
      const recruiterBreakdownQuery = `
        SELECT 
          u.id as recruiter_id,
          u.email as recruiter_email,
          u.full_name as recruiter_name,
          COUNT(*)::int as total_submissions,
          COUNT(*) FILTER (WHERE s.status IN ('Offer Accepted', 'Interview Scheduled', 'Shortlisted'))::int as successful_submissions,
          COUNT(*) FILTER (WHERE s.status = 'Rejected')::int as rejected_submissions,
          ROUND(
            (COUNT(*) FILTER (WHERE s.status IN ('Offer Accepted', 'Interview Scheduled', 'Shortlisted'))::float / 
             NULLIF(COUNT(*), 0)) * 100, 2
          ) as success_rate
        FROM submissions s
        JOIN job_recruiter_assignments jra ON s.job_id = jra.job_id
        JOIN users u ON jra.recruiter_id = u.id
        WHERE u.team_lead_id = $1 
          AND s.tenant_id = $2
          ${dateFilter}
        GROUP BY u.id, u.email, u.full_name
        ORDER BY success_rate DESC
      `;

      const recruiterBreakdownResult = await client.query(recruiterBreakdownQuery, queryParams);

      res.json({
        daily_success_rates: successRateResult.rows,
        summary: summaryResult.rows[0],
        recruiter_breakdown: recruiterBreakdownResult.rows,
      });
    } finally {
      client.release();
    }
  } catch (error) {
    console.error("Get submission success rate error:", error);
    res.status(500).json({ error: "Internal server error", message: "Failed to retrieve submission success rate" });
  }
};

// GET /api/analytics/new-clients-acquired
export const getNewClientsAcquired = async (req: AuthenticatedRequest, res: Response): Promise<void> => {
  try {
    const userId = req.user?.id;
    const userRole = req.user?.role;
    const bdmId = req.query.bdmId as string;
    const fromDate = req.query.from as string;
    const toDate = req.query.to as string;

    if (!userId) {
      res.status(401).json({ error: "Unauthorized" });
      return;
    }

    const client = await getClient();
    try {
      // Build date filter
      let dateFilter = "";
      const queryParams: any[] = [];
      let paramIndex = 1;

      if (fromDate && toDate) {
        dateFilter = "AND cph.changed_at BETWEEN $1 AND $2";
        queryParams.push(fromDate, toDate);
        paramIndex = 3;
      } else if (fromDate) {
        dateFilter = "AND cph.changed_at >= $1";
        queryParams.push(fromDate);
        paramIndex = 2;
      } else if (toDate) {
        dateFilter = "AND cph.changed_at <= $1";
        queryParams.push(toDate);
        paramIndex = 2;
      }

      // Build user scope filter
      let userFilter = "";
      if (userRole === 'admin' && bdmId) {
        userFilter = "AND cph.changed_by = $" + paramIndex;
        queryParams.push(bdmId);
        paramIndex++;
      } else if (userRole !== 'admin') {
        userFilter = "AND cph.changed_by = $" + paramIndex;
        queryParams.push(userId);
        paramIndex++;
      }

      const result = await client.query(
        `SELECT 
          TO_CHAR(cph.changed_at, 'YYYY-MM') as month,
          COUNT(*)::int as count
         FROM client_pipeline_history cph
         WHERE cph.to_stage = 'won'
         ${dateFilter}
         ${userFilter}
         GROUP BY TO_CHAR(cph.changed_at, 'YYYY-MM')
         ORDER BY month ASC`,
        queryParams
      );

      res.json(result.rows);
    } finally {
      client.release();
    }
  } catch (error) {
    console.error("Get new clients acquired error:", error);
    res.status(500).json({ error: "Internal server error", message: "Failed to retrieve new clients acquired" });
  }
};

// GET /api/analytics/revenue-generated
export const getRevenueGenerated = async (req: AuthenticatedRequest, res: Response): Promise<void> => {
  try {
    const userId = req.user?.id;
    const userRole = req.user?.role;
    const bdmId = req.query.bdmId as string;
    const fromDate = req.query.from as string;
    const toDate = req.query.to as string;

    if (!userId) {
      res.status(401).json({ error: "Unauthorized" });
      return;
    }

    const client = await getClient();
    try {
      // Build date filter
      let dateFilter = "";
      const queryParams: any[] = [];
      let paramIndex = 1;

      if (fromDate && toDate) {
        dateFilter = "AND p.placed_at BETWEEN $1 AND $2";
        queryParams.push(fromDate, toDate);
        paramIndex = 3;
      } else if (fromDate) {
        dateFilter = "AND p.placed_at >= $1";
        queryParams.push(fromDate);
        paramIndex = 2;
      } else if (toDate) {
        dateFilter = "AND p.placed_at <= $1";
        queryParams.push(toDate);
        paramIndex = 2;
      }

      // Build user scope filter
      let userFilter = "";
      if (userRole === 'admin' && bdmId) {
        userFilter = "AND c.owner_user_id = $" + paramIndex;
        queryParams.push(bdmId);
        paramIndex++;
      } else if (userRole !== 'admin') {
        userFilter = "AND c.owner_user_id = $" + paramIndex;
        queryParams.push(userId);
        paramIndex++;
      }

      const result = await client.query(
        `SELECT 
          TO_CHAR(p.placed_at, 'YYYY-MM') as month,
          COALESCE(SUM(p.billing_amount), 0) as total_revenue
         FROM placements p
         JOIN job_descriptions jd ON p.job_id = jd.id
         JOIN clients c ON jd.client_id = c.id
         WHERE 1=1
         ${dateFilter}
         ${userFilter}
         GROUP BY TO_CHAR(p.placed_at, 'YYYY-MM')
         ORDER BY month ASC`,
        queryParams
      );

      res.json(result.rows);
    } finally {
      client.release();
    }
  } catch (error) {
    console.error("Get revenue generated error:", error);
    res.status(500).json({ error: "Internal server error", message: "Failed to retrieve revenue generated" });
  }
};

// GET /api/analytics/open-opportunities
export const getOpenOpportunities = async (req: AuthenticatedRequest, res: Response): Promise<void> => {
  try {
    const userId = req.user?.id;
    const userRole = req.user?.role;
    const bdmId = req.query.bdmId as string;
    const fromDate = req.query.from as string;
    const toDate = req.query.to as string;

    if (!userId) {
      res.status(401).json({ error: "Unauthorized" });
      return;
    }

    const client = await getClient();
    try {
      // Build date filter (for pipeline stage changes)
      let dateFilter = "";
      const queryParams: any[] = [];
      let paramIndex = 1;

      if (fromDate && toDate) {
        dateFilter = "AND c.updated_at BETWEEN $1 AND $2";
        queryParams.push(fromDate, toDate);
        paramIndex = 3;
      } else if (fromDate) {
        dateFilter = "AND c.updated_at >= $1";
        queryParams.push(fromDate);
        paramIndex = 2;
      } else if (toDate) {
        dateFilter = "AND c.updated_at <= $1";
        queryParams.push(toDate);
        paramIndex = 2;
      }

      // Build user scope filter
      let userFilter = "";
      if (userRole === 'admin' && bdmId) {
        userFilter = "AND c.owner_user_id = $" + paramIndex;
        queryParams.push(bdmId);
        paramIndex++;
      } else if (userRole !== 'admin') {
        userFilter = "AND c.owner_user_id = $" + paramIndex;
        queryParams.push(userId);
        paramIndex++;
      }

      // Get current snapshot of pipeline funnel
      const result = await client.query(
        `SELECT 
          c.pipeline_stage,
          COUNT(*)::int as count
         FROM clients c
         WHERE c.is_archived = false
         ${dateFilter}
         ${userFilter}
         GROUP BY c.pipeline_stage
         ORDER BY 
           CASE c.pipeline_stage
             WHEN 'prospect' THEN 1
             WHEN 'qualified' THEN 2
             WHEN 'proposal_sent' THEN 3
             WHEN 'negotiation' THEN 4
             WHEN 'won' THEN 5
             WHEN 'lost' THEN 6
             ELSE 7
           END`,
        queryParams
      );

      res.json(result.rows);
    } finally {
      client.release();
    }
  } catch (error) {
    console.error("Get open opportunities error:", error);
    res.status(500).json({ error: "Internal server error", message: "Failed to retrieve open opportunities" });
  }
};
