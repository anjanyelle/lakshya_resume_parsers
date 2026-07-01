import { Request, Response } from "express";
import { getClient } from "../database/db";
import { authenticateToken, requirePermission } from "../middleware/auth.middleware";

// Types
interface CreateCommunicationRequest {
  client_id: string;
  contact_id?: string;
  communication_type: string;
  subject: string;
  notes: string;
  follow_up_date?: string;
}

interface Communication {
  id: string;
  client_id: string;
  contact_id?: string;
  communication_type: string;
  subject: string;
  notes: string;
  follow_up_date?: string;
  logged_by: string;
  created_at: string;
}

// Create communication log
export const createCommunication = async (req: Request, res: Response): Promise<void> => {
  try {
    const { client_id, contact_id, communication_type, subject, notes, follow_up_date }: CreateCommunicationRequest = req.body;
    const userId = (req as any).user?.id;
    const tenantId = (req as any).user?.tenant_id || "default";

    // Validate required fields
    if (!client_id || !communication_type || !subject || !notes) {
      res.status(400).json({
        error: "Bad Request",
        message: "client_id, communication_type, subject, and notes are required",
        code: "MISSING_REQUIRED_FIELDS"
      });
      return;
    }

    if (!userId) {
      res.status(401).json({
        error: "Unauthorized",
        message: "User ID is required",
        code: "USER_ID_REQUIRED"
      });
      return;
    }

    const client = await getClient();
    try {
      await client.query("BEGIN");

      // Validate client belongs to user (ownership check)
      const clientCheck = await client.query(
        `SELECT id, owner_user_id FROM clients WHERE id = $1 AND tenant_id = $2`,
        [client_id, tenantId]
      );

      if (clientCheck.rows.length === 0) {
        await client.query("ROLLBACK");
        res.status(404).json({
          error: "Not Found",
          message: "Client not found",
          code: "CLIENT_NOT_FOUND"
        });
        return;
      }

      const clientData = clientCheck.rows[0];

      // Check if user owns the client
      if (clientData.owner_user_id !== userId) {
        await client.query("ROLLBACK");
        res.status(403).json({
          error: "Forbidden",
          message: "You can only log communications for your own clients",
          code: "FORBIDDEN"
        });
        return;
      }

      // If contact_id is provided, validate it belongs to the client
      if (contact_id) {
        const contactCheck = await client.query(
          `SELECT id FROM client_contacts WHERE id = $1 AND client_id = $2 AND tenant_id = $3`,
          [contact_id, client_id, tenantId]
        );

        if (contactCheck.rows.length === 0) {
          await client.query("ROLLBACK");
          res.status(404).json({
            error: "Not Found",
            message: "Contact not found or does not belong to this client",
            code: "CONTACT_NOT_FOUND"
          });
          return;
        }
      }

      // Validate follow_up_date if provided
      if (follow_up_date) {
        const followUpDate = new Date(follow_up_date);
        if (isNaN(followUpDate.getTime())) {
          await client.query("ROLLBACK");
          res.status(400).json({
            error: "Bad Request",
            message: "follow_up_date must be a valid date",
            code: "INVALID_DATE"
          });
          return;
        }
      }

      // Create communication log
      const communicationResult = await client.query(
        `INSERT INTO client_communications (client_id, contact_id, communication_type, subject, notes, follow_up_date, logged_by, created_at)
         VALUES ($1, $2, $3, $4, $5, $6, $7, NOW())
         RETURNING *`,
        [client_id, contact_id || null, communication_type, subject, notes, follow_up_date || null, userId]
      );

      const communication = communicationResult.rows[0];

      // Insert audit log
      await client.query(
        `INSERT INTO audit_logs (action, table_name, record_id, user_id, tenant_id, created_at, details)
         VALUES ('LOG_COMMUNICATION', 'client_communications', $1, $2, $3, NOW(), $4)`,
        [communication.id, userId, tenantId, JSON.stringify({
          client_id,
          contact_id,
          communication_type,
          subject,
          notes,
          follow_up_date
        })]
      );

      await client.query("COMMIT");

      res.status(201).json({
        message: "Communication logged successfully",
        communication
      });

    } catch (error) {
      await client.query("ROLLBACK");
      console.error("Create communication error:", error);
      res.status(500).json({
        error: "Internal Server Error",
        message: "Failed to log communication",
        code: "CREATE_COMMUNICATION_FAILED"
      });
    } finally {
      client.release();
    }
  } catch (error) {
    console.error("Create communication error:", error);
    res.status(500).json({
      error: "Internal Server Error",
      message: "Failed to log communication",
      code: "CREATE_COMMUNICATION_FAILED"
    });
  }
};

