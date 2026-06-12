import os

file_path = r"c:\Lalataksha V Company\Main-branch\Lakshya-LLM-Resume-Parser\backend\src\models\candidate.model.ts"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Target CandidateModel.create method
target_create = """  static async create(client: any, data: Partial<Candidate>): Promise<Candidate> {
    const id = data.id || crypto.randomUUID();
    const result = await client.query(
      `INSERT INTO candidates (
        id, email, phone, full_name, status, summary, resume_file_path,
        consent_given, tenant_id, review_status, created_at, updated_at
      ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, NOW(), NOW()) RETURNING *`,
      [
        id,
        data.email || null,
        data.phone || null,
        data.full_name || data.name || null,
        data.status || "pending",
        data.summary || null,
        data.resume_path || data.resume_file_path || null,
        data.consent_given !== undefined ? data.consent_given : false,
        data.tenant_id || "default",
        data.review_status || "pending"
      ]
    );
    return result.rows[0];
  }"""

replacement_create = """  static async create(client: any, data: Partial<Candidate>): Promise<Candidate> {
    const id = data.id || crypto.randomUUID();
    const emailHash = data.email
      ? crypto.createHash("md5").update(data.email.trim().toLowerCase()).digest("hex")
      : null;
      
    const result = await client.query(
      `INSERT INTO candidates (
        id, email, phone, full_name, status, summary, resume_file_path,
        consent_given, tenant_id, review_status, email_hash, created_at, updated_at
      ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, NOW(), NOW()) RETURNING *`,
      [
        id,
        data.email || null,
        data.phone || null,
        data.full_name || data.name || null,
        data.status || "pending",
        data.summary || null,
        data.resume_path || data.resume_file_path || null,
        data.consent_given !== undefined ? data.consent_given : false,
        data.tenant_id || "default",
        data.review_status || "pending",
        emailHash
      ]
    );
    return result.rows[0];
  }"""

# 2. Target CandidateModel.update method
target_update = """  static async update(client: any, id: string, data: Partial<Candidate>): Promise<Candidate | null> {
    const result = await client.query(
      "UPDATE candidates SET email = COALESCE($1, email), phone = COALESCE($2, phone), full_name = COALESCE($3, full_name), status = COALESCE($4, status), summary = COALESCE($5, summary), updated_at = NOW() WHERE id = $6 RETURNING *",
      [
        data.email,
        data.phone,
        data.full_name || data.name,
        data.status,
        data.summary,
        id
      ]
    );
    return result.rows[0] || null;
  }"""

replacement_update = """  static async update(client: any, id: string, data: Partial<Candidate>): Promise<Candidate | null> {
    const emailHash = data.email
      ? crypto.createHash("md5").update(data.email.trim().toLowerCase()).digest("hex")
      : null;
      
    const result = await client.query(
      `UPDATE candidates 
       SET email = COALESCE($1, email), 
           phone = COALESCE($2, phone), 
           full_name = COALESCE($3, full_name), 
           status = COALESCE($4, status), 
           summary = COALESCE($5, summary), 
           email_hash = COALESCE($6, email_hash),
           updated_at = NOW() 
       WHERE id = $7 
       RETURNING *`,
      [
        data.email,
        data.phone,
        data.full_name || data.name,
        data.status,
        data.summary,
        emailHash,
        id
      ]
    );
    return result.rows[0] || null;
  }"""

# Replace create handling LF and CRLF
if target_create in content:
    content = content.replace(target_create, replacement_create)
    print("Replaced create method (LF)")
elif target_create.replace("\n", "\r\n") in content:
    content = content.replace(target_create.replace("\n", "\r\n"), replacement_create.replace("\n", "\r\n"))
    print("Replaced create method (CRLF)")
else:
    print("Create method target not found!")

# Replace update handling LF and CRLF
if target_update in content:
    content = content.replace(target_update, replacement_update)
    print("Replaced update method (LF)")
elif target_update.replace("\n", "\r\n") in content:
    content = content.replace(target_update.replace("\n", "\r\n"), replacement_update.replace("\n", "\r\n"))
    print("Replaced update method (CRLF)")
else:
    print("Update method target not found!")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