// Get communications with optional filters
export const getCommunications = async (req: Request, res: Response): Promise<void> => {
  try {
    const { clientId, from, to } = req.query;
    const userId = (req as any).user?.id;
    const tenantId = (req as any).user?.tenant_id || "default";

    if (!userId) {
      res.status(401).json({
        error: "Unauthorized",
        message: "User ID is required",
        code: "USER_ID_REQUIRED"
      });
      return;
    }

    const client = await getClient();
    try {
      // Build query with optional filters
      let whereClause = "WHERE cc.tenant_id = $1";
      const queryParams: any[] = [tenantId];
      let paramCount = 1;

      // Filter by user's clients (ownership check)
      whereClause += ` AND c.owner_user_id = $${paramCount}`;
      queryParams.push(userId);
      paramCount++;

      if (clientId) {
        whereClause += ` AND cc.client_id = $${paramCount}`;
        queryParams.push(clientId);
        paramCount++;
      }

      if (from) {
        whereClause += ` AND cc.created_at >= $${paramCount}`;
        queryParams.push(from);
        paramCount++;
      }

      if (to) {
        whereClause += ` AND cc.created_at <= $${paramCount}`;
        queryParams.push(to);
        paramCount++;
      }

      const query = `
        SELECT 
          cc.id,
          cc.client_id,
          cc.contact_id,
          cc.communication_type,
          cc.subject,
          cc.notes,
          cc.follow_up_date,
          cc.logged_by,
          cc.created_at,
          c.company_name,
          ctc.first_name as contact_first_name,
          ctc.last_name as contact_last_name,
          ctc.email as contact_email,
          u.first_name as logged_by_name,
          u.last_name as logged_by_last_name
        FROM client_communications cc
        JOIN clients c ON cc.client_id = c.id
        LEFT JOIN client_contacts ctc ON cc.contact_id = ctc.id
        LEFT JOIN users u ON cc.logged_by = u.id
        ${whereClause}
        ORDER BY cc.created_at DESC
      `;

      const result = await client.query(query, queryParams);

      res.json({
        communications: result.rows,
        count: result.rows.length
      });

    } finally {
      client.release();
    }
  } catch (error) {
    console.error("Get communications error:", error);
    res.status(500).json({
      error: "Internal Server Error",
      message: "Failed to fetch communications",
      code: "FETCH_COMMUNICATIONS_FAILED"
    });
  }
};

// Get follow-ups due for the current user
export const getFollowUpsDue = async (req: Request, res: Response): Promise<void> => {
  try {
    const userId = (req as any).user?.id;
    const tenantId = (req as any).user?.tenant_id || "default";

    if (!userId) {
      res.status(401).json({
        error: "Unauthorized",
        message: "User ID is required",
        code: "USER_ID_REQUIRED"
      });
      return;
    }

    const client = await getClient();
    try {
      const query = `
        SELECT 
          cc.id,
          cc.client_id,
          cc.contact_id,
          cc.communication_type,
          cc.subject,
          cc.notes,
          cc.follow_up_date,
          cc.logged_by,
          cc.created_at,
          c.company_name,
          ctc.first_name as contact_first_name,
          ctc.last_name as contact_last_name,
          ctc.email as contact_email,
          ctc.phone as contact_phone
        FROM client_communications cc
        JOIN clients c ON cc.client_id = c.id
        LEFT JOIN client_contacts ctc ON cc.contact_id = ctc.id
        WHERE cc.tenant_id = $1
          AND cc.follow_up_date IS NOT NULL
          AND cc.follow_up_date <= NOW()
          AND cc.logged_by = $2
        ORDER BY cc.follow_up_date ASC
      `;

      const result = await client.query(query, [tenantId, userId]);

      res.json({
        followUps: result.rows,
        count: result.rows.length
      });

    } finally {
      client.release();
    }
  } catch (error) {
    console.error("Get follow-ups due error:", error);
    res.status(500).json({
      error: "Internal Server Error",
      message: "Failed to fetch follow-ups due",
      code: "FETCH_FOLLOW_UPS_FAILED"
    });
  }
};